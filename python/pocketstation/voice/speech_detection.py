"""Speech-activity events and detector integration protocols."""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from ..identity import SourceId, StreamId
from ._validation import (
    require_boolean,
    require_inclusive_number,
    require_nonempty,
    require_nonnegative_integer,
    require_positive_integer,
)
from .capabilities import SpeechDetectionCapabilities

SpeechActivityKind = Literal[
    "speech.started",
    "speech.updated",
    "speech.stopped",
    "speech.cancelled",
]


@dataclass(frozen=True, slots=True)
class SpeechActivity:
    """One speech-activity update observed from a source-aware audio stream."""

    kind: SpeechActivityKind
    source_id: SourceId
    stream_id: StreamId
    audio_timestamp_ns: int
    detection_timestamp_ns: int
    provider_id: str
    final: bool
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.kind not in {
            "speech.started",
            "speech.updated",
            "speech.stopped",
            "speech.cancelled",
        }:
            raise ValueError("kind must be a supported speech activity value")
        require_positive_integer("source_id", self.source_id)
        require_positive_integer("stream_id", self.stream_id)
        require_nonnegative_integer("audio_timestamp_ns", self.audio_timestamp_ns)
        require_nonnegative_integer(
            "detection_timestamp_ns", self.detection_timestamp_ns
        )
        require_nonempty("provider_id", self.provider_id)
        require_boolean("final", self.final)
        if self.confidence is not None:
            require_inclusive_number(
                "confidence", self.confidence, minimum=0, maximum=1
            )


@runtime_checkable
class SpeechDetector(Protocol):
    """Observe speech activity without deciding conversation policy."""

    @property
    def capabilities(self) -> SpeechDetectionCapabilities: ...

    def detect(
        self, *, session: object, input: object
    ) -> AsyncIterable[SpeechActivity]: ...

    async def start(self) -> None: ...

    async def aclose(self) -> None: ...


__all__ = [
    "SpeechActivity",
    "SpeechActivityKind",
    "SpeechDetectionCapabilities",
    "SpeechDetector",
]
