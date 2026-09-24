"""Core-backed microphone Source truth and host-selected recovery."""

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import cast

import pocketstation._api as public_api
import pocketstation._native as native
import pytest
from pocketstation import aio
from pocketstation._api import Session, Source
from pocketstation.errors import PocketStationError, SourceError
from pocketstation.source_truth import (
    OpenedNativeFormat,
    SampleRepresentation,
    SourceActivityObservation,
    SourceActivityPolicy,
    SourceActivityState,
    SourceSignalObservation,
    SourceSignalPolicy,
    SourceSignalState,
    evaluate_source_activity,
    evaluate_source_signal,
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
        assert [
            item.opened_native_format for item in metrics.source_native_formats
        ] == [
            OpenedNativeFormat(48_000, 2, SampleRepresentation.FLOAT_32),
            OpenedNativeFormat(48_000, 1, SampleRepresentation.FLOAT_32),
        ]
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


def test_hfp_shaped_replacement_preserves_native_format_and_new_lineage(
    tmp_path,
) -> None:
    session, _, microphone = _declared_session(tmp_path)
    running = session.start()
    try:
        replacement = running.replace_microphone_source(
            microphone, Source.microphone_id("fixture-hfp-16khz-i16")
        )

        assert int(replacement.previous_source_id) == 202
        assert int(replacement.source_id) == 204
        assert replacement.source_generation == 2
        assert replacement.discontinuity_epoch == 1
        assert replacement.opened_native_format == OpenedNativeFormat(
            16_000,
            1,
            SampleRepresentation.SIGNED_INTEGER_16,
        )
        assert replacement.requested_selector_kind is SourceSelectorKind.MICROPHONE_ID
        assert replacement.requested_device_id == "fixture-hfp-16khz-i16"

        deadline = time.monotonic() + 1.0
        while True:
            metrics = running.metrics()
            microphone_index = next(
                index
                for index, item in enumerate(metrics.source_native_formats)
                if item.stem_id == microphone.id
            )
            signal = metrics.source_signals[microphone_index]
            if signal.window_source_generation == 2:
                break
            assert time.monotonic() < deadline
            time.sleep(0.001)
        native_format = metrics.source_native_formats[
            microphone_index
        ].opened_native_format
        recovery = metrics.source_replacements[microphone_index]
        assert native_format == replacement.opened_native_format
        assert recovery.attached_source_id == replacement.source_id
        assert signal.window_source_generation == 2
        assert signal.window_discontinuity_epoch == 1
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


def test_sync_recovery_after_stop_uses_core_source_error(tmp_path) -> None:
    session, _, microphone = _declared_session(tmp_path)
    running = session.start()
    running.stop()

    for operation in (
        lambda: running.replace_microphone_source(
            microphone, Source.microphone_default()
        ),
        lambda: running.reopen_microphone_source(
            microphone, Source.microphone_default()
        ),
    ):
        with pytest.raises(SourceError) as failure:
            operation()
        assert failure.value.code == "source.session_not_running"


@pytest.mark.asyncio
async def test_async_recovery_after_cancel_uses_core_source_error(tmp_path) -> None:
    session, _, microphone = _declared_session(tmp_path)
    running = aio.RunningSession(session.start()._native)
    await running.cancel()

    for operation in (
        running.replace_microphone_source,
        running.reopen_microphone_source,
    ):
        with pytest.raises(SourceError) as failure:
            await operation(microphone, Source.microphone_default())
        assert failure.value.code == "source.session_not_running"


_U64_MAX = (1 << 64) - 1


def _activity_observation(
    *,
    session_started_at_ns: int = 100,
    observed_at_ns: int = 200,
    first_frame_received_at_ns: int | None = None,
    latest_frame_received_at_ns: int | None = None,
    frames_received_total: int = 0,
) -> SourceActivityObservation:
    return SourceActivityObservation(
        session_started_at_ns=session_started_at_ns,
        observed_at_ns=observed_at_ns,
        first_frame_received_at_ns=first_frame_received_at_ns,
        latest_frame_received_at_ns=latest_frame_received_at_ns,
        frames_received_total=frames_received_total,
    )


def _signal_observation(
    *,
    window_samples_total: int = 0,
    window_exact_zero_samples_total: int = 0,
    window_nonzero_samples_total: int = 0,
    window_nonfinite_samples_total: int = 0,
    consecutive_exact_zero_duration_ns: int = 0,
    window_peak_dbfs: float | None = None,
    window_rms_dbfs: float | None = None,
) -> SourceSignalObservation:
    return SourceSignalObservation(
        observed_at_ns=200,
        samples_observed_total=window_samples_total,
        exact_zero_samples_observed_total=window_exact_zero_samples_total,
        nonzero_samples_observed_total=window_nonzero_samples_total,
        nonfinite_samples_observed_total=window_nonfinite_samples_total,
        window_timestamp_start_ns=None,
        window_duration_ns=0,
        window_observed_at_ns=None,
        window_sequence_number=None,
        window_source_generation=0,
        window_discontinuity_epoch=0,
        window_samples_total=window_samples_total,
        window_exact_zero_samples_total=window_exact_zero_samples_total,
        window_nonzero_samples_total=window_nonzero_samples_total,
        window_nonfinite_samples_total=window_nonfinite_samples_total,
        consecutive_exact_zero_duration_ns=consecutive_exact_zero_duration_ns,
        window_peak_linear=None,
        window_rms_linear=None,
        window_peak_dbfs=window_peak_dbfs,
        window_rms_dbfs=window_rms_dbfs,
        window_exact_zero_ratio=None,
    )


def test_source_policies_accept_unsigned_64_bit_boundaries() -> None:
    activity = SourceActivityPolicy(1, _U64_MAX)
    assert activity.first_frame_timeout_ns == 1
    assert activity.stall_timeout_ns == _U64_MAX
    assert SourceSignalPolicy(0.0, -30.0, 1).exact_zero_timeout_ns == 1
    assert SourceSignalPolicy(-30, -40, _U64_MAX).exact_zero_timeout_ns == _U64_MAX
    assert SampleRepresentation.FLOAT_32 == "float-32"


def test_pure_source_evaluators_are_available_from_flat_api() -> None:
    assert public_api.evaluate_source_activity is evaluate_source_activity
    assert public_api.evaluate_source_signal is evaluate_source_signal


def test_unknown_native_sample_representation_is_a_typed_observation_error() -> None:
    unknown = cast(
        native._OpenedNativeFormat,
        SimpleNamespace(
            sample_rate_hz=48_000,
            channel_count=1,
            sample_representation="future-packed-pcm",
        ),
    )

    with pytest.raises(PocketStationError) as failure:
        OpenedNativeFormat._from_native(unknown)

    assert failure.value.code == "session.invalid_observation"
    assert "future-packed-pcm" in str(failure.value)


@pytest.mark.parametrize(
    "value",
    [0, _U64_MAX + 1, True, False, 1.0, "1", None],
    ids=["zero", "u64-overflow", "true", "false", "float", "string", "none"],
)
def test_activity_policy_rejects_non_u64_nanoseconds(value: object) -> None:
    invalid = cast(int, value)
    with pytest.raises(ValueError, match="first_frame_timeout_ns"):
        SourceActivityPolicy(invalid, 1)
    with pytest.raises(ValueError, match="stall_timeout_ns"):
        SourceActivityPolicy(1, invalid)


@pytest.mark.parametrize(
    "value",
    [True, False, "-30", None, float("nan"), float("inf"), float("-inf"), 0.1],
    ids=[
        "true",
        "false",
        "string",
        "none",
        "nan",
        "positive-infinity",
        "negative-infinity",
        "positive-dbfs",
    ],
)
def test_signal_policy_rejects_non_finite_or_positive_dbfs(value: object) -> None:
    invalid = cast(float, value)
    with pytest.raises(ValueError, match="minimum_peak_dbfs"):
        SourceSignalPolicy(invalid, -30.0, 1)
    with pytest.raises(ValueError, match="minimum_rms_dbfs"):
        SourceSignalPolicy(-30.0, invalid, 1)


@pytest.mark.parametrize(
    "value",
    [0, _U64_MAX + 1, True, False, 1.0, "1", None],
    ids=["zero", "u64-overflow", "true", "false", "float", "string", "none"],
)
def test_signal_policy_rejects_non_u64_nanoseconds(value: object) -> None:
    invalid = cast(int, value)
    with pytest.raises(ValueError, match="exact_zero_timeout_ns"):
        SourceSignalPolicy(-30.0, -40.0, invalid)


def test_evaluate_source_activity_matches_core_boundary_precedence() -> None:
    awaiting = evaluate_source_activity(
        _activity_observation(), SourceActivityPolicy(101, 20)
    )
    assert awaiting.state is SourceActivityState.AWAITING_FIRST_FRAME
    assert awaiting.session_age_ns == 100
    assert awaiting.latest_frame_age_ns is None

    timed_out_observation = _activity_observation()
    timed_out = evaluate_source_activity(
        timed_out_observation, SourceActivityPolicy(100, 20)
    )
    assert timed_out.state is SourceActivityState.FIRST_FRAME_TIMED_OUT
    assert timed_out_observation.evaluate(SourceActivityPolicy(100, 20)) == timed_out

    active = evaluate_source_activity(
        _activity_observation(
            first_frame_received_at_ns=150,
            latest_frame_received_at_ns=181,
            frames_received_total=1,
        ),
        SourceActivityPolicy(100, 20),
    )
    assert active.state is SourceActivityState.ACTIVE
    assert active.latest_frame_age_ns == 19

    stalled = evaluate_source_activity(
        _activity_observation(
            first_frame_received_at_ns=150,
            latest_frame_received_at_ns=180,
            frames_received_total=1,
        ),
        SourceActivityPolicy(100, 20),
    )
    assert stalled.state is SourceActivityState.STALLED
    assert stalled.latest_frame_age_ns == 20


def test_evaluate_source_activity_saturates_future_timestamps_at_zero() -> None:
    awaiting = evaluate_source_activity(
        _activity_observation(session_started_at_ns=201),
        SourceActivityPolicy(1, 1),
    )
    assert awaiting.state is SourceActivityState.AWAITING_FIRST_FRAME
    assert awaiting.session_age_ns == 0

    active = evaluate_source_activity(
        _activity_observation(
            session_started_at_ns=201,
            first_frame_received_at_ns=201,
            latest_frame_received_at_ns=201,
            frames_received_total=1,
        ),
        SourceActivityPolicy(1, 1),
    )
    assert active.state is SourceActivityState.ACTIVE
    assert active.session_age_ns == 0
    assert active.latest_frame_age_ns == 0


def test_evaluate_source_signal_matches_core_state_precedence() -> None:
    policy = SourceSignalPolicy(-40.0, -50.0, 40)
    no_samples = _signal_observation(window_nonfinite_samples_total=1)
    assert (
        evaluate_source_signal(no_samples, policy).state
        is SourceSignalState.NO_SAMPLES_OBSERVED
    )

    nonfinite = _signal_observation(
        window_samples_total=2,
        window_exact_zero_samples_total=2,
        window_nonfinite_samples_total=1,
    )
    assert (
        evaluate_source_signal(nonfinite, policy).state
        is SourceSignalState.NONFINITE_SAMPLES_OBSERVED
    )

    pending = _signal_observation(
        window_samples_total=2,
        window_exact_zero_samples_total=2,
        consecutive_exact_zero_duration_ns=39,
    )
    assert (
        evaluate_source_signal(pending, policy).state
        is SourceSignalState.EXACT_DIGITAL_ZERO_PENDING
    )

    sustained = _signal_observation(
        window_samples_total=2,
        window_exact_zero_samples_total=2,
        consecutive_exact_zero_duration_ns=40,
    )
    sustained_result = evaluate_source_signal(sustained, policy)
    assert sustained_result.state is SourceSignalState.SUSTAINED_EXACT_DIGITAL_ZERO
    assert sustained.evaluate(policy) == sustained_result

    below = _signal_observation(
        window_samples_total=2,
        window_nonzero_samples_total=2,
        window_peak_dbfs=-40.0,
    )
    assert (
        evaluate_source_signal(below, policy).state
        is SourceSignalState.BELOW_CALLER_THRESHOLDS
    )

    meets = _signal_observation(
        window_samples_total=2,
        window_nonzero_samples_total=2,
        window_peak_dbfs=-40.0,
        window_rms_dbfs=-50.0,
    )
    meets_result = evaluate_source_signal(meets, policy)
    assert meets_result.state is SourceSignalState.MEETS_CALLER_THRESHOLDS
    assert meets_result.peak_dbfs == -40.0
    assert meets_result.rms_dbfs == -50.0
    assert meets_result.consecutive_exact_zero_duration_ns == 0
