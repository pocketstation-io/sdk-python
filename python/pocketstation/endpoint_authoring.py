"""Advanced Python projection of Core's generic Endpoint lifecycle."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, TypeAlias, runtime_checkable

from ._native import (
    AudioFrame,
)
from ._native import (
    EndpointItem as _NativeEndpointItem,
)
from ._native import (
    EndpointPortInput as _NativeEndpointPortInput,
)
from ._native import (
    EndpointPrepareContext as _NativeEndpointPrepareContext,
)
from ._native import (
    EndpointReceiver as _NativeEndpointReceiver,
)
from ._native import (
    EndpointStartGate as _NativeEndpointStartGate,
)
from ._native import (
    Session as _NativeSession,
)
from ._native import (
    _EndpointManifest as _NativeEndpointManifest,
)
from ._native import (
    _RegisteredEndpoint as _NativeRegisteredEndpoint,
)
from .errors import PocketStationError, _native_call
from .graph import EdgeContract, Endpoint, MediaCaps, PortSpec, SignalSpec
from .observations import EndpointFailureRetryability, EndpointFailureStage
from .signal import SignalEnvelope

EndpointConfigurationInput: TypeAlias = Mapping[str, str] | Iterable[tuple[str, str]]


class EndpointShutdownMode(StrEnum):
    DRAIN = "drain"
    ABORT = "abort"


class EndpointDriverError(PocketStationError):
    """Structured failure raised by a Python-authored generic Endpoint."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "python.endpoint_failure",
        stage: EndpointFailureStage = EndpointFailureStage.PREPARE,
        retryability: EndpointFailureRetryability = EndpointFailureRetryability.NEVER,
    ) -> None:
        super().__init__(message, code)
        self.message = message
        self.stage = stage
        self.retryability = retryability


@dataclass(frozen=True, slots=True)
class EndpointDriverObservations:
    frames_received_total: int = 0
    frames_delivered_total: int = 0
    frames_dropped_total: int = 0
    discontinuities_total: int = 0
    failures_total: int = 0

    def __post_init__(self) -> None:
        if (
            min(
                self.frames_received_total,
                self.frames_delivered_total,
                self.frames_dropped_total,
                self.discontinuities_total,
                self.failures_total,
            )
            < 0
        ):
            raise ValueError("Endpoint observation counters cannot be negative")


@dataclass(frozen=True, slots=True)
class EndpointManifest:
    """Compiler-visible identity and input ports for one generic Endpoint."""

    operator_id: str
    inputs: tuple[PortSpec, ...]
    node_type_id: str | None = None
    _native: _NativeEndpointManifest = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativeEndpointManifest(
                self.operator_id,
                self.node_type_id or self.operator_id,
                [port._native for port in self.inputs],
            )
        )
        object.__setattr__(self, "_native", native)

    @classmethod
    def audio(
        cls,
        operator_id: str,
        *,
        port_name: str = "audio",
        node_type_id: str | None = None,
    ) -> EndpointManifest:
        from .graph import MediaCaps, Multiplicity, SignalSpec

        return cls(
            operator_id=operator_id,
            node_type_id=node_type_id,
            inputs=(
                PortSpec.input(
                    port_name,
                    SignalSpec.audio(),
                    media=MediaCaps.audio(),
                    multiplicity=Multiplicity.MANY,
                ),
            ),
        )


class EndpointStartGate:
    """Read-only Core start barrier supplied to a prepared Endpoint."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpointStartGate) -> None:
        self._native = native

    @property
    def is_open(self) -> bool:
        return self._native.is_open


class EndpointPrepareContext:
    """Session-owned route identity and configuration for one Endpoint input."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpointPrepareContext) -> None:
        self._native = native

    @property
    def session_id(self) -> int:
        return self._native.session_id

    @property
    def endpoint_id(self) -> int:
        return self._native.endpoint_id

    @property
    def connector_id(self) -> int | None:
        return self._native.connector_id

    @property
    def route_id(self) -> int:
        return self._native.route_id

    @property
    def origin_kind(self) -> str:
        return self._native.origin_kind

    @property
    def source_id(self) -> int | None:
        return self._native.source_id

    @property
    def stream_id(self) -> int | None:
        return self._native.stream_id

    @property
    def stem_id(self) -> int | None:
        return self._native.stem_id

    @property
    def session_timeline_origin_ns(self) -> int:
        return self._native.session_timeline_origin_ns

    @property
    def configuration(self) -> Mapping[str, str]:
        return self._native.configuration


class EndpointItem:
    """One owned audio frame or typed signal read from a bounded Core edge."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpointItem) -> None:
        self._native = native

    @property
    def kind(self) -> str:
        return self._native.kind

    @property
    def audio(self) -> AudioFrame | None:
        return self._native.audio

    @property
    def signal(self) -> SignalEnvelope[object] | None:
        value = self._native.signal
        return None if value is None else SignalEnvelope._from_native(value)


class EndpointReceiver:
    """Exclusive bounded input receiver; consume only from an off-realtime worker."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpointReceiver) -> None:
        self._native = native

    def try_recv(self) -> EndpointItem | None:
        value = _native_call(self._native.try_recv)
        return None if value is None else EndpointItem(value)

    @property
    def is_abandoned(self) -> bool:
        return _native_call(self._native.is_abandoned)

    def mark_discontinuity(self) -> None:
        _native_call(self._native.mark_discontinuity)

    def mark_worker_failure(self) -> None:
        _native_call(self._native.mark_worker_failure)


class EndpointPortInput:
    """One compiled input port, receiver, route identity, and edge contract."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpointPortInput) -> None:
        self._native = native

    @property
    def port_name(self) -> str:
        return self._native.port_name

    @property
    def signal(self) -> SignalSpec[object]:
        return SignalSpec._from_native(self._native.signal)

    @property
    def media(self) -> MediaCaps:
        return MediaCaps._from_native(self._native.media)

    @property
    def edge(self) -> EdgeContract:
        return EdgeContract(self._native.edge)

    @property
    def context(self) -> EndpointPrepareContext:
        return EndpointPrepareContext(self._native.context)

    @property
    def receiver(self) -> EndpointReceiver:
        return EndpointReceiver(self._native.receiver)


class PreparedEndpointDriver:
    """Prepared resources held behind Core's closed start gate."""

    def start(self, gate: EndpointStartGate) -> RunningEndpointDriver:
        raise NotImplementedError

    def cancel_preparation(self) -> None:
        """Release prepared resources during transactional rollback."""


class RunningEndpointDriver:
    """Active generic Endpoint resources owned until joined finalization."""

    def observations(self) -> EndpointDriverObservations:
        return EndpointDriverObservations()

    def request_shutdown(self, mode: EndpointShutdownMode) -> None:
        """Request finite drain or immediate abort."""

    def join_and_finalize(self) -> EndpointDriverObservations:
        return self.observations()


@runtime_checkable
class EndpointDriverFactory(Protocol):
    def prepare(
        self, inputs: Sequence[EndpointPortInput]
    ) -> PreparedEndpointDriver: ...


EndpointDriverBuilder: TypeAlias = Callable[
    [Sequence[EndpointPortInput]], PreparedEndpointDriver
]
EndpointConfigurationValidator: TypeAlias = Callable[[Mapping[str, str]], None]
EndpointPreparationGroup: TypeAlias = Callable[[int, Mapping[str, str]], str | None]


class _PreparedAdapter:
    __slots__ = ("_prepared",)

    def __init__(self, prepared: PreparedEndpointDriver) -> None:
        self._prepared = prepared

    def start(self, gate: _NativeEndpointStartGate) -> _RunningAdapter:
        return _RunningAdapter(self._prepared.start(EndpointStartGate(gate)))

    def cancel_preparation(self) -> None:
        self._prepared.cancel_preparation()


class _RunningAdapter:
    __slots__ = ("_running",)

    def __init__(self, running: RunningEndpointDriver) -> None:
        self._running = running

    def observations(self) -> EndpointDriverObservations:
        return self._running.observations()

    def request_shutdown(self, mode: str) -> None:
        self._running.request_shutdown(EndpointShutdownMode(mode))

    def join_and_finalize(self) -> EndpointDriverObservations:
        return self._running.join_and_finalize()


class _FactoryAdapter:
    __slots__ = ("_factory", "_group", "_validator")

    def __init__(
        self,
        factory: EndpointDriverFactory | EndpointDriverBuilder,
        validator: EndpointConfigurationValidator | None,
        group: EndpointPreparationGroup | None,
    ) -> None:
        self._factory = factory
        self._validator = validator
        self._group = group

    def validate_configuration(self, configuration: Mapping[str, str]) -> None:
        if self._validator is not None:
            self._validator(configuration)

    def preparation_group(
        self, route_id: int, configuration: Mapping[str, str]
    ) -> str | None:
        if self._group is None:
            return None
        return self._group(route_id, configuration)

    def prepare(
        self, native_inputs: Sequence[_NativeEndpointPortInput]
    ) -> _PreparedAdapter:
        inputs = tuple(EndpointPortInput(value) for value in native_inputs)
        prepare = getattr(self._factory, "prepare", None)
        prepared = (
            self._factory(inputs)  # type: ignore[operator]
            if prepare is None
            else prepare(inputs)
        )
        return _PreparedAdapter(prepared)


@dataclass(frozen=True, slots=True)
class EndpointProvider:
    """Reusable low-level Endpoint implementation registered into one Session."""

    manifest: EndpointManifest
    factory: EndpointDriverFactory | EndpointDriverBuilder
    validate_configuration: EndpointConfigurationValidator | None = field(
        default=None, repr=False, compare=False
    )
    preparation_group: EndpointPreparationGroup | None = field(
        default=None, repr=False, compare=False
    )
    _native_factory: _FactoryAdapter = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_native_factory",
            _FactoryAdapter(
                self.factory,
                self.validate_configuration,
                self.preparation_group,
            ),
        )


class RegisteredEndpoint:
    """One generic Endpoint implementation bound to a Session draft."""

    __slots__ = ("_native", "_provider", "_session")

    def __init__(
        self,
        session: _SessionDraft,
        provider: EndpointProvider,
        native: _NativeRegisteredEndpoint,
    ) -> None:
        self._session = session
        self._provider = provider
        self._native = native

    @property
    def session_id(self) -> int:
        return self._native.session_id

    def declare(
        self,
        configuration: EndpointConfigurationInput = (),
        *,
        edge: EdgeContract | None = None,
    ) -> Endpoint:
        values = _configuration(configuration)
        selected_edge = edge or _default_edge(self._provider.manifest)
        native = _native_call(
            lambda: self._session._native.declare_registered_endpoint(
                self._native, values, selected_edge._native
            )
        )
        return Endpoint(native)


class _SessionDraft(Protocol):
    _native: _NativeSession


def _configuration(values: EndpointConfigurationInput) -> dict[str, str]:
    entries = tuple(values.items() if isinstance(values, Mapping) else values)
    result: dict[str, str] = {}
    for key, value in entries:
        if not key or key.strip() != key:
            raise ValueError("Endpoint configuration keys must be non-empty and exact")
        if key in result:
            raise ValueError(f"duplicate Endpoint configuration key {key!r}")
        result[key] = value
    return result


def _default_edge(manifest: EndpointManifest) -> EdgeContract:
    if len(manifest.inputs) == 1 and manifest.inputs[0].signal.is_audio:
        return EdgeContract.realtime_audio()
    return EdgeContract.bounded_async()


__all__ = [
    "EndpointConfigurationInput",
    "EndpointDriverBuilder",
    "EndpointDriverError",
    "EndpointDriverFactory",
    "EndpointDriverObservations",
    "EndpointItem",
    "EndpointManifest",
    "EndpointPortInput",
    "EndpointPreparationGroup",
    "EndpointPrepareContext",
    "EndpointProvider",
    "EndpointReceiver",
    "EndpointShutdownMode",
    "EndpointStartGate",
    "PreparedEndpointDriver",
    "RegisteredEndpoint",
    "RunningEndpointDriver",
]
