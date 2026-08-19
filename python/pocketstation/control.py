"""Typed synchronous client for the PocketStation control-plane Session API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import TracebackType
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import httpx

from .errors import PocketStationError

_MAX_ERROR_BODY_BYTES = 4_096
_MAX_JSON_BODY_BYTES = 65_536


class ControlPlaneError(PocketStationError):
    """A configuration, transport, HTTP, or decoding control-plane failure."""

    def __init__(
        self,
        message: str,
        code: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message, code)
        self.status_code = status_code


class SessionId(str):
    """Validated Session identifier safe for one URL path segment."""

    def __new__(cls, value: str) -> SessionId:
        if not value or not all(
            character.isascii() and (character.isalnum() or character in "-_")
            for character in value
        ):
            raise ValueError(
                "Session ID must contain only ASCII letters, digits, '-' or '_'"
            )
        return str.__new__(cls, value)


class SecretToken:
    """Credential that redacts itself unless exposure is explicitly requested."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not value:
            raise ValueError("credential token must not be empty")
        self._value = value

    def expose_secret(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "SecretToken('[redacted]')"


@dataclass(frozen=True, slots=True)
class IceServer:
    urls: tuple[str, ...]
    username: str | None = None
    credential: str | None = None


@dataclass(frozen=True, slots=True)
class SessionCredentials:
    session_id: SessionId
    source_token: SecretToken
    subscriber_token: SecretToken
    whip_url: str | None = None
    whep_url: str | None = None
    ice_servers: tuple[IceServer, ...] = ()


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    session_id: SessionId
    source_active: bool
    subscription_count: int
    codec: str


@dataclass(frozen=True, slots=True)
class SubscriberCredentials:
    session_id: SessionId
    subscriber_token: SecretToken


class ControlClient:
    """Reusable, bounded HTTP client for Session lifecycle operations."""

    def __init__(
        self,
        control_plane_url: str,
        *,
        timeout_seconds: float | None = 10.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.control_plane_url = _normalize_base_url(control_plane_url)
        self._timeout_seconds = timeout_seconds
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(timeout=timeout_seconds)
        self._closed = False

    def create_session(
        self,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionCredentials:
        payload = self._json_request(
            "POST",
            "v1/sessions",
            expected_status=201,
            timeout_seconds=timeout_seconds,
        )
        return _session_credentials(payload)

    def session(
        self,
        session_id: str | SessionId,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionSnapshot:
        identifier = SessionId(str(session_id))
        payload = self._json_request(
            "GET",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=200,
            timeout_seconds=timeout_seconds,
        )
        return _session_snapshot(payload)

    def issue_subscriber_credentials(
        self,
        session_id: str | SessionId,
        *,
        timeout_seconds: float | None = None,
    ) -> SubscriberCredentials:
        identifier = SessionId(str(session_id))
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/subscribe",
            expected_status=200,
            timeout_seconds=timeout_seconds,
        )
        return _subscriber_credentials(payload)

    def delete_session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> None:
        identifier = SessionId(str(session_id))
        self._request(
            "DELETE",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=204,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            expect_json=False,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> ControlClient:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _json_request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        timeout_seconds: float | None,
    ) -> dict[str, Any]:
        return self._request(
            method,
            path,
            expected_status=expected_status,
            timeout_seconds=timeout_seconds,
            authorization=None,
            expect_json=True,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        timeout_seconds: float | None,
        authorization: SecretToken | None,
        expect_json: bool,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        headers = {}
        redacted_values: tuple[str, ...] = ()
        if authorization is not None:
            exposed = authorization.expose_secret()
            headers["Authorization"] = f"Bearer {exposed}"
            redacted_values = (exposed,)
        timeout = self._timeout_seconds if timeout_seconds is None else timeout_seconds
        try:
            with self._http_client.stream(
                method,
                urljoin(self.control_plane_url, path),
                headers=headers,
                timeout=timeout,
            ) as response:
                if response.status_code != expected_status:
                    body = _read_bounded(response.iter_bytes(), _MAX_ERROR_BODY_BYTES)
                    detail = body.decode("utf-8", errors="replace")
                    for value in redacted_values:
                        detail = detail.replace(value, "[redacted]")
                    raise ControlPlaneError(
                        f"control-plane returned HTTP {response.status_code}: {detail}",
                        "control.http_status",
                        status_code=response.status_code,
                    )
                if not expect_json:
                    return {}
                body = _read_bounded(response.iter_bytes(), _MAX_JSON_BODY_BYTES)
        except ControlPlaneError:
            raise
        except httpx.HTTPError as error:
            raise ControlPlaneError(
                f"control-plane request failed: {error}",
                "control.request",
            ) from error
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ControlPlaneError(
                f"control-plane response could not be decoded: {error}",
                "control.response_decode",
            ) from error
        if not isinstance(payload, dict):
            raise ControlPlaneError(
                "control-plane response must be a JSON object",
                "control.response_decode",
            )
        return payload


def _normalize_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("control_plane_url must be an absolute http or https URL")
    return value.split("?", 1)[0].split("#", 1)[0].rstrip("/") + "/"


def _read_bounded(chunks: Any, limit_bytes: int) -> bytes:
    body = bytearray()
    for chunk in chunks:
        remaining = limit_bytes + 1 - len(body)
        if remaining <= 0:
            break
        body.extend(chunk[:remaining])
    if len(body) > limit_bytes:
        raise ControlPlaneError(
            f"control-plane response exceeds {limit_bytes} bytes",
            "control.response_too_large",
        )
    return bytes(body)


def _required(payload: dict[str, Any], key: str, expected_type: type[Any]) -> Any:
    value = payload.get(key)
    if not isinstance(value, expected_type):
        raise ControlPlaneError(
            f"control-plane response field {key!r} has the wrong type",
            "control.response_decode",
        )
    return value


def _ice_servers(payload: dict[str, Any]) -> tuple[IceServer, ...]:
    raw_servers = payload.get("ice_servers", [])
    if not isinstance(raw_servers, list):
        raise ControlPlaneError(
            "control-plane response field 'ice_servers' has the wrong type",
            "control.response_decode",
        )
    servers: list[IceServer] = []
    for raw_server in raw_servers:
        if not isinstance(raw_server, dict):
            raise ControlPlaneError(
                "control-plane ICE server must be a JSON object",
                "control.response_decode",
            )
        urls = _required(raw_server, "urls", list)
        if not all(isinstance(url, str) for url in urls):
            raise ControlPlaneError(
                "control-plane ICE server URLs must be strings",
                "control.response_decode",
            )
        username = raw_server.get("username")
        credential = raw_server.get("credential")
        if username is not None and not isinstance(username, str):
            raise ControlPlaneError(
                "ICE username must be a string", "control.response_decode"
            )
        if credential is not None and not isinstance(credential, str):
            raise ControlPlaneError(
                "ICE credential must be a string", "control.response_decode"
            )
        servers.append(IceServer(tuple(urls), username, credential))
    return tuple(servers)


def _session_credentials(payload: dict[str, Any]) -> SessionCredentials:
    return SessionCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        source_token=SecretToken(_required(payload, "source_token", str)),
        subscriber_token=SecretToken(_required(payload, "subscriber_token", str)),
        whip_url=_optional_string(payload, "whip_url"),
        whep_url=_optional_string(payload, "whep_url"),
        ice_servers=_ice_servers(payload),
    )


def _session_snapshot(payload: dict[str, Any]) -> SessionSnapshot:
    return SessionSnapshot(
        session_id=SessionId(_required(payload, "session_id", str)),
        source_active=_required(payload, "source_active", bool),
        subscription_count=_required(payload, "subscription_count", int),
        codec=_required(payload, "codec", str),
    )


def _subscriber_credentials(payload: dict[str, Any]) -> SubscriberCredentials:
    return SubscriberCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        subscriber_token=SecretToken(_required(payload, "subscriber_token", str)),
    )


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is not None and not isinstance(value, str):
        raise ControlPlaneError(
            f"control-plane response field {key!r} has the wrong type",
            "control.response_decode",
        )
    return value


__all__ = [
    "ControlClient",
    "ControlPlaneError",
    "IceServer",
    "SecretToken",
    "SessionCredentials",
    "SessionId",
    "SessionSnapshot",
    "SubscriberCredentials",
]
