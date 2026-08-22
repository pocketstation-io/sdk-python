"""Generated PCM crosses the Rust bridge without Python hot-path callbacks."""

from __future__ import annotations

from time import monotonic

import pocketstation._native as _native
import pytest
from pocketstation._api import Operator, PocketStationError, Session, Source

GRAPH_OPERATOR_ID = "org.pocketstation.python.conformance.audio-pass-through.v1"
NONCONCRETE_OPERATOR_ID = "org.pocketstation.python.conformance.nonconcrete-audio.v1"


def _conformance_session(tmp_path) -> Session:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    return Session._from_native(_native.Session.conformance(tmp_path))


def test_registered_operator_reenters_generated_audio_with_lineage_and_recording(
    tmp_path,
) -> None:
    session = _conformance_session(tmp_path)
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()

    application.send(endpoint)
    application.record("application")
    derived = microphone.through(
        Operator(GRAPH_OPERATOR_ID),
        input_port="audio-in",
        output_port="audio-out",
    )
    generated = derived.reenter_audio()
    generated.send(endpoint)
    generated.record("generated")

    frames_by_stem = {}
    running = session.start()
    deadline = monotonic() + 5.0
    try:
        while monotonic() < deadline and len(frames_by_stem) < 2:
            frame = running.audio.read(timeout_s=0.1)
            if frame is not None:
                frames_by_stem.setdefault(frame.stem_id, frame)
    finally:
        stop = running.stop()

    assert set(frames_by_stem) == {application.id, generated.id}
    assert all(frame.source_id > 0 for frame in frames_by_stem.values())
    assert all(frame.sequence_number >= 0 for frame in frames_by_stem.values())
    assert all(frame.timestamp_start_ns >= 0 for frame in frames_by_stem.values())
    assert all(frame.samples.readonly for frame in frames_by_stem.values())
    assert stop.success
    assert stop.recording is not None
    assert stop.recording.complete
    assert {stem.stem_name for stem in stop.recording.stems} == {
        "application",
        "generated",
    }


def test_nonconcrete_operator_output_is_rejected_before_runtime_start(tmp_path) -> None:
    session = _conformance_session(tmp_path)
    microphone = session.capture(Source.microphone_default())
    output = microphone.through(
        Operator(NONCONCRETE_OPERATOR_ID),
        input_port="audio-in",
        output_port="audio-out",
    )
    output.reenter_audio().send(session.polled_audio())

    with pytest.raises(PocketStationError) as failure:
        session.start()
    assert failure.value.code == "session.compile_failed"
    assert "cannot enter the audio bridge because it is not concrete PCM" in str(
        failure.value
    )


def test_generated_audio_output_must_remain_exclusive(tmp_path) -> None:
    session = _conformance_session(tmp_path)
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()
    output = microphone.through(
        Operator(GRAPH_OPERATOR_ID),
        input_port="audio-in",
        output_port="audio-out",
    )
    output.reenter_audio().send(endpoint)
    output.send(endpoint)

    with pytest.raises(PocketStationError) as failure:
        session.start()
    assert failure.value.code == "session.compile_failed"
    assert "must have exactly one generated-audio consumer" in str(failure.value)
