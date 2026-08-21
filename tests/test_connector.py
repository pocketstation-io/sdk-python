from __future__ import annotations

from array import array
from threading import Event
from time import monotonic

import pytest
from pocketstation import (
    Connector,
    ConnectorConfigurationField,
    ConnectorConfigurationRequirement,
    ConnectorConfigurationSchema,
    ConnectorConfigurationValue,
    ConnectorConfigurationValueKind,
    ConnectorDeliveryOutcome,
    ConnectorDeliveryReadiness,
    ConnectorDriver,
    ConnectorError,
    ConnectorErrorStage,
    ConnectorHealth,
    ConnectorInputDescriptor,
    ConnectorItem,
    ConnectorManifest,
    ConnectorRecovery,
    ConnectorRetryability,
    ConnectorShutdownMode,
    ConnectorWorker,
    PocketStationError,
    Session,
    connector,
)


class CollectingDriver(ConnectorDriver):
    def __init__(self) -> None:
        self.started = Event()
        self.delivered = Event()
        self.stopped = Event()
        self.shutdown_mode: ConnectorShutdownMode | None = None
        self.items: list[ConnectorItem] = []

    def start(self, context) -> None:
        super().start(context)
        self.started.set()

    def deliver(self, item, context) -> ConnectorDeliveryOutcome:
        self.items.append(item)
        self.delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    def shutdown(self, mode, context) -> None:
        self.shutdown_mode = mode
        self.stopped.set()


def test_python_connector_receives_application_owned_pcm_with_lineage() -> None:
    driver = CollectingDriver()
    prepared: list[tuple[ConnectorInputDescriptor, ...]] = []
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.collect.v1",
        package_version="1.0.0",
    )

    def prepare(
        inputs: tuple[ConnectorInputDescriptor, ...],
    ) -> CollectingDriver:
        prepared.append(inputs)
        return driver

    session = Session()
    audio = session.audio_input("playback", frame_samples_per_channel=4)
    endpoint = session.register_connector(
        Connector.with_driver(manifest, prepare)
    ).declare()
    route_id = audio.output.send(endpoint)

    running = session.start()
    assert driver.started.wait(1.0)
    audio.write(array("f", [0.25, -0.25, 0.5, -0.5]), discontinuity=True)
    assert driver.delivered.wait(1.0)
    stop = running.stop()

    assert stop.success
    assert driver.stopped.wait(1.0)
    assert driver.shutdown_mode is ConnectorShutdownMode.DRAIN
    assert len(prepared) == 1
    assert len(prepared[0]) == 1
    descriptor = prepared[0][0]
    assert descriptor.endpoint_id == endpoint.id
    assert descriptor.connector_id == endpoint.connector_id
    assert descriptor.route_id == route_id
    assert descriptor.port_name == "audio"
    assert descriptor.signal_wire_id == "pks.signal.pcm-audio.v1"
    assert descriptor.signal.is_audio
    assert descriptor.media.kind.value == "audio-pcm"
    assert descriptor.edge.media.kind.value == "audio-pcm"
    assert len(driver.items) == 1
    item = driver.items[0]
    assert item.kind == "audio"
    assert item.signal is None
    assert item.audio is not None
    assert item.audio.source_id == audio.source_id
    assert item.audio.stream_id == audio.stream_id
    assert item.audio.connector_id == endpoint.connector_id
    assert item.audio.sequence_number == 0
    assert item.audio.discontinuity_epoch == 1
    assert list(item.audio.samples.cast("f")) == pytest.approx([0.25, -0.25, 0.5, -0.5])


def test_configuration_is_typed_validated_and_secret_safe() -> None:
    schema = ConnectorConfigurationSchema(
        fields=(
            ConnectorConfigurationField(
                "token",
                ConnectorConfigurationValueKind.SECRET,
                "Provider credential.",
            ),
            ConnectorConfigurationField(
                "timeout_ms",
                ConnectorConfigurationValueKind.DURATION_MILLISECONDS,
                "Finite request timeout.",
                requirement=ConnectorConfigurationRequirement.DEFAULT,
                default=250,
            ),
        )
    )
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.configuration.v1",
        package_version="1.0.0",
        configuration=schema,
    )
    seen: list[dict[str, ConnectorConfigurationValue]] = []

    def prepare(inputs):
        seen.append(dict(inputs[0].configuration))
        return CollectingDriver()

    session = Session()
    endpoint = session.register_connector(
        Connector.with_driver(manifest, prepare)
    ).declare({"token": ConnectorConfigurationValue.secret("very-secret")})
    audio = session.audio_input("playback", frame_samples_per_channel=4)
    audio.output.send(endpoint)
    running = session.start()
    assert running.stop().success

    assert len(seen) == 1
    assert seen[0]["token"].expose_secret() == "very-secret"
    assert "very-secret" not in repr(seen[0]["token"])
    assert seen[0]["timeout_ms"].value == 250

    with pytest.raises(ConnectorError) as unknown:
        schema.configuration({"unknown": "value"})
    assert unknown.value.code == "connector.configuration.unknown_field"

    with pytest.raises(ConnectorError) as mismatch:
        schema.configuration({"token": "not-explicitly-secret"})
    assert mismatch.value.code == "connector.configuration.type_mismatch"

    with pytest.raises(ConnectorError) as duplicate_value:
        schema.configuration(
            [
                ("token", ConnectorConfigurationValue.secret("first")),
                ("token", ConnectorConfigurationValue.secret("second")),
            ]
        )
    assert duplicate_value.value.code == "connector.configuration.duplicate_value"

    with pytest.raises(ConnectorError) as duplicate_field:
        ConnectorConfigurationSchema(fields=(schema.fields[0], schema.fields[0]))
    assert duplicate_field.value.code == "connector.configuration.duplicate_field"


def test_connector_error_keeps_typed_stage_and_retryability() -> None:
    error = ConnectorError(
        "retry later",
        code="provider.unavailable",
        stage=ConnectorErrorStage.DELIVERY,
        retryability=ConnectorRetryability.RETRYABLE,
    )

    assert error.stage is ConnectorErrorStage.DELIVERY
    assert error.retryability is ConnectorRetryability.RETRYABLE


def test_connector_decorator_builds_an_in_process_provider() -> None:
    delivered = Event()
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.decorator.v1",
        package_version="1.0.0",
    )

    @connector(manifest)
    def provider(item, context):
        assert item.audio is not None
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    assert isinstance(provider, Connector)
    session = Session()
    audio = session.audio_input("generated", frame_samples_per_channel=4)
    audio.output.send(session.destination(provider))
    running = session.start()
    audio.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert delivered.wait(1.0)
    assert running.cancel().success


def test_session_destination_reuses_one_connector_registration() -> None:
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.destination.v1",
        package_version="1.0.0",
    )
    provider = Connector.from_handler(
        manifest,
        lambda _item, _context: ConnectorDeliveryOutcome.DELIVERED,
    )
    session = Session()

    first = session.destination(provider)
    registration = session.register_connector(provider)
    second = registration.declare()

    assert first.session_id == session.id
    assert second.session_id == session.id
    assert session.register_connector(provider).session_id == session.id


def test_session_destination_does_not_merge_different_connector_implementations() -> (
    None
):
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.destination-collision.v1",
        package_version="1.0.0",
    )
    first = Connector.from_handler(
        manifest,
        lambda _item, _context: ConnectorDeliveryOutcome.DELIVERED,
    )
    second = Connector.from_handler(
        manifest,
        lambda _item, _context: ConnectorDeliveryOutcome.DROPPED,
    )
    session = Session()
    session.destination(first)

    with pytest.raises(PocketStationError) as failure:
        session.destination(second)

    assert failure.value.code == "connector.registration_failed"


def test_connector_manifest_rejects_output_ports() -> None:
    from pocketstation import MediaCaps, PortDirection, PortSpec, SignalSpec

    with pytest.raises(Exception, match="input"):
        ConnectorManifest(
            operator_id="io.pocketstation.test.invalid.v1",
            package_version="1.0.0",
            inputs=(
                PortSpec(
                    "audio",
                    PortDirection.OUTPUT,
                    SignalSpec.audio(),
                    MediaCaps.audio(),
                ),
            ),
        )


def test_connector_failure_preserves_code_and_retryability_in_session_outcome() -> None:
    attempted = Event()

    def fail(item, context):
        attempted.set()
        raise ConnectorError(
            "provider request timed out",
            code="provider.timeout",
            stage=ConnectorErrorStage.DELIVERY,
            retryability=ConnectorRetryability.RETRYABLE,
        )

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.failure.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("generated", frame_samples_per_channel=4)
    audio.output.send(
        session.register_connector(Connector.from_handler(manifest, fail)).declare()
    )
    running = session.start()
    audio.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert attempted.wait(1.0)
    stop = running.stop()

    assert not stop.success
    assert stop.terminal_event is not None
    failures = stop.terminal_event.failures
    endpoint = next(failure for failure in failures if failure.kind.value == "endpoint")
    assert endpoint.error_code == "provider.timeout"
    assert endpoint.retryability is not None
    assert endpoint.retryability.value == "retryable"
    assert endpoint.message == "provider.timeout: provider request timed out"


def test_audio_connector_convenience_keeps_native_lineage_and_lifecycle() -> None:
    received = []
    delivered = Event()

    def publish(frame, context):
        received.append(frame)
        delivered.set()
        return ConnectorDeliveryOutcome.DELIVERED

    connector = Connector.from_audio_handler(
        "io.pocketstation.test.audio-handler.v1",
        publish,
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("remote-call", frame_samples_per_channel=4)
    audio.output.send(session.register_connector(connector).declare())

    running = session.start()
    audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    assert delivered.wait(1.0)
    assert running.stop().success
    assert connector.manifest.inputs[0].signal.is_audio
    assert received[0].source_id == audio.source_id
    assert received[0].stream_id == audio.stream_id
    assert received[0].route_enqueued_at_ns > 0
    assert received[0].route_received_at_ns >= received[0].route_enqueued_at_ns
    assert received[0].endpoint_enqueued_at_ns is None
    assert received[0].polled_at_ns is None


def test_stream_send_to_declares_the_connector_on_its_owning_session() -> None:
    delivered = Event()

    connector = Connector.from_audio_handler(
        "io.pocketstation.test.stream-destination.v1",
        lambda _frame, _context: delivered.set() or ConnectorDeliveryOutcome.DELIVERED,
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("agent-output", frame_samples_per_channel=4)
    route_id = audio.output.send_to(connector)

    running = session.start()
    audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))

    assert delivered.wait(1.0)
    assert int(route_id) > 0
    assert running.stop().success


def test_connector_observations_preserve_service_state_and_delivery_counters() -> None:
    delivered = Event()

    def handle(item, context):
        context.set_degraded("provider.rate_limited")
        context.set_reconnecting("provider.connection_lost")
        context.record_retry()
        context.set_connected()
        context.set_healthy()
        context.set_ready()
        delivered.set()
        return ConnectorDeliveryOutcome.DROPPED

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.observations.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("generated", frame_samples_per_channel=4)
    registered = session.register_connector(Connector.from_handler(manifest, handle))
    endpoint = registered.declare()
    audio.output.send(endpoint)
    running = session.start()
    audio.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert delivered.wait(1.0)

    observation = registered.observation(endpoint)
    assert observation is not None
    assert (
        observation.service_status.delivery_readiness
        is ConnectorDeliveryReadiness.READY
    )
    assert observation.service_status.health is ConnectorHealth.HEALTHY
    assert observation.service_status.recovery is ConnectorRecovery.IDLE
    assert observation.service_status.accepts_delivery
    assert observation.retry_attempts_total == 1
    assert observation.reconnects_total == 1

    [runtime] = registered.observations()
    assert runtime.endpoint_ids == (endpoint.id,)
    assert runtime.frames_received_total == 1
    assert runtime.frames_delivered_total == 0
    assert runtime.frames_dropped_total == 1
    assert runtime.connector == observation
    assert running.stop().success


def test_connector_context_expires_when_its_driver_is_destroyed() -> None:
    contexts = []
    delivered = Event()

    def handle(item, context):
        contexts.append(context)
        delivered.set()

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.context-lifetime.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input("generated", frame_samples_per_channel=4)
    audio.output.send(
        session.register_connector(Connector.from_handler(manifest, handle)).declare()
    )
    running = session.start()
    audio.write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert delivered.wait(1.0)
    assert running.stop().success

    with pytest.raises(PocketStationError) as failure:
        contexts[0].set_ready()
    assert failure.value.code == "connector.context_closed"


def test_connector_preparation_is_cancelled_during_transactional_rollback() -> None:
    cancelled = Event()

    class PreparedDriver(CollectingDriver):
        def cancel_preparation(self) -> None:
            cancelled.set()

    first = ConnectorManifest.audio(
        "io.pocketstation.test.rollback-first.v1",
        package_version="1.0.0",
    )
    second = ConnectorManifest.audio(
        "io.pocketstation.test.rollback-second.v1",
        package_version="1.0.0",
    )

    def reject(_inputs):
        raise ConnectorError(
            "provider configuration is unavailable",
            code="provider.unavailable",
            stage=ConnectorErrorStage.PREPARE,
        )

    session = Session()
    audio = session.audio_input("generated", frame_samples_per_channel=4)
    audio.output.send(
        session.register_connector(
            Connector.with_driver(first, lambda _inputs: PreparedDriver())
        ).declare()
    )
    audio.output.send(
        session.register_connector(Connector.with_driver(second, reject)).declare()
    )

    with pytest.raises(PocketStationError) as failure:
        session.start()
    assert failure.value.code == "session.endpoint_prepare_failed"
    assert cancelled.wait(1.0)


def test_connector_groups_multiple_routes_into_one_provider_lifecycle() -> None:
    schema = ConnectorConfigurationSchema(
        fields=(
            ConnectorConfigurationField(
                "publisher_group",
                ConnectorConfigurationValueKind.TEXT,
                "Stable provider lifecycle group.",
            ),
        )
    )
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.grouped.v1",
        package_version="1.0.0",
        configuration=schema,
    )
    driver = CollectingDriver()
    prepared: list[tuple[ConnectorInputDescriptor, ...]] = []

    class GroupedFactory:
        def preparation_group(self, route_id, configuration):
            assert route_id > 0
            return str(configuration["publisher_group"].value)

        def prepare(self, inputs):
            prepared.append(tuple(inputs))
            return driver

    session = Session()
    first = session.audio_input("application", frame_samples_per_channel=4)
    second = session.audio_input("microphone", frame_samples_per_channel=4)
    registered = session.register_connector(
        Connector.with_driver(manifest, GroupedFactory())
    )
    first_endpoint = registered.declare({"publisher_group": "broadcast"})
    second_endpoint = registered.declare({"publisher_group": "broadcast"})
    first.output.send(first_endpoint)
    second.output.send(second_endpoint)

    running = session.start()
    first.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    second.write(array("f", [0.5, 0.6, 0.7, 0.8]))
    deadline = monotonic() + 1.0
    while len(driver.items) < 2 and monotonic() < deadline:
        driver.delivered.wait(0.01)
    assert running.stop().success

    assert len(prepared) == 1
    assert len(prepared[0]) == 2
    assert len(driver.items) == 2
    [runtime] = registered.observations()
    assert set(runtime.endpoint_ids) == {first_endpoint.id, second_endpoint.id}
    assert runtime.frames_delivered_total == 2


def test_connector_worker_receives_finite_native_owned_batches() -> None:
    finished = Event()
    batches: list[tuple[ConnectorItem, ...]] = []
    total = 8

    class BatchWorker(ConnectorWorker):
        def deliver_batch(self, items, context):
            batches.append(tuple(items))
            if sum(len(batch) for batch in batches) >= total:
                finished.set()
            return [ConnectorDeliveryOutcome.DELIVERED for _ in items]

    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.batch-worker.v1",
        package_version="1.0.0",
    )
    session = Session()
    audio = session.audio_input(
        "generated",
        capacity_frames=16,
        frame_samples_per_channel=4,
    )
    registered = session.register_connector(
        Connector.with_worker(
            manifest,
            lambda _inputs: BatchWorker(),
            maximum_batch_items=4,
        )
    )
    audio.output.send(registered.declare())
    running = session.start()
    for sequence in range(total):
        audio.write(array("f", [float(sequence)] * 4))
    assert finished.wait(1.0)
    assert running.stop().success

    assert sum(len(batch) for batch in batches) == total
    assert all(1 <= len(batch) <= 4 for batch in batches)
    [runtime] = registered.observations()
    assert runtime.frames_received_total == total
    assert runtime.frames_delivered_total == total
    assert runtime.frames_dropped_total == 0


def test_connector_worker_rejects_unbounded_batch_sizes() -> None:
    manifest = ConnectorManifest.audio(
        "io.pocketstation.test.invalid-batch.v1",
        package_version="1.0.0",
    )
    with pytest.raises(ValueError, match="between 1 and 1024"):
        Connector.with_worker(
            manifest,
            lambda _inputs: ConnectorWorker(),
            maximum_batch_items=0,
        )
