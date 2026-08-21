from __future__ import annotations

from array import array
from collections.abc import Sequence
from threading import Event, Thread
from time import monotonic, sleep

import pytest
from pocketstation import (
    EndpointDriverError,
    EndpointDriverObservations,
    EndpointFailureRetryability,
    EndpointFailureStage,
    EndpointItem,
    EndpointManifest,
    EndpointPortInput,
    EndpointProvider,
    EndpointShutdownMode,
    EndpointStartGate,
    PreparedEndpointDriver,
    RunningEndpointDriver,
    Session,
)


class CollectingEndpoint(RunningEndpointDriver):
    def __init__(self, input: EndpointPortInput, gate: EndpointStartGate) -> None:
        self.input = input
        self.gate = gate
        self.started = Event()
        self.delivered = Event()
        self.stop = Event()
        self.shutdown_mode: EndpointShutdownMode | None = None
        self.items: list[EndpointItem] = []
        self.thread = Thread(target=self._run, name="test-python-endpoint")
        self.thread.start()

    def _run(self) -> None:
        deadline = monotonic() + 1.0
        while not self.gate.is_open and not self.stop.is_set():
            assert monotonic() < deadline
            sleep(0.001)
        self.started.set()
        while not self.stop.is_set():
            item = self.input.receiver.try_recv()
            if item is None:
                sleep(0.001)
                continue
            self.items.append(item)
            self.delivered.set()

    def observations(self) -> EndpointDriverObservations:
        count = len(self.items)
        return EndpointDriverObservations(
            frames_received_total=count,
            frames_delivered_total=count,
        )

    def request_shutdown(self, mode: EndpointShutdownMode) -> None:
        self.shutdown_mode = mode
        self.stop.set()

    def join_and_finalize(self) -> EndpointDriverObservations:
        self.thread.join(1.0)
        assert not self.thread.is_alive()
        return self.observations()


class PreparedCollector(PreparedEndpointDriver):
    def __init__(self, input: EndpointPortInput) -> None:
        self.input = input
        self.running: CollectingEndpoint | None = None
        self.cancelled = False

    def start(self, gate: EndpointStartGate) -> RunningEndpointDriver:
        self.running = CollectingEndpoint(self.input, gate)
        return self.running

    def cancel_preparation(self) -> None:
        self.cancelled = True


def test_generic_endpoint_uses_core_lifecycle_and_preserves_lineage() -> None:
    prepared: list[PreparedCollector] = []

    def prepare(inputs: Sequence[EndpointPortInput]) -> PreparedCollector:
        assert len(inputs) == 1
        value = PreparedCollector(inputs[0])
        prepared.append(value)
        return value

    provider = EndpointProvider(
        EndpointManifest.audio("io.pocketstation.test.endpoint.collect.v1"),
        prepare,
    )
    session = Session()
    audio = session.audio_input("agent-output", frame_samples_per_channel=4)
    endpoint = session.register_endpoint(provider).declare({"mode": "test"})
    route_id = audio.output.send(endpoint)

    running_session = session.start()
    assert prepared[0].running is not None
    endpoint_driver = prepared[0].running
    assert endpoint_driver.started.wait(1.0)
    audio.write(array("f", [0.25, -0.25, 0.5, -0.5]), discontinuity=True)
    assert endpoint_driver.delivered.wait(1.0)
    result = running_session.stop()

    assert result.success
    assert endpoint_driver.shutdown_mode is EndpointShutdownMode.DRAIN
    assert prepared[0].input.context.endpoint_id == endpoint.id
    assert prepared[0].input.context.connector_id is None
    assert prepared[0].input.context.route_id == route_id
    assert prepared[0].input.context.source_id == audio.source_id
    assert prepared[0].input.context.stream_id == audio.stream_id
    assert prepared[0].input.context.configuration == {"mode": "test"}
    assert len(endpoint_driver.items) == 1
    item = endpoint_driver.items[0]
    assert item.kind == "audio"
    assert item.signal is None
    assert item.audio is not None
    assert item.audio.source_id == audio.source_id
    assert item.audio.stream_id == audio.stream_id
    assert item.audio.sequence_number == 0
    assert item.audio.discontinuity_epoch == 1


def test_endpoint_registration_is_idempotent_and_session_scoped() -> None:
    provider = EndpointProvider(
        EndpointManifest.audio("io.pocketstation.test.endpoint.identity.v1"),
        lambda inputs: PreparedCollector(inputs[0]),
    )
    session = Session()
    first = session.register_endpoint(provider)
    second = session.register_endpoint(provider)

    assert first.session_id == session.id
    assert second.session_id == session.id
    with pytest.raises(Exception, match="different Session"):
        other = Session()
        first._session = other
        first.declare()


def test_endpoint_failure_preserves_structure_in_terminal_outcome() -> None:
    class FailingRunning(RunningEndpointDriver):
        def request_shutdown(self, mode: EndpointShutdownMode) -> None:
            raise EndpointDriverError(
                "provider did not drain",
                code="provider.drain_timeout",
                stage=EndpointFailureStage.REQUEST_STOP,
                retryability=EndpointFailureRetryability.RETRYABLE,
            )

    class FailingPrepared(PreparedEndpointDriver):
        def start(self, gate: EndpointStartGate) -> RunningEndpointDriver:
            return FailingRunning()

    session = Session()
    audio = session.audio_input("agent-output", frame_samples_per_channel=4)
    endpoint = session.register_endpoint(
        EndpointProvider(
            EndpointManifest.audio("io.pocketstation.test.endpoint.failure.v1"),
            lambda _inputs: FailingPrepared(),
        )
    ).declare()
    audio.output.send(endpoint)
    running = session.start()
    result = running.stop()

    assert not result.success
    assert result.terminal_event is not None
    failure = next(
        value
        for value in result.terminal_event.failures
        if value.error_code == "provider.drain_timeout"
    )
    assert failure.stage is EndpointFailureStage.REQUEST_STOP
    assert failure.retryability is EndpointFailureRetryability.RETRYABLE


def test_endpoint_prepare_failure_rolls_back_prepared_peer() -> None:
    prepared: list[PreparedCollector] = []

    def prepare_first(inputs: Sequence[EndpointPortInput]) -> PreparedCollector:
        value = PreparedCollector(inputs[0])
        prepared.append(value)
        return value

    def fail_prepare(
        _inputs: Sequence[EndpointPortInput],
    ) -> PreparedEndpointDriver:
        raise EndpointDriverError(
            "provider configuration is unavailable",
            code="provider.prepare_unavailable",
            stage=EndpointFailureStage.PREPARE,
            retryability=EndpointFailureRetryability.RETRYABLE,
        )

    session = Session()
    audio = session.audio_input("agent-output", frame_samples_per_channel=4)
    first = session.register_endpoint(
        EndpointProvider(
            EndpointManifest.audio("io.pocketstation.test.endpoint.rollback.v1"),
            prepare_first,
        )
    ).declare()
    second = session.register_endpoint(
        EndpointProvider(
            EndpointManifest.audio("io.pocketstation.test.endpoint.reject.v1"),
            fail_prepare,
        )
    ).declare()
    audio.output.send(first)
    audio.output.send(second)

    with pytest.raises(Exception, match="provider configuration is unavailable"):
        session.start()

    assert len(prepared) == 1
    assert prepared[0].cancelled
