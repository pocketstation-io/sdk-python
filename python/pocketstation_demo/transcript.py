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
    processing_outcome: str | None = None
    duration_ms: int | None = None
    inference_duration_ns: int | None = None

    @classmethod
    def from_json(cls, payload: str) -> Transcript:
        value: Any = json.loads(payload)
        if not isinstance(value, dict):
            raise TypeError("transcript payload must be a JSON object")
        return cls(
            processing_outcome=None
            if "processing_outcome" not in value
            else _string(value, "processing_outcome"),
            duration_ms=None
            if "duration_ms" not in value
            else _integer(value, "duration_ms"),
            inference_duration_ns=None
            if "inference_duration_ns" not in value
            else _integer(value, "inference_duration_ns"),
            source_id=_integer(value, "source_id"),
            text=_string(value, "text"),
            language=_string(value, "language"),
            timestamp_start_ns=_integer(value, "timestamp_start_ns"),
            timestamp_end_ns=_integer(value, "timestamp_end_ns"),
            discontinuity_reasons=_strings(value, "discontinuity_reasons"),
        )


def _integer(value: dict[str, Any], name: str) -> int:
    field = value.get(name)
    if isinstance(field, bool):
        raise TypeError(f"{name} must be an integer")
    if isinstance(field, int) and abs(field) <= 9_007_199_254_740_991:
        return field
    if (
        isinstance(field, str)
        and field
        and (field.isdigit() or (field.startswith("-") and field[1:].isdigit()))
    ):
        return int(field)
    raise TypeError(f"{name} must be an integer")


def _string(value: dict[str, Any], name: str) -> str:
    field = value.get(name)
    if not isinstance(field, str):
        raise TypeError(f"{name} must be a string")
    return field


def _strings(value: dict[str, Any], name: str) -> tuple[str, ...]:
    field = value.get(name)
    if not isinstance(field, list) or not all(isinstance(item, str) for item in field):
        raise TypeError(f"{name} must be an array of strings")
    return tuple(field)


__all__ = ["TRANSCRIPT_SIGNAL", "Transcript"]
