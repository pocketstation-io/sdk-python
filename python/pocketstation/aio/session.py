"""Asyncio ownership of the canonical native PocketStation Session."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, TypeVar

from .._native import (
    AudioBatch,
    _SessionStartCancellation,
)
from .._native import (
    RunningSession as _NativeRunningSession,
)
from .._native import (
    Session as _NativeSession,
)
from ..audio_input import AudioInputConfig
from ..audio_input import PcmSource as SyncPcmSource
from ..connector import Connector as SyncConnector
from ..connector import RegisteredConnector as SyncRegisteredConnector
from ..errors import PocketStationError, _native_call, _normalize_native_error
from ..extensions import NativeExtensionLibrary
from ..graph import (
    Endpoint,
    Stem,
    _GraphSessionDeclarations,
)
from ..observations import (
    SessionEvent,
    SessionMetrics,
    SessionTraceConfiguration,
    StopResult,
)
from ..operator_authoring import OperatorProvider as SyncOperatorProvider
from ..operator_authoring import (
    RegisteredOperator,
)
from ..operator_authoring import (
    _NativeFactoryAdapter as _NativeOperatorFactoryAdapter,
)
from ..sidecar import SidecarHandle, SidecarProcessSpec
from ..signal import BusSubscription
from ..source_authoring import (
    RegisteredSource,
)
from ..source_authoring import SourceProvider as SyncSourceProvider
from ..source_authoring import (
    _NativeFactoryAdapter as _NativeSourceFactoryAdapter,
)
from ..sources import Source
from .audio_input import AudioInput, PcmSource
from .connector import Connector, RegisteredConnector
from .observations import EventStream
from .operator_authoring import OperatorProvider
from .sidecar import SidecarConnection
from .source_authoring import SourceProvider
from .streams import AudioStream, SignalStream

if TYPE_CHECKING:
    from ..relay import RelayPublisher
    from .relay import RelaySession

_Result = TypeVar("_Result")
_BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


class RunningSession:
    """Running native Session with bounded asyncio batch delivery."""

    def __init__(self, native: _NativeRunningSession) -> None:
        self._native = native
        self._stop_result: StopResult | None = None
        self._stop_lock = asyncio.Lock()
        self._audio = AudioStream(
            poll_batch=self._poll_audio_native,
            wait_batch=self._wait_audio_native,
            is_closed=lambda: self.is_stopped,
        )
        self._events = EventStream(
            poll_event=self._poll_event_native,
            wait_event=self._wait_event_native,
            is_closed=lambda: self.is_stopped,
        )
        self._signals: dict[int, SignalStream] = {}
        self._sidecars: dict[int, SidecarConnection] = {}

    @property
    def session_id(self) -> int:
        return self._native.session_id

    @property
    def is_stopped(self) -> bool:
        return self._stop_result is not None

    @property
    def stop_result(self) -> StopResult | None:
        return self._stop_result

    @property
    def audio(self) -> AudioStream:
        """The exclusive async frame-first native endpoint view."""
        return self._audio

    @property
    def events(self) -> EventStream:
        """The exclusive async lifecycle and failure event stream."""
        return self._events

    def signals(self, subscription: BusSubscription) -> SignalStream:
        """Return the one exclusive asyncio stream for a subscription."""
        stream = self._signals.get(subscription.id)
        if stream is None:
            native = subscription._native
            stream = SignalStream(
                poll_signal=lambda: _native_async(
                    lambda: self._native.poll_signal(native)
                ),
                wait_signal=lambda timeout_ms: _native_async(
                    lambda: self._native.wait_signal(native, timeout_ms)
                ),
                close_signal=lambda: _native_async(
                    lambda: self._native.close_signal(native)
                ),
                signal_metrics=lambda: _native_async(
                    lambda: self._native.signal_metrics(native)
                ),
            )
            self._signals[subscription.id] = stream
        return stream

    def sidecar(self, handle: SidecarHandle) -> SidecarConnection:
        """Return the Session-owned asyncio connection for one child."""
        self._require_running()
        if handle.session_id != self._native.session_id:
            raise ValueError("SidecarHandle belongs to a different Session")
        connection = self._sidecars.get(handle.id)
        if connection is None:
            connection = SidecarConnection(
                handle=handle,
                send_message=lambda message: _native_async(
                    lambda: self._native.send_sidecar(handle.id, message)
                ),
                poll_message=lambda: _native_async(
                    lambda: self._native.poll_sidecar(handle.id)
                ),
                wait_message=lambda timeout_ms: _native_async(
                    lambda: self._native.wait_sidecar(handle.id, timeout_ms)
                ),
                snapshot=lambda: _native_async(
                    lambda: self._native.sidecar_snapshot(handle.id)
                ),
                is_session_stopped=lambda: self.is_stopped,
            )
            self._sidecars[handle.id] = connection
        return connection

    async def poll_audio(self) -> AudioBatch | None:
        """Compatibility alias for the advanced non-blocking batch mode."""
        self._require_running()
        return await self.audio.poll_batch()

    async def wait_audio(self, *, timeout_ms: int = 100) -> AudioBatch | None:
        """Compatibility alias for the advanced bounded batch mode."""
        self._require_running()
        if not 0 <= timeout_ms <= 1_000:
            raise ValueError("timeout_ms must be between 0 and 1000")
        return await self.audio.read_batch(timeout_s=timeout_ms / 1_000)

    def audio_batches(
        self,
        *,
        wait_timeout_ms: int = 100,
    ) -> AsyncIterator[AudioBatch]:
        """Compatibility alias for ``audio.batches()``."""
        self._require_running()
        if not 0 <= wait_timeout_ms <= 1_000:
            raise ValueError("wait_timeout_ms must be between 0 and 1000")
        return self.audio.batches(wait_timeout_s=wait_timeout_ms / 1_000)

    async def poll_event(self) -> SessionEvent | None:
        """Compatibility alias for ``events.poll()``."""
        self._require_running()
        return await self.events.poll()

    async def wait_event(self, *, timeout_ms: int = 100) -> SessionEvent | None:
        """Compatibility alias for the bounded ``events.read()`` mode."""
        self._require_running()
        if not 0 <= timeout_ms <= 1_000:
            raise ValueError("timeout_ms must be between 0 and 1000")
        return await self.events.read(timeout_s=timeout_ms / 1_000)

    async def metrics(self) -> SessionMetrics:
        """Return a complete immutable point-in-time metrics snapshot."""
        self._require_running()
        native = await _native_async(self._native.metrics)
        return SessionMetrics._from_native(native)

    async def stop(self) -> StopResult:
        """Stop once, finalize endpoints/recording, and cache the outcome."""
        async with self._stop_lock:
            if self._stop_result is None:
                native = await _native_async(self._native.stop)
                self._stop_result = StopResult._from_native(native)
            return self._stop_result

    async def cancel(self) -> StopResult:
        """Cancel asynchronous work and sidecars, then join and reap once."""
        async with self._stop_lock:
            if self._stop_result is None:
                native = await _native_async(self._native.cancel)
                self._stop_result = StopResult._from_native(native)
            return self._stop_result

    async def aclose(self) -> None:
        await self.stop()

    async def __aenter__(self) -> RunningSession:
        self._require_running()
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.stop()

    def _require_running(self) -> None:
        if self.is_stopped:
            raise PocketStationError("Session has stopped", "session.stopped")

    async def _poll_audio_native(self) -> AudioBatch | None:
        self._require_running()
        return await _native_async(self._native.poll_audio)

    async def _wait_audio_native(self, timeout_ms: int) -> AudioBatch | None:
        self._require_running()
        return await _native_async(lambda: self._native.wait_audio(timeout_ms))

    async def _poll_event_native(self) -> SessionEvent | None:
        self._require_running()
        event = await _native_async(self._native.poll_event)
        return None if event is None else SessionEvent._from_native(event)

    async def _wait_event_native(self, timeout_ms: int) -> SessionEvent | None:
        self._require_running()
        event = await _native_async(lambda: self._native.wait_event(timeout_ms))
        return None if event is None else SessionEvent._from_native(event)


class Session(_GraphSessionDeclarations):
    """Explicit asyncio façade over the canonical Rust Session."""

    def __init__(
        self,
        *,
        recording_root: str | Path | None = None,
        trace: SessionTraceConfiguration | None = None,
        sample_rate_hz: int = 48_000,
        channels: int = 1,
    ) -> None:
        root = None if recording_root is None else Path(recording_root)
        self._native = _NativeSession(
            recording_root=root,
            trace_path=None if trace is None else trace.path,
            trace_capacity_records=256 if trace is None else trace.capacity_records,
            sample_rate_hz=sample_rate_hz,
            channels=channels,
        )
        self._sample_rate_hz = sample_rate_hz
        self._channels = channels

    @classmethod
    def _from_native(cls, native: _NativeSession) -> Session:
        """Construct an internal façade around a canonical conformance Session."""
        session = cls.__new__(cls)
        session._native = native
        session._sample_rate_hz = 48_000
        session._channels = 1
        return session

    @property
    def id(self) -> int:
        return self._native.id

    def capture(self, source: Source) -> Stem:
        """Declare one independent source-aware stem."""
        return _native_call(lambda: Stem(self._native.capture(source._native)))

    def audio_input(
        self,
        name: str,
        *,
        sample_rate_hz: int | None = None,
        channels: int | None = None,
        capacity_frames: int = 8,
        frame_samples_per_channel: int = 480,
    ) -> AudioInput:
        config = AudioInputConfig(
            name=name,
            sample_rate_hz=(
                self._sample_rate_hz if sample_rate_hz is None else sample_rate_hz
            ),
            channels=self._channels if channels is None else channels,
            capacity_frames=capacity_frames,
            frame_samples_per_channel=frame_samples_per_channel,
        )
        native = _native_call(
            lambda: self._native.audio_input(
                config.sample_rate_hz,
                config.channels,
                config.capacity_frames,
                config.frame_samples_per_channel,
            )
        )
        return AudioInput(SyncPcmSource(native, config))

    def pcm_source(self, config: AudioInputConfig) -> PcmSource:
        native = _native_call(
            lambda: self._native.pcm_source(
                config.sample_rate_hz,
                config.channels,
                config.capacity_frames,
                config.frame_samples_per_channel,
            )
        )
        return PcmSource(SyncPcmSource(native, config))

    def polled_audio(self) -> Endpoint:
        """Declare the bounded managed-language polling endpoint."""
        return _native_call(lambda: Endpoint(self._native.polled_audio()))

    def register_connector(
        self, connector: Connector | SyncConnector
    ) -> RegisteredConnector:
        """Register an asyncio or synchronous in-process Connector."""
        bound = (
            connector._bind(asyncio.get_running_loop())
            if isinstance(connector, Connector)
            else connector
        )
        maximum_batch_items = bound.maximum_batch_items
        if maximum_batch_items is None:
            native = _native_call(
                lambda: self._native.register_connector(
                    bound.manifest._native, bound._native_factory
                )
            )
        else:
            native = _native_call(
                lambda: self._native.register_connector_worker(
                    bound.manifest._native,
                    bound._native_factory,
                    maximum_batch_items,
                )
            )
        return RegisteredConnector(SyncRegisteredConnector(self, bound, native))

    def register_source(
        self, source: SourceProvider | SyncSourceProvider
    ) -> RegisteredSource:
        """Register an asyncio or synchronous typed Source implementation."""
        bound = (
            source._bind(asyncio.get_running_loop())
            if isinstance(source, SourceProvider)
            else source
        )
        native = _native_call(
            lambda: self._native.register_source_provider(
                bound.manifest._native,
                _NativeSourceFactoryAdapter(bound.factory),
            )
        )
        return RegisteredSource(self, bound, native)

    def register_operator(
        self, operator: OperatorProvider | SyncOperatorProvider
    ) -> RegisteredOperator:
        """Register an asyncio or synchronous off-realtime Operator."""
        bound = (
            operator._bind(asyncio.get_running_loop())
            if isinstance(operator, OperatorProvider)
            else operator
        )
        _native_call(
            lambda: self._native.register_operator_provider(
                bound.manifest._native,
                _NativeOperatorFactoryAdapter(bound.factory),
            )
        )
        return RegisteredOperator(self, bound)

    def register_sidecar(self, spec: SidecarProcessSpec) -> SidecarHandle:
        """Register a bounded PKSS child to spawn during transactional start."""
        sidecar_id = _native_call(
            lambda: self._native.register_sidecar(spec._to_native())
        )
        return SidecarHandle(id=sidecar_id, session_id=self._native.id)

    def load_native_extension_library(
        self,
        path: str | Path,
    ) -> NativeExtensionLibrary:
        """Load trusted native code into this Session draft.

        This accepts a raw dynamic library. PocketStation validates its ABI
        records and imports registrations transactionally, but does not verify
        a publisher, signature, checksum, or sandbox the loaded code. Callers
        must establish trust in the exact library and its ABI implementation.
        """
        native = _native_call(
            lambda: self._native.load_native_extension_library(Path(path))
        )
        return NativeExtensionLibrary._from_native(native)

    def relay(self, remote: RelaySession) -> RelayPublisher:
        """Declare the existing bounded Rust relay connector."""
        return remote.publisher(self)

    async def start(self) -> RunningSession:
        """Start transactionally and propagate asyncio cancellation to Rust."""
        cancellation = _SessionStartCancellation()
        start_task = asyncio.create_task(
            asyncio.to_thread(self._native.start, cancellation)
        )
        try:
            native = await asyncio.shield(start_task)
        except asyncio.CancelledError:
            cancellation.request()
            cleanup = asyncio.create_task(_settle_cancelled_start(start_task))
            _BACKGROUND_TASKS.add(cleanup)
            cleanup.add_done_callback(_BACKGROUND_TASKS.discard)
            raise
        except (RuntimeError, ValueError) as error:
            raise _normalize_native_error(error) from error
        return RunningSession(native)


async def _settle_cancelled_start(
    start_task: asyncio.Task[_NativeRunningSession],
) -> None:
    try:
        native = await start_task
    except Exception:
        return
    await asyncio.to_thread(native.stop)


async def _native_async(operation: Callable[[], _Result]) -> _Result:
    native_task = asyncio.create_task(asyncio.to_thread(operation))
    try:
        return await asyncio.shield(native_task)
    except asyncio.CancelledError:
        try:
            await native_task
        except Exception:
            pass
        raise
    except (RuntimeError, ValueError) as error:
        raise _normalize_native_error(error) from error


__all__ = ["Connector", "RegisteredConnector", "RunningSession", "Session"]
