"""Asyncio views of Session-owned native PKSS sidecars."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable

from .._native import _SidecarMessage as _NativeSidecarMessage
from .._native import _SidecarRead as _NativeSidecarRead
from .._native import _SidecarSnapshot as _NativeSidecarSnapshot
from ..errors import SidecarProtocolError
from ..sidecar import (
    SidecarHandle,
    SidecarMessage,
    SidecarReadResult,
    SidecarSnapshot,
)
from ..signal import STREAM_EOF, EndOfStream
from ..streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)


class SidecarStream:
    """Cancellation-safe one-reader view of the native incoming PKSS queue."""

    def __init__(
        self,
        *,
        poll_message: Callable[[], Awaitable[_NativeSidecarRead]],
        wait_message: Callable[[int], Awaitable[_NativeSidecarRead]],
        is_session_stopped: Callable[[], bool],
    ) -> None:
        self._poll_message = poll_message
        self._wait_message = wait_message
        self._is_session_stopped = is_session_stopped
        self._state = _ReaderState()
        self._closed = False

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._closed or self._is_session_stopped()

    async def poll(self) -> SidecarReadResult:
        token = self._state.claim("sidecar_read")
        try:
            return (
                STREAM_EOF
                if self.is_closed
                else self._decode(await self._poll_message())
            )
        finally:
            self._state.release(token)

    async def read(self, *, timeout_s: float = 1.0) -> SidecarReadResult:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("sidecar_read")
        try:
            return (
                STREAM_EOF
                if self.is_closed
                else self._decode(await self._wait_message(timeout_ms))
            )
        finally:
            self._state.release(token)

    def __aiter__(self) -> AsyncIterator[SidecarMessage]:
        return self.messages()

    def messages(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[SidecarMessage]:
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[SidecarMessage]:
            token = self._state.claim("sidecar")
            try:
                while not self.is_closed:
                    result = self._decode(await self._wait_message(timeout_ms))
                    if isinstance(result, EndOfStream):
                        break
                    if result is not None:
                        yield result
            finally:
                self._state.release(token)

        return iterate()

    def _decode(self, value: _NativeSidecarRead) -> SidecarReadResult:
        if value.status == "item":
            if value.message is None:
                raise SidecarProtocolError(
                    "native sidecar read omitted its message",
                    "sidecar.invalid_read",
                )
            return SidecarMessage._from_native(value.message)
        if value.status == "empty":
            return None
        if value.status == "closed":
            self._closed = True
            return STREAM_EOF
        raise SidecarProtocolError(
            f"native sidecar read has unknown state {value.status!r}",
            "sidecar.invalid_read",
        )


class SidecarConnection:
    """Asyncio RunningSession view of one Session-owned child."""

    def __init__(
        self,
        *,
        handle: SidecarHandle,
        send_message: Callable[[_NativeSidecarMessage], Awaitable[None]],
        poll_message: Callable[[], Awaitable[_NativeSidecarRead]],
        wait_message: Callable[[int], Awaitable[_NativeSidecarRead]],
        snapshot: Callable[[], Awaitable[_NativeSidecarSnapshot]],
        is_session_stopped: Callable[[], bool],
    ) -> None:
        self.handle = handle
        self._send_message = send_message
        self._snapshot = snapshot
        self.messages = SidecarStream(
            poll_message=poll_message,
            wait_message=wait_message,
            is_session_stopped=is_session_stopped,
        )

    async def send(self, message: SidecarMessage) -> None:
        """Try one immediate native bounded enqueue without event-loop blocking."""
        await self._send_message(message._to_native())

    async def snapshot(self) -> SidecarSnapshot:
        return SidecarSnapshot._from_native(await self._snapshot())


__all__ = ["SidecarConnection", "SidecarStream"]
