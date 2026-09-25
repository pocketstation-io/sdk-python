"""Measured events retained by one voice conversation."""

from __future__ import annotations

from dataclasses import dataclass

from ._validation import (
    MAX_SAFE_INTEGER,
    require_boolean,
    require_integer,
    require_nonempty,
    require_nonnegative_integer,
    require_optional_nonempty,
    require_optional_nonnegative_integer,
    require_optional_positive_integer,
)


@dataclass(frozen=True, slots=True)
class VoiceEvent:
    """One measured voice lifecycle or media-timing event."""

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
        require_nonempty("voice event kind", self.kind)
        require_nonnegative_integer("timestamp_ns", self.timestamp_ns)
        require_optional_nonnegative_integer("duration_ns", self.duration_ns)
        require_optional_positive_integer("turn_id", self.turn_id)
        require_optional_positive_integer(
            "output_generation_id", self.output_generation_id
        )
        if self.transcript_revision is not None:
            require_integer(
                "transcript_revision",
                self.transcript_revision,
                minimum=1,
                maximum=MAX_SAFE_INTEGER,
            )
        require_optional_nonempty("stage", self.stage)
        require_optional_nonempty("provider_id", self.provider_id)
        require_optional_nonempty("utterance_id", self.utterance_id)
        require_optional_nonempty("response_id", self.response_id)
        require_boolean("available", self.available)


ConversationEvent = VoiceEvent


__all__ = [
    "ConversationEvent",
    "VoiceEvent",
]
