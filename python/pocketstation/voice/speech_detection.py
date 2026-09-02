"""Speech-activity events and detector integration protocols."""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from ..identity import SourceId, StreamId
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
        if self.audio_timestamp_ns < 0 or self.detection_timestamp_ns < 0:
            raise ValueError("speech timestamps must not be negative")
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


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
