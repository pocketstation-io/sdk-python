"""Synchronous event stream ownership and native-wait tests."""

from __future__ import annotations

import threading
from types import SimpleNamespace

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    EventStream,
    RunningSession,
    StreamInUseError,
    StreamModeError,
)


def _event_stream(events):
    remaining = list(events)
    state = {"closed": False, "waits": 0}

    def wait_event(_timeout_ms):
        state["waits"] += 1
        if remaining:
            return remaining.pop(0)
        state["closed"] = True
        return None

    return (
        EventStream(
            poll_event=lambda: remaining.pop(0) if remaining else None,
            wait_event=wait_event,
            is_closed=lambda: state["closed"],
        ),
        state,
    )


def test_event_iteration_uses_bounded_waits() -> None:
    stream, state = _event_stream(["started", "failed"])

    assert list(stream) == ["started", "failed"]
    assert state["waits"] == 3
    assert stream.reader_mode == "events"


def test_event_read_mode_is_exclusive() -> None:
    stream, _ = _event_stream(["started"])

    assert stream.read() == "started"
    with pytest.raises(StreamModeError):
        next(iter(stream))


def test_concurrent_event_reader_fails_immediately() -> None:
    entered = threading.Event()
    release = threading.Event()

    def wait_event(_timeout_ms):
        entered.set()
        assert release.wait(1.0)
        return "started"

    stream = EventStream(
        poll_event=lambda: None,
        wait_event=wait_event,
        is_closed=lambda: False,
    )
    observed = []
    first = threading.Thread(target=lambda: observed.append(stream.read()))
    first.start()
    assert entered.wait(1.0)

    with pytest.raises(StreamInUseError):
        stream.read(timeout_s=0.0)

    release.set()
    first.join(timeout=1.0)
    assert observed == ["started"]


def test_running_session_exposes_events_without_public_poll_loop() -> None:
    class NativeRunning:
        lifecycle_state = "running"

        def poll_audio(self):
            return None

        def wait_audio(self, _timeout_ms):
            return None

        def poll_event(self):
            return None

        def wait_event(self, _timeout_ms):
            return SimpleNamespace(
                kind="lifecycle",
                lifecycle_state="running",
                session_id=1,
                stem_id=None,
                endpoint_id=None,
                route_id=None,
                failures_total=0,
                terminal_state=None,
                source_event_kind=None,
                failures=lambda: [],
            )

    running = RunningSession(NativeRunning())

    assert running.events.read().lifecycle_state == "running"
    with pytest.raises(StreamModeError):
        next(iter(running.events))


def test_event_wait_timeout_remains_bounded() -> None:
    stream, _ = _event_stream([])
    with pytest.raises(ValueError, match=r"between 0\.0 and 1\.0"):
        stream.read(timeout_s=1.1)


def test_event_wait_uses_the_canonical_native_session(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    session = _native.Session.conformance(tmp_path)
    application = session.capture(
        _native.Source.application("PocketStation Python Fixture")
    )
    microphone = session.capture(_native.Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    running = RunningSession(session.start())
    try:
        event = running.events.read(timeout_s=1.0)
        assert event is not None
        assert event.session_id > 0
        assert event.kind
    finally:
        assert running.stop().success
