"""Asyncio lifecycle and failure observations from a running Session."""

from __future__ import annotations

from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable

from ..observations import SessionEvent
from ..streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)

_RETAINED_SESSION_EVENT_CAPACITY = 33


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
        self._producer_is_closed = is_closed
        self._state = _ReaderState()
        self._finished = False
        # Core's queue holds 32 events. One event may be in flight when an
        # asyncio read is cancelled, so the projection retains at most 33.
        self._pending: deque[SessionEvent] = deque(
            maxlen=_RETAINED_SESSION_EVENT_CAPACITY
        )

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return not self._pending and (self._finished or self._producer_is_closed())

    async def poll(self) -> SessionEvent | None:
        token = self._state.claim("event_read")
        try:
            return await self._read_once(timeout_ms=None)
        finally:
            self._state.release(token)

    async def read(
        self,
        *,
        timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> SessionEvent | None:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("event_read")
        try:
            return await self._read_once(timeout_ms=timeout_ms)
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
                    event = await self._read_once(timeout_ms=timeout_ms)
                    if event is not None:
                        yield event
            finally:
                self._state.release(token)

        return iterate()

    def _finish(self, events: tuple[SessionEvent, ...]) -> None:
        """Retain the bounded native event tail and close after it drains."""
        self._pending.extend(events)
        self._finished = True

    def _retain_cancelled_event(self, event: SessionEvent) -> None:
        """Retain one native event accepted before asyncio cancellation."""
        self._pending.append(event)

    async def _read_once(self, *, timeout_ms: int | None) -> SessionEvent | None:
        if self._pending:
            return self._pending.popleft()
        if self.is_closed:
            return None
        if timeout_ms is None:
            return await self._poll_event()
        return await self._wait_event(timeout_ms)


__all__ = ["EventStream"]
