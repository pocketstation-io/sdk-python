"""Synchronous bounded audio-stream ownership tests."""

from __future__ import annotations

import threading

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    STREAM_EOF,
    AudioStream,
    RunningSession,
    StreamInUseError,
    StreamModeError,
)


def _stream_from_batches(batches):
    remaining = list(batches)
    state = {"closed": False, "waits": 0}

    def wait_batch(_timeout_ms):
        state["waits"] += 1
        if remaining:
            return remaining.pop(0)
        state["closed"] = True
        return None

    return (
        AudioStream(
            poll_batch=lambda: None,
            wait_batch=wait_batch,
            is_closed=lambda: state["closed"],
        ),
        state,
    )


def _canonical_running_session(recording_root) -> RunningSession:
    session = _native.Session.conformance(recording_root)
    application = session.capture(
        _native.Source.application("PocketStation Python Fixture")
    )
    microphone = session.capture(_native.Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    return RunningSession(session.start())


def test_frame_iteration_flattens_only_the_current_native_batch() -> None:
    stream, state = _stream_from_batches([["a", "b"], ["c"]])

    assert list(stream) == ["a", "b", "c"]
    assert state["waits"] == 3
    assert stream.reader_mode == "frames"


def test_direct_reads_reuse_one_batch_without_another_native_poll() -> None:
    stream, state = _stream_from_batches([["a", "b"]])

    assert stream.read() == "a"
    assert stream.read() == "b"
    assert state["waits"] == 1
    assert stream.reader_mode == "read"


def test_running_session_exposes_the_same_exclusive_stream() -> None:
    class NativeRunning:
        def __init__(self) -> None:
            self.batches = [["a"]]
            self.lifecycle_state = "running"

        def poll_audio(self):
            return None

        def wait_audio(self, _timeout_ms):
            return self.batches.pop(0) if self.batches else None

    running = RunningSession(NativeRunning())

    assert running.audio.read() == "a"
    with pytest.raises(StreamModeError):
        running.wait_audio()


def test_reader_mode_cannot_change_after_first_consumption() -> None:
    stream, _ = _stream_from_batches([["a"]])
    assert stream.read() == "a"

    with pytest.raises(StreamModeError) as failure:
        next(stream.batches())

    assert failure.value.code == "stream.mode_conflict"
    assert failure.value.active_mode == "read"
    assert failure.value.requested_mode == "batches"


def test_second_iterator_fails_instead_of_competing_for_frames() -> None:
    stream, _ = _stream_from_batches([["a", "b"]])
    first = stream.frames()
    assert next(first) == "a"

    with pytest.raises(StreamInUseError) as failure:
        next(stream.frames())

    assert failure.value.code == "stream.in_use"
    first.close()
    assert list(stream.frames()) == ["b"]


def test_concurrent_direct_read_fails_instead_of_waiting() -> None:
    entered = threading.Event()
    release = threading.Event()

    def wait_batch(_timeout_ms):
        entered.set()
        assert release.wait(1.0)
        return ["a"]

    stream = AudioStream(
        poll_batch=lambda: None,
        wait_batch=wait_batch,
        is_closed=lambda: False,
    )
    first_result = []
    first = threading.Thread(target=lambda: first_result.append(stream.read()))
    first.start()
    assert entered.wait(1.0)

    with pytest.raises(StreamInUseError):
        stream.read(timeout_s=0.0)

    release.set()
    first.join(timeout=1.0)
    assert not first.is_alive()
    assert first_result == ["a"]


@pytest.mark.parametrize("timeout", [-0.1, 1.1])
def test_timeout_must_remain_bounded(timeout: float) -> None:
    stream, _ = _stream_from_batches([])
    with pytest.raises(ValueError, match=r"between 0\.0 and 1\.0"):
        stream.read(timeout_s=timeout)


def test_iteration_rejects_a_busy_poll_timeout() -> None:
    stream, _ = _stream_from_batches([])
    with pytest.raises(ValueError, match=r"at least 0\.001"):
        next(stream.frames(wait_timeout_s=0.0))


def test_audio_batch_result_distinguishes_empty_timeout_and_closed() -> None:
    state = {"closed": False}
    stream = AudioStream(
        poll_batch=lambda: None,
        wait_batch=lambda _timeout_ms: None,
        is_closed=lambda: state["closed"],
    )

    assert stream.poll() is None
    assert stream.read_result(timeout_s=0.001) is None
    state["closed"] = True
    assert stream.poll() is STREAM_EOF
    assert stream.read_result(timeout_s=0.001) is STREAM_EOF


def test_frame_stream_preserves_two_stems_from_canonical_native_session(
    tmp_path,
) -> None:
    """Exercise the public stream over Rust's deterministic Session engine."""
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    running = _canonical_running_session(tmp_path)
    frames = running.audio.frames(wait_timeout_s=0.1)
    observed_stems: set[int] = set()
    try:
        first = next(frames)
        observed_stems.add(first.stem_id)
        assert first.source_id > 0
        assert first.sequence_number >= 0
        assert first.timestamp_start_ns >= 0
        assert first.discontinuity_epoch >= 0
        assert first.clock.id == first.clock_id
        assert first.clock.kind == "process-monotonic"
        assert first.clock.origin == "process-start"
        assert first.clock.tick_rate_hz == 1_000_000_000
        assert first.route_enqueued_at_ns > 0
        assert first.route_received_at_ns >= first.route_enqueued_at_ns
        assert first.endpoint_enqueued_at_ns is not None
        assert first.endpoint_enqueued_at_ns >= first.route_received_at_ns
        assert first.polled_at_ns is not None
        assert first.polled_at_ns >= first.endpoint_enqueued_at_ns
        assert first.samples.readonly

        with pytest.raises(StreamInUseError):
            next(running.audio.frames(wait_timeout_s=0.1))
        with pytest.raises(StreamModeError):
            running.audio.read(timeout_s=0.1)

        for frame in frames:
            observed_stems.add(frame.stem_id)
            if len(observed_stems) == 2:
                break
    finally:
        frames.close()
        stop = running.stop()

    assert len(observed_stems) == 2
    assert stop.success


def test_read_and_batch_modes_use_canonical_native_session(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    direct = _canonical_running_session(tmp_path / "direct")
    frame = direct.audio.read(timeout_s=1.0)
    assert frame is not None
    assert frame.samples.readonly
    assert direct.stop().success

    batched = _canonical_running_session(tmp_path / "batched")
    batches = batched.audio.batches(wait_timeout_s=0.1)
    try:
        batch = next(batches)
        assert len(batch) > 0
        assert all(frame.samples.readonly for frame in batch)
    finally:
        batches.close()
        stop = batched.stop()
    assert stop.success
