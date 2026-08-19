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
    SecretToken,
    SessionCredentials,
    SessionId,
    SessionSnapshot,
    SubscriberCredentials,
    _normalize_base_url,
    _session_credentials,
    _session_snapshot,
    _subscriber_credentials,
)


class ControlClient:
    """Reusable, bounded asyncio HTTP client for Session lifecycle operations."""

    def __init__(
        self,
        control_plane_url: str,
        *,
        timeout_seconds: float | None = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.control_plane_url = _normalize_base_url(control_plane_url)
        self._timeout_seconds = timeout_seconds
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout_seconds)
        self._closed = False

    async def create_session(
        self,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionCredentials:
        payload = await self._json_request(
            "POST",
            "v1/sessions",
            expected_status=201,
            timeout_seconds=timeout_seconds,
        )
        return _session_credentials(payload)

    async def session(
        self,
        session_id: str | SessionId,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionSnapshot:
        identifier = SessionId(str(session_id))
        payload = await self._json_request(
            "GET",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=200,
            timeout_seconds=timeout_seconds,
        )
        return _session_snapshot(payload)

    async def issue_subscriber_credentials(
        self,
        session_id: str | SessionId,
        *,
        timeout_seconds: float | None = None,
    ) -> SubscriberCredentials:
        identifier = SessionId(str(session_id))
        payload = await self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/subscribe",
            expected_status=200,
            timeout_seconds=timeout_seconds,
        )
        return _subscriber_credentials(payload)

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
    ) -> dict[str, Any]:
        return await self._request(
            method,
            path,
            expected_status=expected_status,
            timeout_seconds=timeout_seconds,
            authorization=None,
            expect_json=True,
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
            async with self._http_client.stream(
                method,
                urljoin(self.control_plane_url, path),
                headers=headers,
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
