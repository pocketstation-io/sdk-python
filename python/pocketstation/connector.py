"""Author in-process Python Connectors on the Core worker lifecycle."""

from __future__ import annotations

import hashlib
import importlib.metadata
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, TypeAlias, cast, runtime_checkable

from ._native import AudioFrame
from ._native import ConnectorContext as _NativeConnectorContext
from ._native import ConnectorInputDescriptor as _NativeConnectorInputDescriptor
from ._native import ConnectorItem as _NativeConnectorItem
from ._native import Session as _NativeSession
from ._native import _ConnectorConfiguration as _NativeConnectorConfiguration
from ._native import (
    _ConnectorConfigurationConstraint as _NativeConnectorConfigurationConstraint,
)
from ._native import _ConnectorConfigurationField as _NativeConnectorConfigurationField
from ._native import (
    _ConnectorConfigurationSchema as _NativeConnectorConfigurationSchema,
)
from ._native import _ConnectorConfigurationValue as _NativeConnectorConfigurationValue
from ._native import _ConnectorManifest as _NativeConnectorManifest
from ._native import _ConnectorObservations as _NativeConnectorObservations
from ._native import (
    _ConnectorRuntimeObservations as _NativeConnectorRuntimeObservations,
)
from ._native import _RegisteredConnector as _NativeRegisteredConnector
from .errors import PocketStationError, _native_call
from .graph import (
    EdgeContract,
    Endpoint,
    MediaCaps,
    Multiplicity,
    PortDirection,
    PortSpec,
    SignalSpec,
)
from .signal import SignalEnvelope


class _SessionOwner(Protocol):
    _native: _NativeSession


class ConnectorConfigurationValueKind(StrEnum):
    TEXT = "text"
    BOOLEAN = "boolean"
    SIGNED_INTEGER = "signed-integer"
    UNSIGNED_INTEGER = "unsigned-integer"
    DURATION_MILLISECONDS = "duration-milliseconds"
    BYTE_COUNT = "byte-count"
    SECRET = "secret"


class ConnectorConfigurationRequirement(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEFAULT = "default"


class ConnectorErrorStage(StrEnum):
    CONFIGURATION = "configuration"
    PREPARE = "prepare"
    STARTUP = "startup"
    READINESS = "readiness"
    DELIVERY = "delivery"
    RETRY = "retry"
    SHUTDOWN = "shutdown"
    JOIN = "join"


class ConnectorRetryability(StrEnum):
    NEVER = "never"
    RETRYABLE = "retryable"
    RETRY_AFTER_RECONFIGURATION = "retry-after-reconfiguration"


class ConnectorDeliveryOutcome(StrEnum):
    DELIVERED = "delivered"
    DROPPED = "dropped"


class ConnectorShutdownMode(StrEnum):
    DRAIN = "drain"
    ABORT = "abort"


class ConnectorDeliveryReadiness(StrEnum):
    NOT_READY = "not-ready"
    READY = "ready"


class ConnectorHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class ConnectorRecovery(StrEnum):
    IDLE = "idle"
    RECONNECTING = "reconnecting"


class ConnectorError(PocketStationError):
    """Structured provider failure preserved through Core finalization."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        stage: ConnectorErrorStage,
        retryability: ConnectorRetryability = ConnectorRetryability.NEVER,
    ) -> None:
        super().__init__(message, code)
        self.message = message
        self.stage = stage
        self.retryability = retryability


@dataclass(frozen=True, slots=True)
class ConnectorErrorSnapshot:
    """One structured provider failure retained by Core observations."""

    code: str
    stage: ConnectorErrorStage
    retryability: ConnectorRetryability
    message: str


@dataclass(frozen=True, slots=True)
class ConnectorServiceStatus:
    """Orthogonal delivery, health, and recovery state from Core."""

    delivery_readiness: ConnectorDeliveryReadiness
    health: ConnectorHealth
    recovery: ConnectorRecovery
    readiness_reason_code: str | None
    health_reason_code: str | None
    recovery_reason_code: str | None
    revision: int
    last_transition_elapsed_ns: int
    accepts_delivery: bool


@dataclass(frozen=True, slots=True)
class ConnectorObservations:
    """Immutable provider-service observations for one Connector worker."""

    service_status: ConnectorServiceStatus
    status_transitions_total: int
    retry_attempts_total: int
    reconnects_total: int
    failures_total: int
    last_error: ConnectorErrorSnapshot | None

    @classmethod
    def _from_native(cls, value: _NativeConnectorObservations) -> ConnectorObservations:
        status = value.service_status
        error = value.last_error
        return cls(
            service_status=ConnectorServiceStatus(
                delivery_readiness=ConnectorDeliveryReadiness(
                    status.delivery_readiness
                ),
                health=ConnectorHealth(status.health),
                recovery=ConnectorRecovery(status.recovery),
                readiness_reason_code=status.readiness_reason_code,
                health_reason_code=status.health_reason_code,
                recovery_reason_code=status.recovery_reason_code,
                revision=status.revision,
                last_transition_elapsed_ns=status.last_transition_elapsed_ns,
                accepts_delivery=status.accepts_delivery,
            ),
            status_transitions_total=value.status_transitions_total,
            retry_attempts_total=value.retry_attempts_total,
            reconnects_total=value.reconnects_total,
            failures_total=value.failures_total,
            last_error=(
                None
                if error is None
                else ConnectorErrorSnapshot(
                    code=error.code,
                    stage=ConnectorErrorStage(error.stage),
                    retryability=ConnectorRetryability(error.retryability),
                    message=error.message,
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class ConnectorRuntimeObservations:
    """Connector and Endpoint counters for one prepared worker group."""

    endpoint_ids: tuple[int, ...]
    connector: ConnectorObservations
    frames_received_total: int
    frames_delivered_total: int
    frames_dropped_total: int
    discontinuities_total: int
    endpoint_failures_total: int

    @classmethod
    def _from_native(
        cls, value: _NativeConnectorRuntimeObservations
    ) -> ConnectorRuntimeObservations:
        return cls(
            endpoint_ids=tuple(value.endpoint_ids),
            connector=ConnectorObservations._from_native(value.connector),
            frames_received_total=value.frames_received_total,
            frames_delivered_total=value.frames_delivered_total,
            frames_dropped_total=value.frames_dropped_total,
            discontinuities_total=value.discontinuities_total,
            endpoint_failures_total=value.endpoint_failures_total,
        )


class ConnectorConfigurationValue:
    """One exact typed configuration value owned and validated by Core."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeConnectorConfigurationValue) -> None:
        self._native = native

    @classmethod
    def text(cls, value: str) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.text(value))

    @classmethod
    def boolean(cls, value: bool) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.boolean(value))

    @classmethod
    def signed_integer(cls, value: int) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.signed_integer(value))

    @classmethod
    def unsigned_integer(cls, value: int) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.unsigned_integer(value))

    @classmethod
    def duration_milliseconds(cls, value: int) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.duration_milliseconds(value))

    @classmethod
    def byte_count(cls, value: int) -> ConnectorConfigurationValue:
        return cls(_NativeConnectorConfigurationValue.byte_count(value))

    @classmethod
    def secret(cls, value: str) -> ConnectorConfigurationValue:
        native = _native_call(lambda: _NativeConnectorConfigurationValue.secret(value))
        return cls(native)

    @property
    def kind(self) -> ConnectorConfigurationValueKind:
        return ConnectorConfigurationValueKind(self._native.kind)

    def expose_secret(self) -> str:
        """Explicitly reveal a secret to the provider that owns this value."""
        return _native_call(self._native.expose_secret)

    @property
    def value(self) -> str | bool | int:
        """Return a non-secret value; secret access stays explicit."""
        if self.kind is ConnectorConfigurationValueKind.SECRET:
            raise ConnectorError(
                "secret configuration requires expose_secret()",
                code="connector.configuration.secret_access",
                stage=ConnectorErrorStage.CONFIGURATION,
            )
        text = self._native.as_text()
        if text is not None:
            return text
        boolean = self._native.as_boolean()
        if boolean is not None:
            return boolean
        signed = self._native.as_signed_integer()
        if signed is not None:
            return signed
        unsigned = self._native.as_unsigned_integer()
        if unsigned is not None:
            return unsigned
        raise AssertionError("native Connector value has no compatible Python wrapper")

    def __repr__(self) -> str:
        if self.kind is ConnectorConfigurationValueKind.SECRET:
            return "ConnectorConfigurationValue.secret(<redacted>)"
        return f"ConnectorConfigurationValue.{self.kind.value}({self.value!r})"


ConnectorConfigurationInput: TypeAlias = (
    Mapping[str, ConnectorConfigurationValue | str | bool | int]
    | Sequence[tuple[str, ConnectorConfigurationValue | str | bool | int]]
)


class ConnectorConfigurationConstraint:
    """One Core-enforced constraint on a connector configuration field."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeConnectorConfigurationConstraint) -> None:
        self._native = native

    @classmethod
    def non_empty(cls) -> ConnectorConfigurationConstraint:
        return cls(_NativeConnectorConfigurationConstraint.non_empty())

    @classmethod
    def text_length_bytes(
        cls, minimum: int, maximum: int
    ) -> ConnectorConfigurationConstraint:
        return cls(
            _NativeConnectorConfigurationConstraint.text_length_bytes(minimum, maximum)
        )

    @classmethod
    def signed_range(
        cls, minimum: int, maximum: int
    ) -> ConnectorConfigurationConstraint:
        native = _NativeConnectorConfigurationConstraint.signed_range(minimum, maximum)
        return cls(native)

    @classmethod
    def unsigned_range(
        cls, minimum: int, maximum: int
    ) -> ConnectorConfigurationConstraint:
        native = _NativeConnectorConfigurationConstraint.unsigned_range(
            minimum, maximum
        )
        return cls(native)

    @classmethod
    def one_of(cls, values: Sequence[str]) -> ConnectorConfigurationConstraint:
        return cls(_NativeConnectorConfigurationConstraint.one_of(list(values)))


@dataclass(frozen=True, slots=True)
class ConnectorConfigurationField:
    """One documented typed field in a connector's configuration schema."""

    name: str
    kind: ConnectorConfigurationValueKind
    documentation: str
    requirement: ConnectorConfigurationRequirement = (
        ConnectorConfigurationRequirement.REQUIRED
    )
    default: ConnectorConfigurationValue | str | bool | int | None = None
    constraints: tuple[ConnectorConfigurationConstraint, ...] = ()
    deprecation: str | None = None
    _native: _NativeConnectorConfigurationField = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        default = None
        if self.default is not None:
            default = _coerce_configuration_value(self.kind, self.default)._native
        native = _native_call(
            lambda: _NativeConnectorConfigurationField(
                self.name,
                self.kind.value,
                self.requirement.value,
                self.documentation,
                default,
                [constraint._native for constraint in self.constraints],
                self.deprecation,
            )
        )
        object.__setattr__(self, "_native", native)


@dataclass(frozen=True, slots=True)
class ConnectorConfigurationSchema:
    """Finite configuration schema resolved by Core before provider setup."""

    fields: tuple[ConnectorConfigurationField, ...] = ()
    revision: int = 1
    _native: _NativeConnectorConfigurationSchema = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        duplicate = _first_duplicate(entry.name for entry in self.fields)
        if duplicate is not None:
            raise ConnectorError(
                f"duplicate Connector configuration field {duplicate!r}",
                code="connector.configuration.duplicate_field",
                stage=ConnectorErrorStage.CONFIGURATION,
            )
        native = _native_call(
            lambda: _NativeConnectorConfigurationSchema(
                self.revision, [entry._native for entry in self.fields]
            )
        )
        object.__setattr__(self, "_native", native)

    def configuration(
        self, values: ConnectorConfigurationInput = ()
    ) -> _NativeConnectorConfiguration:
        entries = tuple(values.items() if isinstance(values, Mapping) else values)
        duplicate = _first_duplicate(name for name, _value in entries)
        if duplicate is not None:
            raise ConnectorError(
                f"duplicate Connector configuration value {duplicate!r}",
                code="connector.configuration.duplicate_value",
                stage=ConnectorErrorStage.CONFIGURATION,
            )
        by_name = {entry.name: entry for entry in self.fields}
        native_entries: list[tuple[str, _NativeConnectorConfigurationValue]] = []
        for name, value in entries:
            field = by_name.get(name)
            if field is None:
                raise ConnectorError(
                    f"unknown Connector configuration field {name!r}",
                    code="connector.configuration.unknown_field",
                    stage=ConnectorErrorStage.CONFIGURATION,
                )
            native_entries.append(
                (name, _coerce_configuration_value(field.kind, value)._native)
            )
        return _NativeConnectorConfiguration(native_entries)


@dataclass(frozen=True, slots=True)
class ConnectorCapability:
    """One stable capability advertised by a Connector implementation."""

    id: str
    documentation: str


@dataclass(frozen=True, slots=True)
class ConnectorRequirement:
    """One declared external or host requirement for a Connector."""

    id: str
    documentation: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class ConnectorManifest:
    """Provider-neutral outbound Connector compiled by Core."""

    operator_id: str
    package_version: str
    inputs: tuple[PortSpec, ...]
    configuration: ConnectorConfigurationSchema = field(
        default_factory=ConnectorConfigurationSchema
    )
    node_type_id: str | None = None
    manifest_revision: int = 1
    startup_timeout_ms: int = 5_000
    probe_interval_ms: int = 100
    success_threshold: int = 1
    failure_threshold: int = 1
    capabilities: tuple[ConnectorCapability, ...] = ()
    requirements: tuple[ConnectorRequirement, ...] = ()
    _native: _NativeConnectorManifest = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        node_type_id = self.node_type_id or self.operator_id
        native = _native_call(
            lambda: _NativeConnectorManifest(
                self.operator_id,
                node_type_id,
                self.package_version,
                [port._native for port in self.inputs],
                self.configuration._native,
                self.manifest_revision,
                self.startup_timeout_ms,
                self.probe_interval_ms,
                self.success_threshold,
                self.failure_threshold,
                [
                    (capability.id, capability.documentation)
                    for capability in self.capabilities
                ],
                [
                    (requirement.id, requirement.required, requirement.documentation)
                    for requirement in self.requirements
                ],
            )
        )
        object.__setattr__(self, "_native", native)

    @classmethod
    def audio(
        cls,
        operator_id: str,
        *,
        package_version: str,
        configuration: ConnectorConfigurationSchema | None = None,
        port_name: str = "audio",
        multiplicity: Multiplicity = Multiplicity.ONE,
    ) -> ConnectorManifest:
        """Create the common one-input PCM Connector manifest."""
        return cls(
            operator_id=operator_id,
            package_version=package_version,
            inputs=(
                PortSpec(
                    port_name,
                    PortDirection.INPUT,
                    SignalSpec.audio(),
                    MediaCaps.audio(),
                    multiplicity,
                ),
            ),
            configuration=configuration or ConnectorConfigurationSchema(),
        )


class ConnectorInputDescriptor:
    """Immutable Session route and resolved configuration for one input."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeConnectorInputDescriptor) -> None:
        self._native = native

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
    def port_name(self) -> str:
        return self._native.port_name

    @property
    def signal_wire_id(self) -> str:
        return self._native.signal_wire_id

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
    def configuration(self) -> Mapping[str, ConnectorConfigurationValue]:
        return {
            name: ConnectorConfigurationValue(value)
            for name, value in self._native.configuration.items()
        }


class ConnectorItem:
    """One owned audio frame or typed signal delivered off realtime threads."""

    __slots__ = ("_native", "input")

    def __init__(self, native: _NativeConnectorItem) -> None:
        self._native = native
        self.input = ConnectorInputDescriptor(native.input)

    @property
    def kind(self) -> str:
        return self._native.kind

    @property
    def audio(self) -> AudioFrame | None:
        return self._native.audio

    @property
    def signal(self) -> SignalEnvelope[object] | None:
        native = self._native.signal
        return None if native is None else SignalEnvelope._from_native(native)


class ConnectorContext:
    """Finite lifecycle, readiness, health, and recovery control for a driver."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeConnectorContext) -> None:
        self._native = native

    @property
    def stop_requested(self) -> bool:
        return _native_call(lambda: self._native.stop_requested)

    @property
    def shutdown_mode(self) -> ConnectorShutdownMode | None:
        value = _native_call(lambda: self._native.shutdown_mode)
        return None if value is None else ConnectorShutdownMode(value)

    def set_ready(self) -> bool:
        return _native_call(self._native.set_ready)

    def set_not_ready(self, reason_code: str | None = None) -> bool:
        return _native_call(lambda: self._native.set_not_ready(reason_code))

    def set_degraded(self, reason_code: str) -> bool:
        return _native_call(lambda: self._native.set_degraded(reason_code))

    def set_healthy(self) -> bool:
        return _native_call(self._native.set_healthy)

    def set_reconnecting(self, reason_code: str) -> bool:
        return _native_call(lambda: self._native.set_reconnecting(reason_code))

    def set_connected(self) -> bool:
        return _native_call(self._native.set_connected)

    def record_retry(self) -> None:
        _native_call(self._native.record_retry)


class ConnectorDriver:
    """Idiomatic driver defaults; Core owns polling, bounds, and lifecycle."""

    def start(self, context: ConnectorContext) -> None:
        context.set_ready()

    def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        raise NotImplementedError

    def idle(self, context: ConnectorContext) -> None:
        """Optional finite idle work; override only when the provider needs it."""

    def shutdown(self, mode: ConnectorShutdownMode, context: ConnectorContext) -> None:
        """Optional finite provider shutdown after Core requests drain or abort."""

    def cancel_preparation(self) -> None:
        """Release prepared provider state when Session startup rolls back."""


@runtime_checkable
class ConnectorDriverFactory(Protocol):
    def prepare(
        self, inputs: Sequence[ConnectorInputDescriptor]
    ) -> ConnectorDriver: ...


ConnectorDriverBuilder: TypeAlias = Callable[
    [Sequence[ConnectorInputDescriptor]], ConnectorDriver
]
ConnectorHandler: TypeAlias = Callable[
    [ConnectorItem, ConnectorContext], ConnectorDeliveryOutcome | None
]
AudioConnectorHandler: TypeAlias = Callable[
    [AudioFrame, ConnectorContext], ConnectorDeliveryOutcome | None
]
ConnectorPreparationGroup: TypeAlias = Callable[
    [int, Mapping[str, ConnectorConfigurationValue]], str | None
]
ConnectorBatchOutcome: TypeAlias = (
    ConnectorDeliveryOutcome | Sequence[ConnectorDeliveryOutcome] | None
)


class ConnectorWorker:
    """Advanced finite-batch provider with receivers still owned by Core."""

    def start(self, context: ConnectorContext) -> None:
        context.set_ready()

    def deliver_batch(
        self, items: Sequence[ConnectorItem], context: ConnectorContext
    ) -> ConnectorBatchOutcome:
        raise NotImplementedError

    def idle(self, context: ConnectorContext) -> None:
        """Optional finite idle work; override only when required."""

    def shutdown(self, mode: ConnectorShutdownMode, context: ConnectorContext) -> None:
        """Finalize the provider after Core requests drain or abort."""

    def cancel_preparation(self) -> None:
        """Release prepared state during transactional startup rollback."""


@runtime_checkable
class ConnectorFactory(Protocol):
    def prepare(
        self, inputs: Sequence[ConnectorInputDescriptor]
    ) -> ConnectorWorker: ...


ConnectorWorkerBuilder: TypeAlias = Callable[
    [Sequence[ConnectorInputDescriptor]], ConnectorWorker
]


class _HandlerDriver(ConnectorDriver):
    __slots__ = ("_handler",)

    def __init__(self, handler: ConnectorHandler) -> None:
        self._handler = handler

    def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        return self._handler(item, context)


class _DriverAdapter:
    __slots__ = ("_driver", "_pocketstation_idle_enabled")

    def __init__(self, driver: ConnectorDriver) -> None:
        self._driver = driver
        declared_idle = getattr(driver, "_pocketstation_idle_enabled", None)
        idle = getattr(type(driver), "idle", None)
        self._pocketstation_idle_enabled = (
            bool(declared_idle)
            if declared_idle is not None
            else idle is not None and idle is not ConnectorDriver.idle
        )

    def start(self, native: _NativeConnectorContext) -> None:
        start = getattr(self._driver, "start", None)
        context = ConnectorContext(native)
        if start is None:
            context.set_ready()
        else:
            start(context)

    def deliver(
        self, native_item: _NativeConnectorItem, native_context: _NativeConnectorContext
    ) -> str | None:
        outcome = self._driver.deliver(
            ConnectorItem(native_item), ConnectorContext(native_context)
        )
        return None if outcome is None else outcome.value

    def idle(self, native: _NativeConnectorContext) -> None:
        idle = getattr(self._driver, "idle", None)
        if idle is not None:
            idle(ConnectorContext(native))

    def shutdown(self, mode: str, native_context: _NativeConnectorContext) -> None:
        shutdown = getattr(self._driver, "shutdown", None)
        if shutdown is not None:
            shutdown(ConnectorShutdownMode(mode), ConnectorContext(native_context))

    def cancel_preparation(self) -> None:
        cancel = getattr(self._driver, "cancel_preparation", None)
        if cancel is not None:
            cancel()


class _FactoryAdapter:
    __slots__ = ("_factory",)

    def __init__(
        self, factory: ConnectorDriverFactory | ConnectorDriverBuilder
    ) -> None:
        self._factory = factory

    def prepare(
        self, native_inputs: Sequence[_NativeConnectorInputDescriptor]
    ) -> _DriverAdapter:
        inputs = tuple(ConnectorInputDescriptor(value) for value in native_inputs)
        prepare = getattr(self._factory, "prepare", None)
        if prepare is None:
            driver = self._factory(inputs)  # type: ignore[operator]
        else:
            driver = prepare(inputs)
        if not hasattr(driver, "deliver"):
            raise TypeError("Connector factory must return a driver with deliver()")
        return _DriverAdapter(driver)

    def preparation_group(
        self,
        route_id: int,
        native_configuration: Mapping[str, _NativeConnectorConfigurationValue],
    ) -> str | None:
        group = getattr(self._factory, "preparation_group", None)
        if group is None:
            return None
        configuration = {
            name: ConnectorConfigurationValue(value)
            for name, value in native_configuration.items()
        }
        return cast(str | None, group(route_id, configuration))


class _WorkerAdapter:
    __slots__ = ("_pocketstation_idle_enabled", "_worker")

    def __init__(self, worker: ConnectorWorker) -> None:
        self._worker = worker
        idle = getattr(type(worker), "idle", None)
        self._pocketstation_idle_enabled = (
            idle is not None and idle is not ConnectorWorker.idle
        )

    def start(self, native_context: _NativeConnectorContext) -> None:
        start = getattr(self._worker, "start", None)
        context = ConnectorContext(native_context)
        if start is None:
            context.set_ready()
        else:
            start(context)

    def deliver_batch(
        self,
        native_items: Sequence[_NativeConnectorItem],
        native_context: _NativeConnectorContext,
    ) -> str | list[str] | None:
        outcome = self._worker.deliver_batch(
            tuple(ConnectorItem(item) for item in native_items),
            ConnectorContext(native_context),
        )
        if outcome is None:
            return None
        if isinstance(outcome, ConnectorDeliveryOutcome):
            return outcome.value
        return [value.value for value in outcome]

    def idle(self, native_context: _NativeConnectorContext) -> None:
        idle = getattr(self._worker, "idle", None)
        if idle is not None:
            idle(ConnectorContext(native_context))

    def shutdown(self, mode: str, native_context: _NativeConnectorContext) -> None:
        shutdown = getattr(self._worker, "shutdown", None)
        if shutdown is not None:
            shutdown(ConnectorShutdownMode(mode), ConnectorContext(native_context))

    def cancel_preparation(self) -> None:
        cancel = getattr(self._worker, "cancel_preparation", None)
        if cancel is not None:
            cancel()


class _WorkerFactoryAdapter:
    __slots__ = ("_factory",)

    def __init__(self, factory: ConnectorFactory | ConnectorWorkerBuilder) -> None:
        self._factory = factory

    def prepare(
        self, native_inputs: Sequence[_NativeConnectorInputDescriptor]
    ) -> _WorkerAdapter:
        inputs = tuple(ConnectorInputDescriptor(value) for value in native_inputs)
        prepare = getattr(self._factory, "prepare", None)
        worker = (
            self._factory(inputs)  # type: ignore[operator]
            if prepare is None
            else prepare(inputs)
        )
        if not hasattr(worker, "deliver_batch"):
            raise TypeError(
                "Connector factory must return a worker with deliver_batch()"
            )
        return _WorkerAdapter(worker)

    def preparation_group(
        self,
        route_id: int,
        native_configuration: Mapping[str, _NativeConnectorConfigurationValue],
    ) -> str | None:
        group = getattr(self._factory, "preparation_group", None)
        if group is None:
            return None
        configuration = {
            name: ConnectorConfigurationValue(value)
            for name, value in native_configuration.items()
        }
        return cast(str | None, group(route_id, configuration))


class Connector:
    """Send source-aware audio through one configured provider lifecycle.

    Pass ``send=`` for one function, or subclass this type and implement
    :meth:`send`. Network providers should use
    :class:`pocketstation.aio.Connector` so PocketStation can apply a finite
    deadline to each asynchronous provider call.
    """

    def __init__(
        self,
        manifest: ConnectorManifest | None = None,
        factory: (
            ConnectorDriverFactory
            | ConnectorDriverBuilder
            | ConnectorFactory
            | ConnectorWorkerBuilder
            | None
        ) = None,
        maximum_batch_items: int | None = None,
        *,
        start: Callable[[], None] | None = None,
        send: Callable[[AudioFrame], None] | None = None,
        stop: Callable[[], None] | None = None,
    ) -> None:
        callbacks = (start, send, stop)
        if any(callback is not None for callback in callbacks):
            if (
                manifest is not None
                or factory is not None
                or maximum_batch_items is not None
            ):
                raise TypeError(
                    "lifecycle callbacks cannot be combined with the advanced SPI"
                )
            if send is None:
                raise TypeError(
                    "send is required when lifecycle callbacks are provided"
                )
            if not all(
                callback is None or callable(callback) for callback in callbacks
            ):
                raise TypeError("start, send, and stop must be callable")
            self._manifest = None
            self._factory = None
            self._native_factory = None
            self.maximum_batch_items = None
            self._start_callback = start
            self._send_callback = send
            self._stop_callback = stop
            return
        if manifest is None and factory is None:
            self._manifest = None
            self._factory = None
            self._native_factory = None
            self.maximum_batch_items = None
            return
        if manifest is None or factory is None:
            raise TypeError("manifest and factory must be provided together")
        if maximum_batch_items is not None and not 1 <= maximum_batch_items <= 1_024:
            raise ValueError("maximum_batch_items must be between 1 and 1024")
        self._manifest = manifest
        self._factory = factory
        self.maximum_batch_items = maximum_batch_items
        self._native_factory = (
            _FactoryAdapter(factory)  # type: ignore[arg-type]
            if maximum_batch_items is None
            else _WorkerFactoryAdapter(factory)  # type: ignore[arg-type]
        )

    def start(self) -> None:
        """Open provider resources before the first frame is delivered."""
        callback = getattr(self, "_start_callback", None)
        if callback is not None:
            callback()

    def send(self, frame: AudioFrame) -> None:
        """Deliver one source-aware frame outside realtime execution."""
        callback = getattr(self, "_send_callback", None)
        if callback is not None:
            callback(frame)
            return
        raise NotImplementedError

    def stop(self) -> None:
        """Close provider resources after accepted frames drain or abort."""
        callback = getattr(self, "_stop_callback", None)
        if callback is not None:
            callback()

    @property
    def manifest(self) -> ConnectorManifest:
        manifest = getattr(self, "_manifest", None)
        if manifest is None:
            raise AttributeError(
                "concise Connectors receive an internal manifest "
                "during Session registration"
            )
        return cast(ConnectorManifest, manifest)

    @property
    def factory(
        self,
    ) -> (
        ConnectorDriverFactory
        | ConnectorDriverBuilder
        | ConnectorFactory
        | ConnectorWorkerBuilder
    ):
        factory = getattr(self, "_factory", None)
        if factory is None:
            raise AttributeError(
                "concise Connectors receive an internal factory "
                "during Session registration"
            )
        return cast(
            ConnectorDriverFactory
            | ConnectorDriverBuilder
            | ConnectorFactory
            | ConnectorWorkerBuilder,
            factory,
        )

    def _definition(self) -> Connector:
        if getattr(self, "_manifest", None) is not None:
            return self
        manifest, preparation_group = _provider_manifest(self)
        return Connector.with_driver(
            manifest,
            _ProviderFactory(self, preparation_group),
        )

    @classmethod
    def with_driver(
        cls,
        manifest: ConnectorManifest,
        factory: ConnectorDriverFactory | ConnectorDriverBuilder,
    ) -> Connector:
        return cls(manifest, factory)

    @classmethod
    def with_worker(
        cls,
        manifest: ConnectorManifest,
        factory: ConnectorFactory | ConnectorWorkerBuilder,
        *,
        maximum_batch_items: int = 32,
    ) -> Connector:
        """Create an advanced Connector with finite native-owned batching."""
        return cls(manifest, factory, maximum_batch_items)

    @classmethod
    def from_handler(
        cls,
        manifest: ConnectorManifest,
        handler: ConnectorHandler,
    ) -> Connector:
        """Create the common stateless Connector directly from a handler."""
        return cls(manifest, lambda _inputs: _HandlerDriver(handler))

    @classmethod
    def from_audio_handler(
        cls,
        operator_id: str,
        handler: AudioConnectorHandler,
        *,
        package_version: str,
        port_name: str = "audio",
    ) -> Connector:
        """Create the common PCM Connector without hand-writing a manifest."""

        def deliver(
            item: ConnectorItem,
            context: ConnectorContext,
        ) -> ConnectorDeliveryOutcome | None:
            if item.audio is None:
                raise ConnectorError(
                    "audio Connector received a non-audio item",
                    code="connector.delivery.signal_mismatch",
                    stage=ConnectorErrorStage.DELIVERY,
                )
            return handler(item.audio, context)

        return cls.from_handler(
            ConnectorManifest.audio(
                operator_id,
                package_version=package_version,
                port_name=port_name,
            ),
            deliver,
        )


class _ProviderDriver(ConnectorDriver):
    __slots__ = ("_provider", "_stopped")

    def __init__(self, provider: Connector) -> None:
        self._provider = provider
        self._stopped = False

    def start(self, context: ConnectorContext) -> None:
        try:
            self._provider.start()
        except BaseException as error:
            self._close_after_start_failure(error)
            raise
        context.set_ready()

    def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        del context
        frame = item.audio
        if frame is None:
            raise ConnectorError(
                "audio Connector received a non-audio item",
                code="connector.delivery.signal_mismatch",
                stage=ConnectorErrorStage.DELIVERY,
            )
        try:
            self._provider.send(frame)
        except BaseException as error:
            self._close_after_failure(error)
            raise
        return ConnectorDeliveryOutcome.DELIVERED

    def shutdown(self, mode: ConnectorShutdownMode, context: ConnectorContext) -> None:
        del mode, context
        self._close()

    def _close_after_start_failure(self, error: BaseException) -> None:
        self._close_after_failure(error)

    def _close_after_failure(self, error: BaseException) -> None:
        try:
            self._close()
        except BaseException as cleanup_error:
            error.add_note(f"Connector cleanup also failed: {cleanup_error}")

    def _close(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._provider.stop()


class _ProviderFactory:
    __slots__ = ("_preparation_group", "_provider")

    def __init__(self, provider: Connector, preparation_group: str) -> None:
        self._provider = provider
        self._preparation_group = preparation_group

    def prepare(self, inputs: Sequence[ConnectorInputDescriptor]) -> ConnectorDriver:
        if not inputs:
            raise ConnectorError(
                "Connector requires at least one routed input",
                code="connector.prepare.missing_input",
                stage=ConnectorErrorStage.PREPARE,
            )
        return _ProviderDriver(self._provider)

    def preparation_group(
        self,
        route_id: int,
        configuration: Mapping[str, ConnectorConfigurationValue],
    ) -> str:
        del route_id, configuration
        return self._preparation_group


def _provider_manifest(provider: object) -> tuple[ConnectorManifest, str]:
    provider_type = type(provider)
    distribution, package_version = _provider_distribution(provider_type)
    node_type_id = _provider_node_type_id(provider_type, distribution)
    instance_token = f"{id(provider):x}"
    operator_id = _bounded_identifier(f"{node_type_id}.instance-{instance_token}")
    preparation_group = _bounded_identifier(
        f"{node_type_id}.destination-{instance_token}"
    )
    return (
        ConnectorManifest.audio(
            operator_id,
            package_version=package_version,
            multiplicity=Multiplicity.MANY,
        ),
        preparation_group,
    )


def _provider_distribution(provider_type: type[object]) -> tuple[str, str]:
    top_level_package = provider_type.__module__.partition(".")[0]
    distributions = importlib.metadata.packages_distributions().get(
        top_level_package, ()
    )
    if distributions:
        distribution = sorted(distributions)[0]
        return distribution, importlib.metadata.version(distribution)
    return "local", "0+local"


def _provider_node_type_id(provider_type: type[object], distribution: str) -> str:
    class_name = f"{provider_type.__module__}.{provider_type.__qualname__}"
    raw = f"python.{distribution}.{class_name}.v1"
    segments = (_identifier_segment(segment) for segment in raw.split("."))
    return _bounded_identifier(".".join(segments))


def _identifier_segment(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "local"


def _bounded_identifier(value: str) -> str:
    maximum_bytes = 255
    if len(value.encode("ascii")) <= maximum_bytes:
        return value
    digest = hashlib.sha256(value.encode()).hexdigest()[:16]
    prefix_bytes = maximum_bytes - len(digest) - 1
    return f"{value[:prefix_bytes].rstrip('-_.')}.{digest}"


class RegisteredConnector:
    """One reusable Connector implementation bound to one Session draft."""

    __slots__ = ("_connector", "_native", "_session")

    def __init__(
        self,
        session: _SessionOwner,
        connector: Connector,
        native: _NativeRegisteredConnector,
    ) -> None:
        self._session = session
        self._connector = connector
        self._native = native

    @property
    def session_id(self) -> int:
        return self._native.session_id

    def declare(
        self,
        configuration: ConnectorConfigurationInput = (),
        *,
        edge: EdgeContract | None = None,
    ) -> Endpoint:
        """Declare one configured endpoint using the registered implementation."""
        native_configuration = self._connector.manifest.configuration.configuration(
            configuration
        )
        selected_edge = edge or _default_edge(self._connector.manifest)
        native = _native_call(
            lambda: self._session._native.declare_connector(
                self._native, native_configuration, selected_edge._native
            )
        )
        return Endpoint(native)

    def observations(self) -> tuple[ConnectorRuntimeObservations, ...]:
        """Snapshot every distinct runtime group created for this Connector."""
        values = _native_call(self._native.observations)
        return tuple(
            ConnectorRuntimeObservations._from_native(value) for value in values
        )

    def observation(self, endpoint: Endpoint) -> ConnectorObservations | None:
        """Snapshot the provider-service state for one declared endpoint."""
        value = _native_call(lambda: self._native.observation(endpoint._native))
        return None if value is None else ConnectorObservations._from_native(value)


def connector(
    manifest: ConnectorManifest,
) -> Callable[[ConnectorHandler], Connector]:
    """Decorate one item handler into a reusable in-process Connector."""

    def define(handler: ConnectorHandler) -> Connector:
        return Connector.from_handler(manifest, handler)

    return define


def _coerce_configuration_value(
    kind: ConnectorConfigurationValueKind,
    value: ConnectorConfigurationValue | str | bool | int,
) -> ConnectorConfigurationValue:
    if isinstance(value, ConnectorConfigurationValue):
        if value.kind is not kind:
            raise ConnectorError(
                f"configuration value is {value.kind.value}, expected {kind.value}",
                code="connector.configuration.type_mismatch",
                stage=ConnectorErrorStage.CONFIGURATION,
            )
        return value
    if kind is ConnectorConfigurationValueKind.TEXT and isinstance(value, str):
        return ConnectorConfigurationValue.text(value)
    if kind is ConnectorConfigurationValueKind.BOOLEAN and isinstance(value, bool):
        return ConnectorConfigurationValue.boolean(value)
    if isinstance(value, int) and not isinstance(value, bool):
        if kind is ConnectorConfigurationValueKind.SIGNED_INTEGER:
            return ConnectorConfigurationValue.signed_integer(value)
        if kind is ConnectorConfigurationValueKind.UNSIGNED_INTEGER:
            return ConnectorConfigurationValue.unsigned_integer(value)
        if kind is ConnectorConfigurationValueKind.DURATION_MILLISECONDS:
            return ConnectorConfigurationValue.duration_milliseconds(value)
        if kind is ConnectorConfigurationValueKind.BYTE_COUNT:
            return ConnectorConfigurationValue.byte_count(value)
    raise ConnectorError(
        f"configuration value cannot be represented as {kind.value}",
        code="connector.configuration.type_mismatch",
        stage=ConnectorErrorStage.CONFIGURATION,
    )


def _first_duplicate(values: Iterable[str]) -> str | None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def _default_edge(manifest: ConnectorManifest) -> EdgeContract:
    if len(manifest.inputs) == 1 and manifest.inputs[0].signal.is_audio:
        return EdgeContract.realtime_audio()
    return EdgeContract.bounded_async()


__all__ = [
    "AudioConnectorHandler",
    "Connector",
    "ConnectorBatchOutcome",
    "ConnectorCapability",
    "ConnectorConfigurationConstraint",
    "ConnectorConfigurationField",
    "ConnectorConfigurationInput",
    "ConnectorConfigurationRequirement",
    "ConnectorConfigurationSchema",
    "ConnectorConfigurationValue",
    "ConnectorConfigurationValueKind",
    "ConnectorContext",
    "ConnectorDeliveryOutcome",
    "ConnectorDeliveryReadiness",
    "ConnectorDriver",
    "ConnectorDriverBuilder",
    "ConnectorDriverFactory",
    "ConnectorError",
    "ConnectorErrorSnapshot",
    "ConnectorErrorStage",
    "ConnectorFactory",
    "ConnectorHandler",
    "ConnectorHealth",
    "ConnectorInputDescriptor",
    "ConnectorItem",
    "ConnectorManifest",
    "ConnectorObservations",
    "ConnectorPreparationGroup",
    "ConnectorRecovery",
    "ConnectorRequirement",
    "ConnectorRetryability",
    "ConnectorRuntimeObservations",
    "ConnectorServiceStatus",
    "ConnectorShutdownMode",
    "ConnectorWorker",
    "ConnectorWorkerBuilder",
    "RegisteredConnector",
    "connector",
]
