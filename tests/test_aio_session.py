"""Asyncio Session ownership and cancellation tests."""

from __future__ import annotations

import asyncio
import threading
import time
from array import array

import pytest
from pocketstation.aio import Session


@pytest.mark.asyncio
async def test_cancelled_start_requests_the_native_token() -> None:
    native_started = threading.Event()
    native_cancelled = threading.Event()

    class BlockingNativeSession:
        def start(self, cancellation):
            native_started.set()
            while not cancellation.is_requested():
                time.sleep(0.001)
            native_cancelled.set()
            raise RuntimeError("session.start_cancelled")

    session = Session.__new__(Session)
    session._native = BlockingNativeSession()
    start = asyncio.create_task(session.start())
    assert await asyncio.to_thread(native_started.wait, 1.0)

    start.cancel()
    with pytest.raises(asyncio.CancelledError):
        await start

    assert await asyncio.to_thread(native_cancelled.wait, 1.0)


@pytest.mark.asyncio
async def test_application_owned_pcm_has_an_async_writer() -> None:
    session = Session()
    audio = session.audio_input(
        "playback",
        capacity_frames=2,
        frame_samples_per_channel=4,
    )
    audio.output.send(session.polled_audio())

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    frame = await running.audio.read(timeout_s=1.0)
    await running.stop()

    assert frame is not None
    assert frame.source_id == audio.source_id
    assert frame.stream_id == audio.stream_id
    assert list(frame.samples.cast("f")) == pytest.approx([0.1, 0.2, 0.3, 0.4])
