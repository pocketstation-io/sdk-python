from __future__ import annotations

from threading import Event

import pocketstation.aio as pks_aio
import pytest
from pocketstation import (
    MediaCaps,
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorPrepareContext,
    OperatorProvider,
    PortDirection,
    PortSpec,
    Session,
    SignalEnvelope,
    SignalSpec,
    SourceEmission,
    SourceManifest,
    SourceProvider,
)


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
