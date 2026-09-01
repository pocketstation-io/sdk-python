from __future__ import annotations

import asyncio
from array import array

import pocketstation as pks
import pocketstation.aio as pks_aio


class CollectingConnector(pks_aio.Connector):
    def __init__(self) -> None:
        self.started_total = 0
        self.stopped_total = 0
        self.received: list[pks.AudioFrame] = []
        self.delivered = asyncio.Event()

    async def start(self) -> None:
        self.started_total += 1

    async def send(self, frame: pks.AudioFrame) -> None:
        self.received.append(frame)
        if len(self.received) == 2:
            self.delivered.set()

    async def stop(self) -> None:
        self.stopped_total += 1


async def test_given_two_stems_when_sent_async_then_share_connector_lifecycle() -> None:
    destination = CollectingConnector()
    session = pks_aio.Session()
    application = session.audio_input("application", frame_samples_per_channel=4)
    microphone = session.audio_input("microphone", frame_samples_per_channel=4)
    application.output.send_to(destination)
    microphone.output.send_to(destination)

    running = await session.start()
    await application.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await microphone.write(array("f", [0.5, 0.6, 0.7, 0.8]))
    await asyncio.wait_for(destination.delivered.wait(), 1.0)
    outcome = await running.stop()

    assert outcome.success
    assert destination.started_total == 1
    assert destination.stopped_total == 1
    assert {frame.source_id for frame in destination.received} == {
        application.source_id,
        microphone.source_id,
    }


async def test_given_slow_async_send_when_deadline_expires_then_provider_stops() -> (
    None
):
    class SlowConnector(pks_aio.Connector):
        def __init__(self) -> None:
            self.deadlines = pks_aio.ConnectorDeadlines(delivery_s=0.01)
            self.started = asyncio.Event()
            self.stopped_total = 0

        async def send(self, frame: pks.AudioFrame) -> None:
            del frame
            self.started.set()
            await asyncio.sleep(10)

        async def stop(self) -> None:
            self.stopped_total += 1

    destination = SlowConnector()
    session = pks_aio.Session()
    audio = session.audio_input("application", frame_samples_per_channel=4)
    audio.output.send_to(destination)
    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await asyncio.wait_for(destination.started.wait(), 1.0)
    await asyncio.sleep(0.05)
    outcome = await running.stop()

    assert not outcome.success
    assert destination.stopped_total == 1
    assert outcome.terminal_event is not None
    assert any(
        failure.error_code == "python.async.timeout"
        for failure in outcome.terminal_event.failures
    )


async def test_given_async_callbacks_when_audio_sends_then_lifecycle_is_bounded() -> (
    None
):
    started_total = 0
    stopped_total = 0
    received: list[pks.AudioFrame] = []
    delivered = asyncio.Event()

    async def start() -> None:
        nonlocal started_total
        started_total += 1

    async def send(frame: pks.AudioFrame) -> None:
        received.append(frame)
        delivered.set()

    async def stop() -> None:
        nonlocal stopped_total
        stopped_total += 1

    destination = pks_aio.Connector(start=start, send=send, stop=stop)
    session = pks_aio.Session()
    audio = session.audio_input("application", frame_samples_per_channel=4)
    audio.output.send_to(destination)

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await asyncio.wait_for(delivered.wait(), 1.0)
    outcome = await running.stop()

    assert outcome.success
    assert started_total == stopped_total == 1
    assert len(received) == 1
