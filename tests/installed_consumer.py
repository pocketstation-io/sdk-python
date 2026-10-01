"""Exercise the public SDK from an isolated installed artifact."""

from __future__ import annotations

import json
import math
import random
import sys
from array import array
from pathlib import Path
from threading import Event, Thread
from time import sleep

import httpx
import pocketstation as public_pocketstation
import pocketstation._api as pocketstation
import pocketstation._native as native
from pocketstation.aec import EchoCancellationState, PlaybackReference

_VOICE_FRAME_SAMPLES = 480


class InstalledClassConnector(public_pocketstation.Connector):
    def __init__(self) -> None:
        self.started_total = 0
        self.stopped_total = 0
        self.source_ids: set[object] = set()
        self.delivered = Event()

    def start(self) -> None:
        self.started_total += 1

    def send(self, frame: public_pocketstation.AudioFrame) -> None:
        self.source_ids.add(frame.source_id)
        if len(self.source_ids) == 2:
            self.delivered.set()

    def stop(self) -> None:
        self.stopped_total += 1


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
    if not isinstance(frame, public_pocketstation.AudioFrame):
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


def _exercise_class_connector() -> None:
    destination = InstalledClassConnector()
    session = public_pocketstation.Session()
    application = session.audio_input("application", frame_samples_per_channel=4)
    microphone = session.audio_input("microphone", frame_samples_per_channel=4)
    application.output.send_to(destination)
    microphone.output.send_to(destination)
    running = session.start()
    application.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    microphone.write(array("f", [0.5, 0.6, 0.7, 0.8]))
    if not destination.delivered.wait(1.0):
        raise RuntimeError("installed class Connector did not receive both stems")
    result = running.stop()
    if not result.success:
        raise RuntimeError("installed class Connector did not stop successfully")
    if destination.started_total != 1 or destination.stopped_total != 1:
        raise RuntimeError("installed class Connector did not use one lifecycle")


def _exercise_function_connector() -> None:
    delivered = Event()
    stopped_total = 0

    def send(frame: public_pocketstation.AudioFrame) -> None:
        if frame.samples:
            delivered.set()

    def stop() -> None:
        nonlocal stopped_total
        stopped_total += 1

    destination = public_pocketstation.Connector(send=send, stop=stop)
    session = public_pocketstation.Session()
    audio = session.audio_input("function", frame_samples_per_channel=4)
    audio.output.send_to(destination)
    running = session.start()
    audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    if not delivered.wait(1.0):
        raise RuntimeError("installed function Connector did not receive audio")
    result = running.stop()
    if not result.success or stopped_total != 1:
        raise RuntimeError("installed function Connector did not close once")


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
    audio.output.send_to(
        pocketstation.Connector.with_driver(manifest, InstalledConnectorFactory(driver))
    )
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


def _exercise_operator_pcm_reentry() -> None:
    signal = pocketstation.SignalSpec.audio(role="audio.generated")
    media = pocketstation.MediaCaps.audio(
        pocketstation.AudioCaps(
            sample_rate_hz=48_000,
            frame_samples=_VOICE_FRAME_SAMPLES,
            channel_layout=pocketstation.ChannelLayout.MONO,
        )
    )
    emitted = array("f", [0.0]) * _VOICE_FRAME_SAMPLES
    emitted[:4] = array("f", [0.25, -0.25, 0.5, -0.5])
    closed = Event()

    class InstalledPcmOperator(pocketstation.OperatorNode):
        def process(
            self,
            _input_port: str,
            _envelope: pocketstation.SignalEnvelope[object],
        ) -> tuple[pocketstation.OperatorEmission, ...]:
            return (pocketstation.OperatorEmission.audio(emitted, signal=signal),)

        def close(self) -> None:
            closed.set()

    class InstalledPcmFactory:
        def create(self, _configuration: object) -> InstalledPcmOperator:
            return InstalledPcmOperator()

    provider = pocketstation.OperatorProvider.with_node(
        pocketstation.OperatorManifest(
            "io.pocketstation.operator.installed-pcm.v1",
            inputs=(pocketstation.PortSpec.input("input", signal, media=media),),
            outputs=(pocketstation.PortSpec.output("output", signal, media=media),),
            queue_capacity_signals=2,
        ),
        InstalledPcmFactory(),
    )
    session = pocketstation.Session(frame_duration_ms=10)
    source = session.audio_input(
        "installed-pcm", frame_samples_per_channel=_VOICE_FRAME_SAMPLES
    )
    operator = session.register_operator(provider).declare()
    source.output.connect(operator.input("input"))
    operator.output("output").reenter_audio().send(session.polled_audio())

    running = session.start()
    source.write(array("f", [0.0]) * _VOICE_FRAME_SAMPLES)
    frame = running.audio.read(timeout_s=1.0)
    result = running.stop()
    if not isinstance(frame, public_pocketstation.AudioFrame) or list(
        frame.samples.cast("f")
    ) != list(emitted):
        raise RuntimeError("installed Python Operator PCM did not reenter Core")
    if not result.success or not closed.wait(1.0):
        raise RuntimeError("installed Python Operator PCM did not finalize")


def _exercise_invitation_lifecycle() -> None:
    join_code = "4a54c6b9-fdc2-4e0c-a740-715efdcf03de"
    alias = "gentleglow-cedarbloom-riverglen"
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/invitations"):
            return httpx.Response(
                201,
                json={
                    "join_code": join_code,
                    "join_url": (f"https://receiver.example/join#join={join_code}"),
                    "share_alias": alias,
                    "share_url": (f"https://receiver.example/{alias}#join={join_code}"),
                    "visibility": "private",
                    "expires_at": "2026-09-26T18:15:00Z",
                },
            )
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "share_alias": alias,
                    "visibility": "private",
                    "expires_at": "2026-09-26T18:15:00Z",
                },
            )
        return httpx.Response(
            200,
            json={
                "session_id": "session_123",
                "bus_id": "application",
                "subscriber_token": "installed-subscriber-secret",
                "signal_url": "wss://relay.example/v1/signal",
                "whep_url": ("https://relay.example/v1/sessions/session_123/whep"),
                "ice_servers": [],
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = pocketstation.ControlClient(
            "https://control.example",
            http_client=http_client,
        )
        invitation = client.create_invitation(
            "session_123",
            pocketstation.SecretToken("source-secret"),
            bus_id="application",
            visibility=pocketstation.InvitationVisibility.PRIVATE,
        )
        metadata = client.inspect_invitation(invitation.share_alias)
        if invitation.share_url is None:
            raise RuntimeError("installed invitation omitted its share URL")
        join_token = invitation.share_url.expose_join_code()
        try:
            client.redeem_invitation(invitation.share_alias)
        except pocketstation.InvitationUnavailableError:
            pass
        else:
            raise RuntimeError("readable words authorized without a credential")
        access = client.redeem_invitation(
            invitation.share_alias,
            join_code=join_token,
        )

    if join_code in repr(invitation) or str(invitation.share_url) != "[redacted]":
        raise RuntimeError("installed invitation exposed its delegated join credential")
    if metadata.share_alias != alias or access.bus_id != "application":
        raise RuntimeError("installed invitation lost alias or exact-bus scope")
    if [request.method for request in requests] != ["POST", "GET", "POST"]:
        raise RuntimeError("installed invitation used the wrong HTTP lifecycle")
    if requests[-1].url.path != f"/v1/join/{alias}":
        raise RuntimeError("installed invitation used the wrong join endpoint")
    if json.loads(requests[-1].content) != {"join_code": join_code}:
        raise RuntimeError("installed invitation changed delegated authority")
    if any(join_code in str(request.url) for request in requests):
        raise RuntimeError("installed invitation put its credential in a request URL")


def _exercise_echo_cancellation() -> dict[str, object]:
    session = public_pocketstation.Session(frame_duration_ms=10)
    reference = session.audio_input("installed-playback")
    microphone = session.audio_input("installed-microphone")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    endpoint = session.polled_audio()
    reference.output.send(endpoint)
    cleaned.audio.send(endpoint)
    previous = array("f", [0.0]) * 480
    rng = random.Random(138)
    echo_input_power = echo_output_power = voice_input_power = voice_output_power = 0.0
    with session.start() as running:
        for index in range(400):
            playback = array("f", (rng.uniform(-0.1, 0.1) for _ in range(480)))
            if index < 300:
                mic = array("f", (value * 0.6 for value in previous))
            else:
                playback = array("f", [0.0]) * 480
                mic = array(
                    "f",
                    (0.2 * math.sin(2 * math.pi * 300 * i / 48000) for i in range(480)),
                )
            reference.try_write(playback)
            microphone.try_write(mic)
            delivered: set[str] = set()
            for _ in range(2):
                frame = running.audio.read(timeout_s=1.0)
                if not isinstance(frame, public_pocketstation.AudioFrame):
                    raise RuntimeError("installed AEC did not deliver both stems")
                values = frame.samples.cast("f")
                if frame.source_id == reference.source_id:
                    if (
                        "raw" in delivered
                        or list(values) != list(playback)
                        or frame.processing is not None
                    ):
                        raise RuntimeError(
                            "installed AEC altered the raw application stem"
                        )
                    delivered.add("raw")
                else:
                    if (
                        "processed" in delivered
                        or frame.stem_id != cleaned.audio.id
                        or not all(math.isfinite(value) for value in values)
                        or len(values) != 480
                    ):
                        raise RuntimeError(
                            "installed AEC output or identity is invalid"
                        )
                    metadata = frame.processing
                    if not (
                        metadata is not None
                        and metadata.input_source_id == microphone.source_id
                        and metadata.input_stream_id == microphone.output.stream_id
                        and metadata.input_duration_ns == 10_000_000
                        and frame.source_id != metadata.input_source_id
                        and metadata.padding_samples == 0
                        and not metadata.is_tail
                        and metadata.nominal_delay_samples == 432
                    ):
                        raise RuntimeError("installed AEC lost input provenance")
                    delivered.add("processed")
                    if 200 <= index < 300:
                        echo_output_power += sum(value * value for value in values)
                    elif index >= 350:
                        voice_output_power += sum(value * value for value in values)
            if delivered != {"raw", "processed"}:
                raise RuntimeError("installed AEC lost a branch")
            if 200 <= index < 300:
                echo_input_power += sum(value * value for value in mic)
            elif index >= 350:
                voice_input_power += sum(value * value for value in mic)
            previous = playback
        reference.close()
        microphone.close()
        if not running.stop().success:
            raise RuntimeError("installed AEC Session did not stop successfully")
        for offset in range(4):
            tail = running.audio.read(timeout_s=1.0)
            if not (
                isinstance(tail, public_pocketstation.AudioFrame)
                and tail.processing is not None
                and tail.processing.is_tail
                and tail.processing.input_source_id == microphone.source_id
                and tail.processing.padding_samples == 480
                and tail.processing.tail_offset_samples == offset * 480
            ):
                raise RuntimeError("installed AEC lost the final polled tail")
    observation = cleaned.observations()
    if not (
        observation.state is EchoCancellationState.STOPPED
        and observation.processed_microphone_frames_total == 400
        and observation.output_frames_total == 404
        and observation.tail_frames_total == 4
        and observation.tail_padding_samples_total == 1920
        and observation.discarded_tail_generations_total == 0
        and observation.discarded_output_frames_total == 0
        and observation.nominal_delay_samples == 432
        and observation.drain_duration_ms == 40
        and observation.microphone_source_id == microphone.source_id
        and observation.reference_source_id == reference.source_id
        and echo_input_power > 1.0
        and echo_output_power < echo_input_power * 0.5
        and 0.5 < voice_output_power / voice_input_power < 2.0
        and observation.last_error is None
    ):
        raise RuntimeError(f"installed AEC processing proof failed: {observation}")
    return {
        "processed_frames_total": observation.processed_microphone_frames_total,
        "output_frames_total": observation.output_frames_total,
        "tail_frames_total": observation.tail_frames_total,
        "tail_padding_samples_total": observation.tail_padding_samples_total,
        "discarded_output_frames_total": observation.discarded_output_frames_total,
        "input_provenance_preserved": True,
        "polled_tail_preserved": True,
        "echo_power_ratio": echo_output_power / echo_input_power,
        "voice_power_ratio": voice_output_power / voice_input_power,
        "raw_stem_unchanged": True,
        "terminal_state": observation.state.value,
    }


def main() -> None:
    fixture_exports = {
        "ExtensionConformanceReport",
        "run_extension_conformance",
        "conformance_source_replacement_error",
    }
    if fixture_exports.intersection(dir(native)):
        raise RuntimeError("Release wheel contains conformance-only native exports")
    provider = _exercise_complete_provider_path()
    _exercise_saturation()
    _exercise_class_connector()
    _exercise_function_connector()
    _exercise_abort()
    _exercise_structured_failure()
    _exercise_operator_pcm_reentry()
    _exercise_invitation_lifecycle()
    aec = _exercise_echo_cancellation()
    package_path = Path(pocketstation.__file__).resolve()
    environment_root = Path(sys.prefix).resolve()
    if not package_path.is_relative_to(environment_root):
        raise RuntimeError("PocketStation was not imported from the environment")
    print(
        json.dumps(
            {
                "package_path": str(package_path),
                "python": sys.version.split()[0],
                "aec": aec,
                **provider,
                "success": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
