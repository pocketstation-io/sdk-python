"""Bounded asyncio streams over one native polled-audio endpoint."""

from __future__ import annotations

from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Generic, TypeVar, cast

from .._native import AudioBatch, AudioFrame, _SignalRead, _SignalSubscriptionMetrics
from ..errors import StreamError
from ..signal import (
    STREAM_EOF,
    EndOfStream,
    SignalEnvelope,
    SignalReadResult,
    SignalSubscriptionMetrics,
)
from ..streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    AudioBatchReadResult,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)

_PayloadT = TypeVar("_PayloadT")


class AudioStream:
    """Frame-first asyncio view with one explicit reader and no Python queue."""

    def __init__(
        self,
        *,
        poll_batch: Callable[[], Awaitable[AudioBatch | None]],
        wait_batch: Callable[[int], Awaitable[AudioBatch | None]],
        is_closed: Callable[[], bool],
    ) -> None:
        self._poll_batch = poll_batch
        self._wait_batch = wait_batch
        self._is_closed = is_closed
        self._state = _ReaderState()
        self._pending_frames: deque[AudioFrame] = deque()

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._is_closed()

    async def read(self, *, timeout_s: float = 1.0) -> AudioFrame | None:
        """Read one frame without blocking the event-loop thread."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("read")
        try:
            return await self._read_frame(timeout_ms)
        finally:
            self._state.release(token)

    async def poll_batch(self) -> AudioBatch | None:
        """Advanced non-blocking batch read using the exclusive batch mode."""
        token = self._state.claim("batches")
        try:
            return None if self.is_closed else await self._poll_batch()
        finally:
            self._state.release(token)

    async def poll(self) -> AudioBatchReadResult:
        """Read immediately with distinct batch, empty, and closed outcomes."""
        token = self._state.claim("batches")
        try:
            if self.is_closed:
                return STREAM_EOF
            batch = await self._poll_batch()
            return STREAM_EOF if batch is None and self.is_closed else batch
        finally:
            self._state.release(token)

    async def read_batch(self, *, timeout_s: float = 1.0) -> AudioBatch | None:
        """Advanced bounded batch read using the exclusive batch mode."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("batches")
        try:
            return None if self.is_closed else await self._wait_batch(timeout_ms)
        finally:
            self._state.release(token)

    async def read_result(self, *, timeout_s: float = 1.0) -> AudioBatchReadResult:
        """Wait finitely with distinct batch, timeout, and closed outcomes."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("batches")
        try:
            if self.is_closed:
                return STREAM_EOF
            batch = await self._wait_batch(timeout_ms)
            return STREAM_EOF if batch is None and self.is_closed else batch
        finally:
            self._state.release(token)

    def __aiter__(self) -> AsyncIterator[AudioFrame]:
        return self.frames()

    def frames(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[AudioFrame]:
        """Yield frames lazily until the owning Session closes."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[AudioFrame]:
            token = self._state.claim("frames")
            try:
                while not self.is_closed:
                    frame = await self._read_frame(timeout_ms)
                    if frame is not None:
                        yield frame
            finally:
                self._state.release(token)

        return iterate()

    def batches(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[AudioBatch]:
        """Yield native-owned batches without an event-loop polling loop."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[AudioBatch]:
            token = self._state.claim("batches")
            try:
                while not self.is_closed:
                    batch = await self._wait_batch(timeout_ms)
                    if batch is not None:
                        yield batch
            finally:
                self._state.release(token)

        return iterate()

    async def _read_frame(self, timeout_ms: int) -> AudioFrame | None:
        if self._pending_frames:
            return self._pending_frames.popleft()
        if self.is_closed:
            return None
        batch = await self._wait_batch(timeout_ms)
        if batch is None:
            return None
        self._pending_frames.extend(batch)
        if not self._pending_frames:
            return None
        return self._pending_frames.popleft()


class SignalStream(Generic[_PayloadT]):
    """Cancellation-safe asyncio view of one native ``BusSubscription``."""

    def __init__(
        self,
        *,
        poll_signal: Callable[[], Awaitable[_SignalRead]],
        wait_signal: Callable[[int], Awaitable[_SignalRead]],
        close_signal: Callable[[], Awaitable[None]],
        signal_metrics: Callable[[], Awaitable[_SignalSubscriptionMetrics]],
    ) -> None:
        self._poll_signal = poll_signal
        self._wait_signal = wait_signal
        self._close_signal = close_signal
        self._signal_metrics = signal_metrics
        self._state = _ReaderState()
        self._closed = False

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._closed

    async def poll(self) -> SignalReadResult[_PayloadT]:
        token = self._state.claim("signal_read")
        try:
            return (
                STREAM_EOF if self._closed else self._decode(await self._poll_signal())
            )
        finally:
            self._state.release(token)

    async def read(self, *, timeout_s: float = 1.0) -> SignalReadResult[_PayloadT]:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("signal_read")
        try:
            return (
                STREAM_EOF
                if self._closed
                else self._decode(await self._wait_signal(timeout_ms))
            )
        finally:
            self._state.release(token)

    def __aiter__(self) -> AsyncIterator[SignalEnvelope[_PayloadT]]:
        return self.iter_signals()

    def iter_signals(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[SignalEnvelope[_PayloadT]]:
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[SignalEnvelope[_PayloadT]]:
            token = self._state.claim("signals")
            try:
                while not self._closed:
                    result = self._decode(await self._wait_signal(timeout_ms))
                    if isinstance(result, EndOfStream):
                        break
                    if result is not None:
                        yield result
            finally:
                self._state.release(token)

        return iterate()

    async def aclose(self) -> None:
        if self._closed:
            return
        await self._close_signal()
        self._closed = True

    async def metrics(self) -> SignalSubscriptionMetrics:
        """Snapshot capacity, payload-byte bounds, depth, delivery, and drops."""
        return SignalSubscriptionMetrics._from_native(await self._signal_metrics())

    def _decode(self, result: _SignalRead) -> SignalReadResult[_PayloadT]:
        if result.status == "item":
            if result.envelope is None:
                raise StreamError(
                    "native signal read omitted its envelope",
                    "stream.invalid_read",
                )
            return cast(
                SignalEnvelope[_PayloadT],
                SignalEnvelope._from_native(result.envelope),
            )
        if result.status == "empty":
            return None
        if result.status == "closed":
            self._closed = True
            return STREAM_EOF
        if result.status == "fault":
            self._closed = True
            raise StreamError(
                result.error or "native signal endpoint failed",
                "stream.fault",
            )
        raise StreamError(
            f"native signal read has unknown state {result.status!r}",
            "stream.invalid_read",
        )


__all__ = ["AudioBatchReadResult", "AudioStream", "SignalStream"]
