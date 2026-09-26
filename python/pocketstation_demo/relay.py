"""Connect a demo to the small shared PocketStation Relay service."""

import os
from collections.abc import Sequence

import pocketstation.aio as pks

_CONTROL_PLANE_URL = "https://pocketstation-api.fly.dev"


async def demo_relay_session(
    *, required_buses: Sequence[str] = ("application", "microphone")
) -> pks.RelaySession:
    """Create a RelaySession for an example or a user-operated deployment."""
    control_plane_url = os.getenv("POCKETSTATION_CONTROL_URL", _CONTROL_PLANE_URL)
    return await pks.RelaySession.create(
        control_plane_url=control_plane_url,
        required_buses=tuple(required_buses),
    )


__all__ = ["demo_relay_session"]
