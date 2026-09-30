"""Asyncio Source authoring over Core's blocking Source worker."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable, AsyncIterator, Callable, Coroutine, Mapping
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from math import isfinite
from time import monotonic
from typing import Any, Protocol, TypeAlias, TypeVar, runtime_checkable

from ..source_authoring import (
    RegisteredSource,
    SourceConfigValidator,
    SourceEmission,
    SourceManifest,
    SourcePrepareContext,
)
from ..source_authoring import SourceCancellation as SyncSourceCancellation
from ..source_authoring import SourceDriver as SyncSourceDriver
from ..source_authoring import SourceProvider as SyncSourceProvider

_Result = TypeVar("_Result")
_SOURCE_DRAIN_TIMEOUT_SECONDS = 1.0


class _SourceInterrupted(Exception):
    """The wait helper interrupted next at Core's explicit request."""


@dataclass(slots=True)
class _SourceOperation:
    result: Future[Any] | None = None


@dataclass(frozen=True, slots=True)
class SourceDeadlines:
    """Finite waits while a Core Source worker awaits asyncio provider work."""

    create_s: float = 5.0
    prepare_s: float = 5.0
    next_s: float = 30.0
    close_s: float = 5.0

    def __post_init__(self) -> None:
        for name, value in (
            ("create_s", self.create_s),
            ("prepare_s", self.prepare_s),
            ("next_s", self.next_s),
            ("close_s", self.close_s),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")
            if not isfinite(value) or not 0 < value <= 300:
                raise ValueError(f"{name} must be greater than 0 and at most 300")


class SourceCancellation:
    """Async provider view of Core's cancellation state."""

    __slots__ = ("_sync",)

    def __init__(self, sync: SyncSourceCancellation) -> None:
        self._sync = sync

    @property
    def cancelled(self) -> bool:
        return self._sync.cancelled


class SourceDriver:
    """Async Source behavior executed from the owning event loop."""

    async def prepare(self, context: SourcePrepareContext) -> None:
        """Acquire resources after Core assigns Session identities."""

    async def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        raise NotImplementedError

    async def drain(self) -> SourceEmission | None:
        """Return already accepted input on graceful stop, or None when empty.

        Do not acquire live input or advance an iterator. Each wait uses close_s
        capped at one second; Core limits the complete drain to one second.
        """
        return None

    async def close(self) -> None:
        """Release provider resources exactly once."""


@runtime_checkable
class SourceFactory(Protocol):
    async def create(self, configuration: Mapping[str, str]) -> SourceDriver: ...


SourceDriverBuilder: TypeAlias = Callable[
    [Mapping[str, str]], Coroutine[Any, Any, SourceDriver]
]
SourceIterableFactory: TypeAlias = Callable[
    [Mapping[str, str]], AsyncIterable[SourceEmission]
]


class _AsyncIteratorDriver(SourceDriver):
    __slots__ = ("_iterator",)

    def __init__(self, values: AsyncIterable[SourceEmission]) -> None:
        self._iterator: AsyncIterator[SourceEmission] = aiter(values)

    async def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        if cancellation.cancelled:
            return None
        try:
            return await anext(self._iterator)
        except StopAsyncIteration:
            return None

    async def close(self) -> None:
        close: Callable[[], Coroutine[Any, Any, None]] | None = getattr(
            self._iterator, "aclose", None
        )
        if close is not None:
            await close()


class _AsyncIterableFactory:
    __slots__ = ("_factory", "_validator")

    def __init__(
        self,
        factory: SourceIterableFactory,
        validator: SourceConfigValidator | None,
    ) -> None:
        self._factory = factory
        self._validator = validator

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        if self._validator is not None:
            self._validator(configuration)

    async def create(self, configuration: Mapping[str, str]) -> SourceDriver:
        return _AsyncIteratorDriver(self._factory(configuration))


class _DriverAdapter(SyncSourceDriver):
    __slots__ = ("_deadlines", "_driver", "_loop", "_operation")

    def __init__(
        self,
        driver: SourceDriver,
        loop: asyncio.AbstractEventLoop,
        deadlines: SourceDeadlines,
    ) -> None:
        self._driver = driver
        self._loop = loop
        self._deadlines = deadlines
        self._operation = _SourceOperation()

    def prepare(self, context: SourcePrepareContext) -> None:
        _wait_for_source(
            self._loop,
            self._driver.prepare(context),
            timeout_s=self._deadlines.prepare_s,
            active=self._operation,
        )

    def next(self, cancellation: SyncSourceCancellation) -> SourceEmission | None:
        try:
            return _wait_for_source(
                self._loop,
                self._driver.next(SourceCancellation(cancellation)),
                timeout_s=self._deadlines.next_s,
                cancellation=cancellation,
                active=self._operation,
            )
        except _SourceInterrupted:
            return None

    def drain(self) -> SourceEmission | None:
        drain: Callable[[], Coroutine[Any, Any, SourceEmission | None]] | None = (
            getattr(self._driver, "drain", None)
        )
        if drain is None:
            return None
        return _wait_for_source(
            self._loop,
            drain(),
            timeout_s=min(self._deadlines.close_s, _SOURCE_DRAIN_TIMEOUT_SECONDS),
            active=self._operation,
        )

    def close(self) -> None:
        _wait_for_source(
            self._loop,
            self._driver.close(),
            timeout_s=self._deadlines.close_s,
            active=self._operation,
        )


class _FactoryAdapter:
    __slots__ = ("_deadlines", "_factory", "_loop")

    def __init__(
        self,
        factory: SourceFactory | SourceDriverBuilder,
        loop: asyncio.AbstractEventLoop,
        deadlines: SourceDeadlines,
    ) -> None:
        self._factory = factory
        self._loop = loop
        self._deadlines = deadlines

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        validator = getattr(self._factory, "validate_config", None)
        if validator is not None:
            validator(configuration)

    def create(self, configuration: Mapping[str, str]) -> _DriverAdapter:
        create = getattr(self._factory, "create", None)
        awaitable = (
            self._factory(configuration)  # type: ignore[operator]
            if create is None
            else create(configuration)
        )
        driver = _wait_for_source(
            self._loop,
            awaitable,
            timeout_s=self._deadlines.create_s,
        )
        if not hasattr(driver, "next"):
            raise TypeError("async Source factory must return a SourceDriver")
        return _DriverAdapter(driver, self._loop, self._deadlines)


@dataclass(frozen=True, slots=True)
class SourceProvider:
    """Reusable asyncio Source implementation bound during Session registration."""

    manifest: SourceManifest
    factory: SourceFactory | SourceDriverBuilder
    deadlines: SourceDeadlines = SourceDeadlines()

    @classmethod
    def with_driver(
        cls,
        manifest: SourceManifest,
        factory: SourceFactory | SourceDriverBuilder,
        *,
        deadlines: SourceDeadlines | None = None,
    ) -> SourceProvider:
        return cls(manifest, factory, deadlines or SourceDeadlines())

    @classmethod
    def from_async_iterable(
        cls,
        manifest: SourceManifest,
        factory: SourceIterableFactory,
        *,
        validate_config: SourceConfigValidator | None = None,
        deadlines: SourceDeadlines | None = None,
    ) -> SourceProvider:
        return cls(
            manifest,
            _AsyncIterableFactory(factory, validate_config),
            deadlines or SourceDeadlines(),
        )

    def _bind(self, loop: asyncio.AbstractEventLoop) -> SyncSourceProvider:
        if not loop.is_running():
            raise RuntimeError("async Source requires a running event loop")
        return SyncSourceProvider.with_driver(
            self.manifest,
            _FactoryAdapter(self.factory, loop, self.deadlines),
        )


def source(
    manifest: SourceManifest,
    *,
    validate_config: SourceConfigValidator | None = None,
    deadlines: SourceDeadlines | None = None,
) -> Callable[[SourceIterableFactory], SourceProvider]:
    """Decorate an async iterable factory into a Core-backed Source."""

    def define(factory: SourceIterableFactory) -> SourceProvider:
        return SourceProvider.from_async_iterable(
            manifest,
            factory,
            validate_config=validate_config,
            deadlines=deadlines,
        )

    return define


def _wait_for_source(
    loop: asyncio.AbstractEventLoop,
    awaitable: Coroutine[Any, Any, _Result],
    *,
    timeout_s: float,
    cancellation: SyncSourceCancellation | None = None,
    active: _SourceOperation | None = None,
) -> _Result:
    if active is not None and active.result is not None and not active.result.done():
        awaitable.close()
        raise RuntimeError(
            "asyncio Source callback refused: previous operation cleanup is incomplete"
        )
    operation: Future[asyncio.Task[_Result]] = Future()

    async def tracked() -> _Result:
        task = asyncio.current_task()
        assert task is not None
        operation.set_result(task)
        return await awaitable

    tracked_awaitable = tracked()
    try:
        future: Future[_Result] = asyncio.run_coroutine_threadsafe(
            tracked_awaitable, loop
        )
    except RuntimeError:
        tracked_awaitable.close()
        awaitable.close()
        raise
    if active is not None:
        active.result = future
    deadline = monotonic() + timeout_s
    while True:
        # Preserve an already completed emission or provider error even if Core
        # requested stop before this worker observed that completion.
        if future.done():
            try:
                return future.result()
            except FutureCancelledError as error:
                raise asyncio.CancelledError(
                    "asyncio Source operation was cancelled"
                ) from error
        if cancellation is not None and cancellation.cancelled:
            return _interrupt_source(loop, operation, future, deadline=deadline)
        remaining = deadline - monotonic()
        if remaining <= 0:
            _request_source_interruption(loop, operation)
            raise TimeoutError(
                f"asyncio Source operation exceeded {timeout_s:g} seconds; "
                "cancellation cleanup may be incomplete"
            )
        try:
            return future.result(min(remaining, 0.05))
        except FutureTimeoutError:
            continue
        except FutureCancelledError as error:
            raise asyncio.CancelledError(
                "asyncio Source operation was cancelled"
            ) from error


def _interrupt_source(
    loop: asyncio.AbstractEventLoop,
    operation: Future[asyncio.Task[_Result]],
    result: Future[_Result],
    *,
    deadline: float,
) -> _Result:
    acknowledged = _request_source_interruption(loop, operation)
    try:
        interrupted = acknowledged.result(max(0, deadline - monotonic()))
        try:
            # Cancelling the concurrent Future would return before task cleanup.
            # Await the actual task's completion before Core calls drain or close.
            return result.result(max(0, deadline - monotonic()))
        except FutureCancelledError as error:
            if interrupted:
                raise _SourceInterrupted(
                    "Core interrupted the asyncio Source"
                ) from error
            raise asyncio.CancelledError(
                "asyncio Source operation was cancelled"
            ) from error
    except FutureTimeoutError as error:
        if result.done():
            # FutureTimeoutError aliases TimeoutError. Keep a provider's own
            # completed timeout exception instead of relabelling it as our wait.
            raise
        raise TimeoutError(
            "asyncio Source interruption exceeded the operation deadline; "
            "cancellation cleanup may be incomplete"
        ) from error


def _request_source_interruption(
    loop: asyncio.AbstractEventLoop,
    operation: Future[asyncio.Task[_Result]],
) -> Future[bool]:
    async def request_interruption() -> bool:
        task = await asyncio.wrap_future(operation)
        # Preserve a provider's own cancellation, including its cleanup error.
        return task.cancel() if not task.cancelling() else False

    request = request_interruption()
    try:
        return asyncio.run_coroutine_threadsafe(request, loop)
    except RuntimeError:
        request.close()
        raise


__all__ = [
    "RegisteredSource",
    "SourceCancellation",
    "SourceConfigValidator",
    "SourceDeadlines",
    "SourceDriver",
    "SourceDriverBuilder",
    "SourceEmission",
    "SourceFactory",
    "SourceIterableFactory",
    "SourceManifest",
    "SourcePrepareContext",
    "SourceProvider",
    "source",
]
