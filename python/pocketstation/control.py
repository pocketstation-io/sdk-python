"""Typed synchronous client for the PocketStation control-plane Session API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import TracebackType
from typing import Any, cast
from urllib.parse import quote, urljoin, urlparse

import httpx

from .errors import PocketStationError

_MAX_ERROR_BODY_BYTES = 4_096
_MAX_JSON_BODY_BYTES = 65_536
_MAX_SESSION_ID_BYTES = 128
_MAX_SECRET_BYTES = 4_096
_MAX_ICE_SERVERS = 32
_MAX_ICE_URLS = 16


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
        if (
            not value
            or len(value.encode("utf-8")) > _MAX_SESSION_ID_BYTES
            or not all(
                character.isascii() and (character.isalnum() or character in "-_")
                for character in value
            )
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
        if len(value.encode("utf-8")) > _MAX_SECRET_BYTES:
            raise ValueError(
                f"credential token must not exceed {_MAX_SECRET_BYTES} bytes"
            )
        self._value = value

    def expose_secret(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "SecretToken('[redacted]')"


@dataclass(frozen=True, slots=True)
class IceServer:
    urls: tuple[str, ...]
    username: str | None = None
    credential: SecretToken | None = None


@dataclass(frozen=True, slots=True)
class SessionCredentials:
    session_id: SessionId
    required_buses: tuple[str, ...]
    source_token: SecretToken
    whip_url: str | None = None
    whep_url: str | None = None
    ice_servers: tuple[IceServer, ...] = ()


@dataclass(frozen=True, slots=True)
class BusState:
    bus_id: str
    role: str
    source_active: bool
    source_generation: int


@dataclass(frozen=True, slots=True)
class SubscriptionState:
    subscriber_id: str
    bus_id: str


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    session_id: SessionId
    state_revision: int
    relay_epoch: str | None
    relay_revision: int
    required_buses: tuple[str, ...]
    buses: tuple[BusState, ...]
    subscriptions: tuple[SubscriptionState, ...]
    ready: bool
    subscription_count: int
    codec: str


@dataclass(frozen=True, slots=True)
class Invitation:
    session_id: SessionId
    join_code: str
    join_url: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class SubscriberCredentials:
    session_id: SessionId
    bus_id: str
    subscriber_token: SecretToken


class ControlClient:
    """Reusable, bounded HTTP client for Session lifecycle operations."""

    def __init__(
        self,
        control_plane_url: str,
        *,
        timeout_seconds: float = 10.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.control_plane_url = _normalize_base_url(control_plane_url)
        self._timeout_seconds = _validate_timeout(timeout_seconds)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(timeout=timeout_seconds)
        self._closed = False

    def create_session(
        self,
        *,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        timeout_seconds: float | None = None,
    ) -> SessionCredentials:
        required_buses = _bus_ids(required_buses, "required_buses")
        payload = self._json_request(
            "POST",
            "v1/sessions",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            json_body={"required_buses": list(required_buses)},
        )
        return _session_credentials(payload)

    def session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionSnapshot:
        identifier = SessionId(str(session_id))
        payload = self._json_request(
            "GET",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
        )
        return _session_snapshot(payload)

    def issue_subscriber_credentials(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        timeout_seconds: float | None = None,
    ) -> SubscriberCredentials:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/subscribe",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _subscriber_credentials(payload)

    def create_invitation(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        timeout_seconds: float | None = None,
    ) -> Invitation:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/invitations",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _invitation(payload, identifier)

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
        authorization: SecretToken | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            method,
            path,
            expected_status=expected_status,
            timeout_seconds=timeout_seconds,
            authorization=authorization,
            expect_json=True,
            json_body=json_body,
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
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        headers = {}
        redacted_values: tuple[str, ...] = ()
        if authorization is not None:
            exposed = authorization.expose_secret()
            headers["Authorization"] = f"Bearer {exposed}"
            redacted_values = (exposed,)
        timeout = _resolve_timeout(self._timeout_seconds, timeout_seconds)
        try:
            with self._http_client.stream(
                method,
                urljoin(self.control_plane_url, path),
                headers=headers,
                json=json_body,
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
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("control_plane_url must not contain credentials")
    return value.split("?", 1)[0].split("#", 1)[0].rstrip("/") + "/"


def _validate_timeout(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("timeout_seconds must be a number")
    if not 0 < value <= 300:
        raise ValueError("timeout_seconds must be greater than 0 and at most 300")
    return float(value)


def _resolve_timeout(default: float, override: float | None) -> float:
    """Resolve a per-request override without permitting unbounded I/O."""

    return default if override is None else _validate_timeout(override)


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
    valid = isinstance(value, expected_type)
    if expected_type is int and isinstance(value, bool):
        valid = False
    if not valid:
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
    if len(raw_servers) > _MAX_ICE_SERVERS:
        raise ControlPlaneError(
            f"control-plane returned more than {_MAX_ICE_SERVERS} ICE servers",
            "control.response_too_large",
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
        if len(urls) > _MAX_ICE_URLS:
            raise ControlPlaneError(
                f"ICE server returned more than {_MAX_ICE_URLS} URLs",
                "control.response_too_large",
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
        servers.append(
            IceServer(
                tuple(urls),
                username,
                None if credential is None else SecretToken(credential),
            )
        )
    return tuple(servers)


def _session_credentials(payload: dict[str, Any]) -> SessionCredentials:
    return SessionCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        required_buses=_decoded_bus_ids(
            tuple(_required(payload, "required_buses", list)),
            "required_buses",
        ),
        source_token=SecretToken(_required(payload, "source_token", str)),
        whip_url=_optional_string(payload, "whip_url"),
        whep_url=_optional_string(payload, "whep_url"),
        ice_servers=_ice_servers(payload),
    )


def _session_snapshot(payload: dict[str, Any]) -> SessionSnapshot:
    state_revision = _nonnegative_integer(payload, "state_revision", minimum=1)
    relay_revision = _nonnegative_integer(payload, "relay_revision")
    subscription_count = _required(payload, "subscription_count", int)
    if subscription_count < 0:
        raise ControlPlaneError(
            "control-plane subscription_count must not be negative",
            "control.response_decode",
        )
    return SessionSnapshot(
        session_id=SessionId(_required(payload, "session_id", str)),
        state_revision=state_revision,
        relay_epoch=_optional_string(payload, "relay_epoch"),
        relay_revision=relay_revision,
        required_buses=_decoded_bus_ids(
            tuple(_required(payload, "required_buses", list)),
            "required_buses",
        ),
        buses=_bus_states(payload),
        subscriptions=_subscription_states(payload),
        ready=_required(payload, "ready", bool),
        subscription_count=subscription_count,
        codec=_required(payload, "codec", str),
    )


def _subscriber_credentials(payload: dict[str, Any]) -> SubscriberCredentials:
    return SubscriberCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        bus_id=_bus_id(_required(payload, "bus_id", str), "bus_id"),
        subscriber_token=SecretToken(_required(payload, "subscriber_token", str)),
    )


def _invitation(payload: dict[str, Any], session_id: SessionId) -> Invitation:
    return Invitation(
        session_id=session_id,
        join_code=_required(payload, "join_code", str),
        join_url=_required(payload, "join_url", str),
        expires_at=_required(payload, "expires_at", str),
    )


def _nonnegative_integer(payload: dict[str, Any], key: str, *, minimum: int = 0) -> int:
    value = cast(int, _required(payload, key, int))
    if value < minimum:
        raise ControlPlaneError(
            f"control-plane response field {key!r} must be at least {minimum}",
            "control.response_decode",
        )
    return value


def _identifier(value: str, field: str, maximum: int) -> str:
    if (
        not value
        or len(value) > maximum
        or not all(
            character.isascii() and (character.isalnum() or character in "._-")
            for character in value
        )
    ):
        raise ValueError(
            f"{field} must contain 1 to {maximum} ASCII letters, digits, "
            "'.', '_' or '-'"
        )
    return value


def _bus_id(value: str, field: str) -> str:
    return _identifier(value, field, 64)


def _bus_ids(values: tuple[Any, ...], field: str) -> tuple[str, ...]:
    if not 1 <= len(values) <= 16 or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError(f"{field} must contain between 1 and 16 bus IDs")
    result = tuple(_bus_id(value, field) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicate bus IDs")
    return result


def _decoded_bus_ids(values: tuple[Any, ...], field: str) -> tuple[str, ...]:
    try:
        return _bus_ids(values, field)
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _required_identifier(payload: dict[str, Any], key: str, *, maximum: int) -> str:
    try:
        return _identifier(_required(payload, key, str), key, maximum)
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _bus_states(payload: dict[str, Any]) -> tuple[BusState, ...]:
    raw = _required(payload, "buses", list)
    if len(raw) > 16 or not all(isinstance(value, dict) for value in raw):
        raise ControlPlaneError(
            "control-plane buses must contain at most 16 objects",
            "control.response_decode",
        )
    return tuple(
        BusState(
            bus_id=_required_identifier(value, "bus_id", maximum=64),
            role=_required_identifier(value, "role", maximum=64),
            source_active=_required(value, "source_active", bool),
            source_generation=_nonnegative_integer(value, "source_generation"),
        )
        for value in raw
    )


def _subscription_states(payload: dict[str, Any]) -> tuple[SubscriptionState, ...]:
    raw = _required(payload, "subscriptions", list)
    if len(raw) > 1_024 or not all(isinstance(value, dict) for value in raw):
        raise ControlPlaneError(
            "control-plane subscriptions must contain at most 1024 objects",
            "control.response_decode",
        )
    return tuple(
        SubscriptionState(
            subscriber_id=_required_identifier(value, "subscriber_id", maximum=128),
            bus_id=_required_identifier(value, "bus_id", maximum=64),
        )
        for value in raw
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
    "BusState",
    "ControlClient",
    "ControlPlaneError",
    "IceServer",
    "Invitation",
    "SecretToken",
    "SessionCredentials",
    "SessionId",
    "SessionSnapshot",
    "SubscriberCredentials",
    "SubscriptionState",
]
