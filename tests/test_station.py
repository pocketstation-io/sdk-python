"""Tests for the async PocketStation session client."""
from __future__ import annotations

import json
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


class _FakeWebSocket:
    """Minimal WebSocket stand-in for tests.

    Supports: send (AsyncMock), close (AsyncMock), async iteration over a
    fixed message list. Not a MagicMock so dunder methods work correctly.
    """

    def __init__(self, messages: list) -> None:
        self._messages = messages
        self.send = AsyncMock()
        self.close = AsyncMock()

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for msg in self._messages:
            yield msg


def _make_connect_mock(fake_ws: "_FakeWebSocket") -> AsyncMock:
    """
    Return an AsyncMock that, when called and awaited, returns fake_ws.

    Patch usage:
        with patch("pocketstation.station.websockets.connect", connect_mock):
            ...
    Then ``await websockets.connect(url)`` in the implementation resolves to fake_ws.
    """
    connect_mock = AsyncMock(return_value=fake_ws)
    return connect_mock


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_given_voice_agent_mode_when_created_then_fields_set():
    # Given / When
    station = PocketStation(
        room_id="abc123",
        relay_url="ws://relay.example.com",
        mode=AudioMode.VOICE_AGENT,
    )
    # Then
    assert station.room_id == "abc123"
    assert station.mode is AudioMode.VOICE_AGENT
    assert station._ws is None


# ---------------------------------------------------------------------------
# AudioFrame
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


def test_given_audio_frame_when_constructed_then_timestamp_and_sequence_present():
    # Given / When
    frame = AudioFrame(pcm=b"\x00" * 16, sequence=7, timestamp_ns=123456789)
    # Then
    assert frame.sequence == 7
    assert frame.timestamp_ns == 123456789


# ---------------------------------------------------------------------------
# connect() — POST /v1/rooms + WebSocket SUBSCRIBE
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_voice_agent_mode_when_connect_then_posts_room_and_opens_websocket():
    """
    Given a PocketStation in VOICE_AGENT mode,
    When connect() is called,
    Then it POSTs to /v1/rooms and sends a SUBSCRIBE message over the WebSocket.
    """
    # Given
    mock_http = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)
    fake_ws = _FakeWebSocket(messages=[])
    connect_mock = _make_connect_mock(fake_ws)

    station = PocketStation(
        room_id="room-station-001",
        relay_url="ws://relay.example.com",
        mode=AudioMode.VOICE_AGENT,
    )

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_http), \
         patch("pocketstation.station.websockets.connect", connect_mock):
        # When
        await station.connect()

        # Then — HTTP room creation happened
        mock_http.post.assert_called_once()
        posted_url = mock_http.post.call_args[0][0]
        assert "/v1/rooms" in posted_url

        # Then — WebSocket was opened and SUBSCRIBE was sent
        connect_mock.assert_called_once_with("ws://relay.example.com")
        fake_ws.send.assert_called_once()
        sent = json.loads(fake_ws.send.call_args[0][0])
        assert sent["type"] == "SUBSCRIBE"
        assert sent["room_id"] == "room-station-001"
        assert "token" in sent

        await station.disconnect()


# ---------------------------------------------------------------------------
# broadcast() — must send binary bytes, not base64 JSON
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_connected_when_broadcast_then_sends_binary_bytes_not_base64():
    """
    Given a connected PocketStation,
    When broadcast(audio_bytes) is called,
    Then the WebSocket send receives raw bytes, not a base64-encoded JSON string.
    """
    # Given
    mock_http = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)
    fake_ws = _FakeWebSocket(messages=[])
    connect_mock = _make_connect_mock(fake_ws)

    station = PocketStation(
        room_id="room-station-001",
        relay_url="ws://relay.example.com",
        mode=AudioMode.VOICE_AGENT,
    )
    audio = _make_pcm(n_samples=16)

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_http), \
         patch("pocketstation.station.websockets.connect", connect_mock):
        await station.connect()
        # Reset after the SUBSCRIBE send that happens in connect()
        fake_ws.send.reset_mock()

        # When
        await station.broadcast(audio)

        # Then — exactly one send call with the raw bytes payload
        fake_ws.send.assert_called_once_with(audio)
        sent_arg = fake_ws.send.call_args[0][0]
        assert isinstance(sent_arg, bytes), (
            f"broadcast() must send bytes, not {type(sent_arg).__name__}"
        )
        # Guard: must not be a JSON / base64 string
        assert not isinstance(sent_arg, str)

        await station.disconnect()


# ---------------------------------------------------------------------------
# __aenter__ / __aexit__ — context manager sends LEAVE on exit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_context_manager_when_exit_then_sends_leave():
    """
    Given a PocketStation used as an async context manager,
    When the block exits normally,
    Then a LEAVE message is sent and the WebSocket is closed.
    """
    # Given
    mock_http = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)
    fake_ws = _FakeWebSocket(messages=[])
    connect_mock = _make_connect_mock(fake_ws)

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_http), \
         patch("pocketstation.station.websockets.connect", connect_mock):
        # When
        async with PocketStation(
            room_id="room-station-001",
            relay_url="ws://relay.example.com",
        ) as station:
            pass  # nothing inside the block

        # Then — LEAVE was sent exactly once
        all_sends = fake_ws.send.call_args_list
        leave_sends = [
            c for c in all_sends
            if isinstance(c[0][0], str) and json.loads(c[0][0]).get("type") == "LEAVE"
        ]
        assert len(leave_sends) == 1, (
            f"Expected exactly one LEAVE message, got {all_sends}"
        )
        # Then — WebSocket was closed
        fake_ws.close.assert_called_once()


# ---------------------------------------------------------------------------
# listen() — errors must propagate, not be swallowed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_websocket_closed_when_listen_then_raises_connection_error_not_swallows():
    """
    Given that the WebSocket raises a ConnectionError during iteration,
    When station.listen() is consumed,
    Then the error propagates to the caller instead of being swallowed.
    """
    # Given
    mock_http = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)

    class _FailingWebSocket(_FakeWebSocket):
        async def _gen(self):
            yield _make_pcm(4)  # one good frame before the error
            raise ConnectionError("relay dropped connection")

    fake_ws = _FailingWebSocket(messages=[])
    connect_mock = _make_connect_mock(fake_ws)

    station = PocketStation(
        room_id="room-station-001",
        relay_url="ws://relay.example.com",
    )

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_http), \
         patch("pocketstation.station.websockets.connect", connect_mock):
        await station.connect()

        # When / Then — ConnectionError propagates; only the first frame arrives
        frames: list[AudioFrame] = []
        with pytest.raises(ConnectionError, match="relay dropped connection"):
            async for frame in station.listen():
                frames.append(frame)

    # One frame was produced before the error
    assert len(frames) == 1


# ---------------------------------------------------------------------------
# listen() — binary frames are yielded as AudioFrame objects
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_given_connected_when_listen_then_yields_audio_frames_from_binary_messages():
    """
    Given a WebSocket that delivers three binary PCM frames,
    When station.listen() is iterated,
    Then three AudioFrame objects are yielded with monotonically increasing sequences.
    """
    # Given
    mock_http = _mock_http_client(VALID_ROOM_RESPONSE, status_code=201)
    pcm_frames = [_make_pcm(4), _make_pcm(4), _make_pcm(4)]
    fake_ws = _FakeWebSocket(messages=pcm_frames)
    connect_mock = _make_connect_mock(fake_ws)

    station = PocketStation(
        room_id="room-station-001",
        relay_url="ws://relay.example.com",
    )

    with patch("pocketstation.station.httpx.AsyncClient", return_value=mock_http), \
         patch("pocketstation.station.websockets.connect", connect_mock):
        await station.connect()

        # When
        frames: list[AudioFrame] = []
        async for frame in station.listen():
            frames.append(frame)

        # Then
        assert len(frames) == 3
        for i, frame in enumerate(frames):
            assert isinstance(frame, AudioFrame)
            assert frame.pcm == pcm_frames[i]
            assert frame.sequence == i

        await station.disconnect()
