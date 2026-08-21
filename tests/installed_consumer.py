"""Exercise the public SDK from an isolated installed artifact."""

from __future__ import annotations

import json
import sys
from array import array
from pathlib import Path
from threading import Event, Thread
from time import sleep

import pocketstation


class InstalledSource(pocketstation.SourceDriver):
    def __init__(
        self,
        signal: pocketstation.SignalSpec[str],
        closed: Event,
    ) -> None:
        self._signal = signal
        self._closed = closed
        self._sent = False

    def next(
        self, cancellation: pocketstation.SourceCancellation
    ) -> pocketstation.SourceEmission | None:
        if cancellation.cancelled or self._sent:
            return None
        self._sent = True
        return pocketstation.SourceEmission.text(
            "events", "installed", signal=self._signal, terminal=True
        )

    def close(self) -> None:
        self._closed.set()


class InstalledSourceFactory:
    def __init__(self, driver: InstalledSource) -> None:
        self._driver = driver

    def create(self, _configuration: object) -> InstalledSource:
        return self._driver


class InstalledOperator(pocketstation.OperatorNode):
    def __init__(self, signal: pocketstation.SignalSpec[str], closed: Event) -> None:
        self._signal = signal
        self._closed = closed

    def process(
        self,
        _input_port: str,
        envelope: pocketstation.SignalEnvelope[object],
    ) -> tuple[pocketstation.OperatorEmission, ...]:
        return (
            pocketstation.OperatorEmission.text(
                str(envelope.payload).upper(), signal=self._signal
            ),
        )

    def close(self) -> None:
        self._closed.set()


class InstalledOperatorFactory:
    def __init__(self, node: InstalledOperator) -> None:
        self._node = node

    def create(self, _configuration: object) -> InstalledOperator:
        return self._node


class InstalledConnector(pocketstation.ConnectorDriver):
    def __init__(self, delivered: Event, stopped: Event) -> None:
        self._delivered = delivered
        self._stopped = stopped
        self.shutdown_mode: pocketstation.ConnectorShutdownMode | None = None

    def deliver(
        self,
        item: pocketstation.ConnectorItem,
        _context: pocketstation.ConnectorContext,
    ) -> pocketstation.ConnectorDeliveryOutcome:
        if item.audio is None:
            raise RuntimeError("installed Connector received no audio")
        self._delivered.set()
        return pocketstation.ConnectorDeliveryOutcome.DELIVERED

    def shutdown(
        self,
        mode: pocketstation.ConnectorShutdownMode,
        _context: pocketstation.ConnectorContext,
    ) -> None:
        self.shutdown_mode = mode
        self._stopped.set()


class InstalledConnectorFactory:
    def __init__(self, driver: InstalledConnector) -> None:
        self._driver = driver

    def prepare(
        self,
        _inputs: object,
    ) -> InstalledConnector:
        return self._driver


class InstalledEndpoint(pocketstation.RunningEndpointDriver):
    def __init__(
        self,
        input: pocketstation.EndpointPortInput,
        gate: pocketstation.EndpointStartGate,
        delivered: Event,
    ) -> None:
        self._input = input
        self._gate = gate
        self._delivered = delivered
        self._stop = Event()
        self._thread = Thread(target=self._run, name="installed-endpoint")
        self._thread.start()

    def _run(self) -> None:
        while not self._gate.is_open and not self._stop.is_set():
            sleep(0.001)
        while not self._stop.is_set():
            item = self._input.receiver.try_recv()
            if item is not None and item.audio is not None:
                self._delivered.set()
            else:
                sleep(0.001)

    def request_shutdown(self, mode: pocketstation.EndpointShutdownMode) -> None:
        self._stop.set()

    def join_and_finalize(self) -> pocketstation.EndpointDriverObservations:
        self._thread.join(1.0)
        if self._thread.is_alive():
            raise RuntimeError("installed Endpoint worker did not terminate")
        return pocketstation.EndpointDriverObservations(
            frames_received_total=int(self._delivered.is_set()),
            frames_delivered_total=int(self._delivered.is_set()),
        )


class InstalledPreparedEndpoint(pocketstation.PreparedEndpointDriver):
    def __init__(
        self,
        input: pocketstation.EndpointPortInput,
        delivered: Event,
    ) -> None:
        self._input = input
        self._delivered = delivered

    def start(
        self, gate: pocketstation.EndpointStartGate
    ) -> pocketstation.RunningEndpointDriver:
        return InstalledEndpoint(self._input, gate, self._delivered)


def _exercise_complete_provider_path() -> dict[str, object]:
    delivered = Event()
    source_closed = Event()
    operator_closed = Event()
    connector_stopped = Event()
    endpoint_delivered = Event()
    request_signal = pocketstation.SignalSpec.text(role="request")
    response_signal = pocketstation.SignalSpec.text(role="response.final")

    session = pocketstation.Session()
    source_driver = InstalledSource(request_signal, source_closed)
    source_provider = pocketstation.SourceProvider.with_driver(
        pocketstation.SourceManifest(
            "io.pocketstation.source.installed-consumer.v1",
            outputs=(pocketstation.PortSpec.output("events", request_signal),),
        ),
        InstalledSourceFactory(source_driver),
    )
    operator_node = InstalledOperator(response_signal, operator_closed)
    operator_provider = pocketstation.OperatorProvider.with_node(
        pocketstation.OperatorManifest(
            "io.pocketstation.test.installed-operator.v1",
            inputs=(pocketstation.PortSpec.input("input", request_signal),),
            outputs=(pocketstation.PortSpec.output("output", response_signal),),
            terminal_roles=("response.final",),
        ),
        InstalledOperatorFactory(operator_node),
    )
    source = session.register_source(source_provider).declare()
    operator = session.register_operator(operator_provider).declare()
    source.output("events").connect(operator.input("input"))
    subscription = session.subscribe(operator.output("output"), signal=response_signal)

    audio = session.audio_input(
        "installed-consumer",
        capacity_frames=2,
        frame_samples_per_channel=4,
    )
    manifest = pocketstation.ConnectorManifest.audio(
        "io.pocketstation.test.installed-consumer.v1",
        package_version="1.0.0",
    )
    connector_driver = InstalledConnector(delivered, connector_stopped)
    endpoint = session.destination(
        pocketstation.Connector.with_driver(
            manifest, InstalledConnectorFactory(connector_driver)
        )
    )
    audio.output.send(endpoint)
    generic_endpoint = session.register_endpoint(
        pocketstation.EndpointProvider(
            pocketstation.EndpointManifest.audio(
                "io.pocketstation.test.installed-endpoint.v1"
            ),
            lambda inputs: InstalledPreparedEndpoint(inputs[0], endpoint_delivered),
        )
    ).declare()
    audio.output.send(generic_endpoint)
    audio.output.send(session.polled_audio())

    running = session.start()
    transformed = running.signals(subscription).read(timeout_s=1.0)
    audio.write(array("f", [0.25, -0.25, 0.5, -0.5]))
    frame = running.audio.read(timeout_s=1.0)
    if frame is None:
        raise RuntimeError("installed consumer timed out waiting for audio")
    if not delivered.wait(1.0):
        raise RuntimeError("installed Connector did not receive audio")
    if not endpoint_delivered.wait(1.0):
        raise RuntimeError("installed generic Endpoint did not receive audio")
    stop = running.stop()
    if not stop.success:
        raise RuntimeError("installed consumer Session did not stop successfully")
    if frame.source_id != audio.source_id or frame.stream_id != audio.stream_id:
        raise RuntimeError("installed consumer lost source or stream identity")
    if not isinstance(transformed, pocketstation.SignalEnvelope):
        raise RuntimeError("installed Source and Operator produced no signal")
    if transformed.payload != "INSTALLED":
        raise RuntimeError("installed Source and Operator did not execute")
    if transformed.derivation is None:
        raise RuntimeError("installed Operator output lost derivation")
    if not source_closed.wait(1.0):
        raise RuntimeError("installed Source was not closed exactly")
    if not operator_closed.wait(1.0):
        raise RuntimeError("installed Operator was not closed exactly")
    if not connector_stopped.wait(1.0):
        raise RuntimeError("installed Connector was not stopped exactly")
    if connector_driver.shutdown_mode is not pocketstation.ConnectorShutdownMode.DRAIN:
        raise RuntimeError("installed Connector did not receive drain shutdown")
    return {
        "source_id": frame.source_id,
        "stream_id": frame.stream_id,
        "transformed": transformed.payload,
    }


def _exercise_saturation() -> None:
    session = pocketstation.Session()
    audio = session.audio_input(
        "installed-saturation",
        capacity_frames=1,
        frame_samples_per_channel=4,
    )
    samples = array("f", [0.0, 0.0, 0.0, 0.0])
    audio.try_write(samples)
    try:
        audio.try_write(samples)
    except pocketstation.AudioInputFullError:
        return
    raise RuntimeError("installed AudioInput did not expose finite saturation")


def _exercise_abort() -> None:
    delivered = Event()
    stopped = Event()
    driver = InstalledConnector(delivered, stopped)
    session = pocketstation.Session()
    audio = session.audio_input("installed-abort", frame_samples_per_channel=4)
    manifest = pocketstation.ConnectorManifest.audio(
        "io.pocketstation.test.installed-abort.v1",
        package_version="1.0.0",
    )
    endpoint = session.destination(
        pocketstation.Connector.with_driver(manifest, InstalledConnectorFactory(driver))
    )
    audio.output.send(endpoint)
    running = session.start()
    result = running.cancel()
    if not result.success or not stopped.wait(1.0):
        raise RuntimeError("installed Connector abort did not finalize")
    if driver.shutdown_mode is not pocketstation.ConnectorShutdownMode.ABORT:
        raise RuntimeError("installed Connector did not receive abort shutdown")


def _exercise_structured_failure() -> None:
    attempted = Event()

    def fail(
        _item: pocketstation.ConnectorItem,
        _context: pocketstation.ConnectorContext,
    ) -> pocketstation.ConnectorDeliveryOutcome:
        attempted.set()
        raise pocketstation.ConnectorError(
            "provider request timed out",
            code="provider.timeout",
            stage=pocketstation.ConnectorErrorStage.DELIVERY,
            retryability=pocketstation.ConnectorRetryability.RETRYABLE,
        )

    session = pocketstation.Session()
    audio = session.audio_input("installed-failure", frame_samples_per_channel=4)
    manifest = pocketstation.ConnectorManifest.audio(
        "io.pocketstation.test.installed-failure.v1",
        package_version="1.0.0",
    )
    endpoint = session.destination(pocketstation.Connector.from_handler(manifest, fail))
    audio.output.send(endpoint)
    running = session.start()
    audio.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    if not attempted.wait(1.0):
        raise RuntimeError("installed failing Connector did not execute")
    result = running.stop()
    if result.success or result.terminal_event is None:
        raise RuntimeError("installed Connector failure was not terminal")
    if not any(
        failure.error_code == "provider.timeout"
        and failure.retryability is pocketstation.EndpointFailureRetryability.RETRYABLE
        for failure in result.terminal_event.failures
    ):
        raise RuntimeError("installed Connector failure lost structured fields")


def main() -> None:
    provider = _exercise_complete_provider_path()
    _exercise_saturation()
    _exercise_abort()
    _exercise_structured_failure()
    package_path = Path(pocketstation.__file__).resolve()
    environment_root = Path(sys.prefix).resolve()
    if not package_path.is_relative_to(environment_root):
        raise RuntimeError("PocketStation was not imported from the environment")
    print(
        json.dumps(
            {
                "package_path": str(package_path),
                "python": sys.version.split()[0],
                **provider,
                "success": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
