"""Typed transcript values emitted by demo transcription adapters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pocketstation.graph import SignalSpec, TextFormat

TRANSCRIPT_SIGNAL = SignalSpec.text(
    TextFormat.JSON,
    role="transcript.final",
    schema="io.pocketstation.transcript.batch.v1",
)


@dataclass(frozen=True, slots=True)
class Transcript:
    """One source-aware faster-whisper result."""

    source_id: int
    text: str
    language: str
    timestamp_start_ns: int
    timestamp_end_ns: int
    discontinuity_reasons: tuple[str, ...]

    @classmethod
    def from_json(cls, payload: str) -> Transcript:
        value: Any = json.loads(payload)
        return cls(
            source_id=int(value["source_id"]),
            text=str(value["text"]),
            language=str(value["language"]),
            timestamp_start_ns=int(value["timestamp_start_ns"]),
            timestamp_end_ns=int(value["timestamp_end_ns"]),
            discontinuity_reasons=tuple(value["discontinuity_reasons"]),
        )


__all__ = ["TRANSCRIPT_SIGNAL", "Transcript"]
