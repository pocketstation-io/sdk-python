"""PocketStation session API.

Wire format contract:
  - broadcast() sends raw binary PCM bytes over the WebSocket, never base64 JSON.
  - listen() yields binary WebSocket frames as AudioFrame objects.
  - Errors from the WebSocket propagate to the caller; they are never swallowed.
  - disconnect() sends a LEAVE message before closing the WebSocket.

This preview uses a WebSocket transport and does not implement WebRTC.
"""
from __future__ import annotations

import json
import time
from typing import AsyncIterator, Optional

import httpx
import websockets

from .types import AudioFrame, AudioMode, IceServer, PocketStationError, RoomCredentials

_MSG_TYPE_SUBSCRIBE = "SUBSCRIBE"
_MSG_TYPE_LEAVE = "LEAVE"
_MSG_TYPE_ROOM_STATE = "ROOM_STATE"

_DEFAULT_API_URL = "http://localhost:8090"
_DEFAULT_RELAY_URL = "ws://localhost:8080/v1/signal"
_DEFAULT_FRAME_DURATION_MS = 20


class PocketStation:
    """Receive and send PCM through one PocketStation session.

    Lifecycle::

        station = PocketStation(room_id="abc123", relay_url="wss://...", mode=AudioMode.VOICE_AGENT)
        await station.connect()
        async for frame in station.listen():
            await station.broadcast(tts_bytes)
        await station.disconnect()

    Or as a context manager::

        async with PocketStation(room_id="abc123", relay_url="wss://...") as station:
            async for frame in station.listen():
                await station.broadcast(tts_bytes)
    """

    def __init__(
        self,
        *,
        room_id: Optional[str] = None,
        relay_url: str = _DEFAULT_RELAY_URL,
        api_url: str = _DEFAULT_API_URL,
        mode: AudioMode = AudioMode.VOICE_AGENT,
    ) -> None:
        self.room_id = room_id
        self.relay_url = relay_url
        self.api_url = api_url
        self.mode = mode
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._credentials: Optional[RoomCredentials] = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "PocketStation":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """POST /v1/rooms, open the WebSocket, send SUBSCRIBE.

        :raises PocketStationError: on HTTP failure.
        :raises OSError: if the WebSocket cannot be opened.
        """
        credentials = await self._ensure_room()
        ws = await websockets.connect(self.relay_url)
        self._ws = ws
        subscribe = json.dumps({
            "type": _MSG_TYPE_SUBSCRIBE,
            "room_id": self.room_id,
            "token": credentials.listener_token,
        })
        await ws.send(subscribe)

    async def listen(self) -> AsyncIterator[AudioFrame]:
        """Yield AudioFrame objects for each binary PCM frame received.

        Errors from the WebSocket propagate to the caller; they are not caught here.
        Text (JSON) control frames are consumed silently.

        :raises ConnectionError: (or subclasses) when the WebSocket drops.
        :raises websockets.exceptions.WebSocketException: on protocol errors.
        """
        if self._ws is None:
            raise RuntimeError("call connect() before listen()")

        sequence = 0
        async for message in self._ws:
            if isinstance(message, bytes):
                yield AudioFrame(
                    pcm=message,
                    sequence=sequence,
                    timestamp_ns=time.monotonic_ns(),
                )
                sequence += 1
            # Text frames (e.g. ROOM_STATE JSON) are intentionally skipped here;
            # they carry relay control metadata, not audio payload.

    async def broadcast(self, audio: bytes) -> None:
        """Send raw PCM bytes to the relay.

        The payload is transmitted as binary WebSocket data — not base64 JSON.

        :param audio: raw PCM bytes (f32-LE 48 kHz mono per PY-013).
        :raises RuntimeError: if not connected.
        :raises websockets.exceptions.WebSocketException: on send failure.
        """
        if self._ws is None:
            raise RuntimeError("call connect() before broadcast()")
        await self._ws.send(audio)

    async def disconnect(self) -> None:
        """Send LEAVE, then close the WebSocket.

        Safe to call even if already disconnected.
        """
        if self._ws is None:
            return
        ws = self._ws
        self._ws = None
        try:
            leave = json.dumps({
                "type": _MSG_TYPE_LEAVE,
                "room_id": self.room_id,
            })
            await ws.send(leave)
        finally:
            await ws.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _ensure_room(self) -> RoomCredentials:
        """Create or reuse a room via POST /v1/rooms."""
        if self._credentials is not None:
            return self._credentials

        url = self.api_url.rstrip("/") + "/v1/rooms"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={})
        except httpx.RequestError as exc:
            raise PocketStationError(
                f"network error creating room: {exc}", "network_error"
            ) from exc

        if not response.is_success:
            raise PocketStationError(
                f"relay returned HTTP {response.status_code}: {response.text}",
                "http_error",
            )

        try:
            data = response.json()
        except Exception as exc:
            raise PocketStationError(
                f"failed to parse room creation response: {exc}", "parse_error"
            ) from exc

        credentials = RoomCredentials(
            room_id=data["room_id"],
            source_token=data.get("source_token", ""),
            listener_token=data.get("listener_token", ""),
            qr_url=data.get("qr_url", ""),
            ice_servers=[
                IceServer(
                    urls=s.get("urls", []),
                    username=s.get("username"),
                    credential=s.get("credential"),
                )
                for s in data.get("ice_servers", [])
            ],
        )
        if not self.room_id:
            self.room_id = credentials.room_id
        self._credentials = credentials
        return credentials
