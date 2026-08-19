"""Typed source declarations, discovery, permissions, and runtime identity."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ._native import DiscoveredSource as _NativeDiscoveredSource
from ._native import SessionEvent as _NativeSessionEvent
from ._native import Source as _NativeSource
from ._native import (
    application_capture_available as _native_application_capture_available,
)
from ._native import discover_sources as _native_discover_sources
from ._native import (
    microphone_permission_observation as _native_microphone_permission_observation,
)
from .errors import PocketStationError, _native_call


class Platform(StrEnum):
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    UNKNOWN = "unknown"


class SourceKind(StrEnum):
    APPLICATION = "application"
    OUTPUT_DEVICE = "output-device"
    INPUT_DEVICE = "input-device"
    SYSTEM_MIX = "system-mix"


class SourceState(StrEnum):
    AVAILABLE = "available"
    PLAYING = "playing"
    SILENT = "silent"
    UNAVAILABLE = "unavailable"
    PERMISSION_BLOCKED = "permission-blocked"


class SourceIdentityStrength(StrEnum):
    APPLICATION_ID_AND_PROCESS_ID = "application-id-and-process-id"
    STABLE_APPLICATION_ID = "stable-application-id"
    PROCESS_ID = "process-id"
    STABLE_DEVICE_UID = "stable-device-uid"
    PLATFORM_STABLE_ID = "platform-stable-id"


class SelectorPersistenceScope(StrEnum):
    PROCESS_LIFETIME = "process-lifetime"
    APPLICATION_IDENTITY = "application-identity"
    DEVICE_IDENTITY = "device-identity"
    SESSION_DEFAULT_DEVICE = "session-default-device"
    PLATFORM_IDENTITY = "platform-identity"


class ProcessTreeScope(StrEnum):
    SELECTED_PROCESS_ONLY = "selected-process-only"
    SELECTED_PROCESS_AND_DESCENDANTS = "selected-process-and-descendants"
    APPLICATION_IDENTITY = "application-identity"
    NOT_APPLICABLE = "not-applicable"


class PermissionObservation(StrEnum):
    """Authoritative permission observation, never a prompt result guess."""

    ALLOWED = "allowed"
    DENIED = "denied"
    RESTRICTED = "restricted"
    NOT_DETERMINED = "not-determined"
    REVOKED = "revoked"
    NOT_OBSERVABLE = "not-observable"
    NOT_APPLICABLE = "not-applicable"


class SourceSelectorKind(StrEnum):
    APPLICATION_NAME = "application-name"
    APPLICATION_BUNDLE_ID = "application-bundle-id"
    APPLICATION_PROCESS_ID = "application-process-id"
    APPLICATION_STABLE_ID = "application-stable-id"
    APPLICATION_PROCESS_INSTANCE = "application-process-instance"
    MICROPHONE_DEFAULT = "microphone-default"
    MICROPHONE_ID = "microphone-id"


class SourceRuntimeEventKind(StrEnum):
    SOURCE_UNAVAILABLE = "source-unavailable"
    BACKEND_FAILURE = "backend-failure"


class SourceRecoveryRequirement(StrEnum):
    EXPLICIT_REDISCOVERY_AND_NEW_SESSION = "explicit-rediscovery-and-new-session"


class SourceFailureClass(StrEnum):
    SOURCE_INSTANCE_EXITED = "source-instance-exited"
    PLATFORM_STATUS = "platform-status"
    BACKEND_CLASS = "backend-class"


@dataclass(frozen=True, slots=True)
class StableSourceId:
    """Version-stable native source identity projected without re-hashing."""

    platform: Platform
    kind: SourceKind
    stable_key: str
    source_id: int | None


@dataclass(frozen=True, slots=True)
class DiscoveredSource:
    """Immutable point-in-time result from the canonical Rust discovery query."""

    stable_id: StableSourceId
    name: str
    process_id: int | None
    application_id: str | None
    device_uid: str | None
    state: SourceState
    sample_rate_hz: int
    channel_count: int
    identity_strength: SourceIdentityStrength
    selector_persistence_scope: SelectorPersistenceScope | None
    process_tree_scope: ProcessTreeScope | None

    @classmethod
    def _from_native(cls, source: _NativeDiscoveredSource) -> DiscoveredSource:
        return cls(
            stable_id=StableSourceId(
                platform=Platform(source.platform),
                kind=SourceKind(source.kind),
                stable_key=source.stable_key,
                source_id=source.source_id,
            ),
            name=source.name,
            process_id=source.process_id,
            application_id=source.application_id,
            device_uid=source.device_uid,
            state=SourceState(source.state),
            sample_rate_hz=source.sample_rate_hz,
            channel_count=source.channel_count,
            identity_strength=SourceIdentityStrength(source.identity_strength),
            selector_persistence_scope=(
                None
                if source.selector_persistence_scope is None
                else SelectorPersistenceScope(source.selector_persistence_scope)
            ),
            process_tree_scope=(
                None
                if source.process_tree_scope is None
                else ProcessTreeScope(source.process_tree_scope)
            ),
        )


@dataclass(frozen=True, slots=True)
class SourceQuery:
    """Typed query executed by the canonical Rust source provider."""

    _query_kind: str = "any"
    _value: str | None = None

    @classmethod
    def any(cls) -> SourceQuery:
        return cls()

    @classmethod
    def application(cls, name: str) -> SourceQuery:
        return cls("application", _require_nonempty("application query", name))

    @classmethod
    def kind(cls, kind: SourceKind) -> SourceQuery:
        return cls("kind", kind.value)

    @classmethod
    def stable_key(cls, stable_key: str) -> SourceQuery:
        return cls("stable-key", _require_nonempty("stable source key", stable_key))

    @classmethod
    def playing(cls) -> SourceQuery:
        return cls("playing")


@dataclass(frozen=True, slots=True)
class ProcessInstanceSelector:
    process_id: int
    stable_id: StableSourceId


SourceSelectorValue = str | int | StableSourceId | ProcessInstanceSelector | None


@dataclass(frozen=True, slots=True)
class Source:
    """Immutable declaration lowered by the canonical Rust ``Session``."""

    _native: _NativeSource = field(repr=False)
    kind: SourceKind
    selector_kind: SourceSelectorKind
    selector_value: SourceSelectorValue = None

    @classmethod
    def application(cls, name: str) -> Source:
        """Select one application by its display name."""
        native = _native_call(lambda: _NativeSource.application(name))
        return cls(
            native,
            SourceKind.APPLICATION,
            SourceSelectorKind.APPLICATION_NAME,
            name,
        )

    @classmethod
    def application_bundle_id(cls, bundle_id: str) -> Source:
        """Select one application by an OS bundle/application identifier."""
        native = _native_call(lambda: _NativeSource.application_bundle_id(bundle_id))
        return cls(
            native,
            SourceKind.APPLICATION,
            SourceSelectorKind.APPLICATION_BUNDLE_ID,
            bundle_id,
        )

    @classmethod
    def application_process_id(cls, process_id: int) -> Source:
        """Select the current process instance with the given process ID."""
        native = _native_call(lambda: _NativeSource.application_process_id(process_id))
        return cls(
            native,
            SourceKind.APPLICATION,
            SourceSelectorKind.APPLICATION_PROCESS_ID,
            process_id,
        )

    @classmethod
    def application_stable_id(
        cls,
        platform: Platform | str,
        stable_key: str,
    ) -> Source:
        """Select one application by its PocketStation stable source key."""
        platform_value = _platform_value(platform)
        native = _native_call(
            lambda: _NativeSource.application_stable_id(platform_value, stable_key)
        )
        stable_id = StableSourceId(
            platform=Platform(platform_value),
            kind=SourceKind.APPLICATION,
            stable_key=stable_key,
            source_id=None,
        )
        return cls(
            native,
            SourceKind.APPLICATION,
            SourceSelectorKind.APPLICATION_STABLE_ID,
            stable_id,
        )

    @classmethod
    def application_process_instance(
        cls,
        process_id: int,
        platform: Platform | str,
        stable_key: str,
    ) -> Source:
        """Select an exact process instance and stable application identity."""
        platform_value = _platform_value(platform)
        native = _native_call(
            lambda: _NativeSource.application_process_instance(
                process_id,
                platform_value,
                stable_key,
            )
        )
        stable_id = StableSourceId(
            platform=Platform(platform_value),
            kind=SourceKind.APPLICATION,
            stable_key=stable_key,
            source_id=None,
        )
        return cls(
            native,
            SourceKind.APPLICATION,
            SourceSelectorKind.APPLICATION_PROCESS_INSTANCE,
            ProcessInstanceSelector(process_id, stable_id),
        )

    @classmethod
    def microphone_default(cls) -> Source:
        """Select the host default microphone for this Session open."""
        native = _native_call(_NativeSource.microphone_default)
        return cls(
            native,
            SourceKind.INPUT_DEVICE,
            SourceSelectorKind.MICROPHONE_DEFAULT,
        )

    @classmethod
    def microphone_id(cls, device_id: str) -> Source:
        """Select a microphone by its native stable device identifier."""
        native = _native_call(lambda: _NativeSource.microphone_id(device_id))
        return cls(
            native,
            SourceKind.INPUT_DEVICE,
            SourceSelectorKind.MICROPHONE_ID,
            device_id,
        )

    @classmethod
    def from_discovered(cls, source: DiscoveredSource) -> Source:
        """Build the strongest supported Session declaration from discovery.

        System mix and output devices can be discovered as host capabilities,
        but the frozen public ``Session`` does not expose them as built-in
        ``Source`` variants. This method rejects them instead of fabricating a
        lowering path.
        """
        stable_id = source.stable_id
        if stable_id.kind is SourceKind.APPLICATION:
            if source.process_id is not None:
                return cls.application_process_instance(
                    source.process_id,
                    stable_id.platform,
                    stable_id.stable_key,
                )
            return cls.application_stable_id(
                stable_id.platform,
                stable_id.stable_key,
            )
        if stable_id.kind is SourceKind.INPUT_DEVICE:
            return cls.microphone_id(source.device_uid or stable_id.stable_key)
        raise PocketStationError(
            "discovered "
            f"{stable_id.kind.value!r} is not a frozen built-in Session Source",
            "source.unsupported_session_kind",
        )


@dataclass(frozen=True, slots=True)
class SourceRuntimeEvent:
    """Typed native source disappearance or backend-failure observation."""

    kind: SourceRuntimeEventKind
    stable_id: StableSourceId
    generation: int
    recovery_requirement: SourceRecoveryRequirement | None
    operation: str
    failure_class: SourceFailureClass
    platform_status_code: int | None
    backend_class: str | None

    @classmethod
    def _from_native(cls, event: _NativeSessionEvent) -> SourceRuntimeEvent | None:
        if event.source_event_kind is None:
            return None
        if (
            event.source_platform is None
            or event.source_kind is None
            or event.source_stable_key is None
            or event.source_source_id is None
            or event.source_generation is None
            or event.source_failure_operation is None
            or event.source_failure_class is None
        ):
            raise PocketStationError(
                "native source event is incomplete",
                "source.invalid_runtime_event",
            )
        return cls(
            kind=SourceRuntimeEventKind(event.source_event_kind),
            stable_id=StableSourceId(
                platform=Platform(event.source_platform),
                kind=SourceKind(event.source_kind),
                stable_key=event.source_stable_key,
                source_id=event.source_source_id,
            ),
            generation=event.source_generation,
            recovery_requirement=(
                None
                if event.source_recovery_requirement is None
                else SourceRecoveryRequirement(event.source_recovery_requirement)
            ),
            operation=event.source_failure_operation,
            failure_class=SourceFailureClass(event.source_failure_class),
            platform_status_code=event.source_platform_status_code,
            backend_class=event.source_backend_class,
        )


def discover_sources(query: SourceQuery | None = None) -> tuple[DiscoveredSource, ...]:
    """Return one immutable native discovery snapshot for ``query``."""
    selected = SourceQuery.any() if query is None else query
    native_sources = _native_call(
        lambda: _native_discover_sources(selected._query_kind, selected._value)
    )
    return tuple(DiscoveredSource._from_native(source) for source in native_sources)


def application_capture_available() -> bool:
    """Read native application-capture capability without opening a source."""
    return _native_call(_native_application_capture_available)


def microphone_permission_observation() -> PermissionObservation:
    """Read microphone authorization without prompting.

    Linux and any backend without an authoritative query return
    :attr:`PermissionObservation.NOT_OBSERVABLE`; callers must not reinterpret
    it as allowed or denied.
    """
    observation = _native_call(_native_microphone_permission_observation)
    return PermissionObservation(observation)


def _require_nonempty(label: str, value: str) -> str:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")
    return value


def _platform_value(platform: Platform | str) -> str:
    return platform.value if isinstance(platform, Platform) else platform


__all__ = [
    "DiscoveredSource",
    "PermissionObservation",
    "Platform",
    "ProcessInstanceSelector",
    "ProcessTreeScope",
    "SelectorPersistenceScope",
    "Source",
    "SourceFailureClass",
    "SourceIdentityStrength",
    "SourceKind",
    "SourceQuery",
    "SourceRecoveryRequirement",
    "SourceRuntimeEvent",
    "SourceRuntimeEventKind",
    "SourceSelectorKind",
    "SourceState",
    "StableSourceId",
    "application_capture_available",
    "discover_sources",
    "microphone_permission_observation",
]
