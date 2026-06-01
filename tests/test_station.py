"""Unit tests for pocketstation.station — spec §12.1 voice agent pattern."""
from __future__ import annotations

import struct
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pocketstation import AudioFrame, AudioMode, PocketStation
from pocketstation.types import RoomCredentials


VALID_ROOM_RESPONSE = {
    "room_id": "room-station-001",
    "source_token": "src-station",
    "listener_token": "lst-station",
}


def _make_pcm(n_samples: int = 4) -> bytes:
    """Build n_samples of f32-LE PCM silence."""
    return struct.pack(f"<{n_samples}f", *([0.0] * n_samples))


def _mock_http_client(json_response: dict, status_code: int = 200):
    """Return a context-manager mock for httpx.AsyncClient that yields a mock response."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value=json_response)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    return mock_client


# ---------------------------------------------------------------------------
# AudioMode / construction
# ---------------------------------------------------------------------------


def test_given_voice_agent_mode_when_created_then_fields_set():
    # Given / When
    station = PocketStation(room_id="abc123", mode=AudioMode.VOICE_AGENT)
    # Then
    assert station.room_id == "abc123"
    assert station.mode is AudioMode.VOICE_AGENT
    assert station.frame_duration_ms == 20
    assert station._ws is None
    assert station._credentials is None


# ---------------------------------------------------------------------------
# AudioFrame.samples property
# ---------------------------------------------------------------------------


def test_given_audio_frame_when_samples_then_correct_count():
    # Given
    n = 8
    pcm = _make_pcm(n)
    frame = AudioFrame(pcm=pcm)
    # When
    samples = frame.samples
    # Then
    assert len(samples) == n
    assert all(s == 0.0 for s in samples)


def test_given_audio_frame_with_known_values_when_samples_then_decoded_correctly():
    # Given
    values = [0.5, -0.5, 1.0, -1.0]
    pcm = struct.pack("<4f", *values)
    frame = AudioFrame(pcm=pcm)
    # When
    samples = frame.samples
    # Then
    assert len(samples) == 4
    for actual, expected in zip(samples, values):
        assert abs(actual - expected) < 1e-6


# ---------------------------------------------------------------------------
# _ensure_room — credential reuse
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_room_id_when_ensure_room_then_reuses_credentials():
    # Given — first call creates room via mocked HTTP client
    mock_client = _mock_http_client(VALID_ROOM_RESPONSE)

    station = PocketStation(room_id="existing-room")

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_client):
        # When — call _ensure_room twice
        creds1 = await station._ensure_room()
        creds2 = await station._ensure_room()

    # Then — same object returned; HTTP was called only once
    assert creds1 is creds2
    assert creds1.room_id == "room-station-001"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_given_no_room_id_when_ensure_room_then_room_id_assigned():
    # Given
    mock_client = _mock_http_client(VALID_ROOM_RESPONSE)

    station = PocketStation()  # no room_id

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_client):
        # When
        creds = await station._ensure_room()

    # Then
    assert station.room_id == "room-station-001"
    assert creds.room_id == "room-station-001"


# ---------------------------------------------------------------------------
# listen() — websocket unavailable
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_websocket_unavailable_when_listen_then_yields_nothing():
    # Given — HTTP room creation succeeds, WebSocket connect raises immediately
    mock_client = _mock_http_client(VALID_ROOM_RESPONSE)

    station = PocketStation(room_id="abc123", relay_url="ws://127.0.0.1:1")

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_client), \
         patch("pocketstation.station.websockets.connect", side_effect=OSError("unreachable")):
        # When
        frames = []
        async for frame in station.listen():
            frames.append(frame)

    # Then — no frames, no exception raised
    assert frames == []
