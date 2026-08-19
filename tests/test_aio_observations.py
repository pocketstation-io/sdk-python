"""Asyncio event stream ownership tests."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from pocketstation import StreamInUseError, StreamModeError, _native
from pocketstation.aio import EventStream, RunningSession
from pocketstation.aio.session import _native_async


def _event_stream(events):
    remaining = list(events)
    state = {"closed": False, "waits": 0}

    async def wait_event(_timeout_ms):
        state["waits"] += 1
        await asyncio.sleep(0)
        if remaining:
            return remaining.pop(0)
        state["closed"] = True
        return None

    async def poll_event():
        return remaining.pop(0) if remaining else None

    return (
        EventStream(
            poll_event=poll_event,
            wait_event=wait_event,
            is_closed=lambda: state["closed"],
        ),
        state,
    )


@pytest.mark.asyncio
async def test_async_event_iteration_uses_bounded_native_waits() -> None:
    stream, state = _event_stream(["started", "failed"])

    assert [event async for event in stream] == ["started", "failed"]
    assert state["waits"] == 3
    assert stream.reader_mode == "events"


@pytest.mark.asyncio
async def test_async_event_modes_cannot_be_mixed() -> None:
    stream, _ = _event_stream(["started"])

    assert await stream.read() == "started"
    with pytest.raises(StreamModeError):
        await anext(stream.iter_events())


@pytest.mark.asyncio
async def test_concurrent_async_event_reader_fails_immediately() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    async def wait_event(_timeout_ms):
        entered.set()
        await release.wait()
        return "started"

    async def poll_event():
        return None

    stream = EventStream(
        poll_event=poll_event,
        wait_event=wait_event,
        is_closed=lambda: False,
    )
    first = asyncio.create_task(stream.read())
    await entered.wait()

    with pytest.raises(StreamInUseError):
        await stream.read(timeout_s=0.0)

    release.set()
    assert await first == "started"


@pytest.mark.asyncio
async def test_async_running_session_exposes_event_stream() -> None:
    class NativeRunning:
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

    assert (await running.events.read()).lifecycle_state == "running"
    with pytest.raises(StreamModeError):
        await anext(running.events.iter_events())


@pytest.mark.asyncio
async def test_async_event_wait_uses_the_canonical_native_session(tmp_path) -> None:
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
    running = RunningSession(await _native_async(session.start))
    try:
        event = await running.events.read(timeout_s=1.0)
        assert event is not None
        assert event.session_id > 0
        assert event.kind
    finally:
        assert (await running.stop()).success
