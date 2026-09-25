"""Streaming speech-synthesis protocols that write to an existing PCM input."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable
from dataclasses import dataclass
from typing import Protocol, TypeAlias, runtime_checkable

from ._validation import (
    MAX_SAFE_INTEGER,
    require_boolean,
    require_integer,
    require_optional_nonempty,
    require_optional_nonnegative_integer,
    require_optional_positive_integer,
)
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
        require_integer(
            "sample_rate_hz",
            self.sample_rate_hz,
            minimum=1,
            maximum=MAX_SAFE_INTEGER,
        )
        require_integer("channels", self.channels, minimum=1, maximum=32)
        require_integer("sequence", self.sequence, minimum=0, maximum=MAX_SAFE_INTEGER)
        require_optional_nonempty("response_id", self.response_id)
        require_optional_positive_integer("turn_id", self.turn_id)
        require_optional_nonnegative_integer("timestamp_ns", self.timestamp_ns)
        require_boolean("final", self.final)
        object.__setattr__(
            self, "provider_observations", tuple(self.provider_observations)
        )


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
