"""Bounded provider-neutral contracts for interruptible voice composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .identity import SourceId, StreamId


@dataclass(frozen=True, slots=True)
class ConversationConfig:
    """Finite work, retention, deadline, and output limits for one conversation."""

    history_capacity: int = 32
    event_capacity: int = 128
    transcript_state_capacity: int = 128
    maximum_transcript_characters: int = 32_768
    maximum_response_characters: int = 16_384
    maximum_response_chunks_per_turn: int = 1_024
    maximum_tool_events_per_turn: int = 32
    maximum_output_frames_per_turn: int = 3_000
    provider_start_timeout_s: float = 10.0
    provider_close_timeout_s: float = 10.0
    response_timeout_s: float = 60.0
    synthesis_timeout_s: float = 60.0
    output_write_timeout_s: float = 1.0
    output_drain_timeout_s: float = 5.0
    cancellation_timeout_s: float = 2.0
    signal_wait_timeout_s: float = 0.1

    def __post_init__(self) -> None:
        _bounded_integer("history_capacity", self.history_capacity, maximum=4_096)
        _bounded_integer("event_capacity", self.event_capacity, maximum=16_384)
        _bounded_integer(
            "transcript_state_capacity",
            self.transcript_state_capacity,
            maximum=16_384,
        )
        _bounded_integer(
            "maximum_transcript_characters",
            self.maximum_transcript_characters,
            maximum=1_000_000,
        )
        _bounded_integer(
            "maximum_response_characters",
            self.maximum_response_characters,
            maximum=1_000_000,
        )
        _bounded_integer(
            "maximum_response_chunks_per_turn",
            self.maximum_response_chunks_per_turn,
            maximum=65_536,
        )
        _bounded_integer(
            "maximum_tool_events_per_turn",
            self.maximum_tool_events_per_turn,
            maximum=4_096,
        )
        _bounded_integer(
            "maximum_output_frames_per_turn",
            self.maximum_output_frames_per_turn,
            maximum=1_000_000,
        )
        _bounded_seconds(
            "provider_start_timeout_s", self.provider_start_timeout_s, maximum=300
        )
        _bounded_seconds(
            "provider_close_timeout_s", self.provider_close_timeout_s, maximum=300
        )
        _bounded_seconds("response_timeout_s", self.response_timeout_s, maximum=900)
        _bounded_seconds("synthesis_timeout_s", self.synthesis_timeout_s, maximum=900)
        _bounded_seconds(
            "output_write_timeout_s", self.output_write_timeout_s, maximum=60
        )
        _bounded_seconds(
            "output_drain_timeout_s", self.output_drain_timeout_s, maximum=60
        )
        _bounded_seconds(
            "cancellation_timeout_s", self.cancellation_timeout_s, maximum=60
        )
        _bounded_seconds("signal_wait_timeout_s", self.signal_wait_timeout_s, maximum=1)


@dataclass(frozen=True, slots=True)
class TranscriptUpdate:
    """One bounded revision of speech recognized from a Session stem."""

    utterance_id: str
    revision: int
    text: str
    stable_prefix: str = ""
    final: bool = False
    interrupts: bool = True
    source_id: SourceId | None = None
    stream_id: StreamId | None = None
    source_sequence: int | None = None
    source_timestamp_ns: int | None = None
    audio_start_ns: int | None = None
    audio_end_ns: int | None = None

    def __post_init__(self) -> None:
        if not self.utterance_id.strip():
            raise ValueError("utterance_id must not be empty")
        if len(self.utterance_id) > 128:
            raise ValueError("utterance_id must not exceed 128 characters")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise TypeError("revision must be an integer")
        if self.revision < 1:
            raise ValueError("revision must be greater than zero")
        if not self.text.startswith(self.stable_prefix):
            raise ValueError("stable_prefix must be a prefix of text")
        if self.final and not self.text.strip():
            raise ValueError("a final transcript update must contain text")
        if self.final and self.stable_prefix != self.text:
            raise ValueError("a final transcript update must make all text stable")
        _optional_identity("source_id", self.source_id)
        _optional_identity("stream_id", self.stream_id)
        _optional_sequence("source_sequence", self.source_sequence)
        _optional_timestamp("source_timestamp_ns", self.source_timestamp_ns)
        _optional_timestamp("audio_start_ns", self.audio_start_ns)
        _optional_timestamp("audio_end_ns", self.audio_end_ns)
        if (
            self.audio_start_ns is not None
            and self.audio_end_ns is not None
            and self.audio_end_ns < self.audio_start_ns
        ):
            raise ValueError("audio_end_ns must not precede audio_start_ns")


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    """One final transcript retained with its Session timing and source identity."""

    id: int
    utterance_id: str
    text: str
    source_id: SourceId | None
    stream_id: StreamId | None
    source_sequence: int | None
    source_timestamp_ns: int | None
    audio_start_ns: int | None
    audio_end_ns: int | None
    received_timestamp_ns: int


ConversationRole = Literal["user", "assistant", "tool"]
ConversationDisposition = Literal["completed", "stopped", "cancelled", "failed"]


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """One retained bounded-history message."""

    role: ConversationRole
    content: str
    turn_id: int
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class ToolEvent:
    """One explicit tool observation returned by a response provider."""

    name: str
    outcome: str
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("tool event name must not be empty")
        if not self.outcome.strip():
            raise ValueError("tool event outcome must not be empty")


@dataclass(frozen=True, slots=True)
class ConversationResponse:
    """Text and bounded tool observations produced for one user turn."""

    text: str
    tool_events: tuple[ToolEvent, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("conversation response text must not be empty")


@dataclass(frozen=True, slots=True)
class ConversationResponseChunk:
    """One ordered response fragment supplied to streaming synthesis."""

    text: str = ""
    tool_events: tuple[ToolEvent, ...] = ()

    def __post_init__(self) -> None:
        if not self.text and not self.tool_events:
            raise ValueError("a response chunk must contain text or a tool event")


@dataclass(frozen=True, slots=True)
class ConversationContext:
    """Immutable history and commit state presented to a response provider."""

    history: tuple[ConversationMessage, ...]
    committed: bool


@dataclass(frozen=True, slots=True)
class ConversationEvent:
    """One retained lifecycle, latency, interruption, tool, or failure event."""

    kind: str
    timestamp_ns: int
    turn_id: int | None = None
    utterance_id: str | None = None
    transcript_revision: int | None = None
    output_generation_id: int | None = None
    duration_ns: int | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ConversationOutcome:
    """Terminal facts for one bounded conversation run."""

    disposition: ConversationDisposition
    turns_started: int
    turns_completed: int
    turns_interrupted: int
    transcript_updates_received: int
    speculative_responses_started: int
    speculative_responses_reused: int
    output_generations_cancelled: int
    output_frames_written: int
    history: tuple[ConversationMessage, ...]
    events: tuple[ConversationEvent, ...]
    failure: str | None = None

    @property
    def success(self) -> bool:
        return self.disposition in {"completed", "stopped"} and self.failure is None


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


def _optional_timestamp(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer or None")
    if value < 0:
        raise ValueError(f"{name} must not be negative")


def _optional_identity(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer or None")
    if value < 1:
        raise ValueError(f"{name} must be greater than zero")


def _optional_sequence(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer or None")
    if value < 0:
        raise ValueError(f"{name} must not be negative")


__all__ = [
    "ConversationConfig",
    "ConversationContext",
    "ConversationDisposition",
    "ConversationEvent",
    "ConversationMessage",
    "ConversationOutcome",
    "ConversationResponse",
    "ConversationResponseChunk",
    "ConversationRole",
    "ConversationTurn",
    "ToolEvent",
    "TranscriptUpdate",
]
