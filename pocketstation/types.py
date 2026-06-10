"""PocketStation SDK type definitions. Phase 5."""
from __future__ import annotations
import dataclasses
import enum
import struct
from dataclasses import dataclass, field
from typing import Optional


class AudioMode(enum.Enum):
    """Audio session mode (spec §12.1)."""
    VOICE = "voice"
    VOICE_AGENT = "voice_agent"
    MUSIC = "music"
    BROADCAST = "broadcast"


@dataclasses.dataclass
class AudioFrame:
    """A single audio frame received from the relay.

    pcm: raw PCM bytes, 48 kHz mono f32-LE (PY-013).
    sequence: monotonically increasing frame counter per stream.
    timestamp_ns: monotonic nanosecond timestamp at frame receipt.
    """
    pcm: bytes
    sequence: int = 0
    timestamp_ns: int = 0
    sample_rate: int = 48000
    channels: int = 1
    duration_ms: int = 20

    @property
    def samples(self) -> list[float]:
        """Decode f32-LE PCM bytes to float samples."""
        n = len(self.pcm) // 4
        return list(struct.unpack(f"<{n}f", self.pcm[:n * 4]))


@dataclass
class IceServer:
    """ICE server configuration (PY-023 embedded TURN)."""
    urls: list[str]
    username: Optional[str] = None
    credential: Optional[str] = None


@dataclass
class RoomCredentials:
    """Credentials returned by POST /v1/rooms."""
    room_id: str
    source_token: str
    listener_token: str
    ice_servers: list[IceServer] = field(default_factory=list)
    qr_url: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "RoomCredentials":
        ice_servers = [
            IceServer(
                urls=srv.get("urls", []),
                username=srv.get("username"),
                credential=srv.get("credential"),
            )
            for srv in data.get("ice_servers", [])
        ]
        return cls(
            room_id=data["room_id"],
            source_token=data["source_token"],
            listener_token=data["listener_token"],
            ice_servers=ice_servers,
            qr_url=data.get("qr_url", ""),
        )


class PocketStationError(Exception):
    """Base error for all PocketStation SDK failures."""
    def __init__(self, message: str, code: str = "error") -> None:
        super().__init__(message)
        self.code = code
