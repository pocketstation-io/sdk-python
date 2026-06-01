"""Unit tests for pocketstation.types. Phase 5."""
import pytest
from pocketstation.types import IceServer, PocketStationError, RoomCredentials


def test_given_valid_dict_when_from_dict_then_credentials_parsed():
    # Given
    data = {
        "room_id": "room-abc",
        "source_token": "src-tok",
        "listener_token": "lst-tok",
    }
    # When
    creds = RoomCredentials.from_dict(data)
    # Then
    assert creds.room_id == "room-abc"
    assert creds.source_token == "src-tok"
    assert creds.listener_token == "lst-tok"
    assert creds.ice_servers == []


def test_given_ice_servers_when_from_dict_then_parsed():
    # Given
    data = {
        "room_id": "room-turn",
        "source_token": "s",
        "listener_token": "l",
        "ice_servers": [
            {"urls": ["stun:relay.example.com:3478"]},
            {"urls": ["turn:relay.example.com:3478"], "username": "u", "credential": "p"},
        ],
    }
    # When
    creds = RoomCredentials.from_dict(data)
    # Then
    assert len(creds.ice_servers) == 2
    assert creds.ice_servers[0].urls == ["stun:relay.example.com:3478"]
    assert creds.ice_servers[1].username == "u"
    assert creds.ice_servers[1].credential == "p"


def test_given_pocketstation_error_when_raised_then_code_set():
    # Given / When / Then
    with pytest.raises(PocketStationError) as exc_info:
        raise PocketStationError("connection failed", "network_error")
    assert exc_info.value.code == "network_error"
    assert "connection failed" in str(exc_info.value)


def test_given_ice_server_when_constructed_then_fields_accessible():
    srv = IceServer(urls=["stun:example.com:3478"])
    assert srv.urls == ["stun:example.com:3478"]
    assert srv.username is None
    assert srv.credential is None
