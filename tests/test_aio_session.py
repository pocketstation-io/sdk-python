"""Asyncio Session ownership and cancellation tests."""

from __future__ import annotations

import asyncio
import threading
import time
from array import array

import pytest
from pocketstation import (
    Connector,
    ConnectorDeliveryOutcome,
    ConnectorManifest,
    SessionLifecycleState,
)
from pocketstation.aio import (
    Connector as AsyncConnector,
)
from pocketstation.aio import (
    ConnectorDeadlines,
    ConnectorWorker,
    Session,
)
from pocketstation.errors import AudioInputFullError


@pytest.mark.asyncio
async def test_cancelled_start_requests_the_native_token() -> None:
    native_started = threading.Event()
    native_cancelled = threading.Event()

    class BlockingNativeSession:
        def start(self, cancellation):
            native_started.set()
            while not cancellation.is_requested():
                time.sleep(0.001)
            native_cancelled.set()
            raise RuntimeError("session.start_cancelled")

    session = Session.__new__(Session)
    session._native = BlockingNativeSession()
    start = asyncio.create_task(session.start())
    assert await asyncio.to_thread(native_started.wait, 1.0)

    start.cancel()
    with pytest.raises(asyncio.CancelledError):
        await start

    assert await asyncio.to_thread(native_cancelled.wait, 1.0)


@pytest.mark.asyncio
async def test_application_owned_pcm_has_an_async_writer() -> None:
    session = Session()
    audio = session.audio_input(
        "playback",
        capacity_frames=2,
        frame_samples_per_channel=4,
    )
    audio.output.send(session.polled_audio())

    running = await session.start()
    assert running.state is SessionLifecycleState.RUNNING
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    frame = await running.audio.read(timeout_s=1.0)
    await running.stop()
    assert running.state is SessionLifecycleState.STOPPED
    assert running.is_stopped

    assert frame is not None
    assert frame.source_id == audio.source_id
    assert frame.stream_id == audio.stream_id
    assert list(frame.samples.cast("f")) == pytest.approx([0.1, 0.2, 0.3, 0.4])


@pytest.mark.asyncio
async def test_async_audio_write_wait_is_finite_and_adds_no_python_queue() -> None:
    session = Session()
    audio = session.audio_input(
        "playback",
        capacity_frames=1,
        frame_samples_per_channel=4,
    )
    samples = array("f", [0.1, 0.2, 0.3, 0.4])
    await audio.try_write(samples)

    with pytest.raises(AudioInputFullError):
        await audio.write(samples, timeout_s=0.01)
    with pytest.raises(TypeError):
        await audio.write(samples, timeout_s=True)
    with pytest.raises(ValueError):
        await audio.write(samples, timeout_s=61)

    observations = await audio.observations()
    assert observations.capacity_frames == 1
    assert observations.accepted_total == 1
    assert observations.full_total > 0


@pytest.mark.asyncio
async def test_async_session_registers_the_same_core_connector_contract() -> None:
    delivered = threading.Event()

    def receive(item, context):
        assert item.audio is not None
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.aio-connector.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("playback", frame_samples_per_channel=4)
    endpoint = session.register_connector(
        Connector.from_handler(manifest, receive)
    ).declare()
    audio.output.send(endpoint)

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    assert await asyncio.to_thread(delivered.wait, 1.0)
    assert (await running.stop()).success


@pytest.mark.asyncio
async def test_async_session_destination_reuses_one_connector_registration() -> None:
    async def receive(_item, _context):
        return ConnectorDeliveryOutcome.DELIVERED

    provider = AsyncConnector.from_handler(
        ConnectorManifest.audio(
            "io.pocketstation.test.aio-destination.v1",
            package_version="1.0.0",
        ),
        receive,
    )
    session = Session()

    first = session.destination(provider)
    registration = session.register_connector(provider)
    second = registration.declare()

    assert first.session_id == session.id
    assert second.session_id == session.id
    assert session.register_connector(provider).session_id == session.id


@pytest.mark.asyncio
async def test_async_connector_runs_on_owning_loop_with_observations() -> None:
    delivered = asyncio.Event()
    owning_thread = threading.get_ident()

    async def receive(item, context):
        assert threading.get_ident() == owning_thread
        assert item.audio is not None
        await asyncio.sleep(0)
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.aio-native-connector.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("playback", frame_samples_per_channel=4)
    registered = session.register_connector(
        AsyncConnector.from_handler(manifest, receive)
    )
    endpoint = registered.declare()
    audio.output.send(endpoint)

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await asyncio.wait_for(delivered.wait(), 1.0)
    observation = await registered.observation(endpoint)
    assert observation is not None
    assert observation.service_status.accepts_delivery
    [runtime] = await registered.observations()
    assert runtime.frames_delivered_total == 1
    assert (await running.stop()).success


@pytest.mark.asyncio
async def test_async_audio_connector_convenience_runs_on_owning_loop() -> None:
    delivered = asyncio.Event()
    received = []
    owning_thread = threading.get_ident()

    async def publish(frame, context):
        assert threading.get_ident() == owning_thread
        received.append(frame)
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    connector = AsyncConnector.from_audio_handler(
        "io.pocketstation.test.aio-audio-handler.v1",
        publish,
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("remote-call", frame_samples_per_channel=4)
    audio.output.send(session.destination(connector))

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await asyncio.wait_for(delivered.wait(), 1.0)
    assert (await running.stop()).success
    assert connector.manifest.inputs[0].signal.is_audio
    assert received[0].source_id == audio.source_id
    assert received[0].stream_id == audio.stream_id


@pytest.mark.asyncio
async def test_async_connector_delivery_deadline_is_finite_and_structured() -> None:
    started = asyncio.Event()

    async def hang(item, context):
        started.set()
        await asyncio.sleep(10)

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.aio-timeout.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("playback", frame_samples_per_channel=4)
    audio.output.send(
        session.register_connector(
            AsyncConnector.from_handler(
                manifest,
                hang,
                deadlines=ConnectorDeadlines(delivery_s=0.01),
            )
        ).declare()
    )

    running = await session.start()
    await audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    await asyncio.wait_for(started.wait(), 1.0)
    await asyncio.sleep(0.05)
    stop = await running.stop()
    assert not stop.success
    assert stop.terminal_event is not None
    failure = next(
        value
        for value in stop.terminal_event.failures
        if value.error_code == "python.async.timeout"
    )
    assert failure.retryability is not None
    assert failure.retryability.value == "retryable"


@pytest.mark.asyncio
async def test_async_connector_worker_receives_finite_native_batches() -> None:
    finished = asyncio.Event()
    batches: list[int] = []
    total = 8

    class BatchWorker(ConnectorWorker):
        async def deliver_batch(self, items, context):
            await asyncio.sleep(0)
            batches.append(len(items))
            if sum(batches) >= total:
                finished.set()
            return ConnectorDeliveryOutcome.DELIVERED

    async def prepare(_inputs):
        return BatchWorker()

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.aio-batch.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input(
        "playback",
        capacity_frames=16,
        frame_samples_per_channel=4,
    )
    registered = session.register_connector(
        AsyncConnector.with_worker(
            manifest,
            prepare,
            maximum_batch_items=4,
        )
    )
    audio.output.send(registered.declare())
    running = await session.start()
    for sequence in range(total):
        await audio.write(array("f", [float(sequence)] * 4))
    await asyncio.wait_for(finished.wait(), 1.0)
    assert (await running.stop()).success
    assert sum(batches) == total
    assert all(1 <= size <= 4 for size in batches)
