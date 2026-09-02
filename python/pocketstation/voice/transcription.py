"""Streaming transcript revisions and transcriber integration protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..identity import SourceId, StreamId
from ..signal import BusSubscription, SignalEnvelope
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
        for name, value in (
            ("source_timestamp_ns", self.source_timestamp_ns),
            ("audio_start_ns", self.audio_start_ns),
            ("audio_end_ns", self.audio_end_ns),
            ("provider_timestamp_ns", self.provider_timestamp_ns),
            ("session_timestamp_ns", self.session_timestamp_ns),
        ):
            _optional_timestamp(name, value)
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


def _optional_timestamp(name: str, value: int | None) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value < 0
    ):
        raise TypeError(f"{name} must be a non-negative integer or None")


def _optional_identity(name: str, value: int | None) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value < 1
    ):
        raise TypeError(f"{name} must be a positive integer or None")


def _optional_sequence(name: str, value: int | None) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value < 0
    ):
        raise TypeError(f"{name} must be a non-negative integer or None")


__all__ = [
    "StreamingTranscriber",
    "TranscriptUpdate",
    "TranscriptionConnection",
]
