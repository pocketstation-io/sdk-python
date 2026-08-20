"""Bridge call, agent, or transport PCM without a provider-specific engine."""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass

import pocketstation
import pocketstation.aio as pks_aio


@dataclass(frozen=True, slots=True)
class IncomingAudio:
    """One provider-decoded float32 PCM frame and its continuity boundary."""

    samples: object
    discontinuity: bool = False


def attach_audio_sender(
    session: pks_aio.Session,
    stream: pocketstation.Stem
    | pocketstation.SourceOutput
    | pocketstation.DerivedStream,
    sender: pks_aio.AudioConnectorHandler,
    *,
    connector_id: str,
    package_version: str,
    delivery_timeout_s: float = 5.0,
) -> pks_aio.RegisteredConnector:
    """Route one Session stream into any coroutine-based audio transport."""
    connector = pks_aio.Connector.from_audio_handler(
        connector_id,
        sender,
        package_version=package_version,
        deadlines=pks_aio.ConnectorDeadlines(delivery_s=delivery_timeout_s),
    )
    registered = session.register_connector(connector)
    stream.send(registered.declare())
    return registered


async def ingest_audio(
    target: pks_aio.AudioInput,
    frames: AsyncIterable[IncomingAudio],
    *,
    write_timeout_s: float = 1.0,
) -> None:
    """Feed provider-owned PCM into one bounded source and close it exactly once."""
    try:
        async for frame in frames:
            await target.write(
                frame.samples,
                discontinuity=frame.discontinuity,
                timeout_s=write_timeout_s,
            )
    finally:
        await target.close()


__all__ = ["IncomingAudio", "attach_audio_sender", "ingest_audio"]
