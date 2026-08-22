from __future__ import annotations

from threading import Event

import pocketstation.aio._api as pks_aio
import pytest
from pocketstation._api import (
    MediaCaps,
    Multiplicity,
    PortDirection,
    PortSpec,
    Session,
    SignalEnvelope,
    SignalSpec,
    SourceCancellation,
    SourceConfiguration,
    SourceDriver,
    SourceEmission,
    SourceManifest,
    SourcePrepareContext,
    SourceProvider,
    TextFormat,
    source,
)


def text_manifest(source_type_id: str) -> SourceManifest:
    signal = SignalSpec.text(TextFormat.UTF8, role="transcript")
    return SourceManifest(
        source_type_id,
        outputs=(
            PortSpec(
                "events",
                PortDirection.OUTPUT,
                signal,
                MediaCaps.text(),
                Multiplicity.MANY,
            ),
        ),
    )


def test_iterable_source_runs_in_core_and_receives_session_lineage() -> None:
    signal = SignalSpec.text(TextFormat.UTF8, role="transcript")

    @source(text_manifest("io.pocketstation.source.python-test.v1"))
    def transcript(configuration):
        yield SourceEmission.text(
            "events",
            configuration["text"],
            signal=signal,
            source_timestamp_ns=10,
            observed_timestamp_ns=12,
            duration_ns=5,
            discontinuity_epoch=2,
            terminal=True,
        )

    session = Session()
    registered = session.register_source(transcript)
    instance = registered.declare(SourceConfiguration({"text": "hello"}))
    output = instance.output("events")
    subscription = session.subscribe(output, signal=signal)
    session_id = session.id

    with session.start() as running:
        value = running.signals(subscription).read(timeout_s=1.0)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "hello"
    assert value.lineage is not None
    assert value.lineage.session_id == session_id
    assert value.lineage.source_id == instance.source_id
    assert value.lineage.stream_id == output.stream_id
    assert value.lineage.sequence_number == 0
    assert value.lineage.discontinuity_epoch == 2
    assert value.timing.source_timestamp_ns == 10
    assert value.timing.observed_timestamp_ns == 12
    assert value.timing.duration_ns == 5


class RecordingDriver(SourceDriver):
    def __init__(self, signal: SignalSpec) -> None:
        self.signal = signal
        self.prepared: SourcePrepareContext | None = None
        self.closed = Event()
        self.sent = False

    def prepare(self, context: SourcePrepareContext) -> None:
        self.prepared = context

    def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        assert not cancellation.cancelled
        if self.sent:
            return None
        self.sent = True
        return SourceEmission.text("events", "ready", signal=self.signal)

    def close(self) -> None:
        self.closed.set()


class RecordingFactory:
    def __init__(self, driver: RecordingDriver) -> None:
        self.driver = driver
        self.configurations: list[dict[str, str]] = []

    def validate_config(self, configuration) -> None:
        if configuration.get("mode") != "strict":
            raise ValueError("mode must be strict")

    def create(self, configuration) -> RecordingDriver:
        self.configurations.append(dict(configuration))
        return self.driver


class FactoryWithoutValidator:
    def __init__(self, driver: RecordingDriver) -> None:
        self.driver = driver

    def create(self, _configuration) -> RecordingDriver:
        return self.driver


def test_driver_source_preparation_validation_and_exact_close() -> None:
    signal = SignalSpec.text()
    driver = RecordingDriver(signal)
    provider = SourceProvider.with_driver(
        text_manifest("io.pocketstation.source.python-driver-test.v1"),
        RecordingFactory(driver),
    )
    session = Session()
    registered = session.register_source(provider)

    instance = registered.declare(SourceConfiguration({"mode": "strict"}))
    subscription = session.subscribe(instance.output("events"), signal=signal)
    session_id = session.id
    with session.start() as running:
        value = running.signals(subscription).read(timeout_s=1.0)
        assert isinstance(value, SignalEnvelope)

    assert driver.prepared is not None
    assert driver.prepared.session_id == session_id
    assert driver.prepared.source_id == instance.source_id
    assert driver.prepared.outputs[0].output_port == "events"
    assert driver.closed.wait(1.0)


def test_source_factory_does_not_require_a_noop_validator() -> None:
    signal = SignalSpec.text()
    driver = RecordingDriver(signal)
    session = Session()
    instance = session.register_source(
        SourceProvider.with_driver(
            text_manifest("io.pocketstation.source.no-validator-test.v1"),
            FactoryWithoutValidator(driver),
        )
    ).declare()
    subscription = session.subscribe(instance.output("events"), signal=signal)

    with session.start() as running:
        assert isinstance(
            running.signals(subscription).read(timeout_s=1.0), SignalEnvelope
        )

    assert driver.closed.wait(1.0)


def test_source_manifest_rejects_pcm_and_points_to_audio_input() -> None:
    with pytest.raises(Exception, match=r"Session\.audio_input"):
        SourceManifest(
            "io.pocketstation.source.invalid-audio-test.v1",
            outputs=(
                PortSpec(
                    "audio",
                    PortDirection.OUTPUT,
                    SignalSpec.audio(),
                    MediaCaps.audio(),
                ),
            ),
        )


@pytest.mark.asyncio
async def test_async_iterable_source_runs_on_the_owning_event_loop() -> None:
    signal = SignalSpec.text(role="async-source")
    manifest = SourceManifest(
        "io.pocketstation.source.python-async-test.v1",
        outputs=(
            PortSpec(
                "events",
                PortDirection.OUTPUT,
                signal,
                MediaCaps.text(),
            ),
        ),
    )

    @pks_aio.source(manifest)
    async def events(_configuration):
        yield SourceEmission.text("events", "async", signal=signal)

    session = pks_aio.Session()
    registered = session.register_source(events)
    instance = registered.declare()
    subscription = session.subscribe(instance.output("events"), signal=signal)

    async with await session.start() as running:
        value = await running.signals(subscription).read(timeout_s=1.0)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "async"
    assert value.lineage is not None
