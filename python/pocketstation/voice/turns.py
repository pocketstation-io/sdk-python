"""Committed conversation turns and finite retained context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..identity import SourceId, StreamId

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


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """One message retained in finite conversation history."""

    role: ConversationRole
    content: str
    turn_id: int
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class ConversationContext:
    """Immutable history and commit state presented to a response model."""

    history: tuple[ConversationMessage, ...]
    committed: bool


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
