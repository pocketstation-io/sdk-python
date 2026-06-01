"""Unit tests for pocketstation.client. Phase 5."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pocketstation import PocketStationClient as PocketStation, PocketStationError, RoomCredentials


VALID_ROOM_RESPONSE = {
    "room_id": "room-py-001",
    "source_token": "src-py",
    "listener_token": "lst-py",
}

ROOM_RESPONSE_WITH_ICE = {
    **VALID_ROOM_RESPONSE,
    "ice_servers": [
        {"urls": ["stun:relay.example.com:3478"]},
        {"urls": ["turn:relay.example.com:3478"], "username": "u", "credential": "p"},
    ],
}


def _mock_http_client(json_response: dict, status_code: int = 200):
    """Return a context-manager mock for httpx.AsyncClient."""
    mock_response = MagicMock()
    mock_response.is_success = status_code < 400
    mock_response.status_code = status_code
    mock_response.text = ""
    mock_response.json = MagicMock(return_value=json_response)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def _mock_http_client_error(status_code: int = 500, text: str = "internal error"):
    """Return a mock httpx.AsyncClient whose response indicates an HTTP error."""
    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = status_code
    mock_response.text = text
    mock_response.json = MagicMock(return_value={})

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.asyncio
async def test_given_valid_api_server_when_connect_then_session_has_credentials():
    # Given
    mock_client = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)
    # When
    with patch("pocketstation.client.httpx.AsyncClient", return_value=mock_client):
        async with PocketStation.connect(
            api_url="http://api.example.com",
            relay_url="ws://relay.example.com",
        ) as session:
            # Then
            assert session.room_id == "room-py-001"
            assert session.source_token == "src-py"
            assert session.listener_token == "lst-py"
            assert session.ice_servers == []


@pytest.mark.asyncio
async def test_given_api_server_with_turn_when_connect_then_ice_servers_forwarded():
    # Given
    mock_client = _mock_http_client(ROOM_RESPONSE_WITH_ICE, status_code=201)
    # When
    with patch("pocketstation.client.httpx.AsyncClient", return_value=mock_client):
        async with PocketStation.connect(
            api_url="http://api.example.com",
            relay_url="ws://relay.example.com",
        ) as session:
            # Then
            assert len(session.ice_servers) == 2
            assert session.ice_servers[1].username == "u"


@pytest.mark.asyncio
async def test_given_api_server_500_when_connect_then_raises():
    # Given
    mock_client = _mock_http_client_error(status_code=500, text="internal error")
    # When / Then
    with patch("pocketstation.client.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(PocketStationError) as exc_info:
            async with PocketStation.connect(
                api_url="http://api.example.com",
                relay_url="ws://relay.example.com",
            ):
                pass
    assert exc_info.value.code == "http_error"


@pytest.mark.asyncio
async def test_given_preexisting_credentials_when_connect_then_no_http_call():
    # Given — no patch; any real HTTP call would fail with PermissionError in sandbox
    creds = RoomCredentials.from_dict(VALID_ROOM_RESPONSE)
    # When
    async with PocketStation.connect(
        api_url="http://should-not-be-called.example.com",
        relay_url="ws://relay.example.com",
        credentials=creds,
    ) as session:
        # Then — session uses provided credentials without making any HTTP call
        assert session.room_id == "room-py-001"


@pytest.mark.asyncio
async def test_given_session_when_credentials_property_then_returns_room_credentials():
    creds = RoomCredentials.from_dict(VALID_ROOM_RESPONSE)
    async with PocketStation.connect(
        api_url="http://unused.example.com",
        relay_url="ws://relay.example.com",
        credentials=creds,
    ) as session:
        assert isinstance(session.credentials, RoomCredentials)
        assert session.credentials.room_id == "room-py-001"
