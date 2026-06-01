"""PocketStation SDK type definitions. Phase 5."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IceServer:
    """ICE server configuration (ADR-023 embedded TURN)."""
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
        )


class PocketStationError(Exception):
    """Base error for all PocketStation SDK failures."""
    def __init__(self, message: str, code: str = "error") -> None:
        super().__init__(message)
        self.code = code
