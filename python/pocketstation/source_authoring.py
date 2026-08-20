"""Python-authored typed Sources over the canonical Core source lifecycle."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Protocol, TypeAlias, runtime_checkable

from ._native import Session as _NativeSession
from ._native import _RegisteredSource as _NativeRegisteredSource
from ._native import _SourceCancellation as _NativeSourceCancellation
from ._native import _SourceEmission as _NativeSourceEmission
from ._native import _SourceManifest as _NativeSourceManifest
from ._native import _SourceOutputIdentity as _NativeSourceOutputIdentity
from ._native import _SourcePrepareContext as _NativeSourcePrepareContext
from .errors import _native_call
from .graph import PortSpec, SignalSpec, SourceConfiguration, SourceInstance


class _SessionOwner(Protocol):
    _native: _NativeSession

    def source(
        self, source_type_id: str, configuration: SourceConfiguration | None = None
    ) -> SourceInstance: ...


@dataclass(frozen=True, slots=True)
class SourceManifest:
    """Stable contract for one Python-authored typed Source implementation."""

    source_type_id: str
    outputs: tuple[PortSpec, ...]
    revision: int = 1
    implementation_generation: int = 1
    _native: _NativeSourceManifest = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativeSourceManifest(
                self.source_type_id,
                [output._native for output in self.outputs],
                self.revision,
                self.implementation_generation,
            )
        )
        object.__setattr__(self, "_native", native)


@dataclass(frozen=True, slots=True)
class SourceOutputIdentity:
    """Session-owned identity assigned to one prepared Source output."""

    output_port: str
    stream_id: int

    @classmethod
    def _from_native(cls, value: _NativeSourceOutputIdentity) -> SourceOutputIdentity:
        return cls(value.output_port, value.stream_id)


@dataclass(frozen=True, slots=True)
class SourcePrepareContext:
    """Immutable Session identity supplied before the Source starts."""

    source_type_id: str
    session_id: int | None
    source_id: int | None
    outputs: tuple[SourceOutputIdentity, ...]

    @classmethod
    def _from_native(cls, value: _NativeSourcePrepareContext) -> SourcePrepareContext:
        return cls(
            source_type_id=value.source_type_id,
            session_id=value.session_id,
            source_id=value.source_id,
            outputs=tuple(
                SourceOutputIdentity._from_native(item) for item in value.outputs
            ),
        )


class SourceCancellation:
    """Read-only cancellation signal owned by the Core Source runtime."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeSourceCancellation) -> None:
        self._native = native

    @property
    def cancelled(self) -> bool:
        return self._native.cancelled


class SourceEmission:
    """One typed Source value; Core attaches exact Session lineage."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeSourceEmission) -> None:
        self._native = native

    @classmethod
    def text(
        cls,
        output_port: str,
        payload: str,
        *,
        signal: SignalSpec,
        source_timestamp_ns: int | None = None,
        observed_timestamp_ns: int | None = None,
        duration_ns: int | None = None,
        source_generation: int = 1,
        discontinuity_epoch: int = 0,
        policy_epoch: int = 0,
        clock_domain_id: int = 1,
        terminal: bool = False,
    ) -> SourceEmission:
        return cls(
            _native_call(
                lambda: _NativeSourceEmission.text(
                    output_port,
                    payload,
                    signal._native,
                    source_timestamp_ns,
                    observed_timestamp_ns,
                    duration_ns,
                    source_generation,
                    discontinuity_epoch,
                    policy_epoch,
                    clock_domain_id,
                    terminal,
                )
            )
        )

    @classmethod
    def bytes(
        cls,
        output_port: str,
        payload: bytes,
        *,
        signal: SignalSpec,
        source_timestamp_ns: int | None = None,
        observed_timestamp_ns: int | None = None,
        duration_ns: int | None = None,
        source_generation: int = 1,
        discontinuity_epoch: int = 0,
        policy_epoch: int = 0,
        clock_domain_id: int = 1,
        terminal: bool = False,
    ) -> SourceEmission:
        return cls(
            _native_call(
                lambda: _NativeSourceEmission.bytes(
                    output_port,
                    payload,
                    signal._native,
                    source_timestamp_ns,
                    observed_timestamp_ns,
                    duration_ns,
                    source_generation,
                    discontinuity_epoch,
                    policy_epoch,
                    clock_domain_id,
                    terminal,
                )
            )
        )


class SourceDriver:
    """Blocking-worker Source behavior invoked outside realtime partitions."""

    def prepare(self, context: SourcePrepareContext) -> None:
        """Acquire resources after Core has assigned Session identities."""

    def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources exactly once."""


@runtime_checkable
class SourceFactory(Protocol):
    """Reusable factory retained by one canonical Session."""

    def validate_config(self, configuration: Mapping[str, str]) -> None: ...

    def create(self, configuration: Mapping[str, str]) -> SourceDriver: ...


SourceIterableFactory: TypeAlias = Callable[
    [Mapping[str, str]], Iterable[SourceEmission]
]
SourceConfigValidator: TypeAlias = Callable[[Mapping[str, str]], None]


class _IterableDriver(SourceDriver):
    __slots__ = ("_iterator",)

    def __init__(self, values: Iterable[SourceEmission]) -> None:
        self._iterator: Iterator[SourceEmission] = iter(values)

    def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        if cancellation.cancelled:
            return None
        return next(self._iterator, None)


class _IterableFactory:
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

    def create(self, configuration: Mapping[str, str]) -> SourceDriver:
        return _IterableDriver(self._factory(configuration))


@dataclass(frozen=True, slots=True)
class SourceProvider:
    """Reusable Python implementation of one Core Source contract."""

    manifest: SourceManifest
    factory: SourceFactory

    @classmethod
    def with_driver(
        cls, manifest: SourceManifest, factory: SourceFactory
    ) -> SourceProvider:
        return cls(manifest, factory)

    @classmethod
    def from_iterable(
        cls,
        manifest: SourceManifest,
        factory: SourceIterableFactory,
        *,
        validate_config: SourceConfigValidator | None = None,
    ) -> SourceProvider:
        return cls(manifest, _IterableFactory(factory, validate_config))


class _NativeDriverAdapter:
    __slots__ = ("_driver",)

    def __init__(self, driver: SourceDriver) -> None:
        self._driver = driver

    def prepare(self, context: _NativeSourcePrepareContext) -> None:
        self._driver.prepare(SourcePrepareContext._from_native(context))

    def next(
        self, cancellation: _NativeSourceCancellation
    ) -> _NativeSourceEmission | None:
        emission = self._driver.next(SourceCancellation(cancellation))
        return None if emission is None else emission._native

    def close(self) -> None:
        self._driver.close()


class _NativeFactoryAdapter:
    __slots__ = ("_factory",)

    def __init__(self, factory: SourceFactory) -> None:
        self._factory = factory

    def validate_config(self, configuration: Mapping[str, str]) -> None:
        self._factory.validate_config(configuration)

    def create(self, configuration: Mapping[str, str]) -> _NativeDriverAdapter:
        driver = self._factory.create(configuration)
        if not hasattr(driver, "next"):
            raise TypeError("Source factory must return a SourceDriver")
        return _NativeDriverAdapter(driver)


class RegisteredSource:
    """One Source implementation registered into one canonical Session."""

    __slots__ = ("_native", "_provider", "_session")

    def __init__(
        self,
        session: _SessionOwner,
        provider: SourceProvider,
        native: _NativeRegisteredSource,
    ) -> None:
        self._session = session
        self._provider = provider
        self._native = native

    @property
    def source_type_id(self) -> str:
        return self._native.source_type_id

    def declare(
        self, configuration: SourceConfiguration | None = None
    ) -> SourceInstance:
        return self._session.source(self.source_type_id, configuration)


def source(
    manifest: SourceManifest,
    *,
    validate_config: SourceConfigValidator | None = None,
) -> Callable[[SourceIterableFactory], SourceProvider]:
    """Decorate an iterable factory into a Core-backed typed Source."""

    def define(factory: SourceIterableFactory) -> SourceProvider:
        return SourceProvider.from_iterable(
            manifest,
            factory,
            validate_config=validate_config,
        )

    return define


__all__ = [
    "RegisteredSource",
    "SourceCancellation",
    "SourceConfigValidator",
    "SourceDriver",
    "SourceEmission",
    "SourceFactory",
    "SourceIterableFactory",
    "SourceManifest",
    "SourceOutputIdentity",
    "SourcePrepareContext",
    "SourceProvider",
    "source",
]
