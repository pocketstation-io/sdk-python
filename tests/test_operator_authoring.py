from __future__ import annotations

from array import array
from threading import Event

import pocketstation.aio as pks_aio
import pytest
from pocketstation import (
    AudioCaps,
    ChannelLayout,
    Connector,
    ConnectorDeliveryOutcome,
    MediaCaps,
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorPrepareContext,
    OperatorProvider,
    PocketStationError,
    PortDirection,
    PortSpec,
    Session,
    SignalEnvelope,
    SignalSpec,
    SourceEmission,
    SourceManifest,
    SourceProvider,
)


def _pcm_media(*, frame_samples: int = 4) -> MediaCaps:
    return MediaCaps.audio(
        AudioCaps(
            sample_rate_hz=48_000,
            frame_samples=frame_samples,
            channel_layout=ChannelLayout.MONO,
        )
    )


def _pcm_operator(
    *,
    samples: array[float],
    frame_samples: int = 4,
) -> tuple[OperatorProvider, Event]:
    input_signal = SignalSpec.audio(role="audio.input")
    output_signal = SignalSpec.audio(role="audio.generated")
    closed = Event()

    class GeneratePcm(OperatorNode):
        def process(self, _input_port, _envelope):
            return (OperatorEmission.audio(samples, signal=output_signal),)

        def close(self) -> None:
            closed.set()

    class Factory:
        def create(self, _configuration) -> GeneratePcm:
            return GeneratePcm()

    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.python-pcm-test.v1",
            inputs=(PortSpec.input("input", input_signal, media=_pcm_media()),),
            outputs=(
                PortSpec.output(
                    "output",
                    output_signal,
                    media=_pcm_media(frame_samples=frame_samples),
                ),
            ),
            queue_capacity_signals=2,
        ),
        Factory(),
    )
    return provider, closed


def test_python_operator_processes_source_signal_with_derivation() -> None:
    input_signal = SignalSpec.text(role="request")
    output_signal = SignalSpec.text(role="result.final")
    source = SourceProvider.from_iterable(
        SourceManifest(
            "io.pocketstation.source.operator-input-test.v1",
            outputs=(
                PortSpec(
                    "events",
                    PortDirection.OUTPUT,
                    input_signal,
                    MediaCaps.text(),
                ),
            ),
        ),
        lambda _configuration: (
            SourceEmission.text("events", "hello", signal=input_signal),
        ),
    )

    class Uppercase(OperatorNode):
        def __init__(self) -> None:
            self.prepared: OperatorPrepareContext | None = None
            self.closed = Event()

        def prepare(self, context: OperatorPrepareContext) -> None:
            self.prepared = context

        def process(self, input_port, envelope):
            assert input_port == "input"
            assert envelope.payload == "hello"
            return (OperatorEmission.text("HELLO", signal=output_signal),)

        def close(self) -> None:
            self.closed.set()

    node = Uppercase()

    class Factory:
        def validate_config(self, _configuration) -> None:
            pass

        def create(self, _configuration) -> Uppercase:
            return node

    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.uppercase-test.v1",
            inputs=(
                PortSpec(
                    "input",
                    PortDirection.INPUT,
                    input_signal,
                    MediaCaps.text(),
                ),
            ),
            outputs=(
                PortSpec(
                    "output",
                    PortDirection.OUTPUT,
                    output_signal,
                    MediaCaps.text(),
                ),
            ),
            terminal_roles=("result.final",),
        ),
        Factory(),
    )

    session = Session()
    source_instance = session.register_source(source).declare()
    operator_instance = session.register_operator(provider).declare()
    source_instance.output("events").connect(operator_instance.input("input"))
    subscription = session.subscribe(
        operator_instance.output("output"), signal=output_signal
    )

    running = session.start()
    value = running.signals(subscription).read(timeout_s=1.0)
    stop = running.stop()
    assert stop.success
    if not isinstance(value, SignalEnvelope):
        raise AssertionError(stop)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "HELLO"
    assert value.lineage is not None
    assert value.derivation is not None
    assert value.derivation.operator_id == provider.manifest.operator_id
    assert node.prepared is not None
    assert node.prepared.execution_partition == "async-worker"
    assert node.prepared.inputs[0].port_name == "input"
    assert node.prepared.outputs[0].port_name == "output"
    assert node.closed.wait(1.0)


def test_operator_factory_does_not_require_a_noop_validator() -> None:
    input_signal = SignalSpec.text(role="request")
    output_signal = SignalSpec.text(role="result")
    source = SourceProvider.from_iterable(
        SourceManifest(
            "io.pocketstation.source.no-validator-operator-input.v1",
            outputs=(PortSpec.output("events", input_signal),),
        ),
        lambda _configuration: (
            SourceEmission.text("events", "hello", signal=input_signal),
        ),
    )

    class Uppercase(OperatorNode):
        def process(self, _input_port, envelope):
            return (
                OperatorEmission.text(
                    str(envelope.payload).upper(), signal=output_signal
                ),
            )

    class Factory:
        def create(self, _configuration) -> Uppercase:
            return Uppercase()

    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.no-validator-test.v1",
            inputs=(PortSpec.input("input", input_signal),),
            outputs=(PortSpec.output("output", output_signal),),
        ),
        Factory(),
    )
    session = Session()
    source_instance = session.register_source(source).declare()
    operator_instance = session.register_operator(provider).declare()
    source_instance.output("events").connect(operator_instance.input("input"))
    subscription = session.subscribe(
        operator_instance.output("output"), signal=output_signal
    )

    with session.start() as running:
        value = running.signals(subscription).read(timeout_s=1.0)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "HELLO"


@pytest.mark.asyncio
async def test_async_operator_runs_on_owning_loop() -> None:
    input_signal = SignalSpec.text(role="async.request")
    output_signal = SignalSpec.text(role="async.result")
    source = SourceProvider.from_iterable(
        SourceManifest(
            "io.pocketstation.source.async-operator-input-test.v1",
            outputs=(
                PortSpec(
                    "events",
                    PortDirection.OUTPUT,
                    input_signal,
                    MediaCaps.text(),
                ),
            ),
        ),
        lambda _configuration: (
            SourceEmission.text("events", "hello", signal=input_signal),
        ),
    )
    manifest = OperatorManifest(
        "io.pocketstation.operator.async-uppercase-test.v1",
        inputs=(
            PortSpec(
                "input",
                PortDirection.INPUT,
                input_signal,
                MediaCaps.text(),
            ),
        ),
        outputs=(
            PortSpec(
                "output",
                PortDirection.OUTPUT,
                output_signal,
                MediaCaps.text(),
            ),
        ),
    )

    @pks_aio.operator(manifest)
    async def uppercase(input_port, envelope):
        assert input_port == "input"
        return (
            OperatorEmission.text(str(envelope.payload).upper(), signal=output_signal),
        )

    session = pks_aio.Session()
    source_instance = session.register_source(source).declare()
    operator_instance = session.register_operator(uppercase).declare()
    source_instance.output("events").connect(operator_instance.input("input"))
    subscription = session.subscribe(
        operator_instance.output("output"), signal=output_signal
    )
    running = await session.start()
    value = await running.signals(subscription).read(timeout_s=1.0)
    stop = await running.stop()

    assert stop.success
    assert isinstance(value, SignalEnvelope)
    assert value.payload == "HELLO"


def test_python_operator_emits_pcm_into_core_reentry_and_recording(tmp_path) -> None:
    provider, closed = _pcm_operator(samples=array("f", [0.25, -0.25, 0.5, -0.5]))
    delivered = Event()
    connector_frames = []

    def deliver(frame, _context):
        connector_frames.append(frame)
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    connector = Connector.from_audio_handler(
        "io.pocketstation.connector.python-pcm-test.v1",
        deliver,
        package_version="1.0.0",
    )
    session = Session(recording_root=tmp_path)
    source = session.audio_input("operator-input", frame_samples_per_channel=4)
    operator = session.register_operator(provider).declare()
    source.output.connect(operator.input("input"))
    generated = operator.output("output").reenter_audio()
    generated.send(session.polled_audio())
    generated.send(session.destination(connector))
    generated.record("generated")

    running = session.start()
    source.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    frame = running.audio.read(timeout_s=1.0)
    assert delivered.wait(1.0)
    stop = running.stop()

    assert frame is not None
    assert list(frame.samples.cast("f")) == pytest.approx([0.25, -0.25, 0.5, -0.5])
    assert frame.sample_rate_hz == 48_000
    assert frame.channel_count == 1
    assert frame.sequence_number == 0
    assert frame.source_id != source.source_id
    assert frame.stem_id == generated.id
    assert len(connector_frames) == 1
    assert connector_frames[0].source_id == frame.source_id
    assert connector_frames[0].stem_id == frame.stem_id
    assert connector_frames[0].sequence_number == frame.sequence_number
    assert stop.success
    assert stop.recording is not None
    assert stop.recording.complete
    assert [stem.stem_name for stem in stop.recording.stems] == ["generated"]
    assert closed.wait(1.0)


def test_python_operator_rejects_wrong_pcm_frame_size() -> None:
    provider, closed = _pcm_operator(samples=array("f", [0.0, 0.0, 0.0]))
    session = Session()
    source = session.audio_input("operator-input", frame_samples_per_channel=4)
    operator = session.register_operator(provider).declare()
    source.output.connect(operator.input("input"))
    operator.output("output").reenter_audio().send(session.polled_audio())

    running = session.start()
    source.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert running.audio.read(timeout_s=0.2) is None
    stop = running.stop()

    assert not stop.success
    assert stop.terminal_event is not None
    assert any(
        "expected 4"
        in " ".join(
            value
            for value in (
                failure.message,
                failure.component_diagnostic,
                failure.error_class,
            )
            if value is not None
        )
        for failure in stop.terminal_event.failures
    )
    assert closed.wait(1.0)


def test_pcm_operator_requires_an_exact_output_contract() -> None:
    signal = SignalSpec.audio(role="audio.generated")

    class GeneratePcm(OperatorNode):
        def process(self, _input_port, _envelope):
            return (OperatorEmission.audio(array("f", [0.0]), signal=signal),)

    class Factory:
        def create(self, _configuration) -> GeneratePcm:
            return GeneratePcm()

    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.non-concrete-python-pcm-test.v1",
            inputs=(PortSpec.input("input", signal),),
            outputs=(PortSpec.output("output", signal),),
        ),
        Factory(),
    )

    with pytest.raises(PocketStationError) as failure:
        Session().register_operator(provider)
    assert failure.value.code == "operator.invalid_contract"
    assert "exact sample rate" in str(failure.value)


def test_pcm_operator_rejects_a_frame_beyond_the_edge_payload_bound() -> None:
    signal = SignalSpec.audio(role="audio.generated")

    class GeneratePcm(OperatorNode):
        def process(self, _input_port, _envelope):
            return ()

    class Factory:
        def create(self, _configuration) -> GeneratePcm:
            return GeneratePcm()

    oversized = _pcm_media(frame_samples=262_145)
    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.oversized-python-pcm-test.v1",
            inputs=(PortSpec.input("input", signal, media=_pcm_media()),),
            outputs=(PortSpec.output("output", signal, media=oversized),),
        ),
        Factory(),
    )

    with pytest.raises(PocketStationError) as failure:
        Session().register_operator(provider)
    assert failure.value.code == "operator.invalid_contract"
    assert "payload bound" in str(failure.value)


def test_pcm_emission_rejects_non_contiguous_input() -> None:
    signal = SignalSpec.audio(role="audio.generated")
    samples = memoryview(array("f", [0.0, 0.1, 0.2, 0.3]))[::2]

    with pytest.raises(PocketStationError) as failure:
        OperatorEmission.audio(samples, signal=signal)
    assert failure.value.code == "operator.invalid_contract"
    assert "C-contiguous float32" in str(failure.value)


def test_pcm_operator_fails_explicitly_when_its_native_pool_is_saturated() -> None:
    signal = SignalSpec.audio(role="audio.generated")
    samples = array("f", [0.0, 0.0, 0.0, 0.0])

    class EmitBeyondCapacity(OperatorNode):
        def process(self, _input_port, _envelope):
            return (
                OperatorEmission.audio(samples, signal=signal),
                OperatorEmission.audio(samples, signal=signal),
            )

    class Factory:
        def create(self, _configuration) -> EmitBeyondCapacity:
            return EmitBeyondCapacity()

    provider = OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.saturated-python-pcm-test.v1",
            inputs=(PortSpec.input("input", signal, media=_pcm_media()),),
            outputs=(PortSpec.output("output", signal, media=_pcm_media()),),
            queue_capacity_signals=1,
        ),
        Factory(),
    )
    session = Session()
    source = session.audio_input("operator-input", frame_samples_per_channel=4)
    operator = session.register_operator(provider).declare()
    source.output.connect(operator.input("input"))
    operator.output("output").reenter_audio().send(session.polled_audio())

    running = session.start()
    source.write(samples)
    assert running.audio.read(timeout_s=0.2) is None
    stop = running.stop()

    assert not stop.success
    assert stop.terminal_event is not None
    assert any(
        "buffer pool is full"
        in " ".join(
            value
            for value in (
                failure.message,
                failure.component_diagnostic,
                failure.error_class,
            )
            if value is not None
        )
        for failure in stop.terminal_event.failures
    )


@pytest.mark.asyncio
async def test_async_operator_pcm_uses_the_same_core_reentry(tmp_path) -> None:
    provider, closed = _pcm_operator(samples=array("f", [0.1, 0.2, 0.3, 0.4]))
    session = pks_aio.Session(recording_root=tmp_path)
    source = session.audio_input("operator-input", frame_samples_per_channel=4)
    operator = session.register_operator(provider).declare()
    source.output.connect(operator.input("input"))
    generated = operator.output("output").reenter_audio()
    generated.send(session.polled_audio())
    generated.record("generated")

    running = await session.start()
    await source.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    frame = await running.audio.read(timeout_s=1.0)
    stop = await running.stop()

    assert frame is not None
    assert list(frame.samples.cast("f")) == pytest.approx([0.1, 0.2, 0.3, 0.4])
    assert stop.success
    assert stop.recording is not None
    assert stop.recording.complete
    assert closed.wait(1.0)
