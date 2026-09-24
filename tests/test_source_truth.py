"""Core-backed microphone Source truth and host-selected recovery."""

from __future__ import annotations

import pocketstation._native as native
import pytest
from pocketstation import aio
from pocketstation._api import Session, Source
from pocketstation.errors import SourceError
from pocketstation.source_truth import (
    SampleRepresentation,
    SourceActivityPolicy,
    SourceActivityState,
    SourceSignalPolicy,
    SourceSignalState,
)
from pocketstation.sources import SourceSelectorKind


def _declared_session(tmp_path):
    if not hasattr(native.Session, "conformance"):
        pytest.skip("native extension needs conformance-fixtures")
    session = Session._from_native(native.Session.conformance(tmp_path))
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    output = session.polled_audio()
    application.send(output)
    microphone.send(output)
    return session, application, microphone


def test_core_source_truth_and_explicit_recovery(tmp_path) -> None:
    session, application, microphone = _declared_session(tmp_path)
    running = session.start()
    try:
        assert running.audio.read(timeout_s=1.0) is not None
        metrics = running.metrics()
        assert len(metrics.sources) == 2
        assert len(metrics.source_native_formats) == 2
        assert len(metrics.source_activities) == 2
        assert len(metrics.source_signals) == 2
        assert len(metrics.source_replacements) == 2
        assert [item.stem_id for item in metrics.source_native_formats] == [
            application.id,
            microphone.id,
        ]
        assert metrics.source_native_formats[1].opened_native_format is None
        assert metrics.source_activities[1].frames_received_total > 0
        assert (
            metrics.source_activities[1]
            .evaluate(SourceActivityPolicy(1_000_000_000, 1_000_000_000))
            .state
            is SourceActivityState.ACTIVE
        )
        assert metrics.source_signals[1].samples_observed_total > 0
        assert metrics.source_signals[1].window_peak_linear == pytest.approx(0.5)
        assert (
            metrics.source_signals[1]
            .evaluate(SourceSignalPolicy(-30.0, -30.0, 1_000_000_000))
            .state
            is SourceSignalState.MEETS_CALLER_THRESHOLDS
        )
        with pytest.raises(ValueError, match="microphone Source"):
            running.replace_microphone_source(microphone, Source.system_audio())
        with pytest.raises(SourceError) as non_microphone:
            running.replace_microphone_source(
                application, Source.microphone_id("fixture-selected-microphone")
            )
        assert non_microphone.value.code == "source.not_microphone"
        prior = metrics.source_replacements[1]
        assert prior.attempts_total == 0
        replacement = running.replace_microphone_source(
            microphone, Source.microphone_id("fixture-selected-microphone")
        )
        assert replacement.stem_id == microphone.id
        assert replacement.requested_selector_kind is SourceSelectorKind.MICROPHONE_ID
        assert replacement.requested_device_id == "fixture-selected-microphone"
        assert replacement.source_generation > prior.source_generation
        after = running.metrics().source_replacements[1]
        assert after.attempts_total == 1
        assert after.completed_total == 1
        assert after.attached_source_id == replacement.source_id
        reopened = running.reopen_microphone_source(
            microphone, Source.microphone_default()
        )
        assert reopened.source_generation > replacement.source_generation
        assert reopened.requested_selector_kind is SourceSelectorKind.MICROPHONE_DEFAULT
        assert reopened.requested_device_id is None
        final = running.metrics().source_replacements[1]
        assert final.attempts_total == 2
        assert final.completed_total == 2
        assert final.discontinuity_epoch == reopened.discontinuity_epoch
    finally:
        running.stop()


@pytest.mark.asyncio
async def test_async_source_truth_and_recovery(tmp_path) -> None:
    session, _, microphone = _declared_session(tmp_path)
    running = aio.RunningSession(session.start()._native)
    try:
        metrics = await running.metrics()
        assert len(metrics.source_activities) == 2
        replacement = await running.replace_microphone_source(
            microphone, Source.microphone_id("fixture-selected-microphone")
        )
        assert replacement.stem_id == microphone.id
        assert replacement.requested_device_id == "fixture-selected-microphone"
        reopened = await running.reopen_microphone_source(
            microphone, Source.microphone_default()
        )
        assert reopened.source_generation > replacement.source_generation
        assert reopened.requested_selector_kind is SourceSelectorKind.MICROPHONE_DEFAULT
    finally:
        await running.stop()


def test_source_policies_reject_invalid_thresholds() -> None:
    with pytest.raises(ValueError, match="positive"):
        SourceActivityPolicy(0, 1)
    with pytest.raises(ValueError, match="thresholds"):
        SourceSignalPolicy(float("nan"), -30.0, 1)
    assert SampleRepresentation.FLOAT_32 == "float-32"
