"""Bounded asyncio API for Core's advanced Endpoint lifecycle."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping, Sequence
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, Protocol, TypeAlias, TypeVar, runtime_checkable

from ..endpoint_authoring import (
    EndpointConfigurationInput,
    EndpointDriverError,
    EndpointDriverObservations,
    EndpointItem,
    EndpointManifest,
    EndpointPortInput,
    EndpointPreparationGroup,
    EndpointPrepareContext,
    EndpointReceiver,
    EndpointShutdownMode,
    EndpointStartGate,
)
from ..endpoint_authoring import EndpointProvider as SyncEndpointProvider
from ..endpoint_authoring import PreparedEndpointDriver as SyncPreparedEndpointDriver
from ..endpoint_authoring import RegisteredEndpoint as SyncRegisteredEndpoint
from ..endpoint_authoring import RunningEndpointDriver as SyncRunningEndpointDriver
from ..graph import EdgeContract, Endpoint, RouteSettings
from ..observations import EndpointFailureStage

_Result = TypeVar("_Result")


@dataclass(frozen=True, slots=True)
class EndpointDeadlines:
    """Finite waits while Core awaits asyncio Endpoint lifecycle work."""

    prepare_s: float = 5.0
    start_s: float = 5.0
    shutdown_s: float = 5.0

    def __post_init__(self) -> None:
        for name, value in (
            ("prepare_s", self.prepare_s),
            ("start_s", self.start_s),
            ("shutdown_s", self.shutdown_s),
        ):
            if not 0 < value <= 300:
                raise ValueError(f"{name} must be greater than 0 and at most 300")


class PreparedEndpointDriver:
    """Async prepared resources held behind Core's closed start gate."""

    async def start(self, gate: EndpointStartGate) -> RunningEndpointDriver:
        raise NotImplementedError

    async def cancel_preparation(self) -> None:
        """Release prepared resources during transactional rollback."""


class RunningEndpointDriver:
    """Async Endpoint resources owned until Core joins finalization."""

    async def observations(self) -> EndpointDriverObservations:
        return EndpointDriverObservations()

    async def request_shutdown(self, mode: EndpointShutdownMode) -> None:
        """Request finite drain or immediate abort."""

    async def join_and_finalize(self) -> EndpointDriverObservations:
        return await self.observations()


@runtime_checkable
class EndpointDriverFactory(Protocol):
    async def prepare(
        self, inputs: Sequence[EndpointPortInput]
    ) -> PreparedEndpointDriver: ...


EndpointDriverBuilder: TypeAlias = Callable[
    [Sequence[EndpointPortInput]], Coroutine[Any, Any, PreparedEndpointDriver]
]
EndpointConfigurationValidator: TypeAlias = Callable[[Mapping[str, str]], None]


class _RunningAdapter(SyncRunningEndpointDriver):
    __slots__ = ("_deadlines", "_loop", "_running")

    def __init__(
        self,
        running: RunningEndpointDriver,
        loop: asyncio.AbstractEventLoop,
        deadlines: EndpointDeadlines,
    ) -> None:
        self._running = running
        self._loop = loop
        self._deadlines = deadlines

    def observations(self) -> EndpointDriverObservations:
        return _wait_for_provider(
            self._loop,
            self._running.observations(),
            timeout_s=self._deadlines.shutdown_s,
            stage=EndpointFailureStage.JOIN_FINALIZE,
        )

    def request_shutdown(self, mode: EndpointShutdownMode) -> None:
        _wait_for_provider(
            self._loop,
            self._running.request_shutdown(mode),
            timeout_s=self._deadlines.shutdown_s,
            stage=EndpointFailureStage.REQUEST_STOP,
        )

    def join_and_finalize(self) -> EndpointDriverObservations:
        return _wait_for_provider(
            self._loop,
            self._running.join_and_finalize(),
            timeout_s=self._deadlines.shutdown_s,
            stage=EndpointFailureStage.JOIN_FINALIZE,
        )


class _PreparedAdapter(SyncPreparedEndpointDriver):
    __slots__ = ("_deadlines", "_loop", "_prepared")

    def __init__(
        self,
        prepared: PreparedEndpointDriver,
        loop: asyncio.AbstractEventLoop,
        deadlines: EndpointDeadlines,
    ) -> None:
        self._prepared = prepared
        self._loop = loop
        self._deadlines = deadlines

    def start(self, gate: EndpointStartGate) -> SyncRunningEndpointDriver:
        running = _wait_for_provider(
            self._loop,
            self._prepared.start(gate),
            timeout_s=self._deadlines.start_s,
            stage=EndpointFailureStage.START,
        )
        return _RunningAdapter(running, self._loop, self._deadlines)

    def cancel_preparation(self) -> None:
        _wait_for_provider(
            self._loop,
            self._prepared.cancel_preparation(),
            timeout_s=self._deadlines.shutdown_s,
            stage=EndpointFailureStage.CANCEL_PREPARATION,
        )


class _FactoryAdapter:
    __slots__ = ("_deadlines", "_factory", "_loop")

    def __init__(
        self,
        factory: EndpointDriverFactory | EndpointDriverBuilder,
        loop: asyncio.AbstractEventLoop,
        deadlines: EndpointDeadlines,
    ) -> None:
        self._factory = factory
        self._loop = loop
        self._deadlines = deadlines

    def prepare(self, inputs: Sequence[EndpointPortInput]) -> _PreparedAdapter:
        prepare = getattr(self._factory, "prepare", None)
        awaitable = (
            self._factory(inputs)  # type: ignore[operator]
            if prepare is None
            else prepare(inputs)
        )
        prepared = _wait_for_provider(
            self._loop,
            awaitable,
            timeout_s=self._deadlines.prepare_s,
            stage=EndpointFailureStage.PREPARE,
        )
        return _PreparedAdapter(prepared, self._loop, self._deadlines)


@dataclass(frozen=True, slots=True)
class EndpointProvider:
    """Reusable asyncio implementation of Core's advanced Endpoint SPI."""

    manifest: EndpointManifest
    factory: EndpointDriverFactory | EndpointDriverBuilder
    deadlines: EndpointDeadlines = EndpointDeadlines()
    validate_configuration: EndpointConfigurationValidator | None = None
    preparation_group: EndpointPreparationGroup | None = None

    def _bind(self, loop: asyncio.AbstractEventLoop) -> SyncEndpointProvider:
        if not loop.is_running():
            raise RuntimeError("async Endpoint requires a running event loop")
        return SyncEndpointProvider(
            self.manifest,
            _FactoryAdapter(self.factory, loop, self.deadlines),
            validate_configuration=self.validate_configuration,
            preparation_group=self.preparation_group,
        )


class RegisteredEndpoint:
    """Async Session view of one Core-registered advanced Endpoint."""

    __slots__ = ("_registered",)

    def __init__(self, registered: SyncRegisteredEndpoint) -> None:
        self._registered = registered

    @property
    def session_id(self) -> int:
        return self._registered.session_id

    def declare(
        self,
        configuration: EndpointConfigurationInput = (),
        *,
        route_settings: RouteSettings | None = None,
        edge: EdgeContract | None = None,
    ) -> Endpoint:
        return self._registered.declare(
            configuration,
            route_settings=route_settings,
            edge=edge,
        )


def _wait_for_provider(
    loop: asyncio.AbstractEventLoop,
    awaitable: Coroutine[Any, Any, _Result],
    *,
    timeout_s: float,
    stage: EndpointFailureStage,
) -> _Result:
    try:
        future: Future[_Result] = asyncio.run_coroutine_threadsafe(awaitable, loop)
    except RuntimeError as error:
        awaitable.close()
        raise EndpointDriverError(
            "asyncio Endpoint event loop is not available",
            code="python.async.loop_unavailable",
            stage=stage,
        ) from error
    try:
        return future.result(timeout_s)
    except FutureTimeoutError as error:
        future.cancel()
        raise EndpointDriverError(
            f"asyncio Endpoint operation exceeded {timeout_s:g} seconds",
            code="python.async.timeout",
            stage=stage,
        ) from error
    except FutureCancelledError as error:
        raise EndpointDriverError(
            "asyncio Endpoint operation was cancelled",
            code="python.async.cancelled",
            stage=stage,
        ) from error
    except EndpointDriverError:
        raise
    except Exception as error:
        raise EndpointDriverError(
            str(error),
            code="python.async.endpoint_exception",
            stage=stage,
        ) from error


__all__ = [
    "EndpointConfigurationInput",
    "EndpointDeadlines",
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
