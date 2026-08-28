"""Incremental response contracts for provider-neutral voice composition."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable
from dataclasses import dataclass
from typing import Protocol, TypeAlias, runtime_checkable

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
        if not self.name.strip():
            raise ValueError("tool event name must not be empty")
        if not self.outcome.strip():
            raise ValueError("tool event outcome must not be empty")


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
        if not self.text and not self.tool_events and not self.final:
            raise ValueError(
                "a response chunk must contain text, a tool event, or final"
            )
        if self.response_id is not None and not self.response_id.strip():
            raise ValueError("response_id must not be empty")
        if self.turn_id is not None and self.turn_id < 1:
            raise ValueError("turn_id must be greater than zero")
        if self.provider_timestamp_ns is not None and self.provider_timestamp_ns < 0:
            raise ValueError("provider_timestamp_ns must not be negative")


@dataclass(frozen=True, slots=True)
class ConversationResponse:
    """Compatibility value for a complete non-streaming response."""

    text: str
    tool_events: tuple[ToolEvent, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("conversation response text must not be empty")


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
