"""Author bounded Python Connectors with asyncio lifecycle methods."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping, Sequence
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, Protocol, TypeAlias, TypeVar, runtime_checkable

from .._native import AudioFrame
from ..connector import (
    Connector as SyncConnector,
)
from ..connector import (
    ConnectorBatchOutcome,
    ConnectorCapability,
    ConnectorConfigurationConstraint,
    ConnectorConfigurationField,
    ConnectorConfigurationInput,
    ConnectorConfigurationRequirement,
    ConnectorConfigurationSchema,
    ConnectorConfigurationValue,
    ConnectorConfigurationValueKind,
    ConnectorContext,
    ConnectorDeliveryOutcome,
    ConnectorDeliveryReadiness,
    ConnectorError,
    ConnectorErrorSnapshot,
    ConnectorErrorStage,
    ConnectorHealth,
    ConnectorInputDescriptor,
    ConnectorItem,
    ConnectorManifest,
    ConnectorObservations,
    ConnectorPreparationGroup,
    ConnectorRecovery,
    ConnectorRequirement,
    ConnectorRetryability,
    ConnectorRuntimeObservations,
    ConnectorServiceStatus,
    ConnectorShutdownMode,
)
from ..connector import (
    ConnectorDriver as SyncConnectorDriver,
)
from ..connector import (
    ConnectorWorker as SyncConnectorWorker,
)
from ..connector import (
    RegisteredConnector as SyncRegisteredConnector,
)
from ..graph import EdgeContract, Endpoint


@dataclass(frozen=True, slots=True)
class ConnectorDeadlines:
    """Finite waits applied while a Core worker awaits asyncio provider work."""

    prepare_s: float = 5.0
    start_s: float = 5.0
    delivery_s: float = 30.0
    shutdown_s: float = 5.0

    def __post_init__(self) -> None:
        for name, value in (
            ("prepare_s", self.prepare_s),
            ("start_s", self.start_s),
            ("delivery_s", self.delivery_s),
            ("shutdown_s", self.shutdown_s),
        ):
            if not 0 < value <= 300:
                raise ValueError(f"{name} must be greater than 0 and at most 300")


class ConnectorDriver:
    """Async provider behavior; Core retains queues and Endpoint lifecycle."""

    async def start(self, context: ConnectorContext) -> None:
        context.set_ready()

    async def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        raise NotImplementedError

    async def idle(self, context: ConnectorContext) -> None:
        """Optional finite idle work; override only when required."""

    async def shutdown(
        self, mode: ConnectorShutdownMode, context: ConnectorContext
    ) -> None:
        """Finalize provider state after Core requests drain or abort."""

    async def cancel_preparation(self) -> None:
        """Release prepared state during transactional startup rollback."""


@runtime_checkable
class ConnectorDriverFactory(Protocol):
    async def prepare(
        self, inputs: Sequence[ConnectorInputDescriptor]
    ) -> ConnectorDriver: ...


ConnectorDriverBuilder: TypeAlias = Callable[
    [Sequence[ConnectorInputDescriptor]], Coroutine[Any, Any, ConnectorDriver]
]
ConnectorHandler: TypeAlias = Callable[
    [ConnectorItem, ConnectorContext],
    Coroutine[Any, Any, ConnectorDeliveryOutcome | None],
]
AudioConnectorHandler: TypeAlias = Callable[
    [AudioFrame, ConnectorContext],
    Coroutine[Any, Any, ConnectorDeliveryOutcome | None],
]
_Result = TypeVar("_Result")


class ConnectorWorker:
    """Advanced asyncio provider receiving finite native-owned batches."""

    async def start(self, context: ConnectorContext) -> None:
        context.set_ready()

    async def deliver_batch(
        self, items: Sequence[ConnectorItem], context: ConnectorContext
    ) -> ConnectorBatchOutcome:
        raise NotImplementedError

    async def idle(self, context: ConnectorContext) -> None:
        """Optional finite idle work; override only when required."""

    async def shutdown(
        self, mode: ConnectorShutdownMode, context: ConnectorContext
    ) -> None:
        """Finalize provider state after Core requests drain or abort."""

    async def cancel_preparation(self) -> None:
        """Release prepared state during transactional startup rollback."""


@runtime_checkable
class ConnectorFactory(Protocol):
    async def prepare(
        self, inputs: Sequence[ConnectorInputDescriptor]
    ) -> ConnectorWorker: ...


ConnectorWorkerBuilder: TypeAlias = Callable[
    [Sequence[ConnectorInputDescriptor]], Coroutine[Any, Any, ConnectorWorker]
]


class _HandlerDriver(ConnectorDriver):
    __slots__ = ("_handler",)

    def __init__(self, handler: ConnectorHandler) -> None:
        self._handler = handler

    async def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        return await self._handler(item, context)


class _DriverAdapter(SyncConnectorDriver):
    __slots__ = (
        "_deadlines",
        "_driver",
        "_loop",
        "_pocketstation_idle_enabled",
    )

    def __init__(
        self,
        driver: ConnectorDriver,
        loop: asyncio.AbstractEventLoop,
        deadlines: ConnectorDeadlines,
    ) -> None:
        self._driver = driver
        self._loop = loop
        self._deadlines = deadlines
        idle = getattr(type(driver), "idle", None)
        self._pocketstation_idle_enabled = (
            idle is not None and idle is not ConnectorDriver.idle
        )

    def start(self, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._driver.start(context),
            timeout_s=self._deadlines.start_s,
            stage=ConnectorErrorStage.STARTUP,
        )

    def deliver(
        self, item: ConnectorItem, context: ConnectorContext
    ) -> ConnectorDeliveryOutcome | None:
        return _wait_for_provider(
            self._loop,
            self._driver.deliver(item, context),
            timeout_s=self._deadlines.delivery_s,
            stage=ConnectorErrorStage.DELIVERY,
        )

    def idle(self, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._driver.idle(context),
            timeout_s=self._deadlines.delivery_s,
            stage=ConnectorErrorStage.DELIVERY,
        )

    def shutdown(self, mode: ConnectorShutdownMode, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._driver.shutdown(mode, context),
            timeout_s=self._deadlines.shutdown_s,
            stage=ConnectorErrorStage.SHUTDOWN,
        )

    def cancel_preparation(self) -> None:
        _wait_for_provider(
            self._loop,
            self._driver.cancel_preparation(),
            timeout_s=self._deadlines.shutdown_s,
            stage=ConnectorErrorStage.PREPARE,
        )


class _FactoryAdapter:
    __slots__ = ("_deadlines", "_factory", "_loop")

    def __init__(
        self,
        factory: ConnectorDriverFactory | ConnectorDriverBuilder,
        loop: asyncio.AbstractEventLoop,
        deadlines: ConnectorDeadlines,
    ) -> None:
        self._factory = factory
        self._loop = loop
        self._deadlines = deadlines

    def prepare(self, inputs: Sequence[ConnectorInputDescriptor]) -> _DriverAdapter:
        prepare = getattr(self._factory, "prepare", None)
        awaitable = (
            self._factory(inputs)  # type: ignore[operator]
            if prepare is None
            else prepare(inputs)
        )
        driver = _wait_for_provider(
            self._loop,
            awaitable,
            timeout_s=self._deadlines.prepare_s,
            stage=ConnectorErrorStage.PREPARE,
        )
        if not hasattr(driver, "deliver"):
            raise TypeError(
                "async Connector factory must return a driver with deliver()"
            )
        return _DriverAdapter(driver, self._loop, self._deadlines)

    def preparation_group(
        self,
        route_id: int,
        configuration: Mapping[str, ConnectorConfigurationValue],
    ) -> str | None:
        group: ConnectorPreparationGroup | None = getattr(
            self._factory, "preparation_group", None
        )
        return None if group is None else group(route_id, configuration)


class _WorkerAdapter(SyncConnectorWorker):
    __slots__ = (
        "_deadlines",
        "_loop",
        "_pocketstation_idle_enabled",
        "_worker",
    )

    def __init__(
        self,
        worker: ConnectorWorker,
        loop: asyncio.AbstractEventLoop,
        deadlines: ConnectorDeadlines,
    ) -> None:
        self._worker = worker
        self._loop = loop
        self._deadlines = deadlines
        idle = getattr(type(worker), "idle", None)
        self._pocketstation_idle_enabled = (
            idle is not None and idle is not ConnectorWorker.idle
        )

    def start(self, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._worker.start(context),
            timeout_s=self._deadlines.start_s,
            stage=ConnectorErrorStage.STARTUP,
        )

    def deliver_batch(
        self, items: Sequence[ConnectorItem], context: ConnectorContext
    ) -> ConnectorBatchOutcome:
        return _wait_for_provider(
            self._loop,
            self._worker.deliver_batch(items, context),
            timeout_s=self._deadlines.delivery_s,
            stage=ConnectorErrorStage.DELIVERY,
        )

    def idle(self, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._worker.idle(context),
            timeout_s=self._deadlines.delivery_s,
            stage=ConnectorErrorStage.DELIVERY,
        )

    def shutdown(self, mode: ConnectorShutdownMode, context: ConnectorContext) -> None:
        _wait_for_provider(
            self._loop,
            self._worker.shutdown(mode, context),
            timeout_s=self._deadlines.shutdown_s,
            stage=ConnectorErrorStage.SHUTDOWN,
        )

    def cancel_preparation(self) -> None:
        _wait_for_provider(
            self._loop,
            self._worker.cancel_preparation(),
            timeout_s=self._deadlines.shutdown_s,
            stage=ConnectorErrorStage.PREPARE,
        )


class _WorkerFactoryAdapter:
    __slots__ = ("_deadlines", "_factory", "_loop")

    def __init__(
        self,
        factory: ConnectorFactory | ConnectorWorkerBuilder,
        loop: asyncio.AbstractEventLoop,
        deadlines: ConnectorDeadlines,
    ) -> None:
        self._factory = factory
        self._loop = loop
        self._deadlines = deadlines

    def prepare(self, inputs: Sequence[ConnectorInputDescriptor]) -> _WorkerAdapter:
        prepare = getattr(self._factory, "prepare", None)
        awaitable = (
            self._factory(inputs)  # type: ignore[operator]
            if prepare is None
            else prepare(inputs)
        )
        worker = _wait_for_provider(
            self._loop,
            awaitable,
            timeout_s=self._deadlines.prepare_s,
            stage=ConnectorErrorStage.PREPARE,
        )
        if not hasattr(worker, "deliver_batch"):
            raise TypeError(
                "async Connector factory must return a worker with deliver_batch()"
            )
        return _WorkerAdapter(worker, self._loop, self._deadlines)

    def preparation_group(
        self,
        route_id: int,
        configuration: Mapping[str, ConnectorConfigurationValue],
    ) -> str | None:
        group: ConnectorPreparationGroup | None = getattr(
            self._factory, "preparation_group", None
        )
        return None if group is None else group(route_id, configuration)


@dataclass(frozen=True, slots=True)
class Connector:
    """Reusable asyncio provider implementation bound at Session registration."""

    manifest: ConnectorManifest
    factory: (
        ConnectorDriverFactory
        | ConnectorDriverBuilder
        | ConnectorFactory
        | ConnectorWorkerBuilder
    )
    deadlines: ConnectorDeadlines = ConnectorDeadlines()
    maximum_batch_items: int | None = None

    @classmethod
    def with_driver(
        cls,
        manifest: ConnectorManifest,
        factory: ConnectorDriverFactory | ConnectorDriverBuilder,
        *,
        deadlines: ConnectorDeadlines | None = None,
    ) -> Connector:
        return cls(manifest, factory, deadlines or ConnectorDeadlines())

    @classmethod
    def from_handler(
        cls,
        manifest: ConnectorManifest,
        handler: ConnectorHandler,
        *,
        deadlines: ConnectorDeadlines | None = None,
    ) -> Connector:
        async def prepare(
            _inputs: Sequence[ConnectorInputDescriptor],
        ) -> ConnectorDriver:
            return _HandlerDriver(handler)

        return cls.with_driver(manifest, prepare, deadlines=deadlines)

    @classmethod
    def from_audio_handler(
        cls,
        operator_id: str,
        handler: AudioConnectorHandler,
        *,
        package_version: str,
        port_name: str = "audio",
        deadlines: ConnectorDeadlines | None = None,
    ) -> Connector:
        """Create the common async PCM Connector without a manual manifest."""

        async def deliver(
            item: ConnectorItem,
            context: ConnectorContext,
        ) -> ConnectorDeliveryOutcome | None:
            if item.audio is None:
                raise ConnectorError(
                    "audio Connector received a non-audio item",
                    code="connector.delivery.signal_mismatch",
                    stage=ConnectorErrorStage.DELIVERY,
                )
            return await handler(item.audio, context)

        return cls.from_handler(
            ConnectorManifest.audio(
                operator_id,
                package_version=package_version,
                port_name=port_name,
            ),
            deliver,
            deadlines=deadlines,
        )

    @classmethod
    def with_worker(
        cls,
        manifest: ConnectorManifest,
        factory: ConnectorFactory | ConnectorWorkerBuilder,
        *,
        maximum_batch_items: int = 32,
        deadlines: ConnectorDeadlines | None = None,
    ) -> Connector:
        if not 1 <= maximum_batch_items <= 1_024:
            raise ValueError("maximum_batch_items must be between 1 and 1024")
        return cls(
            manifest,
            factory,
            deadlines or ConnectorDeadlines(),
            maximum_batch_items,
        )

    def _bind(self, loop: asyncio.AbstractEventLoop) -> SyncConnector:
        if not loop.is_running():
            raise RuntimeError("async Connector requires a running event loop")
        if self.maximum_batch_items is None:
            return SyncConnector.with_driver(
                self.manifest,
                _FactoryAdapter(
                    self.factory,  # type: ignore[arg-type]
                    loop,
                    self.deadlines,
                ),
            )
        return SyncConnector.with_worker(
            self.manifest,
            _WorkerFactoryAdapter(
                self.factory,  # type: ignore[arg-type]
                loop,
                self.deadlines,
            ),
            maximum_batch_items=self.maximum_batch_items,
        )


class RegisteredConnector:
    """Async observation view over one Core-registered Connector."""

    __slots__ = ("_registered",)

    def __init__(self, registered: SyncRegisteredConnector) -> None:
        self._registered = registered

    @property
    def session_id(self) -> int:
        return self._registered.session_id

    def declare(
        self,
        configuration: ConnectorConfigurationInput = (),
        *,
        edge: EdgeContract | None = None,
    ) -> Endpoint:
        return self._registered.declare(configuration, edge=edge)

    async def observations(self) -> tuple[ConnectorRuntimeObservations, ...]:
        return await asyncio.to_thread(self._registered.observations)

    async def observation(self, endpoint: Endpoint) -> ConnectorObservations | None:
        return await asyncio.to_thread(self._registered.observation, endpoint)


def connector(
    manifest: ConnectorManifest,
    *,
    deadlines: ConnectorDeadlines | None = None,
) -> Callable[[ConnectorHandler], Connector]:
    """Decorate one coroutine handler into a bounded asyncio Connector."""

    def define(handler: ConnectorHandler) -> Connector:
        return Connector.from_handler(manifest, handler, deadlines=deadlines)

    return define


def _wait_for_provider(
    loop: asyncio.AbstractEventLoop,
    awaitable: Coroutine[Any, Any, _Result],
    *,
    timeout_s: float,
    stage: ConnectorErrorStage,
) -> _Result:
    try:
        future: Future[_Result] = asyncio.run_coroutine_threadsafe(awaitable, loop)
    except RuntimeError as error:
        awaitable.close()
        raise ConnectorError(
            "asyncio Connector event loop is not available",
            code="python.async.loop_unavailable",
            stage=stage,
        ) from error
    try:
        return future.result(timeout_s)
    except FutureTimeoutError as error:
        future.cancel()
        raise ConnectorError(
            f"asyncio Connector operation exceeded {timeout_s:g} seconds",
            code="python.async.timeout",
            stage=stage,
            retryability=ConnectorRetryability.RETRYABLE,
        ) from error
    except FutureCancelledError as error:
        raise ConnectorError(
            "asyncio Connector operation was cancelled",
            code="python.async.cancelled",
            stage=stage,
        ) from error


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
    "ConnectorDeadlines",
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
