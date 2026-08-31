"""Multistem recording remains attached to source-aware Rust Session stems."""

from __future__ import annotations

from time import monotonic
from types import SimpleNamespace

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    RecordingDiscontinuityKind,
    RecordingOutcome,
    RecordingState,
    Session,
    Source,
)


def test_application_and_microphone_record_as_independent_stems(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    session = Session._from_native(_native.Session.conformance(tmp_path))
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    application.record("application")
    microphone.record("microphone")

    running = session.start()
    observed_stems: set[int] = set()
    deadline = monotonic() + 5.0
    try:
        while monotonic() < deadline and len(observed_stems) < 2:
            frame = running.audio.read(timeout_s=0.1)
            if frame is not None:
                observed_stems.add(frame.stem_id)
    finally:
        stop = running.stop()

    assert observed_stems == {application.id, microphone.id}
    assert stop.success
    assert stop.recording is not None
    assert stop.recording.complete
    assert stop.recording.session_id == running.session_id
    assert stop.recording.group_id == "session.multistem.default.v1"
    assert stop.recording.manifest_path == (
        stop.recording.session_directory / "manifest.json"
    )
    assert stop.recording.manifest_path.is_file()
    assert stop.recording.manifest_schema_version == 2
    outcomes = {stem.stem_name: stem for stem in stop.recording.stems}
    assert set(outcomes) == {"application", "microphone"}
    assert all(stem.frames_written_total > 0 for stem in outcomes.values())
    assert all(stem.error is None for stem in outcomes.values())
    assert all(stem.discontinuities == () for stem in outcomes.values())
    assert stop.recording.error_code is None


def test_incomplete_recording_preserves_stable_code_and_gap_detail(tmp_path) -> None:
    gap = SimpleNamespace(
        stem_id=7,
        label="application",
        kind="timestamp-gap",
        timestamp_start_ns=100,
        timestamp_end_ns=200,
        sequence_start=4,
        sequence_end=5,
    )
    stem = SimpleNamespace(
        stem_name="application",
        frames_written_total=10,
        stale_frames_total=1,
        error="fixture failure",
        queue_capacity_frames=8,
        queue_peak_frames=4,
        frames_delivered_total=10,
        frames_dropped_total=1,
        queue_full_drops_total=1,
        discontinuities_total=1,
        discontinuities=lambda: [gap],
    )
    outcome = RecordingOutcome._from_native(
        SimpleNamespace(
            session_id=7,
            group_id="session.multistem.default.v1",
            state="incomplete",
            complete=False,
            completed_stems=0,
            failed_stems=1,
            session_directory=str(tmp_path),
            manifest_path=str(tmp_path / "manifest.json"),
            manifest_schema_version=1,
            error_code="recording.incomplete",
            stems=lambda: [stem],
        )
    )

    assert outcome.state is RecordingState.INCOMPLETE
    assert outcome.error_code == "recording.incomplete"
    [record] = outcome.stems[0].discontinuities
    assert record.kind is RecordingDiscontinuityKind.TIMESTAMP_GAP
    assert record.timestamp_end_ns - record.timestamp_start_ns == 100
