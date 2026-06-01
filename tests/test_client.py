"""Unit tests for pocketstation.client. Phase 5."""
import pytest
import httpx
import respx

from pocketstation import PocketStation, PocketStationError, RoomCredentials


VALID_ROOM_RESPONSE = {
    "room_id": "room-py-001",
    "source_token": "src-py",
    "listener_token": "lst-py",
}


@respx.mock
@pytest.mark.asyncio
async def test_given_valid_api_server_when_connect_then_session_has_credentials():
    # Given
    respx.post("http://api.example.com/v1/rooms").mock(
        return_value=httpx.Response(201, json=VALID_ROOM_RESPONSE)
    )
    # When
    async with PocketStation.connect(
        api_url="http://api.example.com",
        relay_url="ws://relay.example.com",
    ) as session:
        # Then
        assert session.room_id == "room-py-001"
        assert session.source_token == "src-py"
        assert session.listener_token == "lst-py"
        assert session.ice_servers == []


@respx.mock
@pytest.mark.asyncio
async def test_given_api_server_with_turn_when_connect_then_ice_servers_forwarded():
    # Given
    respx.post("http://api.example.com/v1/rooms").mock(
        return_value=httpx.Response(201, json={
            **VALID_ROOM_RESPONSE,
            "ice_servers": [
                {"urls": ["stun:relay.example.com:3478"]},
                {"urls": ["turn:relay.example.com:3478"], "username": "u", "credential": "p"},
            ],
        })
    )
    # When
    async with PocketStation.connect(
        api_url="http://api.example.com",
        relay_url="ws://relay.example.com",
    ) as session:
        # Then
        assert len(session.ice_servers) == 2
        assert session.ice_servers[1].username == "u"


@respx.mock
@pytest.mark.asyncio
async def test_given_api_server_500_when_connect_then_raises():
    # Given
    respx.post("http://api.example.com/v1/rooms").mock(
        return_value=httpx.Response(500, text="internal error")
    )
    # When / Then
    with pytest.raises(PocketStationError) as exc_info:
        async with PocketStation.connect(
            api_url="http://api.example.com",
            relay_url="ws://relay.example.com",
        ):
            pass
    assert exc_info.value.code == "http_error"


@pytest.mark.asyncio
async def test_given_preexisting_credentials_when_connect_then_no_http_call():
    # Given — no network mock; any http call would error
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
