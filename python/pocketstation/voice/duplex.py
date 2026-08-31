"""Contracts for stateful providers that accept and produce live audio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .capabilities import DuplexVoiceCapabilities
from .configuration import ConversationConfig
from .turns import ConversationOutcome


@dataclass(frozen=True, slots=True)
class DuplexVoiceContext:
    """Existing Session boundaries supplied to a duplex provider adapter."""

    session: object
    input: object
    output: object
    config: ConversationConfig


@runtime_checkable
class DuplexVoiceConnection(Protocol):
    """One finite provider connection attached to a PocketStation Session."""

    async def start(self, running: object) -> None: ...

    async def wait(self) -> ConversationOutcome: ...

    async def interrupt(self) -> None: ...

    async def cancel_output(self) -> None: ...

    def stop(self) -> None: ...

    async def aclose(self) -> None: ...


DuplexConnectResult = DuplexVoiceConnection


@runtime_checkable
class DuplexVoiceModel(Protocol):
    """Declare one stateful provider connection before the Session starts."""

    @property
    def capabilities(self) -> DuplexVoiceCapabilities: ...

    def connect(self, context: DuplexVoiceContext) -> DuplexConnectResult: ...


__all__ = [
    "DuplexConnectResult",
    "DuplexVoiceConnection",
    "DuplexVoiceContext",
    "DuplexVoiceModel",
]
