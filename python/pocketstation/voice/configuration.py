"""Finite configuration for one voice conversation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class VoiceLimits:
    """Finite retained state and work limits for voice composition."""

    history_messages: int = 32
    retained_events: int = 128
    transcript_states: int = 128
    transcript_characters: int = 32_768
    response_characters: int = 16_384
    response_chunks_per_turn: int = 1_024
    tool_observations_per_turn: int = 32
    generated_audio_frames_per_turn: int = 3_000
    provider_event_bytes: int = 262_144
    provider_event_queue: int = 128

    def __post_init__(self) -> None:
        for name, integer_value, maximum in (
            ("history_messages", self.history_messages, 4_096),
            ("retained_events", self.retained_events, 16_384),
            ("transcript_states", self.transcript_states, 16_384),
            ("transcript_characters", self.transcript_characters, 1_000_000),
            ("response_characters", self.response_characters, 1_000_000),
            ("response_chunks_per_turn", self.response_chunks_per_turn, 65_536),
            ("tool_observations_per_turn", self.tool_observations_per_turn, 4_096),
            (
                "generated_audio_frames_per_turn",
                self.generated_audio_frames_per_turn,
                1_000_000,
            ),
            ("provider_event_bytes", self.provider_event_bytes, 4_194_304),
            ("provider_event_queue", self.provider_event_queue, 16_384),
        ):
            _bounded_integer(name, integer_value, maximum=maximum)


@dataclass(frozen=True, slots=True)
class VoiceDeadlines:
    """Deadlines for provider, output, cancellation, and shutdown work."""

    provider_start_s: float = 10.0
    provider_close_s: float = 10.0
    response_s: float = 60.0
    synthesis_s: float = 60.0
    output_write_s: float = 1.0
    output_drain_s: float = 5.0
    cancellation_s: float = 2.0
    signal_wait_s: float = 0.1

    def __post_init__(self) -> None:
        for name, seconds, maximum in (
            ("provider_start_s", self.provider_start_s, 300.0),
            ("provider_close_s", self.provider_close_s, 300.0),
            ("response_s", self.response_s, 900.0),
            ("synthesis_s", self.synthesis_s, 900.0),
            ("output_write_s", self.output_write_s, 60.0),
            ("output_drain_s", self.output_drain_s, 60.0),
            ("cancellation_s", self.cancellation_s, 60.0),
            ("signal_wait_s", self.signal_wait_s, 1.0),
        ):
            _bounded_seconds(name, seconds, maximum=maximum)


InterruptionTrigger = Literal["speech-started", "transcript-update"]


@dataclass(frozen=True, slots=True)
class InterruptionConfig:
    """Policy for cancelling a response after new input is observed."""

    enabled: bool = True
    trigger: InterruptionTrigger = "speech-started"
    minimum_speech_ms: int = 120
    cancel_provider_work: bool = True
    cancel_pending_output: bool = True
    require_receiver_observation: bool = False

    def __post_init__(self) -> None:
        if self.trigger not in {"speech-started", "transcript-update"}:
            raise ValueError("trigger must be speech-started or transcript-update")
        if isinstance(self.minimum_speech_ms, bool) or not isinstance(
            self.minimum_speech_ms, int
        ):
            raise TypeError("minimum_speech_ms must be an integer")
        if not 0 <= self.minimum_speech_ms <= 10_000:
            raise ValueError("minimum_speech_ms must be between 0 and 10000")
        if self.enabled and not (
            self.cancel_provider_work or self.cancel_pending_output
        ):
            raise ValueError(
                "enabled interruption must cancel provider work, pending output, "
                "or both"
            )


@dataclass(frozen=True, slots=True)
class ConversationConfig:
    """Validated limits, deadlines, and interruption policy for one run.

    The flat fields preserve the existing 0.1 developer API. ``limits`` and
    ``deadlines`` expose the same values as grouped provider-neutral records.
    """

    history_capacity: int = 32
    event_capacity: int = 128
    transcript_state_capacity: int = 128
    maximum_transcript_characters: int = 32_768
    maximum_response_characters: int = 16_384
    maximum_response_chunks_per_turn: int = 1_024
    maximum_tool_events_per_turn: int = 32
    maximum_output_frames_per_turn: int = 3_000
    provider_event_bytes: int = 262_144
    provider_event_queue_capacity: int = 128
    provider_start_timeout_s: float = 10.0
    provider_close_timeout_s: float = 10.0
    response_timeout_s: float = 60.0
    synthesis_timeout_s: float = 60.0
    output_write_timeout_s: float = 1.0
    output_drain_timeout_s: float = 5.0
    cancellation_timeout_s: float = 2.0
    signal_wait_timeout_s: float = 0.1
    interruption: InterruptionConfig = InterruptionConfig()

    def __post_init__(self) -> None:
        for name, integer_value, maximum in (
            ("history_capacity", self.history_capacity, 4_096),
            ("event_capacity", self.event_capacity, 16_384),
            ("transcript_state_capacity", self.transcript_state_capacity, 16_384),
            (
                "maximum_transcript_characters",
                self.maximum_transcript_characters,
                1_000_000,
            ),
            (
                "maximum_response_characters",
                self.maximum_response_characters,
                1_000_000,
            ),
            (
                "maximum_response_chunks_per_turn",
                self.maximum_response_chunks_per_turn,
                65_536,
            ),
            (
                "maximum_tool_events_per_turn",
                self.maximum_tool_events_per_turn,
                4_096,
            ),
            (
                "maximum_output_frames_per_turn",
                self.maximum_output_frames_per_turn,
                1_000_000,
            ),
            ("provider_event_bytes", self.provider_event_bytes, 4_194_304),
            (
                "provider_event_queue_capacity",
                self.provider_event_queue_capacity,
                16_384,
            ),
        ):
            _bounded_integer(name, integer_value, maximum=maximum)
        for name, seconds, maximum_seconds in (
            ("provider_start_timeout_s", self.provider_start_timeout_s, 300.0),
            ("provider_close_timeout_s", self.provider_close_timeout_s, 300.0),
            ("response_timeout_s", self.response_timeout_s, 900.0),
            ("synthesis_timeout_s", self.synthesis_timeout_s, 900.0),
            ("output_write_timeout_s", self.output_write_timeout_s, 60.0),
            ("output_drain_timeout_s", self.output_drain_timeout_s, 60.0),
            ("cancellation_timeout_s", self.cancellation_timeout_s, 60.0),
            ("signal_wait_timeout_s", self.signal_wait_timeout_s, 1.0),
        ):
            _bounded_seconds(name, seconds, maximum=maximum_seconds)
        _ = (self.limits, self.deadlines)

    @property
    def limits(self) -> VoiceLimits:
        return VoiceLimits(
            history_messages=self.history_capacity,
            retained_events=self.event_capacity,
            transcript_states=self.transcript_state_capacity,
            transcript_characters=self.maximum_transcript_characters,
            response_characters=self.maximum_response_characters,
            response_chunks_per_turn=self.maximum_response_chunks_per_turn,
            tool_observations_per_turn=self.maximum_tool_events_per_turn,
            generated_audio_frames_per_turn=self.maximum_output_frames_per_turn,
            provider_event_bytes=self.provider_event_bytes,
            provider_event_queue=self.provider_event_queue_capacity,
        )

    @property
    def deadlines(self) -> VoiceDeadlines:
        return VoiceDeadlines(
            provider_start_s=self.provider_start_timeout_s,
            provider_close_s=self.provider_close_timeout_s,
            response_s=self.response_timeout_s,
            synthesis_s=self.synthesis_timeout_s,
            output_write_s=self.output_write_timeout_s,
            output_drain_s=self.output_drain_timeout_s,
            cancellation_s=self.cancellation_timeout_s,
            signal_wait_s=self.signal_wait_timeout_s,
        )

    @classmethod
    def from_parts(
        cls,
        *,
        limits: VoiceLimits | None = None,
        deadlines: VoiceDeadlines | None = None,
        interruption: InterruptionConfig | None = None,
    ) -> ConversationConfig:
        selected_limits = VoiceLimits() if limits is None else limits
        selected_deadlines = VoiceDeadlines() if deadlines is None else deadlines
        return cls(
            history_capacity=selected_limits.history_messages,
            event_capacity=selected_limits.retained_events,
            transcript_state_capacity=selected_limits.transcript_states,
            maximum_transcript_characters=selected_limits.transcript_characters,
            maximum_response_characters=selected_limits.response_characters,
            maximum_response_chunks_per_turn=selected_limits.response_chunks_per_turn,
            maximum_tool_events_per_turn=selected_limits.tool_observations_per_turn,
            maximum_output_frames_per_turn=(
                selected_limits.generated_audio_frames_per_turn
            ),
            provider_event_bytes=selected_limits.provider_event_bytes,
            provider_event_queue_capacity=selected_limits.provider_event_queue,
            provider_start_timeout_s=selected_deadlines.provider_start_s,
            provider_close_timeout_s=selected_deadlines.provider_close_s,
            response_timeout_s=selected_deadlines.response_s,
            synthesis_timeout_s=selected_deadlines.synthesis_s,
            output_write_timeout_s=selected_deadlines.output_write_s,
            output_drain_timeout_s=selected_deadlines.output_drain_s,
            cancellation_timeout_s=selected_deadlines.cancellation_s,
            signal_wait_timeout_s=selected_deadlines.signal_wait_s,
            interruption=InterruptionConfig() if interruption is None else interruption,
        )


def _bounded_integer(name: str, value: int, *, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not 1 <= value <= maximum:
        raise ValueError(f"{name} must be between 1 and {maximum}")


def _bounded_seconds(name: str, value: float, *, maximum: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    if not 0 < value <= maximum:
        raise ValueError(f"{name} must be greater than 0 and at most {maximum}")


__all__ = [
    "ConversationConfig",
    "InterruptionConfig",
    "InterruptionTrigger",
    "VoiceDeadlines",
    "VoiceLimits",
]
