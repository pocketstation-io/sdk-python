"""Measured events retained by one voice conversation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceEvent:
    """One measured voice lifecycle or media-boundary event."""

    kind: str
    timestamp_ns: int
    stage: str | None = None
    provider_id: str | None = None
    turn_id: int | None = None
    utterance_id: str | None = None
    transcript_revision: int | None = None
    response_id: str | None = None
    output_generation_id: int | None = None
    duration_ns: int | None = None
    available: bool = True
    detail: str | None = None

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("voice event kind must not be empty")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must not be negative")
        if self.duration_ns is not None and self.duration_ns < 0:
            raise ValueError("duration_ns must not be negative")


ConversationEvent = VoiceEvent


__all__ = [
    "ConversationEvent",
    "VoiceEvent",
]
