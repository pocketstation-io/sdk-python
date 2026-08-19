"""Asyncio lifecycle and failure observations from a running Session."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable

from ..observations import SessionEvent
from ..streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)


class EventStream:
    """Exclusive asyncio view over the native bounded Session event queue."""

    def __init__(
        self,
        *,
        poll_event: Callable[[], Awaitable[SessionEvent | None]],
        wait_event: Callable[[int], Awaitable[SessionEvent | None]],
        is_closed: Callable[[], bool],
    ) -> None:
        self._poll_event = poll_event
        self._wait_event = wait_event
        self._is_closed = is_closed
        self._state = _ReaderState()

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._is_closed()

    async def poll(self) -> SessionEvent | None:
        token = self._state.claim("event_read")
        try:
            return None if self.is_closed else await self._poll_event()
        finally:
            self._state.release(token)

    async def read(self, *, timeout_s: float = 1.0) -> SessionEvent | None:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("event_read")
        try:
            return None if self.is_closed else await self._wait_event(timeout_ms)
        finally:
            self._state.release(token)

    def __aiter__(self) -> AsyncIterator[SessionEvent]:
        return self.iter_events()

    def iter_events(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[SessionEvent]:
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[SessionEvent]:
            token = self._state.claim("events")
            try:
                while not self.is_closed:
                    event = await self._wait_event(timeout_ms)
                    if event is not None:
                        yield event
            finally:
                self._state.release(token)

        return iterate()


__all__ = ["EventStream"]
