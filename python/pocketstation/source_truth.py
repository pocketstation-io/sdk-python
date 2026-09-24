"""Measured microphone Source state and explicit host-controlled recovery."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real
from typing import Literal, cast

from ._native import (
    _OpenedNativeFormat,
    _SourceActivityObservation,
    _SourceNativeFormatObservation,
    _SourceReplacement,
    _SourceReplacementObservation,
    _SourceSignalObservation,
)
from .errors import PocketStationError
from .identity import SourceId, StemId
from .sources import Source, SourceSelectorKind

_U64_MAX = (1 << 64) - 1


def _require_positive_u64_nanoseconds(value: object, name: str) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
        or value > _U64_MAX
    ):
        raise ValueError(f"{name} must be a nonzero unsigned 64-bit nanosecond value")


def _require_dbfs(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be finite and no greater than 0 dBFS")
    try:
        numeric_value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} must be finite and no greater than 0 dBFS") from error
    if not math.isfinite(numeric_value) or numeric_value > 0:
        raise ValueError(f"{name} must be finite and no greater than 0 dBFS")


def _saturating_elapsed(observed_at_ns: int, earlier_at_ns: int) -> int:
    return observed_at_ns - earlier_at_ns if observed_at_ns >= earlier_at_ns else 0


class SampleRepresentation(StrEnum):
    SIGNED_INTEGER_8 = "signed-integer-8"
    SIGNED_INTEGER_16 = "signed-integer-16"
    SIGNED_INTEGER_24 = "signed-integer-24"
    SIGNED_INTEGER_32 = "signed-integer-32"
    SIGNED_INTEGER_64 = "signed-integer-64"
    UNSIGNED_INTEGER_8 = "unsigned-integer-8"
    UNSIGNED_INTEGER_16 = "unsigned-integer-16"
    UNSIGNED_INTEGER_24 = "unsigned-integer-24"
    UNSIGNED_INTEGER_32 = "unsigned-integer-32"
    UNSIGNED_INTEGER_64 = "unsigned-integer-64"
    FLOAT_32 = "float-32"
    FLOAT_64 = "float-64"


@dataclass(frozen=True, slots=True)
class OpenedNativeFormat:
    sample_rate_hz: int
    channel_count: int
    sample_representation: SampleRepresentation

    @classmethod
    def _from_native(cls, value: _OpenedNativeFormat) -> OpenedNativeFormat:
        try:
            sample_representation = SampleRepresentation(value.sample_representation)
        except ValueError as error:
            raise PocketStationError(
                "Native Session returned an unknown native PCM sample representation: "
                f"{value.sample_representation}",
                "session.invalid_observation",
            ) from error
        return cls(
            value.sample_rate_hz,
            value.channel_count,
            sample_representation,
        )


@dataclass(frozen=True, slots=True)
class SourceNativeFormatObservation:
    stem_id: StemId
    opened_native_format: OpenedNativeFormat | None

    @classmethod
    def _from_native(
        cls, value: _SourceNativeFormatObservation
    ) -> SourceNativeFormatObservation:
        native_format = value.opened_native_format
        return cls(
            StemId(value.stem_id),
            None
            if native_format is None
            else OpenedNativeFormat._from_native(native_format),
        )


@dataclass(frozen=True, slots=True)
class SourceReplacementObservation:
    stem_id: StemId
    attempts_total: int
    completed_total: int
    failed_before_attach_total: int
    response_timeouts_total: int
    attached_source_id: SourceId | None
    source_generation: int
    discontinuity_epoch: int
    latest_completed_at_ns: int | None

    @classmethod
    def _from_native(
        cls, value: _SourceReplacementObservation
    ) -> SourceReplacementObservation:
        return cls(
            StemId(value.stem_id),
            value.attempts_total,
            value.completed_total,
            value.failed_before_attach_total,
            value.response_timeouts_total,
            None
            if value.attached_source_id is None
            else SourceId(value.attached_source_id),
            value.source_generation,
            value.discontinuity_epoch,
            value.latest_completed_at_ns,
        )


@dataclass(frozen=True, slots=True)
class SourceReplacement:
    stem_id: StemId
    previous_source_id: SourceId
    source_id: SourceId
    source_generation: int
    discontinuity_epoch: int
    opened_native_format: OpenedNativeFormat | None
    requested_selector_kind: Literal[
        SourceSelectorKind.MICROPHONE_DEFAULT,
        SourceSelectorKind.MICROPHONE_ID,
    ]
    requested_device_id: str | None

    @classmethod
    def _from_native(
        cls, value: _SourceReplacement, source: Source
    ) -> SourceReplacement:
        native_format = value.opened_native_format
        selector_kind = cast(
            Literal[
                SourceSelectorKind.MICROPHONE_DEFAULT,
                SourceSelectorKind.MICROPHONE_ID,
            ],
            source.selector_kind,
        )
        device_id = None
        if selector_kind is SourceSelectorKind.MICROPHONE_ID:
            if not isinstance(source.selector_value, str):
                raise ValueError("microphone ID Source has no device identifier")
            device_id = source.selector_value
        return cls(
            StemId(value.stem_id),
            SourceId(value.previous_source_id),
            SourceId(value.source_id),
            value.source_generation,
            value.discontinuity_epoch,
            None
            if native_format is None
            else OpenedNativeFormat._from_native(native_format),
            selector_kind,
            device_id,
        )


class SourceActivityState(StrEnum):
    AWAITING_FIRST_FRAME = "awaiting-first-frame"
    ACTIVE = "active"
    FIRST_FRAME_TIMED_OUT = "first-frame-timed-out"
    STALLED = "stalled"


@dataclass(frozen=True, slots=True)
class SourceActivityPolicy:
    first_frame_timeout_ns: int
    stall_timeout_ns: int

    def __post_init__(self) -> None:
        _require_positive_u64_nanoseconds(
            self.first_frame_timeout_ns, "first_frame_timeout_ns"
        )
        _require_positive_u64_nanoseconds(self.stall_timeout_ns, "stall_timeout_ns")


@dataclass(frozen=True, slots=True)
class SourceActivityEvaluation:
    state: SourceActivityState
    session_age_ns: int
    latest_frame_age_ns: int | None


@dataclass(frozen=True, slots=True)
class SourceActivityObservation:
    session_started_at_ns: int
    observed_at_ns: int
    first_frame_received_at_ns: int | None
    latest_frame_received_at_ns: int | None
    frames_received_total: int

    @classmethod
    def _from_native(
        cls, value: _SourceActivityObservation
    ) -> SourceActivityObservation:
        return cls(
            value.session_started_at_ns,
            value.observed_at_ns,
            value.first_frame_received_at_ns,
            value.latest_frame_received_at_ns,
            value.frames_received_total,
        )

    def evaluate(self, policy: SourceActivityPolicy) -> SourceActivityEvaluation:
        return evaluate_source_activity(self, policy)


def evaluate_source_activity(
    observation: SourceActivityObservation,
    policy: SourceActivityPolicy,
) -> SourceActivityEvaluation:
    """Evaluate measured frame delivery without starting recovery."""

    session_age_ns = _saturating_elapsed(
        observation.observed_at_ns, observation.session_started_at_ns
    )
    latest_frame_received_at_ns = observation.latest_frame_received_at_ns
    if latest_frame_received_at_ns is None:
        state = (
            SourceActivityState.FIRST_FRAME_TIMED_OUT
            if session_age_ns >= policy.first_frame_timeout_ns
            else SourceActivityState.AWAITING_FIRST_FRAME
        )
        return SourceActivityEvaluation(state, session_age_ns, None)

    latest_frame_age_ns = _saturating_elapsed(
        observation.observed_at_ns, latest_frame_received_at_ns
    )
    state = (
        SourceActivityState.STALLED
        if latest_frame_age_ns >= policy.stall_timeout_ns
        else SourceActivityState.ACTIVE
    )
    return SourceActivityEvaluation(state, session_age_ns, latest_frame_age_ns)


class SourceSignalState(StrEnum):
    NO_SAMPLES_OBSERVED = "no-samples-observed"
    EXACT_DIGITAL_ZERO_PENDING = "exact-digital-zero-pending"
    SUSTAINED_EXACT_DIGITAL_ZERO = "sustained-exact-digital-zero"
    BELOW_CALLER_THRESHOLDS = "below-caller-thresholds"
    MEETS_CALLER_THRESHOLDS = "meets-caller-thresholds"
    NONFINITE_SAMPLES_OBSERVED = "nonfinite-samples-observed"


@dataclass(frozen=True, slots=True)
class SourceSignalPolicy:
    minimum_peak_dbfs: float
    minimum_rms_dbfs: float
    exact_zero_timeout_ns: int

    def __post_init__(self) -> None:
        _require_dbfs(self.minimum_peak_dbfs, "minimum_peak_dbfs")
        _require_dbfs(self.minimum_rms_dbfs, "minimum_rms_dbfs")
        _require_positive_u64_nanoseconds(
            self.exact_zero_timeout_ns, "exact_zero_timeout_ns"
        )


@dataclass(frozen=True, slots=True)
class SourceSignalEvaluation:
    state: SourceSignalState
    peak_dbfs: float | None
    rms_dbfs: float | None
    consecutive_exact_zero_duration_ns: int


@dataclass(frozen=True, slots=True)
class SourceSignalObservation:
    observed_at_ns: int
    samples_observed_total: int
    exact_zero_samples_observed_total: int
    nonzero_samples_observed_total: int
    nonfinite_samples_observed_total: int
    window_timestamp_start_ns: int | None
    window_duration_ns: int
    window_observed_at_ns: int | None
    window_sequence_number: int | None
    window_source_generation: int
    window_discontinuity_epoch: int
    window_samples_total: int
    window_exact_zero_samples_total: int
    window_nonzero_samples_total: int
    window_nonfinite_samples_total: int
    consecutive_exact_zero_duration_ns: int
    window_peak_linear: float | None
    window_rms_linear: float | None
    window_peak_dbfs: float | None
    window_rms_dbfs: float | None
    window_exact_zero_ratio: float | None

    @classmethod
    def _from_native(cls, value: _SourceSignalObservation) -> SourceSignalObservation:
        return cls(
            observed_at_ns=value.observed_at_ns,
            samples_observed_total=value.samples_observed_total,
            exact_zero_samples_observed_total=value.exact_zero_samples_observed_total,
            nonzero_samples_observed_total=value.nonzero_samples_observed_total,
            nonfinite_samples_observed_total=value.nonfinite_samples_observed_total,
            window_timestamp_start_ns=value.window_timestamp_start_ns,
            window_duration_ns=value.window_duration_ns,
            window_observed_at_ns=value.window_observed_at_ns,
            window_sequence_number=value.window_sequence_number,
            window_source_generation=value.window_source_generation,
            window_discontinuity_epoch=value.window_discontinuity_epoch,
            window_samples_total=value.window_samples_total,
            window_exact_zero_samples_total=value.window_exact_zero_samples_total,
            window_nonzero_samples_total=value.window_nonzero_samples_total,
            window_nonfinite_samples_total=value.window_nonfinite_samples_total,
            consecutive_exact_zero_duration_ns=value.consecutive_exact_zero_duration_ns,
            window_peak_linear=value.window_peak_linear,
            window_rms_linear=value.window_rms_linear,
            window_peak_dbfs=value.window_peak_dbfs,
            window_rms_dbfs=value.window_rms_dbfs,
            window_exact_zero_ratio=value.window_exact_zero_ratio,
        )

    def evaluate(self, policy: SourceSignalPolicy) -> SourceSignalEvaluation:
        return evaluate_source_signal(self, policy)


def evaluate_source_signal(
    observation: SourceSignalObservation,
    policy: SourceSignalPolicy,
) -> SourceSignalEvaluation:
    """Evaluate measured PCM without inferring speech, permission, or routing."""

    if observation.window_samples_total == 0:
        state = SourceSignalState.NO_SAMPLES_OBSERVED
    elif observation.window_nonfinite_samples_total > 0:
        state = SourceSignalState.NONFINITE_SAMPLES_OBSERVED
    elif (
        observation.window_exact_zero_samples_total == observation.window_samples_total
    ):
        state = (
            SourceSignalState.SUSTAINED_EXACT_DIGITAL_ZERO
            if observation.consecutive_exact_zero_duration_ns
            >= policy.exact_zero_timeout_ns
            else SourceSignalState.EXACT_DIGITAL_ZERO_PENDING
        )
    else:
        peak_dbfs = (
            observation.window_peak_dbfs
            if observation.window_peak_dbfs is not None
            else float("-inf")
        )
        rms_dbfs = (
            observation.window_rms_dbfs
            if observation.window_rms_dbfs is not None
            else float("-inf")
        )
        state = (
            SourceSignalState.MEETS_CALLER_THRESHOLDS
            if peak_dbfs >= policy.minimum_peak_dbfs
            and rms_dbfs >= policy.minimum_rms_dbfs
            else SourceSignalState.BELOW_CALLER_THRESHOLDS
        )
    return SourceSignalEvaluation(
        state,
        observation.window_peak_dbfs,
        observation.window_rms_dbfs,
        observation.consecutive_exact_zero_duration_ns,
    )
