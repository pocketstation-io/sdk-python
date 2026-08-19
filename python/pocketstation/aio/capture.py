"""High-signal asyncio recipe over the explicit Session API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from types import TracebackType

from .._native import AudioBatch
from ..graph import Stem
from ..observations import (
    RecordingOutcome,
    SessionEvent,
    SessionMetrics,
    SessionTraceConfiguration,
    StopResult,
)
from ..sources import Source
from .observations import EventStream
from .session import RunningSession, Session
from .streams import AudioStream


class Capture:
    """One application and optional microphone captured as independent stems."""

    def __init__(
        self,
        *,
        application: str,
        microphone: bool | str = True,
        record_to: str | Path | None = None,
        trace: SessionTraceConfiguration | None = None,
    ) -> None:
        if not application.strip():
            raise ValueError("application must not be empty")
        if not isinstance(microphone, (bool, str)):
            raise TypeError("microphone must be True, False, or a device ID")
        if isinstance(microphone, str) and not microphone.strip():
            raise ValueError("microphone device ID must not be empty")

        self._application_name = application
        self._microphone = microphone
        self._record_to = None if record_to is None else Path(record_to)
        self._trace = trace
        self._running: RunningSession | None = None
        self._entered = False
        self._declare()

    def _declare(self) -> None:
        session = (
            Session(recording_root=self._record_to)
            if self._trace is None
            else Session(recording_root=self._record_to, trace=self._trace)
        )
        application = session.capture(Source.application(self._application_name))
        microphone: Stem | None = None
        if self._microphone is True:
            microphone = session.capture(Source.microphone_default())
        elif isinstance(self._microphone, str):
            microphone = session.capture(Source.microphone_id(self._microphone))

        audio = session.polled_audio()
        self.application_route_id = application.send(audio)
        self.microphone_route_id = (
            None if microphone is None else microphone.send(audio)
        )
        if self._record_to is not None:
            application.record("application")
            if microphone is not None:
                microphone.record("microphone")

        self.session = session
        self.application_stem = application
        self.microphone_stem = microphone

    @property
    def is_running(self) -> bool:
        return self._running is not None and not self._running.is_stopped

    @property
    def stop_result(self) -> StopResult | None:
        return None if self._running is None else self._running.stop_result

    @property
    def recording_outcome(self) -> RecordingOutcome | None:
        result = self.stop_result
        return None if result is None else result.recording

    @property
    def audio(self) -> AudioStream:
        """Frame-first bounded audio from the running native Session."""
        return self._require_running().audio

    @property
    def events(self) -> EventStream:
        """Async lifecycle and failure events from the native Session."""
        return self._require_running().events

    async def start(self) -> Capture:
        if self._running is not None:
            raise RuntimeError("Capture has already started")
        self._running = await self.session.start()
        return self

    async def poll_audio(self) -> AudioBatch | None:
        return await self._require_running().poll_audio()

    async def wait_audio(self, *, timeout_ms: int = 100) -> AudioBatch | None:
        return await self._require_running().wait_audio(timeout_ms=timeout_ms)

    def audio_batches(
        self,
        *,
        wait_timeout_ms: int = 100,
    ) -> AsyncIterator[AudioBatch]:
        return self._require_running().audio_batches(wait_timeout_ms=wait_timeout_ms)

    async def poll_event(self) -> SessionEvent | None:
        return await self._require_running().poll_event()

    async def wait_event(self, *, timeout_ms: int = 100) -> SessionEvent | None:
        return await self._require_running().wait_event(timeout_ms=timeout_ms)

    async def metrics(self) -> SessionMetrics:
        return await self._require_running().metrics()

    async def stop(self) -> StopResult:
        return await self._require_started().stop()

    async def aclose(self) -> None:
        if self._running is not None:
            await self._running.aclose()

    async def __aenter__(self) -> Capture:
        if self._entered:
            raise RuntimeError("Capture context cannot be entered twice")
        self._entered = True
        return await self.start()

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    def _require_started(self) -> RunningSession:
        if self._running is None:
            raise RuntimeError("Capture has not started")
        return self._running

    def _require_running(self) -> RunningSession:
        running = self._require_started()
        if running.is_stopped:
            raise RuntimeError("Capture has stopped")
        return running


def capture(
    *,
    application: str,
    microphone: bool | str = True,
    record_to: str | Path | None = None,
    trace: SessionTraceConfiguration | None = None,
) -> Capture:
    """Declare a concise app+mic recipe backed by one native Rust Session."""
    return Capture(
        application=application,
        microphone=microphone,
        record_to=record_to,
        trace=trace,
    )


__all__ = ["Capture", "capture"]
