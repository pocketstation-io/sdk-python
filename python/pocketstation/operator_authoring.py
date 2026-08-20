"""Python-authored Operators over Core's bounded async-worker runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, TypeAlias, runtime_checkable

from ._native import _OperatorEmission as _NativeOperatorEmission
from ._native import _OperatorManifest as _NativeOperatorManifest
from ._native import _OperatorPortContext as _NativeOperatorPortContext
from ._native import _OperatorPrepareContext as _NativeOperatorPrepareContext
from ._native import _SignalEnvelope as _NativeSignalEnvelope
from .errors import _native_call
from .graph import (
    EdgeContract,
    MediaCaps,
    Operator,
    OperatorConfiguration,
    OperatorInstance,
    PortDirection,
    PortSpec,
    SignalSpec,
)
from .signal import SignalEnvelope


class _SessionOwner(Protocol):
    def operator(self, operator: Operator) -> OperatorInstance: ...


@dataclass(frozen=True, slots=True)
class OperatorManifest:
    """Validated contract for one off-realtime Python Operator."""

    operator_id: str
    inputs: tuple[PortSpec, ...]
    outputs: tuple[PortSpec, ...]
    revision: int = 1
    implementation_generation: int = 1
    queue_capacity_signals: int = 8
    process_timeout_ms: int = 30_000
    network_allowed: bool = False
    filesystem_allowed: bool = False
    drain_queued: bool = False
    continue_on_failure: bool = False
    terminal_roles: tuple[str, ...] = ()
    _native: _NativeOperatorManifest = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativeOperatorManifest(
                self.operator_id,
                [port._native for port in self.inputs],
                [port._native for port in self.outputs],
                self.revision,
                self.implementation_generation,
                self.queue_capacity_signals,
                self.process_timeout_ms,
                self.network_allowed,
                self.filesystem_allowed,
                self.drain_queued,
                self.continue_on_failure,
                list(self.terminal_roles),
            )
        )
        object.__setattr__(self, "_native", native)


@dataclass(frozen=True, slots=True)
class OperatorPortContext:
    edge_id: int | None
    port_name: str
    direction: PortDirection
    capacity_signals: int
    signal: SignalSpec[object]
    media: MediaCaps
    edge: EdgeContract

    @classmethod
    def _from_native(cls, value: _NativeOperatorPortContext) -> OperatorPortContext:
        return cls(
            edge_id=value.edge_id,
            port_name=value.port_name,
            direction=PortDirection(value.direction),
            capacity_signals=value.capacity_signals,
            signal=SignalSpec._from_native(value.signal),
            media=MediaCaps._from_native(value.media),
            edge=EdgeContract(value.edge),
        )


@dataclass(frozen=True, slots=True)
class OperatorPrepareContext:
    execution_partition: str
    inputs: tuple[OperatorPortContext, ...]
    outputs: tuple[OperatorPortContext, ...]

    @classmethod
    def _from_native(
        cls, value: _NativeOperatorPrepareContext
    ) -> OperatorPrepareContext:
        return cls(
            execution_partition=value.execution_partition,
            inputs=tuple(
                OperatorPortContext._from_native(item) for item in value.inputs
            ),
            outputs=tuple(
                OperatorPortContext._from_native(item) for item in value.outputs
            ),
        )


class OperatorEmission:
    """One derived typed payload; Core attaches derivation and lineage."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeOperatorEmission) -> None:
        self._native = native

    @classmethod
    def text(cls, payload: str, *, signal: SignalSpec[str]) -> OperatorEmission:
        return cls(
            _native_call(lambda: _NativeOperatorEmission.text(payload, signal._native))
        )

    @classmethod
    def bytes(cls, payload: bytes, *, signal: SignalSpec[bytes]) -> OperatorEmission:
        return cls(
            _native_call(lambda: _NativeOperatorEmission.bytes(payload, signal._native))
        )


class OperatorNode:
    """Off-realtime computation hosted by Core's Operator worker."""

    def prepare(self, context: OperatorPrepareContext) -> None:
        """Observe compiled port and edge contracts before processing."""

    def process(
        self, input_port: str, envelope: SignalEnvelope[object]
    ) -> Sequence[OperatorEmission]:
        raise NotImplementedError

    def flush(self) -> Sequence[OperatorEmission]:
        return ()

    def cancel(self) -> None:
        """Cancel provider work after Core requests cancellation."""

    def close(self) -> None:
        """Release provider resources exactly once."""


@runtime_checkable
class OperatorFactory(Protocol):
    def create(self, configuration: Mapping[str, str]) -> OperatorNode: ...


OperatorHandler: TypeAlias = Callable[
    [str, SignalEnvelope[object]], Sequence[OperatorEmission]
]
OperatorConfigValidator: TypeAlias = Callable[[Mapping[str, str]], None]


class _HandlerNode(OperatorNode):
    __slots__ = ("_handler",)

    def __init__(self, handler: OperatorHandler) -> None:
        self._handler = handler

    def process(
        self, input_port: str, envelope: SignalEnvelope[object]
    ) -> Sequence[OperatorEmission]:
        return self._handler(input_port, envelope)


class _HandlerFactory:
    __slots__ = ("_handler", "_validator")

    def __init__(
        self,
        handler: OperatorHandler,
        validator: OperatorConfigValidator | None,
    ) -> None:
        self._handler = handler
        self._validator = validator

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        if self._validator is not None:
            self._validator(configuration)

    def create(self, _configuration: Mapping[str, str]) -> OperatorNode:
        return _HandlerNode(self._handler)


@dataclass(frozen=True, slots=True)
class OperatorProvider:
    manifest: OperatorManifest
    factory: OperatorFactory

    @classmethod
    def with_node(
        cls, manifest: OperatorManifest, factory: OperatorFactory
    ) -> OperatorProvider:
        return cls(manifest, factory)

    @classmethod
    def from_handler(
        cls,
        manifest: OperatorManifest,
        handler: OperatorHandler,
        *,
        validate_config: OperatorConfigValidator | None = None,
    ) -> OperatorProvider:
        return cls(manifest, _HandlerFactory(handler, validate_config))


class _NativeNodeAdapter:
    __slots__ = ("_node",)

    def __init__(self, node: OperatorNode) -> None:
        self._node = node

    def prepare(self, context: _NativeOperatorPrepareContext) -> None:
        self._node.prepare(OperatorPrepareContext._from_native(context))

    def process(
        self, input_port: str, envelope: _NativeSignalEnvelope
    ) -> list[_NativeOperatorEmission]:
        return [
            item._native
            for item in self._node.process(
                input_port, SignalEnvelope._from_native(envelope)
            )
        ]

    def flush(self) -> list[_NativeOperatorEmission]:
        return [item._native for item in self._node.flush()]

    def cancel(self) -> None:
        self._node.cancel()

    def close(self) -> None:
        self._node.close()


class _NativeFactoryAdapter:
    __slots__ = ("_factory",)

    def __init__(self, factory: OperatorFactory) -> None:
        self._factory = factory

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        validator = getattr(self._factory, "validate_config", None)
        if validator is not None:
            validator(configuration)

    def create(self, configuration: Mapping[str, str]) -> _NativeNodeAdapter:
        node = self._factory.create(configuration)
        if not hasattr(node, "process"):
            raise TypeError("Operator factory must return an OperatorNode")
        return _NativeNodeAdapter(node)


class RegisteredOperator:
    __slots__ = ("_provider", "_session")

    def __init__(self, session: _SessionOwner, provider: OperatorProvider) -> None:
        self._session = session
        self._provider = provider

    @property
    def operator_id(self) -> str:
        return self._provider.manifest.operator_id

    def declare(
        self, configuration: OperatorConfiguration | None = None
    ) -> OperatorInstance:
        return self._session.operator(
            Operator(self.operator_id, configuration or OperatorConfiguration())
        )


def operator(
    manifest: OperatorManifest,
    *,
    validate_config: OperatorConfigValidator | None = None,
) -> Callable[[OperatorHandler], OperatorProvider]:
    """Decorate one function into a Core-backed typed Operator."""

    def define(handler: OperatorHandler) -> OperatorProvider:
        return OperatorProvider.from_handler(
            manifest,
            handler,
            validate_config=validate_config,
        )

    return define


__all__ = [
    "OperatorConfigValidator",
    "OperatorEmission",
    "OperatorFactory",
    "OperatorHandler",
    "OperatorManifest",
    "OperatorNode",
    "OperatorPortContext",
    "OperatorPrepareContext",
    "OperatorProvider",
    "RegisteredOperator",
    "operator",
]
