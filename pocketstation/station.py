"""High-level PocketStation session API (spec §12.1)."""
from __future__ import annotations

import base64
import json
from typing import AsyncIterator, Callable, Optional

import httpx
import websockets

from .types import AudioFrame, AudioMode, IceServer, PocketStationError, RoomCredentials

_AUDIO_FRAME_MSG_TYPE = "AUDIO_FRAME"
_SUBSCRIBE_MSG_TYPE = "SUBSCRIBE"
_ROOM_STATE_MSG_TYPE = "ROOM_STATE"

_DEFAULT_API_URL = "http://localhost:8090"
_DEFAULT_RELAY_URL = "ws://localhost:8080/v1/signal"
_DEFAULT_FRAME_DURATION_MS = 20


class PocketStation:
    """Voice agent / broadcast session manager (spec §12.1).

    Construct directly when you already have a room ID::

        station = PocketStation(room_id="abc123", mode=AudioMode.VOICE_AGENT)
        async for frame in station.listen():
            transcript = await stt.transcribe(frame.pcm)
            await station.broadcast(tts_bytes)
        await station.close()

    Or create a room and connect in one step::

        station = await PocketStation.create(relay_url="wss://relay.pocketstation.io")
    """

    def __init__(
        self,
        *,
        room_id: Optional[str] = None,
        mode: AudioMode = AudioMode.VOICE_AGENT,
        api_url: str = _DEFAULT_API_URL,
        relay_url: str = _DEFAULT_RELAY_URL,
        opus_frame_duration_ms: int = _DEFAULT_FRAME_DURATION_MS,
        on_listener_count: Optional[Callable[[int], None]] = None,
        on_packet_loss: Optional[Callable[[], None]] = None,
    ) -> None:
        self.room_id = room_id
        self.mode = mode
        self.api_url = api_url
        self.relay_url = relay_url
        self.frame_duration_ms = opus_frame_duration_ms
        self.on_listener_count = on_listener_count
        self.on_packet_loss = on_packet_loss
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._credentials: Optional[RoomCredentials] = None

    @classmethod
    async def create(
        cls,
        *,
        relay_url: str = _DEFAULT_RELAY_URL,
        api_url: str = _DEFAULT_API_URL,
        mode: AudioMode = AudioMode.VOICE_AGENT,
        opus_frame_duration_ms: int = _DEFAULT_FRAME_DURATION_MS,
    ) -> "PocketStation":
        """Create a new room via the API server and return a ready PocketStation instance.

        :param relay_url: WebSocket URL of the relay.
        :param api_url: Base URL of the api-server used to provision the room.
        :param mode: Audio session mode.
        :param opus_frame_duration_ms: Opus frame duration in milliseconds.
        :raises PocketStationError: on network or HTTP failure.
        """
        station = cls(api_url=api_url, relay_url=relay_url, mode=mode,
                      opus_frame_duration_ms=opus_frame_duration_ms)
        await station._ensure_room()
        return station

    async def _ensure_room(self) -> RoomCredentials:
        """Create or reuse a room on the API server."""
        if self._credentials is not None:
            return self._credentials

        url = self.api_url.rstrip("/") + "/v1/rooms"
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={})
        except httpx.RequestError as exc:
            raise PocketStationError(
                f"network error creating room: {exc}", "network_error"
            ) from exc

        if not r.is_success:
            raise PocketStationError(
                f"relay returned HTTP {r.status_code}: {r.text}", "http_error"
            )

        try:
            data = r.json()
        except Exception as exc:
            raise PocketStationError(
                f"failed to parse room creation response: {exc}", "parse_error"
            ) from exc

        creds = RoomCredentials(
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
            self.room_id = creds.room_id
        self._credentials = creds
        return creds

    async def listen(self) -> AsyncIterator[AudioFrame]:
        """Subscribe to audio frames from the relay.

        Connects via WebSocket, sends a SUBSCRIBE message, and yields AudioFrame objects.
        Yields nothing if the relay is unreachable.
        """
        creds = await self._ensure_room()
        subscribe_msg = json.dumps({
            "type": _SUBSCRIBE_MSG_TYPE,
            "room_id": self.room_id,
            "token": creds.listener_token,
        })
        try:
            async with websockets.connect(self.relay_url) as ws:
                self._ws = ws
                await ws.send(subscribe_msg)
                seq = 0
                async for raw in ws:
                    if isinstance(raw, bytes):
                        yield AudioFrame(
                            pcm=raw,
                            sequence=seq,
                            duration_ms=self.frame_duration_ms,
                        )
                        seq += 1
                    elif isinstance(raw, str):
                        msg = json.loads(raw)
                        if msg.get("type") == _ROOM_STATE_MSG_TYPE and self.on_listener_count:
                            self.on_listener_count(msg.get("listener_count", 0))
        except Exception:
            return
        finally:
            self._ws = None

    async def broadcast(self, audio: bytes) -> None:
        """Send raw PCM bytes (f32-LE 48 kHz mono) to the relay.

        No-ops silently when not connected.
        """
        if self._ws is None:
            return
        try:
            await self._ws.send(json.dumps({
                "type": _AUDIO_FRAME_MSG_TYPE,
                "pcm_b64": base64.b64encode(audio).decode(),
            }))
        except Exception:
            pass

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
