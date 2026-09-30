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
    AudioReadResult,
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
        is_drained: Callable[[], bool] | None = None,
    ) -> None:
        self._poll_batch = poll_batch
        self._wait_batch = wait_batch
        self._is_closed = is_closed
        self._is_drained = is_drained or is_closed
        self._discarded = False
        self._state = _ReaderState()
        self._pending_frames: deque[AudioFrame] = deque()
        self._pending_batches: deque[AudioBatch] = deque(maxlen=1)

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._discarded or self._is_closed()

    @property
    def _at_eof(self) -> bool:
        return self._discarded or self._is_drained()

    def _discard(self) -> None:
        """Discard the existing delivery cache after explicit close or cancel."""
        self._discarded = True
        self._pending_frames.clear()
        self._pending_batches.clear()

    async def read(
        self,
        *,
        timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AudioReadResult:
        """Read a frame, time out, or report terminal state without blocking."""
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
            if self._pending_batches:
                return self._pending_batches.popleft()
            if self._at_eof:
                return None
            batch = await self._poll_batch()
            return None if self._discarded else batch
        finally:
            self._state.release(token)

    async def poll(self) -> AudioBatchReadResult:
        """Read immediately with distinct batch, empty, and closed outcomes."""
        token = self._state.claim("batches")
        try:
            if self._pending_batches:
                return self._pending_batches.popleft()
            if self._at_eof:
                return STREAM_EOF
            batch = await self._poll_batch()
            return (
                STREAM_EOF
                if self._discarded or (batch is None and self._at_eof)
                else batch
            )
        finally:
            self._state.release(token)

    async def read_batch(
        self,
        *,
        timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AudioBatch | None:
        """Advanced bounded batch read using the exclusive batch mode."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("batches")
        try:
            if self._pending_batches:
                return self._pending_batches.popleft()
            if self._at_eof:
                return None
            batch = await self._wait_batch(timeout_ms)
            return None if self._discarded else batch
        finally:
            self._state.release(token)

    async def read_result(
        self,
        *,
        timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AudioBatchReadResult:
        """Wait finitely with distinct batch, timeout, and closed outcomes."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("batches")
        try:
            if self._pending_batches:
                return self._pending_batches.popleft()
            if self._at_eof:
                return STREAM_EOF
            batch = await self._wait_batch(timeout_ms)
            return (
                STREAM_EOF
                if self._discarded or (batch is None and self._at_eof)
                else batch
            )
        finally:
            self._state.release(token)

    def __aiter__(self) -> AsyncIterator[AudioFrame]:
        return self.frames()

    def frames(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> AsyncIterator[AudioFrame]:
        """Yield accepted frames lazily, including the final drain after stop."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        async def iterate() -> AsyncIterator[AudioFrame]:
            token = self._state.claim("frames")
            try:
                while True:
                    frame = await self._read_frame(timeout_ms)
                    if isinstance(frame, EndOfStream):
                        break
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
                while self._pending_batches or not self._at_eof:
                    batch = (
                        self._pending_batches.popleft()
                        if self._pending_batches
                        else await self._wait_batch(timeout_ms)
                    )
                    if batch is not None and not self._discarded:
                        yield batch
            finally:
                self._state.release(token)

        return iterate()

    async def _read_frame(self, timeout_ms: int) -> AudioReadResult:
        if self._pending_frames:
            return self._pending_frames.popleft()
        if self._at_eof:
            return STREAM_EOF
        batch = await self._wait_batch(timeout_ms)
        if batch is None:
            return STREAM_EOF if self._at_eof else None
        if self._discarded:
            return STREAM_EOF
        self._pending_frames.extend(batch)
        if not self._pending_frames:
            return STREAM_EOF if self._at_eof else None
        return self._pending_frames.popleft()

    def _retain_cancelled_batch(self, batch: AudioBatch | None) -> None:
        """Retain one accepted native batch when its await is cancelled."""
        if batch is None or self._discarded:
            return
        if self._state.mode in {"read", "frames"}:
            self._pending_frames.extend(batch)
        else:
            self._pending_batches.append(batch)


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
        self._pending_reads: deque[_SignalRead] = deque(maxlen=1)

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._closed

    async def poll(self) -> SignalReadResult[_PayloadT]:
        token = self._state.claim("signal_read")
        try:
            return await self._read_once(self._poll_signal)
        finally:
            self._state.release(token)

    async def read(
        self,
        *,
        timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> SignalReadResult[_PayloadT]:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("signal_read")
        try:
            return await self._read_once(lambda: self._wait_signal(timeout_ms))
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
                while self._pending_reads or not self._closed:
                    result = await self._read_once(
                        lambda: self._wait_signal(timeout_ms)
                    )
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

    async def _read_once(
        self,
        read: Callable[[], Awaitable[_SignalRead]],
    ) -> SignalReadResult[_PayloadT]:
        if self._pending_reads:
            return self._decode(self._pending_reads.popleft())
        if self._closed:
            return STREAM_EOF
        return self._decode(await read())

    def _retain_cancelled_read(self, result: _SignalRead) -> None:
        """Retain one native result accepted before asyncio cancellation."""
        self._pending_reads.append(result)

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


__all__ = [
    "AudioBatchReadResult",
    "AudioReadResult",
    "AudioStream",
    "SignalStream",
]
