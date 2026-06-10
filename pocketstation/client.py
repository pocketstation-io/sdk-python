"""
PocketStation Python async client SDK.

Phase scope: Phase 5.

Usage::

    import asyncio
    from pocketstation import PocketStation

    async def main():
        async with PocketStation.connect(
            api_url="https://api.pocketstation.io",
            relay_url="wss://relay.pocketstation.io",
        ) as session:
            print(f"Connected to room {session.room_id}")
            creds = session.credentials
            # Use creds.source_token / creds.listener_token for signaling

    asyncio.run(main())
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import httpx

from .types import IceServer, PocketStationError, RoomCredentials


class PocketStationSession:
    """
    Active PocketStation session.

    Invariant: valid only within the ``async with PocketStation.connect()`` block.
    Ownership: created and owned by PocketStation.connect(); do not instantiate directly.
    Failure behavior: network errors raise PocketStationError.

    Phase 5: HTTP room creation implemented. WebSocket signaling and WebRTC
    publish/subscribe wiring are Phase 5 follow-up (requires native WebRTC
    Python binding or aiortc).
    """

    def __init__(self, credentials: RoomCredentials) -> None:
        self._credentials = credentials

    @property
    def credentials(self) -> RoomCredentials:
        """Room credentials including TURN servers (PY-023)."""
        return self._credentials

    @property
    def room_id(self) -> str:
        return self._credentials.room_id

    @property
    def source_token(self) -> str:
        return self._credentials.source_token

    @property
    def listener_token(self) -> str:
        return self._credentials.listener_token

    @property
    def ice_servers(self) -> list[IceServer]:
        """TURN/STUN servers for WebRTC PeerConnection config."""
        return self._credentials.ice_servers


class PocketStation:
    """
    PocketStation async context manager.

    Creates a room on enter, cleans up on exit.
    """

    @staticmethod
    @asynccontextmanager
    async def connect(
        *,
        api_url: str,
        relay_url: str,
        credentials: Optional[RoomCredentials] = None,
    ) -> AsyncGenerator[PocketStationSession, None]:
        """
        Async context manager that creates a PocketStation session.

        On entry: creates a new room via POST /v1/rooms (or uses provided credentials).
        On exit: releases the session (future: sends LEAVE, closes WebSocket).

        :param api_url: Base URL of the api-server.
        :param relay_url: Base URL of the relay (wss://...).
        :param credentials: Pre-obtained credentials. If None, a new room is created.
        :raises PocketStationError: on network or protocol failure.
        """
        if credentials is None:
            credentials = await PocketStation._create_room(api_url)

        session = PocketStationSession(credentials)
        try:
            yield session
        finally:
            # Phase 5 TODO: send LEAVE via signaling WebSocket.
            pass

    @staticmethod
    async def create_room(api_url: str) -> RoomCredentials:
        """Create a new room and return credentials. Does not start a session."""
        return await PocketStation._create_room(api_url)

    @staticmethod
    async def _create_room(api_url: str) -> RoomCredentials:
        url = api_url.rstrip("/") + "/v1/rooms"
        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(url, json={})
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
        except json.JSONDecodeError as exc:
            raise PocketStationError(
                f"failed to parse room creation response: {exc}", "parse_error"
            ) from exc

        return RoomCredentials.from_dict(data)
