"""Streaming speech-synthesis contracts over the existing PCM input boundary."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable
from dataclasses import dataclass
from typing import Protocol, TypeAlias, runtime_checkable

from .capabilities import SynthesisCapabilities
from .response import ResponseChunk
from .turns import ConversationTurn


@dataclass(frozen=True, slots=True)
class SynthesisRequest:
    """One response fragment selected for speech synthesis."""

    response: ResponseChunk
    turn: ConversationTurn


@dataclass(frozen=True, slots=True)
class SynthesisChunk:
    """One generated PCM chunk with response and turn ownership."""

    samples: object
    sample_rate_hz: int
    channels: int
    sequence: int
    response_id: str | None = None
    turn_id: int | None = None
    timestamp_ns: int | None = None
    final: bool = False
    provider_observations: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be greater than zero")
        if not 1 <= self.channels <= 32:
            raise ValueError("channels must be between 1 and 32")
        if self.sequence < 0:
            raise ValueError("sequence must not be negative")
        if self.turn_id is not None and self.turn_id < 1:
            raise ValueError("turn_id must be greater than zero")
        if self.timestamp_ns is not None and self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must not be negative")


SynthesisResult: TypeAlias = (
    AsyncIterable[SynthesisChunk | object]
    | Awaitable[AsyncIterable[SynthesisChunk | object]]
)


@runtime_checkable
class SpeechSynthesizer(Protocol):
    """Produce PCM incrementally for one response fragment."""

    @property
    def capabilities(self) -> SynthesisCapabilities: ...

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult: ...

    async def start(self) -> None: ...

    async def aclose(self) -> None: ...


__all__ = [
    "SpeechSynthesizer",
    "SynthesisChunk",
    "SynthesisRequest",
    "SynthesisResult",
]
