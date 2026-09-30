"""Select an existing playback reference for native Session echo cancellation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from ._native import _EchoCancellationObservations as _NativeObservations
from ._native import _EchoCancelledAudio as _NativeEchoCancelledAudio
from ._native import _PlaybackReference as _NativePlaybackReference
from .errors import _native_call
from .graph import DerivedStream, SourceOutput, Stem, _DestinationResolver
from .identity import SourceId

EchoAudioInput: TypeAlias = Stem | SourceOutput | DerivedStream


class EchoCancellationState(StrEnum):
    """Native lifecycle state; PROCESSING does not assert acoustic convergence."""

    WAITING_FOR_REFERENCE = "waiting-for-reference"
    PROCESSING = "processing"
    RESET = "reset"
    INTERRUPTED = "interrupted"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass(frozen=True, slots=True)
class EchoCancellationObservations:
    """An immutable snapshot that remains available after Session stop."""

    state: EchoCancellationState
    processed_microphone_frames_total: int
    output_frames_total: int
    tail_frames_total: int
    tail_padding_samples_total: int
    discarded_tail_generations_total: int
    nominal_delay_samples: int
    drain_duration_ms: int
    discarded_microphone_frames_total: int
    discarded_reference_frames_total: int
    resets_total: int
    processing_generation: int
    microphone_queue_depth_frames: int
    reference_queue_depth_frames: int
    queue_capacity_frames: int
    latest_processing_duration_ns: int
    maximum_processing_duration_ns: int
    latest_reference_age_ns: int
    latest_reference_lead_ns: int
    maximum_cadence_error_ns: int
    analyzed_reference_frames_total: int
    interrupted_requests_total: int
    reference_source_id: SourceId | None
    microphone_source_id: SourceId | None
    qualified_algorithmic_delay_samples: int | None
    last_error: str | None

    @classmethod
    def _from_native(cls, value: _NativeObservations) -> EchoCancellationObservations:
        return cls(
            state=EchoCancellationState(value.state),
            processed_microphone_frames_total=value.processed_microphone_frames_total,
            output_frames_total=value.output_frames_total,
            tail_frames_total=value.tail_frames_total,
            tail_padding_samples_total=value.tail_padding_samples_total,
            discarded_tail_generations_total=value.discarded_tail_generations_total,
            nominal_delay_samples=value.nominal_delay_samples,
            drain_duration_ms=value.drain_duration_ms,
            discarded_microphone_frames_total=value.discarded_microphone_frames_total,
            discarded_reference_frames_total=value.discarded_reference_frames_total,
            resets_total=value.resets_total,
            processing_generation=value.processing_generation,
            microphone_queue_depth_frames=value.microphone_queue_depth_frames,
            reference_queue_depth_frames=value.reference_queue_depth_frames,
            queue_capacity_frames=value.queue_capacity_frames,
            latest_processing_duration_ns=value.latest_processing_duration_ns,
            maximum_processing_duration_ns=value.maximum_processing_duration_ns,
            latest_reference_age_ns=value.latest_reference_age_ns,
            latest_reference_lead_ns=value.latest_reference_lead_ns,
            maximum_cadence_error_ns=value.maximum_cadence_error_ns,
            analyzed_reference_frames_total=value.analyzed_reference_frames_total,
            interrupted_requests_total=value.interrupted_requests_total,
            reference_source_id=(
                None
                if value.reference_source_id is None
                else SourceId(value.reference_source_id)
            ),
            microphone_source_id=(
                None
                if value.microphone_source_id is None
                else SourceId(value.microphone_source_id)
            ),
            qualified_algorithmic_delay_samples=value.qualified_algorithmic_delay_samples,
            last_error=value.last_error,
        )


def _require_audio(input: EchoAudioInput) -> EchoAudioInput:
    if not isinstance(input, (Stem, SourceOutput, DerivedStream)):
        raise TypeError("echo input must be a Stem, SourceOutput or DerivedStream")
    return input


class PlaybackReference:
    """Explicitly select already-declared audio without opening another device."""

    __slots__ = ("_input", "_native")

    def __init__(self, native: _NativePlaybackReference, input: EchoAudioInput) -> None:
        self._native = native
        self._input = input

    @property
    def input(self) -> EchoAudioInput:
        return self._input

    @classmethod
    def selected_application(cls, input: EchoAudioInput) -> PlaybackReference:
        """Use only the selected application's already-declared audio."""
        value = _require_audio(input)
        return cls(
            _native_call(
                lambda: _NativePlaybackReference.selected_application(value._native)
            ),
            value,
        )

    @classmethod
    def output_mix(cls, input: EchoAudioInput) -> PlaybackReference:
        """Use a complete output mix that the caller separately authorized."""
        value = _require_audio(input)
        return cls(
            _native_call(lambda: _NativePlaybackReference.output_mix(value._native)),
            value,
        )

    @classmethod
    def rendered_audio(cls, input: EchoAudioInput) -> PlaybackReference:
        """Use caller-owned audio that is also sent to a playback device."""
        value = _require_audio(input)
        return cls(
            _native_call(
                lambda: _NativePlaybackReference.rendered_audio(value._native)
            ),
            value,
        )


class EchoCancelledAudio:
    """Processed microphone audio, selected inputs, and native observations."""

    __slots__ = ("_audio", "_microphone", "_native", "_reference")

    def __init__(
        self,
        native: _NativeEchoCancelledAudio,
        microphone: EchoAudioInput,
        reference: PlaybackReference,
        destination: _DestinationResolver,
    ) -> None:
        self._native = native
        self._microphone = microphone
        self._reference = reference
        self._audio = Stem(native.audio, destination)

    @property
    def audio(self) -> Stem:
        """Use the normal Stem methods to record, publish, or send this audio."""
        return self._audio

    @property
    def microphone(self) -> EchoAudioInput:
        return self._microphone

    @property
    def reference(self) -> PlaybackReference:
        return self._reference

    @property
    def reference_coverage(self) -> str:
        return self._native.reference_coverage

    def observations(self) -> EchoCancellationObservations:
        return EchoCancellationObservations._from_native(
            _native_call(self._native.observations)
        )


__all__ = [
    "EchoAudioInput",
    "EchoCancellationObservations",
    "EchoCancellationState",
    "EchoCancelledAudio",
    "PlaybackReference",
]
