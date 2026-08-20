"""Asyncio Operator authoring over Core's bounded Operator runtime."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping, Sequence
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, Protocol, TypeAlias, TypeVar, runtime_checkable

from ..operator_authoring import (
    OperatorConfigValidator,
    OperatorEmission,
    OperatorManifest,
    OperatorPrepareContext,
    RegisteredOperator,
)
from ..operator_authoring import OperatorNode as SyncOperatorNode
from ..operator_authoring import OperatorProvider as SyncOperatorProvider
from ..signal import SignalEnvelope

_Result = TypeVar("_Result")


@dataclass(frozen=True, slots=True)
class OperatorDeadlines:
    """Finite waits while Core awaits asyncio Operator work."""

    create_s: float = 5.0
    prepare_s: float = 5.0
    process_s: float = 30.0
    close_s: float = 5.0

    def __post_init__(self) -> None:
        for name, value in (
            ("create_s", self.create_s),
            ("prepare_s", self.prepare_s),
            ("process_s", self.process_s),
            ("close_s", self.close_s),
        ):
            if not 0 < value <= 300:
                raise ValueError(f"{name} must be greater than 0 and at most 300")


class OperatorNode:
    async def prepare(self, context: OperatorPrepareContext) -> None:
        """Observe compiled port and edge contracts before processing."""

    async def process(
        self, input_port: str, envelope: SignalEnvelope
    ) -> Sequence[OperatorEmission]:
        raise NotImplementedError

    async def flush(self) -> Sequence[OperatorEmission]:
        return ()

    async def cancel(self) -> None:
        """Cancel provider work after Core requests cancellation."""

    async def close(self) -> None:
        """Release provider resources exactly once."""


@runtime_checkable
class OperatorFactory(Protocol):
    def validate_config(self, configuration: Mapping[str, str]) -> None: ...

    async def create(self, configuration: Mapping[str, str]) -> OperatorNode: ...


OperatorNodeBuilder: TypeAlias = Callable[
    [Mapping[str, str]], Coroutine[Any, Any, OperatorNode]
]
OperatorHandler: TypeAlias = Callable[
    [str, SignalEnvelope], Coroutine[Any, Any, Sequence[OperatorEmission]]
]


class _HandlerNode(OperatorNode):
    __slots__ = ("_handler",)

    def __init__(self, handler: OperatorHandler) -> None:
        self._handler = handler

    async def process(
        self, input_port: str, envelope: SignalEnvelope
    ) -> Sequence[OperatorEmission]:
        return await self._handler(input_port, envelope)


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

    async def create(self, _configuration: Mapping[str, str]) -> OperatorNode:
        return _HandlerNode(self._handler)


class _NodeAdapter(SyncOperatorNode):
    __slots__ = ("_deadlines", "_loop", "_node")

    def __init__(
        self,
        node: OperatorNode,
        loop: asyncio.AbstractEventLoop,
        deadlines: OperatorDeadlines,
    ) -> None:
        self._node = node
        self._loop = loop
        self._deadlines = deadlines

    def prepare(self, context: OperatorPrepareContext) -> None:
        _wait_for_operator(
            self._loop,
            self._node.prepare(context),
            timeout_s=self._deadlines.prepare_s,
        )

    def process(
        self, input_port: str, envelope: SignalEnvelope
    ) -> Sequence[OperatorEmission]:
        return _wait_for_operator(
            self._loop,
            self._node.process(input_port, envelope),
            timeout_s=self._deadlines.process_s,
        )

    def flush(self) -> Sequence[OperatorEmission]:
        return _wait_for_operator(
            self._loop,
            self._node.flush(),
            timeout_s=self._deadlines.process_s,
        )

    def cancel(self) -> None:
        _wait_for_operator(
            self._loop,
            self._node.cancel(),
            timeout_s=self._deadlines.close_s,
        )

    def close(self) -> None:
        _wait_for_operator(
            self._loop,
            self._node.close(),
            timeout_s=self._deadlines.close_s,
        )


class _FactoryAdapter:
    __slots__ = ("_deadlines", "_factory", "_loop")

    def __init__(
        self,
        factory: OperatorFactory | OperatorNodeBuilder,
        loop: asyncio.AbstractEventLoop,
        deadlines: OperatorDeadlines,
    ) -> None:
        self._factory = factory
        self._loop = loop
        self._deadlines = deadlines

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        validator = getattr(self._factory, "validate_config", None)
        if validator is not None:
            validator(configuration)

    def create(self, configuration: Mapping[str, str]) -> _NodeAdapter:
        create = getattr(self._factory, "create", None)
        awaitable = (
            self._factory(configuration)  # type: ignore[operator]
            if create is None
            else create(configuration)
        )
        node = _wait_for_operator(
            self._loop,
            awaitable,
            timeout_s=self._deadlines.create_s,
        )
        if not hasattr(node, "process"):
            raise TypeError("async Operator factory must return an OperatorNode")
        return _NodeAdapter(node, self._loop, self._deadlines)


@dataclass(frozen=True, slots=True)
class OperatorProvider:
    manifest: OperatorManifest
    factory: OperatorFactory | OperatorNodeBuilder
    deadlines: OperatorDeadlines = OperatorDeadlines()

    def __post_init__(self) -> None:
        if self.deadlines.process_s * 1_000 > self.manifest.process_timeout_ms:
            raise ValueError(
                "async Operator process deadline cannot exceed the Core "
                "manifest deadline"
            )

    @classmethod
    def with_node(
        cls,
        manifest: OperatorManifest,
        factory: OperatorFactory | OperatorNodeBuilder,
        *,
        deadlines: OperatorDeadlines | None = None,
    ) -> OperatorProvider:
        selected = deadlines or OperatorDeadlines(
            process_s=manifest.process_timeout_ms / 1_000
        )
        return cls(manifest, factory, selected)

    @classmethod
    def from_handler(
        cls,
        manifest: OperatorManifest,
        handler: OperatorHandler,
        *,
        validate_config: OperatorConfigValidator | None = None,
        deadlines: OperatorDeadlines | None = None,
    ) -> OperatorProvider:
        return cls.with_node(
            manifest,
            _HandlerFactory(handler, validate_config),
            deadlines=deadlines,
        )

    def _bind(self, loop: asyncio.AbstractEventLoop) -> SyncOperatorProvider:
        if not loop.is_running():
            raise RuntimeError("async Operator requires a running event loop")
        return SyncOperatorProvider.with_node(
            self.manifest,
            _FactoryAdapter(self.factory, loop, self.deadlines),
        )


def operator(
    manifest: OperatorManifest,
    *,
    validate_config: OperatorConfigValidator | None = None,
    deadlines: OperatorDeadlines | None = None,
) -> Callable[[OperatorHandler], OperatorProvider]:
    """Decorate one coroutine into a Core-backed typed Operator."""

    def define(handler: OperatorHandler) -> OperatorProvider:
        return OperatorProvider.from_handler(
            manifest,
            handler,
            validate_config=validate_config,
            deadlines=deadlines,
        )

    return define


def _wait_for_operator(
    loop: asyncio.AbstractEventLoop,
    awaitable: Coroutine[Any, Any, _Result],
    *,
    timeout_s: float,
) -> _Result:
    try:
        future: Future[_Result] = asyncio.run_coroutine_threadsafe(awaitable, loop)
    except RuntimeError:
        awaitable.close()
        raise
    try:
        return future.result(timeout_s)
    except FutureTimeoutError as error:
        future.cancel()
        raise TimeoutError(
            f"asyncio Operator operation exceeded {timeout_s:g} seconds"
        ) from error
    except FutureCancelledError as error:
        raise asyncio.CancelledError(
            "asyncio Operator operation was cancelled"
        ) from error


__all__ = [
    "OperatorDeadlines",
    "OperatorFactory",
    "OperatorHandler",
    "OperatorManifest",
    "OperatorNode",
    "OperatorNodeBuilder",
    "OperatorProvider",
    "RegisteredOperator",
    "operator",
]
