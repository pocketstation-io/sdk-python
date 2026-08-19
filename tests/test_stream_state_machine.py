"""Protocol state-machine tests independent of platform capture timing."""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass

import pytest

from pocketstation import STREAM_EOF, StreamError, StreamInUseError, StreamModeError
from pocketstation.aio import SignalStream as AsyncSignalStream
from pocketstation.streams import SignalStream


@dataclass
class _Read:
    status: str
    envelope: object | None = None
    error: str | None = None


@dataclass
class _Metrics:
    capacity_signals: int = 16
    max_payload_bytes: int = 1024
    maximum_buffered_payload_bytes: int = 16_384
    depth_signals: int = 0
    peak_depth_signals: int = 0
    enqueued_total: int = 0
    received_total: int = 0
    dropped_total: int = 0


def test_timeout_eof_fault_and_close_are_distinct_and_sticky() -> None:
    reads = [_Read("empty"), _Read("closed")]
    closes = 0

    def close() -> None:
        nonlocal closes
        closes += 1

    stream = SignalStream(
        poll_signal=lambda: reads.pop(0),  # type: ignore[arg-type]
        wait_signal=lambda _timeout_ms: reads.pop(0),  # type: ignore[arg-type]
        close_signal=close,
        signal_metrics=_Metrics,  # type: ignore[arg-type]
    )
    assert stream.poll() is None
    assert stream.read(timeout_s=0.0) is STREAM_EOF
    assert stream.poll() is STREAM_EOF
    stream.close()
    assert closes == 0

    fault = SignalStream(
        poll_signal=lambda: _Read("fault", error="fixture failed"),  # type: ignore[arg-type]
        wait_signal=lambda _timeout_ms: _Read("empty"),  # type: ignore[arg-type]
        close_signal=lambda: None,
        signal_metrics=_Metrics,  # type: ignore[arg-type]
    )
    with pytest.raises(StreamError) as failure:
        fault.poll()
    assert failure.value.code == "stream.fault"
    assert fault.is_closed


def test_signal_reader_mode_and_concurrent_ownership_fail_fast() -> None:
    entered = threading.Event()
    release = threading.Event()

    def wait(_timeout_ms: int) -> _Read:
        entered.set()
        assert release.wait(1.0)
        return _Read("empty")

    stream = SignalStream(
        poll_signal=lambda: _Read("empty"),  # type: ignore[arg-type]
        wait_signal=wait,  # type: ignore[arg-type]
        close_signal=lambda: None,
        signal_metrics=_Metrics,  # type: ignore[arg-type]
    )
    first = threading.Thread(target=stream.read)
    first.start()
    assert entered.wait(1.0)
    with pytest.raises(StreamInUseError):
        stream.read(timeout_s=0.0)
    release.set()
    first.join(timeout=1.0)
    assert not first.is_alive()

    with pytest.raises(StreamModeError):
        next(stream.iter_signals())


@pytest.mark.asyncio
async def test_cancelled_async_reader_releases_ownership_after_cleanup() -> None:
    entered = asyncio.Event()
    settled = asyncio.Event()

    async def wait(_timeout_ms: int) -> _Read:
        entered.set()
        try:
            await asyncio.Future()
        finally:
            settled.set()

    async def poll() -> _Read:
        return _Read("empty")

    async def close() -> None:
        return None

    async def metrics() -> _Metrics:
        return _Metrics()

    stream = AsyncSignalStream(
        poll_signal=poll,  # type: ignore[arg-type]
        wait_signal=wait,  # type: ignore[arg-type]
        close_signal=close,
        signal_metrics=metrics,  # type: ignore[arg-type]
    )
    reader = asyncio.create_task(stream.read())
    await entered.wait()
    reader.cancel()
    with pytest.raises(asyncio.CancelledError):
        await reader
    assert settled.is_set()
    assert await stream.poll() is None


@pytest.mark.parametrize("timeout", [-0.1, 1.1])
def test_signal_waits_remain_bounded(timeout: float) -> None:
    stream = SignalStream(
        poll_signal=lambda: _Read("empty"),  # type: ignore[arg-type]
        wait_signal=lambda _timeout_ms: _Read("empty"),  # type: ignore[arg-type]
        close_signal=lambda: None,
        signal_metrics=_Metrics,  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match=r"between 0\.0 and 1\.0"):
        stream.read(timeout_s=timeout)
