"""Progressive synchronous capture recipe tests."""

from __future__ import annotations

import importlib

import pytest

capture_module = importlib.import_module("pocketstation.capture")


class FakeStopResult:
    success = True
    recording = None


class FakeRunning:
    def __init__(self) -> None:
        self.is_stopped = False
        self.stop_result = None
        self.stop_calls = 0
        self.audio = object()

    def stop(self):
        self.stop_calls += 1
        self.is_stopped = True
        self.stop_result = FakeStopResult()
        return self.stop_result

    def close(self):
        self.stop()

    def poll_audio(self):
        return None

    def audio_batches(self, *, wait_timeout_ms=100):
        return iter(())

    def poll_event(self):
        return None

    def metrics(self):
        return {"source_count": 2}


class FakeEndpoint:
    pass


class FakeStem:
    next_id = 1

    def __init__(self, source) -> None:
        self.source = source
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
        stem = FakeStem(source)
        self.stems.append(stem)
        return stem

    def polled_audio(self):
        return self.endpoint

    def start(self):
        return self.running


def test_given_recipe_when_entered_then_one_session_owns_two_stems(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(capture_module, "Session", FakeSession)

    with capture_module.capture(
        application="Spotify",
        microphone=True,
        record_to=tmp_path,
    ) as live:
        declared = FakeSession.latest
        assert declared is not None
        assert len(declared.stems) == 2
        assert declared.stems[0].sent == [declared.endpoint]
        assert declared.stems[1].sent == [declared.endpoint]
        assert declared.stems[0].recorded == ["application"]
        assert declared.stems[1].recorded == ["microphone"]
        assert live.application_stem.id != live.microphone_stem.id
        assert live.audio is declared.running.audio

    assert declared.running.stop_calls == 1


def test_given_recipe_without_microphone_when_declared_then_one_stem(monkeypatch):
    monkeypatch.setattr(capture_module, "Session", FakeSession)
    live = capture_module.capture(application="Spotify")

    assert len(FakeSession.latest.stems) == 1
    assert live.microphone_stem is None
    assert live.microphone_route_id is None


@pytest.mark.parametrize("microphone", [None, 3, object()])
def test_given_invalid_microphone_selector_when_declared_then_rejected(microphone):
    with pytest.raises(TypeError, match="microphone must be"):
        capture_module.capture(application="Spotify", microphone=microphone)
