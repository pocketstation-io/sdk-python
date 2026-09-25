"""Incremental response protocols for provider-neutral voice composition."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable
from dataclasses import dataclass
from typing import Protocol, TypeAlias, runtime_checkable

from ._validation import (
    require_boolean,
    require_nonempty,
    require_optional_nonempty,
    require_optional_nonnegative_integer,
    require_optional_positive_integer,
)
from .capabilities import ResponseCapabilities
from .transcription import TranscriptUpdate
from .turns import ConversationContext


@dataclass(frozen=True, slots=True)
class ToolEvent:
    """One bounded observation returned by provider-managed tool work."""

    name: str
    outcome: str
    detail: str = ""

    def __post_init__(self) -> None:
        require_nonempty("tool event name", self.name)
        require_nonempty("tool event outcome", self.outcome)


@dataclass(frozen=True, slots=True)
class ResponseRequest:
    """A transcript revision and finite history presented to a response model."""

    transcript: TranscriptUpdate
    context: ConversationContext


@dataclass(frozen=True, slots=True)
class ResponseChunk:
    """One ordered response fragment."""

    text: str = ""
    tool_events: tuple[ToolEvent, ...] = ()
    response_id: str | None = None
    turn_id: int | None = None
    final: bool = False
    provider_timestamp_ns: int | None = None

    def __post_init__(self) -> None:
        require_boolean("final", self.final)
        object.__setattr__(self, "tool_events", tuple(self.tool_events))
        if not self.text and not self.tool_events and not self.final:
            raise ValueError(
                "a response chunk must contain text, a tool event, or final"
            )
        require_optional_nonempty("response_id", self.response_id)
        require_optional_positive_integer("turn_id", self.turn_id)
        require_optional_nonnegative_integer(
            "provider_timestamp_ns", self.provider_timestamp_ns
        )


@dataclass(frozen=True, slots=True)
class ConversationResponse:
    """Compatibility value for a complete non-streaming response."""

    text: str
    tool_events: tuple[ToolEvent, ...] = ()

    def __post_init__(self) -> None:
        require_nonempty("conversation response text", self.text)
        object.__setattr__(self, "tool_events", tuple(self.tool_events))


ConversationResponseChunk = ResponseChunk
ResponseItem: TypeAlias = str | ConversationResponse | ResponseChunk
ResponseResult: TypeAlias = (
    ResponseItem
    | AsyncIterable[ResponseItem]
    | Awaitable[ResponseItem | AsyncIterable[ResponseItem]]
)


@runtime_checkable
class ResponseModel(Protocol):
    """Produce bounded incremental text from a transcript and history."""

    @property
    def capabilities(self) -> ResponseCapabilities: ...

    def respond(self, request: ResponseRequest) -> ResponseResult: ...

    async def start(self) -> None: ...

    async def aclose(self) -> None: ...


__all__ = [
    "ConversationResponse",
    "ConversationResponseChunk",
    "ResponseChunk",
    "ResponseItem",
    "ResponseModel",
    "ResponseRequest",
    "ResponseResult",
    "ToolEvent",
]
