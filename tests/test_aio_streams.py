"""Asyncio bounded audio-stream ownership and cancellation tests."""

from __future__ import annotations

import asyncio
import threading
from time import monotonic

import pytest
from pocketstation import STREAM_EOF, StreamInUseError, StreamModeError, _native
from pocketstation.aio import AudioStream, RunningSession
from pocketstation.aio.session import _native_async


def _stream_from_batches(batches):
    remaining = list(batches)
    state = {"closed": False, "waits": 0}

    async def wait_batch(_timeout_ms):
        state["waits"] += 1
        await asyncio.sleep(0)
        if remaining:
            return remaining.pop(0)
        state["closed"] = True
        return None

    async def poll_batch():
        return None

    return (
        AudioStream(
            poll_batch=poll_batch,
            wait_batch=wait_batch,
            is_closed=lambda: state["closed"],
        ),
        state,
    )


async def _canonical_running_session(recording_root) -> RunningSession:
    session = _native.Session.conformance(recording_root)
    application = session.capture(
        _native.Source.application("PocketStation Python Fixture")
    )
    microphone = session.capture(_native.Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    return RunningSession(await _native_async(session.start))


@pytest.mark.asyncio
async def test_async_iteration_flattens_native_batches() -> None:
    stream, state = _stream_from_batches([["a", "b"], ["c"]])

    observed = [frame async for frame in stream]

    assert observed == ["a", "b", "c"]
    assert state["waits"] == 3
    assert stream.reader_mode == "frames"


@pytest.mark.asyncio
async def test_async_running_session_exposes_the_same_exclusive_stream() -> None:
    class NativeRunning:
        def __init__(self) -> None:
            self.batches = [["a"]]
            self.lifecycle_state = "running"

        def poll_audio(self):
            return None

        def wait_audio(self, _timeout_ms):
            return self.batches.pop(0) if self.batches else None

    running = RunningSession(NativeRunning())

    assert await running.audio.read() == "a"
    with pytest.raises(StreamModeError):
        await running.wait_audio()


@pytest.mark.asyncio
async def test_concurrent_async_read_fails_immediately() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    async def wait_batch(_timeout_ms):
        entered.set()
        await release.wait()
        return ["a"]

    async def poll_batch():
        return None

    stream = AudioStream(
        poll_batch=poll_batch,
        wait_batch=wait_batch,
        is_closed=lambda: False,
    )
    first = asyncio.create_task(stream.read())
    await entered.wait()

    with pytest.raises(StreamInUseError):
        await stream.read(timeout_s=0.0)

    release.set()
    assert await first == "a"


@pytest.mark.asyncio
async def test_cancelled_reader_settles_before_releasing_ownership() -> None:
    entered = asyncio.Event()
    settled = asyncio.Event()

    async def wait_batch(_timeout_ms):
        entered.set()
        try:
            await asyncio.Future()
        finally:
            settled.set()

    async def poll_batch():
        return None

    stream = AudioStream(
        poll_batch=poll_batch,
        wait_batch=wait_batch,
        is_closed=lambda: False,
    )
    reader = asyncio.create_task(stream.read())
    await entered.wait()
    reader.cancel()

    with pytest.raises(asyncio.CancelledError):
        await reader

    assert settled.is_set()


@pytest.mark.asyncio
async def test_async_reader_mode_cannot_change() -> None:
    stream, _ = _stream_from_batches([["a"]])
    assert await stream.read() == "a"

    with pytest.raises(StreamModeError):
        await anext(stream.frames())


@pytest.mark.asyncio
async def test_native_cancellation_waits_for_bounded_thread_cleanup() -> None:
    entered = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    def operation() -> str:
        entered.set()
        assert release.wait(1.0)
        finished.set()
        return "done"

    task = asyncio.create_task(_native_async(operation))
    assert await asyncio.to_thread(entered.wait, 1.0)
    started = monotonic()
    task.cancel()
    asyncio.get_running_loop().call_later(0.02, release.set)

    with pytest.raises(asyncio.CancelledError):
        await task

    assert monotonic() - started >= 0.015
    assert finished.is_set()


@pytest.mark.asyncio
async def test_async_iteration_rejects_a_busy_poll_timeout() -> None:
    stream, _ = _stream_from_batches([])
    with pytest.raises(ValueError, match=r"at least 0\.001"):
        await anext(stream.frames(wait_timeout_s=0.0))


@pytest.mark.asyncio
async def test_async_audio_batch_result_distinguishes_states() -> None:
    state = {"closed": False}

    async def empty() -> None:
        return None

    async def wait_empty(_timeout_ms: int) -> None:
        return None

    stream = AudioStream(
        poll_batch=empty,
        wait_batch=wait_empty,
        is_closed=lambda: state["closed"],
    )

    assert await stream.poll() is None
    assert await stream.read_result(timeout_s=0.001) is None
    state["closed"] = True
    assert await stream.poll() is STREAM_EOF
    assert await stream.read_result(timeout_s=0.001) is STREAM_EOF


@pytest.mark.asyncio
async def test_async_frame_stream_preserves_two_stems_from_canonical_native_session(
    tmp_path,
) -> None:
    """Exercise async iteration over Rust's deterministic Session engine."""
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    running = await _canonical_running_session(tmp_path)
    frames = running.audio.frames(wait_timeout_s=0.1)
    observed_stems: set[int] = set()
    try:
        first = await anext(frames)
        observed_stems.add(first.stem_id)
        assert first.source_id > 0
        assert first.sequence_number >= 0
        assert first.timestamp_start_ns >= 0
        assert first.discontinuity_epoch >= 0
        assert first.samples.readonly

        with pytest.raises(StreamInUseError):
            await anext(running.audio.frames(wait_timeout_s=0.1))
        with pytest.raises(StreamModeError):
            await running.audio.read(timeout_s=0.1)

        async for frame in frames:
            observed_stems.add(frame.stem_id)
            if len(observed_stems) == 2:
                break
    finally:
        await frames.aclose()
        stop = await running.stop()

    assert len(observed_stems) == 2
    assert stop.success


@pytest.mark.asyncio
async def test_async_read_and_batch_modes_use_canonical_native_session(
    tmp_path,
) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    direct = await _canonical_running_session(tmp_path / "direct")
    frame = await direct.audio.read(timeout_s=1.0)
    assert frame is not None
    assert frame.samples.readonly
    assert (await direct.stop()).success

    batched = await _canonical_running_session(tmp_path / "batched")
    batches = batched.audio.batches(wait_timeout_s=0.1)
    try:
        batch = await anext(batches)
        assert len(batch) > 0
        assert all(frame.samples.readonly for frame in batch)
    finally:
        await batches.aclose()
        stop = await batched.stop()
    assert stop.success
