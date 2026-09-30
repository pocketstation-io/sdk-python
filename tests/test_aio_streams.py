"""Asyncio bounded audio-stream ownership and cancellation tests."""

from __future__ import annotations

import asyncio
import threading

import pocketstation._native as _native
import pytest
from pocketstation._api import STREAM_EOF, StreamInUseError, StreamModeError
from pocketstation.aio._api import AudioStream, RunningSession
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
async def test_async_iteration_drains_a_terminal_batch_before_eof() -> None:
    state = {"closed": False, "waits": 0}

    async def terminal_batch(_timeout_ms: int):
        state["waits"] += 1
        state["closed"] = True
        return ["first", "second"]

    async def poll_empty():
        return None

    stream = AudioStream(
        poll_batch=poll_empty,
        wait_batch=terminal_batch,
        is_closed=lambda: state["closed"],
    )

    assert [frame async for frame in stream.frames()] == ["first", "second"]
    assert state["waits"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", ["read", "read_batch", "read_result"])
async def test_async_direct_audio_wait_defaults_forward_exactly_100_milliseconds(
    method_name: str,
) -> None:
    observed: list[int] = []

    async def wait_batch(timeout_ms: int):
        observed.append(timeout_ms)
        return None

    async def poll_batch():
        return None

    stream = AudioStream(
        poll_batch=poll_batch,
        wait_batch=wait_batch,
        is_closed=lambda: False,
    )

    assert await getattr(stream, method_name)() is None
    assert observed == [100]


@pytest.mark.asyncio
async def test_async_audio_read_distinguishes_timeout_from_repeated_eof() -> None:
    async def empty(_timeout_ms: int):
        return None

    async def poll_empty():
        return None

    timeout_stream = AudioStream(
        poll_batch=poll_empty,
        wait_batch=empty,
        is_closed=lambda: False,
    )
    assert await timeout_stream.read() is None

    observed: list[int] = []
    state = {"closed": False}

    async def close_after_wait(timeout_ms: int):
        observed.append(timeout_ms)
        state["closed"] = True
        return None

    terminal_stream = AudioStream(
        poll_batch=poll_empty,
        wait_batch=close_after_wait,
        is_closed=lambda: state["closed"],
    )
    assert await terminal_stream.read() is STREAM_EOF
    assert await terminal_stream.read() is STREAM_EOF
    assert observed == [100]


@pytest.mark.asyncio
async def test_async_running_session_exposes_the_same_exclusive_stream() -> None:
    class NativeRunning:
        def __init__(self) -> None:
            self.batches = [["a"]]
            self.lifecycle_state = "running"
            self.audio_drained = False

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
async def test_cancelled_native_audio_batch_is_returned_by_the_next_read() -> None:
    entered = threading.Event()
    release = threading.Event()

    class NativeRunning:
        lifecycle_state = "running"
        audio_drained = False

        def __init__(self) -> None:
            self.waits = 0

        def wait_audio(self, _timeout_ms):
            self.waits += 1
            entered.set()
            assert release.wait(1.0)
            return ["first", "second"]

        def poll_audio(self):
            return None

    native = NativeRunning()
    running = RunningSession(native)
    reader = asyncio.create_task(running.audio.read())
    assert await asyncio.to_thread(entered.wait, 1.0)

    reader.cancel()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await reader

    assert await running.audio.read() == "first"
    assert await running.audio.read() == "second"
    assert native.waits == 1


@pytest.mark.parametrize("mode", ["read", "poll", "read_result", "frames", "batches"])
async def test_async_stopped_producer_drains_existing_receipt_before_eof(
    mode: str,
) -> None:
    batches = [["first", "second"], ["tail"]]

    async def poll_batch():
        return batches.pop(0) if batches else None

    async def wait_batch(_timeout_ms):
        return await poll_batch()

    stream = AudioStream(
        poll_batch=poll_batch,
        wait_batch=wait_batch,
        is_closed=lambda: True,
        is_drained=lambda: not batches,
    )
    assert stream.is_closed
    if mode == "read":
        assert [await stream.read(), await stream.read(), await stream.read()] == [
            "first",
            "second",
            "tail",
        ]
        assert await stream.read() is STREAM_EOF
    elif mode in {"poll", "read_result"}:
        operation = getattr(stream, mode)
        assert await operation() == ["first", "second"]
        assert await operation() == ["tail"]
        assert await operation() is STREAM_EOF
    elif mode == "frames":
        assert [frame async for frame in stream.frames()] == ["first", "second", "tail"]
    else:
        assert [batch async for batch in stream.batches()] == [
            ["first", "second"],
            ["tail"],
        ]


async def test_async_discard_ignores_late_cancelled_batch() -> None:
    stream, _ = _stream_from_batches([["first", "second"]])
    assert await stream.read() == "first"
    stream._discard()
    stream._retain_cancelled_batch(["late"])  # type: ignore[arg-type]
    assert await stream.read() is STREAM_EOF


@pytest.mark.parametrize(
    "mode", ["read", "poll", "read_result", "poll_batch", "read_batch", "batches"]
)
async def test_async_discard_during_read_does_not_deliver_a_late_batch(
    mode: str,
) -> None:
    async def poll_batch():
        await asyncio.sleep(0)
        stream._discard()
        return ["late"]

    async def wait_batch(_timeout_ms):
        return await poll_batch()

    stream = AudioStream(
        poll_batch=poll_batch,
        wait_batch=wait_batch,
        is_closed=lambda: False,
    )
    if mode == "batches":
        assert [batch async for batch in stream.batches()] == []
    elif mode in {"poll_batch", "read_batch"}:
        assert await getattr(stream, mode)() is None
    else:
        assert await getattr(stream, mode)() is STREAM_EOF


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
    task.cancel()
    asyncio.get_running_loop().call_later(0.02, release.set)

    with pytest.raises(asyncio.CancelledError):
        await task

    assert finished.is_set()


@pytest.mark.asyncio
async def test_native_operation_is_not_started_when_cancelled_before_dispatch() -> None:
    started = threading.Event()
    task = asyncio.create_task(_native_async(lambda: started.set()))
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0)

    assert not started.is_set()


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
