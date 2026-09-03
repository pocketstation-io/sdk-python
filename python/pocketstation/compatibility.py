"""Machine-readable compatibility facts for the installed SDK build."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeCompatibility:
    """Native component and interpreter versions embedded by the wheel."""

    sdk_version: str
    core_version: str
    relay_connector_version: str
    python_requires: str
    python_abi: str
    free_threaded_cpython: bool


RUNTIME_COMPATIBILITY = RuntimeCompatibility(
    sdk_version="0.1.2",
    core_version="1.1.5",
    relay_connector_version="0.1.2",
    python_requires=">=3.11",
    python_abi="abi3-py311",
    free_threaded_cpython=False,
)


__all__ = ["RUNTIME_COMPATIBILITY", "RuntimeCompatibility"]
