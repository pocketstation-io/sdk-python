"""Typed source declarations, discovery, permissions, and runtime identity."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ._native import CaptureAuthorizationSnapshot as _NativeCaptureAuthorizationSnapshot
from ._native import CapturePermissionLifecycle as _NativeCapturePermissionLifecycle
from ._native import CapturePermissionTransition as _NativeCapturePermissionTransition
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
from .identity import SourceId


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


class CapturePermissionTransitionKind(StrEnum):
    CHANGED = "permission-changed"
    REVOKED = "permission-revoked"


class CaptureCapabilityState(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"


class ApplicationPolicyObservation(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_OBSERVABLE = "not-observable"
    NOT_APPLICABLE = "not-applicable"


class CaptureSessionGrant(StrEnum):
    GRANTED_BY_EXPLICIT_SELECTION = "granted-by-explicit-selection"
    DENIED = "denied"
    NOT_EVALUATED = "not-evaluated"


class CaptureScopeKind(StrEnum):
    EXACT_APPLICATION = "exact-application"
    EXACT_INPUT_DEVICE = "exact-input-device"
    EXACT_OUTPUT_DEVICE = "exact-output-device"
    SYSTEM_MIX = "system-mix"


class CaptureOpenOutcome(StrEnum):
    NOT_ATTEMPTED = "not-attempted"
    SUCCEEDED = "succeeded"
    PERMISSION_DENIED = "permission-denied"
    SOURCE_UNAVAILABLE = "source-unavailable"
    BACKEND_FAILED = "backend-failed"


@dataclass(frozen=True, slots=True)
class CaptureAuthorizationSnapshot:
    """Point-in-time authorization evidence for one exact discovered source."""

    capability: CaptureCapabilityState
    os_permission: PermissionObservation
    application_policy: ApplicationPolicyObservation
    session_grant: CaptureSessionGrant
    capture_scope: CaptureScopeKind
    scope_stable_id: str | None
    identity_strength: SourceIdentityStrength
    permission_epoch: int
    observed_at_ns: int
    open_outcome: CaptureOpenOutcome

    @classmethod
    def _from_native(
        cls, snapshot: _NativeCaptureAuthorizationSnapshot
    ) -> CaptureAuthorizationSnapshot:
        return cls(
            capability=CaptureCapabilityState(snapshot.capability),
            os_permission=PermissionObservation(snapshot.os_permission),
            application_policy=ApplicationPolicyObservation(
                snapshot.application_policy
            ),
            session_grant=CaptureSessionGrant(snapshot.session_grant),
            capture_scope=CaptureScopeKind(snapshot.capture_scope),
            scope_stable_id=snapshot.scope_stable_id,
            identity_strength=SourceIdentityStrength(snapshot.identity_strength),
            permission_epoch=snapshot.permission_epoch,
            observed_at_ns=snapshot.observed_at_ns,
            open_outcome=CaptureOpenOutcome(snapshot.open_outcome),
        )


@dataclass(frozen=True, slots=True)
class CapturePermissionTransition:
    """One authoritative host-supplied permission-state transition."""

    kind: CapturePermissionTransitionKind
    previous: PermissionObservation
    current: PermissionObservation
    permission_epoch: int

    @classmethod
    def _from_native(
        cls, transition: _NativeCapturePermissionTransition
    ) -> CapturePermissionTransition:
        return cls(
            kind=CapturePermissionTransitionKind(transition.kind),
            previous=PermissionObservation(transition.previous),
            current=PermissionObservation(transition.current),
            permission_epoch=transition.permission_epoch,
        )


class CapturePermissionLifecycle:
    """Track host-reported capture permission changes for one epoch.

    The host supplies authoritative platform observations. Equal observations
    produce no transition; PocketStation never converts generic backend errors
    into permission state.
    """

    def __init__(self, current: PermissionObservation) -> None:
        self._native = _native_call(
            lambda: _NativeCapturePermissionLifecycle(current.value)
        )

    @property
    def current(self) -> PermissionObservation:
        return PermissionObservation(self._native.current)

    @property
    def permission_epoch(self) -> int:
        return self._native.permission_epoch

    def observe(
        self, current: PermissionObservation
    ) -> CapturePermissionTransition | None:
        transition = _native_call(lambda: self._native.observe(current.value))
        return (
            None
            if transition is None
            else CapturePermissionTransition._from_native(transition)
        )


class SourceSelectorKind(StrEnum):
    APPLICATION_NAME = "application-name"
    APPLICATION_BUNDLE_ID = "application-bundle-id"
    APPLICATION_PROCESS_ID = "application-process-id"
    APPLICATION_STABLE_ID = "application-stable-id"
    APPLICATION_PROCESS_INSTANCE = "application-process-instance"
    MICROPHONE_DEFAULT = "microphone-default"
    MICROPHONE_ID = "microphone-id"
    SYSTEM_MIX = "system-mix"


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
    source_id: SourceId | None


@dataclass(frozen=True, slots=True)
class DiscoveredSource:
    """Immutable point-in-time result from native source discovery."""

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
    _native: _NativeDiscoveredSource | None = field(
        default=None, repr=False, compare=False
    )

    @classmethod
    def _from_native(cls, source: _NativeDiscoveredSource) -> DiscoveredSource:
        return cls(
            stable_id=StableSourceId(
                platform=Platform(source.platform),
                kind=SourceKind(source.kind),
                stable_key=source.stable_key,
                source_id=SourceId(source.source_id),
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
            _native=source,
        )

    def authorization_before_open(
        self,
        *,
        os_permission: PermissionObservation = PermissionObservation.NOT_OBSERVABLE,
        application_policy: ApplicationPolicyObservation = (
            ApplicationPolicyObservation.NOT_OBSERVABLE
        ),
        session_grant: CaptureSessionGrant = CaptureSessionGrant.NOT_EVALUATED,
        permission_epoch: int = 1,
    ) -> CaptureAuthorizationSnapshot:
        """Create truthful pre-open evidence without inferring backend success."""
        native = self._native
        if native is None:
            raise ValueError(
                "authorization evidence requires a native discovery result"
            )
        snapshot = _native_call(
            lambda: native.authorization_before_open(
                os_permission.value,
                application_policy.value,
                session_grant.value,
                permission_epoch,
            )
        )
        return CaptureAuthorizationSnapshot._from_native(snapshot)


@dataclass(frozen=True, slots=True)
class SourceQuery:
    """Describe a typed query for the native source provider to execute."""

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
    """Immutable Source declaration compiled by the Rust ``Session``."""

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

        Output devices and system mix remain discovery-only in the stable 1.1
        Session declaration contract.
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


def _capture_application(application: str | int) -> Source:
    """Resolve the concise capture façade's name-or-process selector."""
    if isinstance(application, int):
        return Source.application_process_id(application)
    if application.isascii() and application.isdecimal():
        return Source.application_process_id(int(application))
    if application.startswith("app:"):
        process_id = application.removeprefix("app:")
        if not process_id.isascii() or not process_id.isdecimal():
            raise ValueError("app: application selector must contain a process ID")
        return Source.application_process_id(int(process_id))
    if application.startswith("bundle:"):
        return Source.application_bundle_id(application.removeprefix("bundle:"))
    return Source.application(application)


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
                source_id=SourceId(event.source_source_id),
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

    Linux, Python hosts on Windows with Core 1.1.4, and any backend without an
    authoritative query return :attr:`PermissionObservation.NOT_OBSERVABLE`;
    callers must not reinterpret it as allowed or denied.
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
    "ApplicationPolicyObservation",
    "CaptureAuthorizationSnapshot",
    "CaptureCapabilityState",
    "CaptureOpenOutcome",
    "CapturePermissionLifecycle",
    "CapturePermissionTransition",
    "CapturePermissionTransitionKind",
    "CaptureScopeKind",
    "CaptureSessionGrant",
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
