"""Versioned compiled-extension descriptors backed by PocketStation's C ABI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ._native import _NativeExtensionLibrary, _NativeExtensionRegistration
from ._native import extension_abi_is_compatible as _abi_is_compatible
from ._native import extension_abi_version as _abi_version
from ._native import validate_extension_descriptor as _validate_descriptor
from .errors import _native_call


class ExtensionKind(StrEnum):
    """Open compiled extension roles admitted by ABI 1.x."""

    SOURCE = "source"
    OPERATOR = "operator"
    ENDPOINT = "endpoint"


class ExtensionPortDirection(StrEnum):
    """Direction of one named typed-signal port."""

    INPUT = "input"
    OUTPUT = "output"


@dataclass(frozen=True, slots=True)
class ExtensionAbiVersion:
    """Native authority for the linked PocketStation extension ABI."""

    struct_size_bytes: int
    abi_major: int
    abi_minor: int

    @classmethod
    def current(cls) -> ExtensionAbiVersion:
        value = _native_call(_abi_version)
        return cls(
            struct_size_bytes=value.struct_size_bytes,
            abi_major=value.abi_major,
            abi_minor=value.abi_minor,
        )

    def require_compatible(self) -> None:
        _native_call(
            lambda: _abi_is_compatible(
                self.abi_major,
                self.abi_minor,
                self.struct_size_bytes,
            )
        )


@dataclass(frozen=True, slots=True)
class ExtensionPort:
    """One versioned named port preserving SignalSpec wire identity."""

    name: str
    direction: ExtensionPortDirection
    signal_id: str
    required: bool = True
    semantic_role: str = ""
    schema: str = ""

    def _native_tuple(self) -> tuple[str, str, bool, str, str, str]:
        return (
            self.name,
            self.direction.value,
            self.required,
            self.signal_id,
            self.semantic_role,
            self.schema,
        )


@dataclass(frozen=True, slots=True)
class ExtensionDescriptor:
    """Copied source, operator, or endpoint ABI descriptor.

    Construction validates the complete record using the linked frozen native
    ABI. This object is a descriptor, not an executable Python callback.
    """

    extension_id: str
    kind: ExtensionKind
    ports: tuple[ExtensionPort, ...]
    revision: int = 1
    generation: int = 1
    abi_major: int | None = None
    abi_minor: int | None = None

    def __post_init__(self) -> None:
        ports = tuple(self.ports)
        if any(not isinstance(port, ExtensionPort) for port in ports):
            raise TypeError("ports must contain only ExtensionPort values")
        object.__setattr__(self, "ports", ports)
        current = ExtensionAbiVersion.current()
        major = current.abi_major if self.abi_major is None else self.abi_major
        minor = current.abi_minor if self.abi_minor is None else self.abi_minor
        _native_call(
            lambda: _validate_descriptor(
                self.extension_id,
                self.kind.value,
                self.revision,
                self.generation,
                major,
                minor,
                [port._native_tuple() for port in ports],
            )
        )
        object.__setattr__(self, "abi_major", major)
        object.__setattr__(self, "abi_minor", minor)


@dataclass(frozen=True, slots=True)
class NativeExtensionRegistration:
    """One source, operator, or endpoint imported into a Session."""

    id: str
    kind: ExtensionKind
    revision: int
    generation: int

    @classmethod
    def _from_native(
        cls,
        native: _NativeExtensionRegistration,
    ) -> NativeExtensionRegistration:
        return cls(
            id=native.id,
            kind=ExtensionKind(native.kind),
            revision=native.revision,
            generation=native.generation,
        )


@dataclass(frozen=True, slots=True)
class NativeExtensionLibrary:
    """Immutable receipt for one library imported into a native Session."""

    canonical_path: Path
    registrations: tuple[NativeExtensionRegistration, ...]

    @classmethod
    def _from_native(cls, native: _NativeExtensionLibrary) -> NativeExtensionLibrary:
        return cls(
            canonical_path=Path(native.canonical_path),
            registrations=tuple(
                NativeExtensionRegistration._from_native(registration)
                for registration in native.registrations
            ),
        )


__all__ = [
    "ExtensionAbiVersion",
    "ExtensionDescriptor",
    "ExtensionKind",
    "ExtensionPort",
    "ExtensionPortDirection",
    "NativeExtensionLibrary",
    "NativeExtensionRegistration",
]
