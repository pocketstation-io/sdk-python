"""Committed conversation turns and finite retained context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..identity import SourceId, StreamId
from ._validation import (
    MAX_SAFE_INTEGER,
    require_boolean,
    require_integer,
    require_nonempty,
    require_nonnegative_integer,
    require_optional_nonnegative_integer,
    require_optional_positive_integer,
    require_positive_integer,
)

ConversationRole = Literal["user", "assistant", "tool"]
ConversationDisposition = Literal["completed", "stopped", "cancelled", "failed"]


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    """A final transcript with its source identity and Session timing."""

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

    def __post_init__(self) -> None:
        require_positive_integer("id", self.id)
        require_nonempty("utterance_id", self.utterance_id)
        require_optional_positive_integer("source_id", self.source_id)
        require_optional_positive_integer("stream_id", self.stream_id)
        require_optional_nonnegative_integer("source_sequence", self.source_sequence)
        require_optional_nonnegative_integer(
            "source_timestamp_ns", self.source_timestamp_ns
        )
        require_optional_nonnegative_integer("audio_start_ns", self.audio_start_ns)
        require_optional_nonnegative_integer("audio_end_ns", self.audio_end_ns)
        require_nonnegative_integer("received_timestamp_ns", self.received_timestamp_ns)
        if (
            self.audio_start_ns is not None
            and self.audio_end_ns is not None
            and self.audio_end_ns < self.audio_start_ns
        ):
            raise ValueError("audio_end_ns must not precede audio_start_ns")


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """One message retained in finite conversation history."""

    role: ConversationRole
    content: str
    turn_id: int
    timestamp_ns: int

    def __post_init__(self) -> None:
        if self.role not in {"user", "assistant", "tool"}:
            raise ValueError("role must be user, assistant, or tool")
        require_positive_integer("turn_id", self.turn_id)
        require_nonnegative_integer("timestamp_ns", self.timestamp_ns)


@dataclass(frozen=True, slots=True)
class ConversationContext:
    """Immutable history and commit state presented to a response model."""

    history: tuple[ConversationMessage, ...]
    committed: bool

    def __post_init__(self) -> None:
        require_boolean("committed", self.committed)
        object.__setattr__(self, "history", tuple(self.history))


@dataclass(frozen=True, slots=True)
class ConversationOutcome:
    """Terminal facts from one bounded conversation run."""

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
    events: tuple[object, ...]
    failure: str | None = None
    provider_tasks_cancelled: int = 0
    connector_queues_cleared: int = 0
    receiver_observations_received: int = 0
    acoustic_hearing_known: bool = False

    def __post_init__(self) -> None:
        if self.disposition not in {"completed", "stopped", "cancelled", "failed"}:
            raise ValueError(
                "disposition must be completed, stopped, cancelled, or failed"
            )
        for name, value in (
            ("turns_started", self.turns_started),
            ("turns_completed", self.turns_completed),
            ("turns_interrupted", self.turns_interrupted),
            ("transcript_updates_received", self.transcript_updates_received),
            ("speculative_responses_started", self.speculative_responses_started),
            ("speculative_responses_reused", self.speculative_responses_reused),
            ("output_generations_cancelled", self.output_generations_cancelled),
            ("output_frames_written", self.output_frames_written),
            ("provider_tasks_cancelled", self.provider_tasks_cancelled),
            ("connector_queues_cleared", self.connector_queues_cleared),
            ("receiver_observations_received", self.receiver_observations_received),
        ):
            require_integer(name, value, minimum=0, maximum=MAX_SAFE_INTEGER)
        require_boolean("acoustic_hearing_known", self.acoustic_hearing_known)
        object.__setattr__(self, "history", tuple(self.history))
        object.__setattr__(self, "events", tuple(self.events))

    @property
    def success(self) -> bool:
        return self.disposition in {"completed", "stopped"} and self.failure is None


__all__ = [
    "ConversationContext",
    "ConversationDisposition",
    "ConversationMessage",
    "ConversationOutcome",
    "ConversationRole",
    "ConversationTurn",
]
