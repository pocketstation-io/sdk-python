"""Real Session coverage for bounded asyncio event ingress."""

from __future__ import annotations

import json

import pocketstation.aio as pks
import pytest
from pocketstation.errors import EventInputFullError
from pocketstation.signal import EndOfStream


@pytest.mark.asyncio
async def test_event_input_preserves_json_and_timing_through_session() -> None:
    session = pks.Session()
    events = session.event_input("provider-events", capacity_events=2)
    subscription = session.subscribe(events.output, signal=events.signal)
    running = await session.start()
    try:
        events.try_write({"type": "speech.started", "revision": 1}, timestamp_ns=42)
        envelope = await running.signals(subscription).read(timeout_s=1.0)

        assert envelope is not None
        assert not isinstance(envelope, EndOfStream)
        assert json.loads(envelope.payload) == {
            "revision": 1,
            "type": "speech.started",
        }
        assert envelope.timing.source_timestamp_ns == 42
        assert events.observations().accepted_total == 1
    finally:
        await events.aclose()
        await running.stop()


@pytest.mark.asyncio
async def test_event_input_reports_finite_capacity_before_session_start() -> None:
    session = pks.Session()
    events = session.event_input("provider-events", capacity_events=1)
    events.try_write({"type": "first"})

    with pytest.raises(EventInputFullError, match="event input is full"):
        events.try_write({"type": "second"})

    observations = events.observations()
    assert observations.capacity_events == 1
    assert observations.depth_events == 1
    assert observations.accepted_total == 1
    assert observations.full_total == 1
