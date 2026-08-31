"""Asyncio access to shared native source discovery and permission policy."""

from __future__ import annotations

import asyncio

from ..sources import (
    DiscoveredSource,
    PermissionObservation,
    SourceQuery,
)
from ..sources import (
    application_capture_available as _application_capture_available,
)
from ..sources import discover_sources as _discover_sources
from ..sources import (
    microphone_permission_observation as _microphone_permission_observation,
)


async def discover_sources(
    query: SourceQuery | None = None,
) -> tuple[DiscoveredSource, ...]:
    """Run native source discovery without blocking the asyncio event loop."""
    return await asyncio.to_thread(_discover_sources, query)


async def application_capture_available() -> bool:
    """Read the native application-capture capability off the event loop."""
    return await asyncio.to_thread(_application_capture_available)


async def microphone_permission_observation() -> PermissionObservation:
    """Read the current microphone authorization without prompting."""
    return _microphone_permission_observation()


__all__ = [
    "application_capture_available",
    "discover_sources",
    "microphone_permission_observation",
]
