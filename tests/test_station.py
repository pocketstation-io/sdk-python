"""Root package ownership and vocabulary tests."""

from __future__ import annotations

import pocketstation
from pocketstation.control import ControlClient


def test_given_primary_exports_when_inspected_then_room_vocabulary_is_absent():
    assert "PocketStation" not in pocketstation.__all__
    assert "RoomCredentials" not in pocketstation.__all__
    assert "ControlClient" not in pocketstation.__all__
    assert ControlClient.__module__ == "pocketstation.control"
    assert "Session" in pocketstation.__all__


def test_given_retired_room_api_when_inspected_then_it_is_not_shipped():
    assert not hasattr(pocketstation, "PocketStation")
    assert not hasattr(pocketstation, "RoomCredentials")
    assert not hasattr(pocketstation, "AudioMode")
