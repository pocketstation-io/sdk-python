"""Capability declarations used to validate voice components before capture."""

from __future__ import annotations

from dataclasses import dataclass

from .configuration import InterruptionTrigger


@dataclass(frozen=True, slots=True)
class TranscriptionCapabilities:
    """Speech-recognition behavior supported by one transcriber."""

    streaming: bool
    transcript_revisions: bool = False
    stable_prefix: bool = False
    provider_timestamps: bool = False
    supported_sample_rates_hz: tuple[int, ...] = ()
    input_formats: tuple[str, ...] = ()
    maximum_session_duration_s: float | None = None

    def __post_init__(self) -> None:
        _sample_rates(self.supported_sample_rates_hz)
        _duration(self.maximum_session_duration_s)


@dataclass(frozen=True, slots=True)
class ResponseCapabilities:
    """Incremental response behavior supported by one response model."""

    streaming: bool
    speculative_requests: bool = False
    cancellation: bool = False
    tools: bool = False
    usage_reporting: bool = False
    provider_history_truncation: bool = False
    maximum_context_characters: int | None = None

    def __post_init__(self) -> None:
        _optional_positive(
            "maximum_context_characters", self.maximum_context_characters
        )


@dataclass(frozen=True, slots=True)
class SynthesisCapabilities:
    """Generated-audio behavior supported by one speech synthesizer."""

    streaming: bool
    cancellation: bool = False
    output_formats: tuple[str, ...] = ()
    supported_sample_rates_hz: tuple[int, ...] = ()
    usage_reporting: bool = False

    def __post_init__(self) -> None:
        _sample_rates(self.supported_sample_rates_hz)


@dataclass(frozen=True, slots=True)
class SpeechDetectionCapabilities:
    """Speech-activity information supported by one detector."""

    streaming: bool = True
    provisional_events: bool = False
    confidence: bool = False
    provider_timestamps: bool = False
    supported_sample_rates_hz: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _sample_rates(self.supported_sample_rates_hz)


@dataclass(frozen=True, slots=True)
class DuplexVoiceCapabilities:
    """Voice behavior supplied through one stateful audio connection."""

    transcript_revisions: bool = False
    stable_prefix: bool = False
    provider_speech_detection: bool = False
    interruption: bool = False
    interruption_triggers: tuple[InterruptionTrigger, ...] = ()
    response_cancellation: bool = False
    provider_history_truncation: bool = False
    receiver_playout_clear: bool = False
    playout_acknowledgement: bool = False
    tools: bool = False
    usage_reporting: bool = False
    input_formats: tuple[str, ...] = ()
    output_formats: tuple[str, ...] = ()
    supported_sample_rates_hz: tuple[int, ...] = ()
    maximum_session_duration_s: float | None = None

    def __post_init__(self) -> None:
        _sample_rates(self.supported_sample_rates_hz)
        _duration(self.maximum_session_duration_s)
        if len(set(self.interruption_triggers)) != len(self.interruption_triggers):
            raise ValueError("interruption_triggers must not contain duplicates")
        if any(
            trigger not in {"speech-started", "transcript-update"}
            for trigger in self.interruption_triggers
        ):
            raise ValueError("interruption_triggers contains an unsupported value")
        if self.interruption and not self.interruption_triggers:
            raise ValueError(
                "interruption_triggers is required when interruption is supported"
            )
        if not self.interruption and self.interruption_triggers:
            raise ValueError(
                "interruption_triggers requires interruption to be supported"
            )


@dataclass(frozen=True, slots=True)
class VoiceCapabilities:
    """Capabilities of one validated voice composition."""

    transcription: TranscriptionCapabilities | None = None
    response: ResponseCapabilities | None = None
    synthesis: SynthesisCapabilities | None = None
    speech_detection: SpeechDetectionCapabilities | None = None
    duplex: DuplexVoiceCapabilities | None = None

    def __post_init__(self) -> None:
        separate = (self.transcription, self.response, self.synthesis)
        if self.duplex is not None and any(value is not None for value in separate):
            raise ValueError(
                "duplex capabilities cannot be combined with separate "
                "transcription, response, or synthesis capabilities"
            )


def _sample_rates(values: tuple[int, ...]) -> None:
    if any(isinstance(value, bool) or value <= 0 for value in values):
        raise ValueError("supported sample rates must be positive integers")
    if len(set(values)) != len(values):
        raise ValueError("supported sample rates must not contain duplicates")


def _duration(value: float | None) -> None:
    if value is not None and (isinstance(value, bool) or not 0 < value <= 86_400):
        raise ValueError("maximum_session_duration_s must be between 0 and 86400")


def _optional_positive(name: str, value: int | None) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
    ):
        raise ValueError(f"{name} must be a positive integer or None")


__all__ = [
    "DuplexVoiceCapabilities",
    "ResponseCapabilities",
    "SpeechDetectionCapabilities",
    "SynthesisCapabilities",
    "TranscriptionCapabilities",
    "VoiceCapabilities",
]
