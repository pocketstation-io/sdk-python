"""Typed asyncio client for the PocketStation control-plane Session API."""

from __future__ import annotations

import json
from types import TracebackType
from typing import Any
from urllib.parse import quote, urljoin

import httpx

from ..control import (
    _MAX_ERROR_BODY_BYTES,
    _MAX_JSON_BODY_BYTES,
    ControlPlaneError,
    Invitation,
    SecretToken,
    SessionCredentials,
    SessionId,
    SessionSnapshot,
    SubscriberCredentials,
    _bus_id,
    _bus_ids,
    _invitation,
    _normalize_base_url,
    _resolve_timeout,
    _session_credentials,
    _session_snapshot,
    _subscriber_credentials,
    _validate_timeout,
)


class ControlClient:
    """Reusable, bounded asyncio HTTP client for Session lifecycle operations."""

    def __init__(
        self,
        control_plane_url: str,
        *,
        timeout_seconds: float = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.control_plane_url = _normalize_base_url(control_plane_url)
        self._timeout_seconds = _validate_timeout(timeout_seconds)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout_seconds)
        self._closed = False

    async def create_session(
        self,
        *,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        timeout_seconds: float | None = None,
    ) -> SessionCredentials:
        required_buses = _bus_ids(required_buses, "required_buses")
        payload = await self._json_request(
            "POST",
            "v1/sessions",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            json_body={"required_buses": list(required_buses)},
        )
        return _session_credentials(payload)

    async def session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionSnapshot:
        identifier = SessionId(str(session_id))
        payload = await self._json_request(
            "GET",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
        )
        return _session_snapshot(payload)

    async def issue_subscriber_credentials(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        timeout_seconds: float | None = None,
    ) -> SubscriberCredentials:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = await self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/subscribe",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _subscriber_credentials(payload)

    async def create_invitation(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        timeout_seconds: float | None = None,
    ) -> Invitation:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = await self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/invitations",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _invitation(payload, identifier)

    async def delete_session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> None:
        identifier = SessionId(str(session_id))
        await self._request(
            "DELETE",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=204,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            expect_json=False,
        )

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> ControlClient:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _json_request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        timeout_seconds: float | None,
        authorization: SecretToken | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            method,
            path,
            expected_status=expected_status,
            timeout_seconds=timeout_seconds,
            authorization=authorization,
            expect_json=True,
            json_body=json_body,
        )

    async def _request(
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
            async with self._http_client.stream(
                method,
                urljoin(self.control_plane_url, path),
                headers=headers,
                json=json_body,
                timeout=timeout,
            ) as response:
                if response.status_code != expected_status:
                    body = await _read_bounded(
                        response.aiter_bytes(),
                        _MAX_ERROR_BODY_BYTES,
                    )
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
                body = await _read_bounded(
                    response.aiter_bytes(),
                    _MAX_JSON_BODY_BYTES,
                )
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


async def _read_bounded(chunks: Any, limit_bytes: int) -> bytes:
    body = bytearray()
    async for chunk in chunks:
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


__all__ = ["ControlClient"]
