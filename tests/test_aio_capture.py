"""Progressive asyncio capture recipe tests."""

from __future__ import annotations

import importlib

import pytest

capture_module = importlib.import_module("pocketstation.aio.capture")


class FakeStopResult:
    success = True
    recording = None


class FakeRunning:
    def __init__(self) -> None:
        self.is_stopped = False
        self.stop_result = None
        self.stop_calls = 0
        self.audio = object()

    async def stop(self):
        self.stop_calls += 1
        self.is_stopped = True
        self.stop_result = FakeStopResult()
        return self.stop_result

    async def aclose(self):
        await self.stop()


class FakeEndpoint:
    pass


class FakeStem:
    next_id = 1

    def __init__(self) -> None:
        self.id = FakeStem.next_id
        FakeStem.next_id += 1
        self.sent = []
        self.recorded = []

    def send(self, endpoint):
        self.sent.append(endpoint)
        return self.id + 100

    def record(self, name):
        self.recorded.append(name)
        return FakeEndpoint()


class FakeSession:
    latest = None

    def __init__(self, *, recording_root=None) -> None:
        FakeSession.latest = self
        self.recording_root = recording_root
        self.stems = []
        self.endpoint = FakeEndpoint()
        self.running = FakeRunning()

    def capture(self, source):
        stem = FakeStem()
        self.stems.append(stem)
        return stem

    def polled_audio(self):
        return self.endpoint

    async def start(self):
        return self.running


@pytest.mark.asyncio
async def test_given_async_recipe_when_exited_then_native_session_stops(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(capture_module, "Session", FakeSession)

    async with capture_module.capture(
        application="Spotify",
        microphone=True,
        record_to=tmp_path,
    ) as live:
        declared = FakeSession.latest
        assert declared is not None
        assert len(declared.stems) == 2
        assert live.is_running
        assert live.audio is declared.running.audio

    assert declared.running.stop_calls == 1
