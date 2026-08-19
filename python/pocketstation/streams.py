"""Bounded synchronous streams over one native polled-audio endpoint."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterator
from threading import Lock
from typing import Literal

from ._native import AudioBatch, AudioFrame, _SignalRead, _SignalSubscriptionMetrics
from .errors import StreamError, StreamInUseError, StreamModeError
from .signal import (
    STREAM_EOF,
    EndOfStream,
    SignalEnvelope,
    SignalReadResult,
    SignalSubscriptionMetrics,
)

_ReaderMode = Literal[
    "frames",
    "batches",
    "read",
    "events",
    "event_read",
    "signals",
    "signal_read",
    "sidecar",
    "sidecar_read",
]
_MAXIMUM_TIMEOUT_SECONDS = 1.0
_DEFAULT_ITERATION_TIMEOUT_SECONDS = 0.1


class _ReaderState:
    """Fail-fast one-mode/one-reader ownership shared by sync and asyncio."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._mode: _ReaderMode | None = None
        self._active: object | None = None

    @property
    def mode(self) -> str | None:
        with self._lock:
            return self._mode

    def claim(self, mode: _ReaderMode) -> object:
        token = object()
        with self._lock:
            if self._mode is not None and self._mode != mode:
                raise StreamModeError(self._mode, mode)
            if self._active is not None:
                raise StreamInUseError(mode)
            self._mode = mode
            self._active = token
        return token

    def release(self, token: object) -> None:
        with self._lock:
            if self._active is token:
                self._active = None


def _timeout_milliseconds(timeout_s: float, *, label: str = "timeout_s") -> int:
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError(f"{label} must be a number")
    value = float(timeout_s)
    if not 0.0 <= value <= _MAXIMUM_TIMEOUT_SECONDS:
        raise ValueError(f"{label} must be between 0.0 and 1.0")
    return round(value * 1_000)


def _iteration_timeout_milliseconds(timeout_s: float) -> int:
    timeout_ms = _timeout_milliseconds(timeout_s, label="wait_timeout_s")
    if timeout_ms == 0:
        raise ValueError("wait_timeout_s must be at least 0.001")
    return timeout_ms


class AudioStream:
    """Frame-first view of one native bounded audio endpoint.

    Native batches are flattened lazily. At most one batch is retained while
    its frames are consumed, so this object never creates a second audio queue.
    The first reader mode is permanent for the stream lifetime and concurrent
    readers fail immediately.
    """

    def __init__(
        self,
        *,
        poll_batch: Callable[[], AudioBatch | None],
        wait_batch: Callable[[int], AudioBatch | None],
        is_closed: Callable[[], bool],
    ) -> None:
        self._poll_batch = poll_batch
        self._wait_batch = wait_batch
        self._is_closed = is_closed
        self._state = _ReaderState()
        self._pending_frames: deque[AudioFrame] = deque()

    @property
    def reader_mode(self) -> str | None:
        """Return the permanently selected reader mode, if consumption began."""
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._is_closed()

    def read(self, *, timeout_s: float = 1.0) -> AudioFrame | None:
        """Read one frame, or return ``None`` when the bounded wait expires."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("read")
        try:
            return self._read_frame(timeout_ms)
        finally:
            self._state.release(token)

    def poll_batch(self) -> AudioBatch | None:
        """Advanced non-blocking batch read using the exclusive batch mode."""
        token = self._state.claim("batches")
        try:
            return None if self.is_closed else self._poll_batch()
        finally:
            self._state.release(token)

    def read_batch(self, *, timeout_s: float = 1.0) -> AudioBatch | None:
        """Advanced bounded batch read using the exclusive batch mode."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("batches")
        try:
            return None if self.is_closed else self._wait_batch(timeout_ms)
        finally:
            self._state.release(token)

    def __iter__(self) -> Iterator[AudioFrame]:
        return self.frames()

    def frames(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> Iterator[AudioFrame]:
        """Yield frames lazily until the owning Session closes."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        def iterate() -> Iterator[AudioFrame]:
            token = self._state.claim("frames")
            try:
                while not self.is_closed:
                    frame = self._read_frame(timeout_ms)
                    if frame is not None:
                        yield frame
            finally:
                self._state.release(token)

        return iterate()

    def batches(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> Iterator[AudioBatch]:
        """Yield native-owned batches without adding a managed queue."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        def iterate() -> Iterator[AudioBatch]:
            token = self._state.claim("batches")
            try:
                while not self.is_closed:
                    batch = self._wait_batch(timeout_ms)
                    if batch is not None:
                        yield batch
            finally:
                self._state.release(token)

        return iterate()

    def _read_frame(self, timeout_ms: int) -> AudioFrame | None:
        if self._pending_frames:
            return self._pending_frames.popleft()
        if self.is_closed:
            return None
        batch = self._wait_batch(timeout_ms)
        if batch is None:
            return None
        self._pending_frames.extend(batch)
        if not self._pending_frames:
            return None
        return self._pending_frames.popleft()


class SignalStream:
    """Exclusive Pythonic view of one native bounded ``BusSubscription``.

    ``None`` means a bounded read timed out, while ``STREAM_EOF`` means the
    endpoint is permanently closed. Iteration handles both states naturally
    and owns no queue or worker beyond the canonical Rust edge.
    """

    def __init__(
        self,
        *,
        poll_signal: Callable[[], _SignalRead],
        wait_signal: Callable[[int], _SignalRead],
        close_signal: Callable[[], None],
        signal_metrics: Callable[[], _SignalSubscriptionMetrics],
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

    def poll(self) -> SignalReadResult:
        """Read immediately: envelope, ``None`` for empty, or ``STREAM_EOF``."""
        token = self._state.claim("signal_read")
        try:
            return STREAM_EOF if self._closed else self._decode(self._poll_signal())
        finally:
            self._state.release(token)

    def read(self, *, timeout_s: float = 1.0) -> SignalReadResult:
        """Perform one native bounded wait with explicit timeout and EOF states."""
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("signal_read")
        try:
            return (
                STREAM_EOF
                if self._closed
                else self._decode(self._wait_signal(timeout_ms))
            )
        finally:
            self._state.release(token)

    def __iter__(self) -> Iterator[SignalEnvelope]:
        return self.iter_signals()

    def iter_signals(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> Iterator[SignalEnvelope]:
        """Yield immutable envelopes until native EOF or explicit close."""
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        def iterate() -> Iterator[SignalEnvelope]:
            token = self._state.claim("signals")
            try:
                while not self._closed:
                    result = self._decode(self._wait_signal(timeout_ms))
                    if isinstance(result, EndOfStream):
                        break
                    if result is not None:
                        yield result
            finally:
                self._state.release(token)

        return iterate()

    def close(self) -> None:
        """Idempotently close this receipt without stopping its Session."""
        if self._closed:
            return
        self._close_signal()
        self._closed = True

    def metrics(self) -> SignalSubscriptionMetrics:
        """Snapshot capacity, payload-byte bounds, depth, delivery, and drops."""
        return SignalSubscriptionMetrics._from_native(self._signal_metrics())

    def _decode(self, result: _SignalRead) -> SignalReadResult:
        if result.status == "item":
            if result.envelope is None:
                raise StreamError(
                    "native signal read omitted its envelope",
                    "stream.invalid_read",
                )
            return SignalEnvelope._from_native(result.envelope)
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


__all__ = ["AudioStream", "SignalStream"]
