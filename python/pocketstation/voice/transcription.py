"""Streaming transcript revisions and transcriber integration protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..identity import SourceId, StreamId
from ..signal import BusSubscription, SignalEnvelope
from ._validation import (
    MAX_SAFE_INTEGER,
    require_boolean,
    require_integer,
    require_nonempty,
    require_optional_nonnegative_integer,
    require_optional_positive_integer,
)
from .capabilities import TranscriptionCapabilities


@dataclass(frozen=True, slots=True)
class TranscriptUpdate:
    """One revision of speech recognized from a source-aware audio stream."""

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
    provider_timestamp_ns: int | None = None
    session_timestamp_ns: int | None = None

    def __post_init__(self) -> None:
        require_nonempty("utterance_id", self.utterance_id)
        if len(self.utterance_id) > 128:
            raise ValueError("utterance_id must not exceed 128 characters")
        require_integer("revision", self.revision, minimum=1, maximum=MAX_SAFE_INTEGER)
        require_boolean("final", self.final)
        require_boolean("interrupts", self.interrupts)
        if not self.text.startswith(self.stable_prefix):
            raise ValueError("stable_prefix must be a prefix of text")
        if self.final and not self.text.strip():
            raise ValueError("a final transcript update must contain text")
        if self.final and self.stable_prefix != self.text:
            raise ValueError("a final transcript update must make all text stable")
        require_optional_positive_integer("source_id", self.source_id)
        require_optional_positive_integer("stream_id", self.stream_id)
        require_optional_nonnegative_integer("source_sequence", self.source_sequence)
        for name, value in (
            ("source_timestamp_ns", self.source_timestamp_ns),
            ("audio_start_ns", self.audio_start_ns),
            ("audio_end_ns", self.audio_end_ns),
            ("provider_timestamp_ns", self.provider_timestamp_ns),
            ("session_timestamp_ns", self.session_timestamp_ns),
        ):
            require_optional_nonnegative_integer(name, value)
        if (
            self.audio_start_ns is not None
            and self.audio_end_ns is not None
            and self.audio_end_ns < self.audio_start_ns
        ):
            raise ValueError("audio_end_ns must not precede audio_start_ns")


@runtime_checkable
class TranscriptionConnection(Protocol):
    """A declared transcript signal and its provider-specific decoder."""

    @property
    def subscription(self) -> BusSubscription[str]: ...

    def decode(self, envelope: SignalEnvelope[str]) -> TranscriptUpdate | None: ...

    async def start(self) -> None: ...

    async def aclose(self) -> None: ...


@runtime_checkable
class StreamingTranscriber(Protocol):
    """Attach speech recognition to one existing Session audio stream."""

    @property
    def capabilities(self) -> TranscriptionCapabilities: ...

    def transcribe(
        self,
        *,
        session: object,
        input: object,
    ) -> TranscriptionConnection: ...


__all__ = [
    "StreamingTranscriber",
    "TranscriptUpdate",
    "TranscriptionConnection",
]
