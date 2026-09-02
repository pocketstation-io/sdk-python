"""Build and operate a native PocketStation Session synchronously."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, TypeVar, cast

from ._native import (
    AudioBatch,
    AudioFrame,
)
from ._native import (
    RunningSession as _NativeRunningSession,
)
from ._native import (
    Session as _NativeSession,
)
from ._native import _RegisteredConnector as _NativeRegisteredConnector
from ._native import _RegisteredEndpoint as _NativeRegisteredEndpoint
from .audio_input import AudioInput, AudioInputConfig, PcmSource
from .connector import (
    Connector,
    ConnectorConfigurationInput,
    RegisteredConnector,
)
from .endpoint_authoring import EndpointProvider, RegisteredEndpoint
from .errors import PocketStationError, _native_call
from .extensions import NativeExtensionLibrary
from .graph import (
    EdgeContract,
    Endpoint,
    RouteSettings,
    Stem,
    _GraphSessionDeclarations,
)
from .identity import RuntimeSessionId
from .observations import (
    EventStream,
    RecordingOutcome,
    RecordingStemOutcome,
    RouteMetrics,
    SessionEvent,
    SessionLifecycleState,
    SessionMetrics,
    SessionTraceConfiguration,
    StopResult,
)
from .operator_authoring import (
    OperatorProvider,
    RegisteredOperator,
)
from .operator_authoring import (
    _NativeFactoryAdapter as _NativeOperatorFactoryAdapter,
)
from .sidecar import SidecarConnection, SidecarHandle, SidecarProcessSpec
from .signal import BusSubscription
from .source_authoring import RegisteredSource, SourceProvider, _NativeFactoryAdapter
from .sources import Source
from .streams import AudioStream, SignalStream

if TYPE_CHECKING:
    from .relay import RelayPublisher, RelaySession

_PayloadT = TypeVar("_PayloadT")


class RunningSession:
    """Running native Session with bounded synchronous batch delivery."""

    def __init__(self, native: _NativeRunningSession) -> None:
        self._native = native
        self._stop_result: StopResult | None = None
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
        self._signals: dict[int, SignalStream[object]] = {}
        self._sidecars: dict[int, SidecarConnection] = {}

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def is_stopped(self) -> bool:
        return self.state in {
            SessionLifecycleState.STOPPED,
            SessionLifecycleState.FAILED,
        }

    @property
    def state(self) -> SessionLifecycleState:
        """Return the native binding owner's authoritative lifecycle state."""
        return SessionLifecycleState(self._native.lifecycle_state)

    @property
    def stop_result(self) -> StopResult | None:
        return self._stop_result

    @property
    def audio(self) -> AudioStream:
        """The exclusive frame-first view of the native bounded endpoint."""
        return self._audio

    @property
    def events(self) -> EventStream:
        """The exclusive typed lifecycle and failure event stream."""
        return self._events

    def signals(
        self, subscription: BusSubscription[_PayloadT]
    ) -> SignalStream[_PayloadT]:
        """Return the one exclusive stream for a declared subscription."""
        stream = self._signals.get(subscription.id)
        if stream is None:
            native = subscription._native
            stream = SignalStream(
                poll_signal=lambda: _native_call(
                    lambda: self._native.poll_signal(native)
                ),
                wait_signal=lambda timeout_ms: _native_call(
                    lambda: self._native.wait_signal(native, timeout_ms)
                ),
                close_signal=lambda: _native_call(
                    lambda: self._native.close_signal(native)
                ),
                signal_metrics=lambda: _native_call(
                    lambda: self._native.signal_metrics(native)
                ),
            )
            self._signals[subscription.id] = stream
        return cast(SignalStream[_PayloadT], stream)

    def sidecar(self, handle: SidecarHandle) -> SidecarConnection:
        """Return the Session-owned bounded connection for one child."""
        self._require_running()
        if handle.session_id != self._native.session_id:
            raise ValueError("SidecarHandle belongs to a different Session")
        connection = self._sidecars.get(handle.id)
        if connection is None:
            connection = SidecarConnection(
                handle=handle,
                send_message=lambda message: _native_call(
                    lambda: self._native.send_sidecar(handle.id, message)
                ),
                poll_message=lambda: _native_call(
                    lambda: self._native.poll_sidecar(handle.id)
                ),
                wait_message=lambda timeout_ms: _native_call(
                    lambda: self._native.wait_sidecar(handle.id, timeout_ms)
                ),
                snapshot=lambda: _native_call(
                    lambda: self._native.sidecar_snapshot(handle.id)
                ),
                is_session_stopped=lambda: self.is_stopped,
            )
            self._sidecars[handle.id] = connection
        return connection

    def poll_audio(self) -> AudioBatch | None:
        """Compatibility alias for the advanced non-blocking batch mode."""
        self._require_running()
        return self.audio.poll_batch()

    def wait_audio(self, *, timeout_ms: int = 100) -> AudioBatch | None:
        """Compatibility alias for the advanced bounded batch mode."""
        self._require_running()
        if not 0 <= timeout_ms <= 1_000:
            raise ValueError("timeout_ms must be between 0 and 1000")
        return self.audio.read_batch(timeout_s=timeout_ms / 1_000)

    def audio_batches(self, *, wait_timeout_ms: int = 100) -> Iterator[AudioBatch]:
        """Compatibility alias for ``audio.batches()``."""
        self._require_running()
        if not 0 <= wait_timeout_ms <= 1_000:
            raise ValueError("wait_timeout_ms must be between 0 and 1000")
        return self.audio.batches(wait_timeout_s=wait_timeout_ms / 1_000)

    def poll_event(self) -> SessionEvent | None:
        """Compatibility alias for ``events.poll()``."""
        self._require_running()
        return self.events.poll()

    def wait_event(self, *, timeout_ms: int = 100) -> SessionEvent | None:
        """Compatibility alias for the bounded ``events.read()`` mode."""
        self._require_running()
        if not 0 <= timeout_ms <= 1_000:
            raise ValueError("timeout_ms must be between 0 and 1000")
        return self.events.read(timeout_s=timeout_ms / 1_000)

    def metrics(self) -> SessionMetrics:
        """Return a complete immutable point-in-time metrics snapshot."""
        self._require_running()
        return SessionMetrics._from_native(_native_call(self._native.metrics))

    def stop(self) -> StopResult:
        """Stop once, finalize endpoints/recording, and cache the outcome."""
        if self._stop_result is None:
            self._stop_result = StopResult._from_native(_native_call(self._native.stop))
        return self._stop_result

    def cancel(self) -> StopResult:
        """Cancel asynchronous work and sidecars, then join and reap once."""
        if self._stop_result is None:
            self._stop_result = StopResult._from_native(
                _native_call(self._native.cancel)
            )
        return self._stop_result

    def close(self) -> None:
        """Context-manager compatible alias that deterministically stops."""
        self.stop()

    def __enter__(self) -> RunningSession:
        self._require_running()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.stop()

    def _require_running(self) -> None:
        if self.is_stopped:
            raise PocketStationError("Session has stopped", "session.stopped")

    def _poll_audio_native(self) -> AudioBatch | None:
        self._require_running()
        return _native_call(self._native.poll_audio)

    def _wait_audio_native(self, timeout_ms: int) -> AudioBatch | None:
        self._require_running()
        return _native_call(lambda: self._native.wait_audio(timeout_ms))

    def _poll_event_native(self) -> SessionEvent | None:
        self._require_running()
        event = _native_call(self._native.poll_event)
        return None if event is None else SessionEvent._from_native(event)

    def _wait_event_native(self, timeout_ms: int) -> SessionEvent | None:
        self._require_running()
        event = _native_call(lambda: self._native.wait_event(timeout_ms))
        return None if event is None else SessionEvent._from_native(event)


class Session(_GraphSessionDeclarations):
    """Build and operate one Rust Session from synchronous Python code."""

    def __init__(
        self,
        *,
        recording_root: str | Path | None = None,
        trace: SessionTraceConfiguration | None = None,
        sample_rate_hz: int = 48_000,
        channels: int = 1,
        frame_duration_ms: int = 20,
    ) -> None:
        root = None if recording_root is None else Path(recording_root)
        self._native = _native_call(
            lambda: _NativeSession(
                recording_root=root,
                trace_path=None if trace is None else trace.path,
                trace_capacity_records=256 if trace is None else trace.capacity_records,
                sample_rate_hz=sample_rate_hz,
                channels=channels,
                frame_duration_ms=frame_duration_ms,
            )
        )
        self._sample_rate_hz = sample_rate_hz
        self._channels = channels
        self._frame_duration_ms = frame_duration_ms
        self._connector_registrations: dict[
            int, tuple[Connector, Connector, _NativeRegisteredConnector]
        ] = {}
        self._endpoint_registrations: dict[
            int, tuple[EndpointProvider, _NativeRegisteredEndpoint]
        ] = {}

    @classmethod
    def _from_native(cls, native: _NativeSession) -> Session:
        """Construct an internal façade around a conformance Session."""
        session = cls.__new__(cls)
        session._native = native
        session._sample_rate_hz = 48_000
        session._channels = 1
        session._frame_duration_ms = 20
        session._connector_registrations = {}
        session._endpoint_registrations = {}
        return session

    @property
    def id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.id)

    def capture(self, source: Source) -> Stem:
        """Declare one independent source-aware stem."""
        return _native_call(
            lambda: Stem(
                self._native.capture(source._native),
                self._destination_for_stream,
            )
        )

    def audio_input(
        self,
        name: str,
        *,
        sample_rate_hz: int | None = None,
        channels: int | None = None,
        capacity_frames: int = 8,
        frame_samples_per_channel: int = 480,
    ) -> AudioInput:
        """Open bounded input for PCM already owned by this application."""
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
        return AudioInput(native, config, self._destination_for_stream)

    def pcm_source(self, config: AudioInputConfig) -> PcmSource:
        """Open the advanced explicit source-output and writer ownership API."""
        native = _native_call(
            lambda: self._native.pcm_source(
                config.sample_rate_hz,
                config.channels,
                config.capacity_frames,
                config.frame_samples_per_channel,
            )
        )
        return PcmSource(native, config, self._destination_for_stream)

    def polled_audio(self) -> Endpoint:
        """Declare the bounded managed-language polling endpoint."""
        return _native_call(lambda: Endpoint(self._native.polled_audio()))

    def register_connector(self, connector: Connector) -> RegisteredConnector:
        """Register one in-process Python Connector implementation."""
        identity = id(connector)
        cached = self._connector_registrations.get(identity)
        if cached is not None and cached[0] is connector:
            return RegisteredConnector(self, cached[1], cached[2])
        definition = connector._definition()
        maximum_batch_items = definition.maximum_batch_items
        if maximum_batch_items is None:
            native = _native_call(
                lambda: self._native.register_connector(
                    definition.manifest._native, definition._native_factory
                )
            )
        else:
            native = _native_call(
                lambda: self._native.register_connector_worker(
                    definition.manifest._native,
                    definition._native_factory,
                    maximum_batch_items,
                )
            )
        self._connector_registrations[identity] = (connector, definition, native)
        return RegisteredConnector(self, definition, native)

    def destination(
        self,
        connector: Connector,
        configuration: ConnectorConfigurationInput = (),
        *,
        route_settings: RouteSettings | None = None,
        edge: EdgeContract | None = None,
    ) -> Endpoint:
        """Declare one Connector destination using an idempotent registration.

        Use this form for the common one-destination case.
        :meth:`register_connector` remains available when one implementation
        must declare several independently configured Endpoints.
        """
        return self.register_connector(connector).declare(
            configuration,
            route_settings=route_settings,
            edge=edge,
        )

    def register_endpoint(self, endpoint: EndpointProvider) -> RegisteredEndpoint:
        """Register one advanced Python implementation of Core's Endpoint SPI.

        Most outbound integrations should use :meth:`destination` with a
        :class:`Connector`. This lower-level API exists for Endpoint behavior
        that is not a provider transport specialization.
        """
        identity = id(endpoint)
        cached = self._endpoint_registrations.get(identity)
        if cached is not None and cached[0] is endpoint:
            return RegisteredEndpoint(self, endpoint, cached[1])
        native = _native_call(
            lambda: self._native.register_endpoint_provider(
                endpoint.manifest._native, endpoint._native_factory
            )
        )
        self._endpoint_registrations[identity] = (endpoint, native)
        return RegisteredEndpoint(self, endpoint, native)

    def register_source(self, source: SourceProvider) -> RegisteredSource:
        """Register one Python-authored typed Source implementation."""
        native = _native_call(
            lambda: self._native.register_source_provider(
                source.manifest._native,
                _NativeFactoryAdapter(source.factory),
            )
        )
        return RegisteredSource(self, source, native)

    def register_operator(self, operator: OperatorProvider) -> RegisteredOperator:
        """Register one Python-authored off-realtime Operator."""
        _native_call(
            lambda: self._native.register_operator_provider(
                operator.manifest._native,
                _NativeOperatorFactoryAdapter(operator.factory),
            )
        )
        return RegisteredOperator(self, operator)

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

    def start(self) -> RunningSession:
        """Transactionally start the frozen native Session declaration."""
        return _native_call(lambda: RunningSession(self._native.start()))


__all__ = [
    "AudioBatch",
    "AudioFrame",
    "AudioInput",
    "AudioInputConfig",
    "Connector",
    "Endpoint",
    "OperatorProvider",
    "RecordingOutcome",
    "RecordingStemOutcome",
    "RegisteredConnector",
    "RegisteredOperator",
    "RegisteredSource",
    "RouteMetrics",
    "RunningSession",
    "Session",
    "SessionEvent",
    "SessionMetrics",
    "SidecarConnection",
    "SidecarHandle",
    "SidecarProcessSpec",
    "SignalStream",
    "Source",
    "SourceProvider",
    "Stem",
    "StopResult",
]
