from __future__ import annotations

import asyncio
from array import array

import pocketstation
import pocketstation.aio as pks_aio
import pytest

from examples.integrations import IncomingAudio, attach_audio_sender, ingest_audio


@pytest.mark.asyncio
async def test_call_audio_template_uses_core_source_and_connector() -> None:
    delivered = asyncio.Event()
    received = []

    async def send(frame, context):
        received.append(frame)
        delivered.set()
        return pocketstation.ConnectorDeliveryOutcome.DELIVERED

    async def incoming():
        yield IncomingAudio(array("f", [0.1, 0.2, 0.3, 0.4]))

    session = pks_aio.Session(sample_rate_hz=16_000)
    caller = session.audio_input(
        "caller",
        sample_rate_hz=16_000,
        frame_samples_per_channel=4,
    )
    registered = attach_audio_sender(
        session,
        caller.output,
        send,
        connector_id="io.pocketstation.test.call.v1",
        package_version="1.0.0",
    )
    running = await session.start()
    await ingest_audio(caller, incoming())
    await asyncio.wait_for(delivered.wait(), 1.0)
    assert (await running.stop()).success
    assert received[0].source_id == caller.source_id
    assert received[0].stream_id == caller.stream_id
    [observation] = await registered.observations()
    assert observation.frames_delivered_total == 1
