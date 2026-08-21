"""Static interface for the PyO3 extension."""

from collections.abc import Iterator
from pathlib import Path

from .identity import (
    ClockDomainId,
    ClockDomainKind,
    ClockDomainOrigin,
    ConnectorId,
    EndpointId,
    OperatorInstanceId,
    RouteId,
    RuntimeSessionId,
    SourceId,
    SourceInstanceId,
    StemId,
    StreamId,
)

class _ExtensionAbiVersion:
    struct_size_bytes: int
    abi_major: int
    abi_minor: int

class _NativeExtensionRegistration:
    id: str
    kind: str
    revision: int
    generation: int

class _NativeExtensionLibrary:
    canonical_path: Path
    registrations: list[_NativeExtensionRegistration]

def extension_abi_version() -> _ExtensionAbiVersion: ...
def extension_abi_is_compatible(
    abi_major: int,
    abi_minor: int,
    struct_size_bytes: int,
) -> None: ...
def validate_extension_descriptor(
    extension_id: str,
    kind: str,
    revision: int,
    generation: int,
    abi_major: int,
    abi_minor: int,
    ports: list[tuple[str, str, bool, str, str, str]],
) -> None: ...

class Source:
    @staticmethod
    def application(name: str) -> Source: ...
    @staticmethod
    def application_bundle_id(bundle_id: str) -> Source: ...
    @staticmethod
    def application_process_id(process_id: int) -> Source: ...
    @staticmethod
    def application_stable_id(platform: str, stable_key: str) -> Source: ...
    @staticmethod
    def application_process_instance(
        process_id: int,
        platform: str,
        stable_key: str,
    ) -> Source: ...
    @staticmethod
    def microphone_default() -> Source: ...
    @staticmethod
    def microphone_id(device_id: str) -> Source: ...
    @staticmethod
    def system_mix() -> Source: ...

class DiscoveredSource:
    platform: str
    kind: str
    stable_key: str
    source_id: SourceId
    name: str
    process_id: int | None
    application_id: str | None
    device_uid: str | None
    state: str
    sample_rate_hz: int
    channel_count: int
    identity_strength: str
    selector_persistence_scope: str | None
    process_tree_scope: str | None
    def authorization_before_open(
        self,
        os_permission: str = "not-observable",
        application_policy: str = "not-observable",
        session_grant: str = "not-evaluated",
        permission_epoch: int = 1,
    ) -> CaptureAuthorizationSnapshot: ...

class CaptureAuthorizationSnapshot:
    capability: str
    os_permission: str
    application_policy: str
    session_grant: str
    capture_scope: str
    scope_stable_id: str | None
    identity_strength: str
    permission_epoch: int
    observed_at_ns: int
    open_outcome: str

class CapturePermissionTransition:
    kind: str
    previous: str
    current: str
    permission_epoch: int

class CapturePermissionLifecycle:
    def __init__(self, current: str) -> None: ...
    current: str
    permission_epoch: int
    def observe(self, current: str) -> CapturePermissionTransition | None: ...

def discover_sources(
    query_kind: str = "any",
    value: str | None = None,
) -> list[DiscoveredSource]: ...
def application_capture_available() -> bool: ...
def microphone_permission_observation() -> str: ...

class _SignalSpec:
    def __init__(
        self,
        kind: str,
        format: str | None = None,
        custom_id: str | None = None,
        role: str | None = None,
        schema: str | None = None,
    ) -> None: ...
    kind: str
    format: str | None
    custom_id: str | None
    role: str | None
    schema: str | None
    wire_id: str
    is_audio: bool
    def is_compatible_with(self, other: _SignalSpec) -> bool: ...

class _MediaCaps:
    def __init__(
        self,
        kind: str,
        format: str | None = None,
        sample_rate_hz: int | None = None,
        frame_samples: int | None = None,
        channel_layout: str | None = None,
    ) -> None: ...
    kind: str
    format: str | None
    sample_rate_hz: int | None
    frame_samples: int | None
    channel_layout: str | None
    def is_compatible_with(self, other: _MediaCaps) -> bool: ...
    def negotiate(self, other: _MediaCaps) -> _MediaCaps | None: ...
    def supports_signal(self, signal: _SignalSpec) -> bool: ...

class _PortSpec:
    def __init__(
        self,
        name: str,
        direction: str,
        signal: _SignalSpec,
        media: _MediaCaps,
        multiplicity: str,
        required: bool,
    ) -> None: ...
    name: str
    direction: str
    signal: _SignalSpec
    media: _MediaCaps
    multiplicity: str
    required: bool

class _EdgeContract:
    @staticmethod
    def realtime_audio() -> _EdgeContract: ...
    @staticmethod
    def bounded_async() -> _EdgeContract: ...
    media: _MediaCaps
    clock: str
    latency_budget_ms: int | None
    jitter_budget_ms: int | None
    backpressure: str
    delivery: str
    loss: str
    copy_policy: str
    observability: str
    max_payload_bytes: int | None
    def with_media(self, media: _MediaCaps) -> _EdgeContract: ...
    def with_backpressure(self, value: str) -> _EdgeContract: ...
    def with_copy_policy(self, value: str) -> _EdgeContract: ...
    def with_jitter_budget_ms(self, value: int | None) -> _EdgeContract: ...
    def with_max_payload_bytes(self, value: int) -> _EdgeContract: ...

class BusSubscription:
    id: int
    session_id: RuntimeSessionId
    route_id: RouteId
    signal: _SignalSpec
    edge: _EdgeContract

class _SignalTiming:
    source_timestamp_ns: int | None
    observed_timestamp_ns: int
    session_timestamp_ns: int | None
    duration_ns: int | None

class _SignalLineage:
    session_id: RuntimeSessionId
    stream_id: StreamId
    source_id: SourceId
    clock_id: ClockDomainId
    clock: ClockDomainDescriptor
    sequence_number: int
    source_generation: int
    discontinuity_epoch: int
    policy_epoch: int

class _SignalDerivation:
    upstream_lineage: _SignalLineage
    upstream_timing: _SignalTiming
    operator_id: str
    operator_revision: int
    operator_generation: int
    connector_id: ConnectorId | None

class _SignalAudioPayload:
    samples: memoryview
    samples_f32le: bytes
    sample_count: int
    sample_rate_hz: int
    channel_count: int
    stream_id: StreamId
    source_id: SourceId
    sequence_number: int
    timestamp_ns: int
    sample_format: str

class _SignalEnvelope:
    signal: _SignalSpec
    timing: _SignalTiming
    lineage: _SignalLineage | None
    derivation: _SignalDerivation | None
    payload_kind: str
    text: str | None
    bytes: bytes | None
    audio: _SignalAudioPayload | None

class _SignalRead:
    status: str
    envelope: _SignalEnvelope | None
    error: str | None

class _SignalSubscriptionMetrics:
    capacity_signals: int
    max_payload_bytes: int
    maximum_buffered_payload_bytes: int
    depth_signals: int
    peak_depth_signals: int
    enqueued_total: int
    received_total: int
    dropped_total: int

class _EndpointDescriptor:
    def __init__(
        self,
        node_type_id: str,
        operator_id: str,
        configuration: dict[str, str],
        input_edge: _EdgeContract | None = None,
    ) -> None: ...

class _ConnectorConfigurationValue:
    @staticmethod
    def text(value: str) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def boolean(value: bool) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def signed_integer(value: int) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def unsigned_integer(value: int) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def duration_milliseconds(value: int) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def byte_count(value: int) -> _ConnectorConfigurationValue: ...
    @staticmethod
    def secret(value: str) -> _ConnectorConfigurationValue: ...
    kind: str
    def expose_secret(self) -> str: ...
    def as_text(self) -> str | None: ...
    def as_boolean(self) -> bool | None: ...
    def as_signed_integer(self) -> int | None: ...
    def as_unsigned_integer(self) -> int | None: ...

class _ConnectorConfigurationConstraint:
    @staticmethod
    def non_empty() -> _ConnectorConfigurationConstraint: ...
    @staticmethod
    def text_length_bytes(
        minimum: int,
        maximum: int,
    ) -> _ConnectorConfigurationConstraint: ...
    @staticmethod
    def signed_range(
        minimum: int,
        maximum: int,
    ) -> _ConnectorConfigurationConstraint: ...
    @staticmethod
    def unsigned_range(
        minimum: int,
        maximum: int,
    ) -> _ConnectorConfigurationConstraint: ...
    @staticmethod
    def one_of(values: list[str]) -> _ConnectorConfigurationConstraint: ...

class _ConnectorConfigurationField:
    def __init__(
        self,
        name: str,
        kind: str,
        requirement: str,
        documentation: str,
        default: _ConnectorConfigurationValue | None = None,
        constraints: list[_ConnectorConfigurationConstraint] = [],
        deprecation: str | None = None,
    ) -> None: ...

class _ConnectorConfigurationSchema:
    def __init__(
        self,
        revision: int = 1,
        fields: list[_ConnectorConfigurationField] = [],
    ) -> None: ...

class _ConnectorConfiguration:
    def __init__(
        self,
        entries: list[tuple[str, _ConnectorConfigurationValue]] = [],
    ) -> None: ...

class _ConnectorManifest:
    def __init__(
        self,
        operator_id: str,
        node_type_id: str,
        package_version: str,
        inputs: list[_PortSpec],
        configuration: _ConnectorConfigurationSchema,
        manifest_revision: int = 1,
        startup_timeout_ms: int = 5_000,
        probe_interval_ms: int = 100,
        success_threshold: int = 1,
        failure_threshold: int = 1,
        capabilities: list[tuple[str, str]] = [],
        requirements: list[tuple[str, bool, str]] = [],
    ) -> None: ...

class ConnectorInputDescriptor:
    endpoint_id: int
    connector_id: int | None
    route_id: int
    port_name: str
    signal_wire_id: str
    signal: _SignalSpec
    media: _MediaCaps
    edge: _EdgeContract
    configuration: dict[str, _ConnectorConfigurationValue]

class ConnectorItem:
    kind: str
    input: ConnectorInputDescriptor
    audio: AudioFrame | None
    signal: _SignalEnvelope | None

class ConnectorContext:
    stop_requested: bool
    shutdown_mode: str | None
    def set_ready(self) -> bool: ...
    def set_not_ready(self, reason_code: str | None = None) -> bool: ...
    def set_degraded(self, reason_code: str) -> bool: ...
    def set_healthy(self) -> bool: ...
    def set_reconnecting(self, reason_code: str) -> bool: ...
    def set_connected(self) -> bool: ...
    def record_retry(self) -> None: ...

class _ConnectorErrorSnapshot:
    code: str
    stage: str
    retryability: str
    message: str

class _ConnectorServiceStatus:
    delivery_readiness: str
    health: str
    recovery: str
    readiness_reason_code: str | None
    health_reason_code: str | None
    recovery_reason_code: str | None
    revision: int
    last_transition_elapsed_ns: int
    accepts_delivery: bool

class _ConnectorObservations:
    service_status: _ConnectorServiceStatus
    status_transitions_total: int
    retry_attempts_total: int
    reconnects_total: int
    failures_total: int
    last_error: _ConnectorErrorSnapshot | None

class _ConnectorRuntimeObservations:
    endpoint_ids: list[int]
    connector: _ConnectorObservations
    frames_received_total: int
    frames_delivered_total: int
    frames_dropped_total: int
    discontinuities_total: int
    endpoint_failures_total: int

class _RegisteredConnector:
    session_id: int
    def observations(self) -> list[_ConnectorRuntimeObservations]: ...
    def observation(self, endpoint: Endpoint) -> _ConnectorObservations | None: ...

class Endpoint:
    id: EndpointId
    session_id: RuntimeSessionId
    connector_id: ConnectorId | None

class RelayPublisher: ...

class OperatorInput:
    port_name: str

class OperatorInstance:
    session_id: RuntimeSessionId
    instance_id: OperatorInstanceId
    def input(self, port_name: str) -> OperatorInput: ...
    def output(self, port_name: str) -> DerivedStream: ...

class Stem:
    @property
    def id(self) -> StemId: ...
    def send(self, endpoint: Endpoint) -> RouteId: ...
    def send_to(self, endpoint: Endpoint, input_port: str | None) -> RouteId: ...
    def connect(self, input: OperatorInput) -> RouteId: ...
    def through(
        self,
        operator_id: str,
        configuration: dict[str, str],
        input_port: str | None = None,
        output_port: str | None = None,
    ) -> DerivedStream: ...
    def record(self, stem_name: str) -> Endpoint: ...
    def publish(self, publisher: RelayPublisher, bus_id: str) -> RouteId: ...
    session_id: RuntimeSessionId

class DerivedStream:
    session_id: RuntimeSessionId
    operator_instance_id: OperatorInstanceId
    output_port: str | None
    def output(self, port_name: str) -> DerivedStream: ...
    def connect(self, input: OperatorInput) -> RouteId: ...
    def through(
        self,
        operator_id: str,
        configuration: dict[str, str],
        input_port: str | None = None,
        output_port: str | None = None,
    ) -> DerivedStream: ...
    def send(self, endpoint: Endpoint) -> RouteId: ...
    def send_to(self, endpoint: Endpoint, input_port: str | None) -> RouteId: ...
    def reenter_audio(self) -> Stem: ...

class SourceInstance:
    session_id: RuntimeSessionId
    instance_id: SourceInstanceId
    source_id: SourceId
    def output(self, port_name: str) -> SourceOutput: ...

class SourceOutput:
    session_id: RuntimeSessionId
    source_instance_id: SourceInstanceId
    source_id: SourceId
    stream_id: StreamId
    output_port: str
    def connect(self, input: OperatorInput) -> RouteId: ...
    def through(
        self,
        operator_id: str,
        configuration: dict[str, str],
        input_port: str | None = None,
        output_port: str | None = None,
    ) -> DerivedStream: ...
    def send(self, endpoint: Endpoint) -> RouteId: ...
    def send_to(self, endpoint: Endpoint, input_port: str | None) -> RouteId: ...
    def record(self, stem_name: str) -> Endpoint: ...
    def publish(self, publisher: RelayPublisher, bus_id: str) -> RouteId: ...

class ClockDomainDescriptor:
    id: ClockDomainId
    kind: ClockDomainKind
    origin: ClockDomainOrigin
    tick_rate_hz: int | None

class AudioFrame:
    sample_rate_hz: int
    channel_count: int
    session_id: RuntimeSessionId
    stream_id: StreamId
    source_id: SourceId
    stem_id: StemId
    clock_id: ClockDomainId
    clock: ClockDomainDescriptor
    sequence_number: int
    timestamp_start_ns: int
    duration_ns: int
    source_generation: int
    discontinuity_epoch: int
    permission_epoch: int
    endpoint_id: EndpointId
    connector_id: ConnectorId | None
    route_id: RouteId
    route_enqueued_at_ns: int
    route_received_at_ns: int
    endpoint_enqueued_at_ns: int | None
    polled_at_ns: int | None
    @property
    def samples(self) -> memoryview: ...
    @property
    def samples_f32le(self) -> bytes: ...
    @property
    def sample_count(self) -> int: ...
    @property
    def sample_format(self) -> str: ...
    def __repr__(self) -> str: ...

class AudioBatch:
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[AudioFrame]: ...
    def __getitem__(self, index: int) -> AudioFrame: ...
    def frames(self) -> list[AudioFrame]: ...

class RecordingDiscontinuity:
    stem_id: int
    label: str
    kind: str
    timestamp_start_ns: int
    timestamp_end_ns: int
    sequence_start: int | None
    sequence_end: int | None

class RecordingStemOutcome:
    stem_name: str
    frames_written_total: int
    stale_frames_total: int
    error: str | None
    queue_capacity_frames: int
    queue_peak_frames: int
    frames_delivered_total: int
    frames_dropped_total: int
    queue_full_drops_total: int
    discontinuities_total: int
    def discontinuities(self) -> list[RecordingDiscontinuity]: ...

class RecordingOutcome:
    session_id: RuntimeSessionId
    group_id: str
    complete: bool
    state: str
    completed_stems: int
    failed_stems: int
    session_directory: str
    manifest_path: str
    manifest_schema_version: int
    error_code: str | None
    def stems(self) -> list[RecordingStemOutcome]: ...

class StopResult:
    success: bool
    already_stopped: bool
    disposition: str
    runtime_worker_panicked: bool
    capture_finalization_failures_total: int
    operator_finalization_failures_total: int
    endpoint_finalization_failures_total: int
    runtime_failures_total: int
    lineage_failures_total: int
    source_send_rejections_total: int
    runtime_events_total: int
    recording: RecordingOutcome | None
    trace: SessionTraceRecorderOutcome | None
    trace_error: str | None
    terminal_event: SessionEvent | None
    def relay_outcomes(self) -> list[RelayPublishOutcome]: ...
    def sidecar_outcomes(self) -> list[_SidecarSnapshot]: ...

class RelayPublishOutcome:
    bus_id: str
    endpoint_id: int
    route_id: int
    frames_received_total: int
    rtp_packets_sent_total: int
    rtp_payload_bytes_sent_total: int
    ingress_queue_drops_total: int
    publisher_stale_drops_total: int
    failures_total: int
    error: str | None

class SessionEvent:
    kind: str
    lifecycle_state: str | None
    session_id: int
    stem_id: int | None
    endpoint_id: int | None
    route_id: int | None
    failures_total: int
    terminal_state: str | None
    source_event_kind: str | None
    source_platform: str | None
    source_kind: str | None
    source_stable_key: str | None
    source_source_id: int | None
    source_generation: int | None
    source_recovery_requirement: str | None
    source_failure_operation: str | None
    source_failure_class: str | None
    source_platform_status_code: int | None
    source_backend_class: str | None
    def failures(self) -> list[_SessionFailure]: ...

class _SessionFailure:
    kind: str
    stage: str | None
    operation: str | None
    error_class: str | None
    error_code: str | None
    retryability: str | None
    component: str | None
    component_kind: str | None
    message: str | None
    stem_id: int | None
    route_id: int | None
    endpoint_id: int | None
    operator_instance_id: int | None
    sidecar_id: int | None
    source_event_kind: str | None
    source_platform: str | None
    source_kind: str | None
    source_stable_key: str | None
    source_source_id: int | None
    source_generation: int | None
    source_recovery_requirement: str | None
    source_failure_operation: str | None
    source_failure_class: str | None
    source_platform_status_code: int | None
    source_backend_class: str | None

class _EdgeMetrics:
    queue_capacity_frames: int
    queue_depth_frames: int
    queue_peak_frames: int
    frames_enqueued_total: int
    frames_delivered_total: int
    frames_dropped_total: int
    overruns_total: int
    receiver_unavailable_drops_total: int
    queue_full_drops_total: int
    shared_reference_exhausted_drops_total: int
    branch_pool_exhausted_drops_total: int
    invalid_copy_policy_drops_total: int
    freeze_failed_drops_total: int
    discontinuities_total: int
    source_identity_discontinuities_total: int
    sequence_discontinuities_total: int
    timestamp_discontinuities_total: int
    lineage_epoch_discontinuities_total: int
    manually_reported_discontinuities_total: int
    enqueue_to_receive_samples_total: int
    enqueue_to_receive_invalid_order_total: int
    enqueue_to_receive_p50_ns: int
    enqueue_to_receive_p95_ns: int
    enqueue_to_receive_p99_ns: int
    enqueue_to_receive_max_ns: int
    source_timestamp_to_receive_samples_total: int
    source_timestamp_to_receive_missing_total: int
    source_timestamp_to_receive_future_total: int
    source_timestamp_to_receive_p50_ns: int
    source_timestamp_to_receive_p95_ns: int
    source_timestamp_to_receive_p99_ns: int
    source_timestamp_to_receive_max_ns: int
    worker_failures_total: int
    shutdown_discarded_total: int

class RouteMetrics:
    route_id: int
    endpoint_id: int
    endpoint_observation_stage: str
    queue_capacity_frames: int
    queue_depth_frames: int
    queue_peak_frames: int
    frames_enqueued_total: int
    frames_attempted_total: int
    frames_delivered_total: int
    frames_dropped_total: int
    queue_full_drops_total: int
    overruns_total: int
    receiver_unavailable_drops_total: int
    shared_reference_exhausted_drops_total: int
    branch_pool_exhausted_drops_total: int
    invalid_copy_policy_drops_total: int
    freeze_failed_drops_total: int
    discontinuities_total: int
    source_identity_discontinuities_total: int
    sequence_discontinuities_total: int
    timestamp_discontinuities_total: int
    lineage_epoch_discontinuities_total: int
    manually_reported_discontinuities_total: int
    enqueue_to_receive_samples_total: int
    enqueue_to_receive_invalid_order_total: int
    enqueue_to_receive_p50_ns: int
    enqueue_to_receive_p95_ns: int
    enqueue_to_receive_p99_ns: int
    enqueue_to_receive_max_ns: int
    source_timestamp_to_receive_samples_total: int
    source_timestamp_to_receive_missing_total: int
    source_timestamp_to_receive_future_total: int
    source_timestamp_to_receive_p50_ns: int
    source_timestamp_to_receive_p95_ns: int
    source_timestamp_to_receive_p99_ns: int
    source_timestamp_to_receive_max_ns: int
    worker_failures_total: int
    shutdown_discarded_total: int
    endpoint_frames_received_total: int
    endpoint_frames_delivered_total: int
    endpoint_frames_dropped_total: int
    endpoint_discontinuities_total: int
    endpoint_failures_total: int
    endpoint_finalization_failures_total: int
    drop_observation_interval: str
    drop_rate_pct: float
    source_latency_boundary: str
    source_latency_unit: str

class _SessionSourceMetrics:
    stem_id: int
    callback_buffers_total: int
    capture_frames_enqueued_total: int
    capture_pool_exhausted_total: int
    capture_dispatch_queue_full_total: int
    capture_invalid_buffer_total: int
    capture_oversized_buffer_total: int
    capture_stream_errors_total: int
    capture_timestamp_epoch_clamps_total: int
    frame_stream_delivered_frames_total: int
    frame_stream_dropped_newest_frames_total: int
    frames_discarded_before_start_total: int
    runtime_event_capacity_count: int
    runtime_event_maximum_event_owned_bytes: int
    runtime_event_maximum_buffered_owned_bytes: int
    runtime_event_depth_count: int
    runtime_event_depth_owned_bytes: int
    runtime_event_peak_depth_owned_bytes: int
    runtime_events_enqueued_total: int
    runtime_events_dropped_total: int
    runtime_events_dropped_oversized_total: int
    ingress_queue_capacity_frames: int
    ingress_queue_depth_frames: int
    ingress_queue_peak_frames: int
    ingress_frames_enqueued_total: int
    ingress_frames_delivered_total: int
    ingress_frames_rejected_full_total: int
    ingress_frames_rejected_cancelled_total: int
    ingress_frames_discarded_total: int

class _ExternalSourceMetrics:
    source_instance_id: int
    source_id: int
    emitted_total: int
    dropped_total: int
    failure_total: int
    cancellation_total: int
    discontinuity_total: int
    recovery_total: int
    policy_change_total: int
    ready: bool
    joined: bool

class _OperatorInputMetrics:
    port_name: str
    edge: _EdgeMetrics

class _OperatorWorkerMetrics:
    input_attempted_total: int
    input_dropped_total: int
    processed_total: int
    output_emitted_total: int
    output_dropped_total: int
    output_nonterminal_total: int
    output_terminal_total: int
    process_failure_total: int
    timeout_total: int
    cancellation_total: int
    graceful_finish_total: int
    idle_poll_total: int
    ready: bool
    joined: bool

class _OperatorMetrics:
    operator_instance_id: int
    input_edge: _EdgeMetrics
    worker: _OperatorWorkerMetrics
    finalization_failures_total: int
    def input_ports(self) -> list[_OperatorInputMetrics]: ...

class _TypedEdgeMetrics:
    capacity_signals: int
    max_payload_bytes: int
    maximum_buffered_payload_bytes: int
    depth_signals: int
    peak_depth_signals: int
    enqueued_total: int
    received_total: int
    dropped_total: int

class _DerivedRouteMetrics:
    route_id: int
    endpoint_id: int
    output: _TypedEdgeMetrics
    endpoint_observation_stage: str
    endpoint_frames_received_total: int
    endpoint_frames_delivered_total: int
    endpoint_frames_dropped_total: int
    endpoint_discontinuities_total: int
    endpoint_failures_total: int
    endpoint_finalization_failures_total: int

class _AudioReentryMetrics:
    operator_instance_id: int
    stem_id: int
    queue_capacity_signals: int
    queue_depth_signals: int
    queue_peak_signals: int
    signals_enqueued_total: int
    signals_received_total: int
    signals_dropped_total: int
    pool_slots: int
    frame_capacity_samples: int
    maximum_buffered_audio_bytes: int
    normalized_total: int
    invalid_total: int
    shared_audio_rejected_total: int
    pool_exhausted_total: int
    ingress_rejected_total: int
    audio_frames_enqueued_total: int
    cancellation_total: int
    joined: bool

class SessionMetrics:
    event_capacity_count: int
    event_maximum_event_owned_bytes: int
    event_maximum_buffered_owned_bytes: int
    event_depth_count: int
    event_depth_owned_bytes: int
    event_peak_depth_count: int
    event_peak_depth_owned_bytes: int
    events_enqueued_total: int
    events_dropped_total: int
    events_dropped_oversized_total: int
    event_receiver_closed_total: int
    audio_registered_endpoints: int
    audio_queue_capacity_frames: int
    audio_queue_depth_frames: int
    audio_queue_peak_frames: int
    audio_queue_depth_invariant_failures_total: int
    audio_frames_received_total: int
    audio_frames_delivered_total: int
    audio_queue_full_drops_total: int
    audio_invalid_ownership_drops_total: int
    audio_lease_capacity_count: int
    audio_outstanding_leases: int
    audio_lease_exhausted_total: int
    audio_batches_polled_total: int
    audio_frames_polled_total: int
    source_count: int
    external_source_count: int
    route_count: int
    operator_count: int
    derived_route_count: int
    audio_reentry_count: int
    routes: list[RouteMetrics]
    sources: list[_SessionSourceMetrics]
    external_sources: list[_ExternalSourceMetrics]
    operators: list[_OperatorMetrics]
    derived_routes: list[_DerivedRouteMetrics]
    audio_reentries: list[_AudioReentryMetrics]

class SessionTraceRecorderOutcome:
    path: str
    records_attempted_total: int
    records_enqueued_total: int
    records_dropped_total: int
    records_written_total: int
    rolling_hash: int
    complete: bool

class _SessionTraceValidation:
    session_id: int
    lifecycle: list[str]
    terminal_state: str
    source_failures_total: int
    endpoint_failures_total: int
    rollback_failures_total: int
    finalization_failures_total: int
    records_validated_total: int

class SessionTraceRecord:
    sequence_index: int
    observed_at_ns: int
    session_id: int
    kind: str
    lifecycle_state: str | None
    terminal_state: str | None
    stem_id: int | None
    route_id: int | None
    endpoint_id: int | None
    endpoint_stage: str | None
    rollback_stage: str | None
    finalization_stage: str | None
    source_failures_total: int | None
    endpoint_failures_total: int | None
    rollback_failures_total: int | None
    finalization_failures_total: int | None

class SessionTrace:
    @staticmethod
    def read(path: Path) -> SessionTrace: ...
    session_id: int
    outcome: SessionTraceRecorderOutcome
    records_total: int
    def records(self) -> list[SessionTraceRecord]: ...
    def validate(self) -> _SessionTraceValidation: ...

class _SidecarProcessSpec:
    def __init__(
        self,
        id: int,
        program: Path,
        arguments: list[str] = [],
        configuration: bytes = b"",
        data_capacity_messages: int = 64,
        max_signal_id_bytes: int = 256,
        max_role_bytes: int = 256,
        max_schema_bytes: int = 1024,
        max_payload_bytes: int = 1048576,
        ready_timeout_ms: int = 5000,
        processing_timeout_ms: int = 5000,
        shutdown_timeout_ms: int = 2000,
    ) -> None: ...
    id: int
    program: Path
    arguments: list[str]
    configuration: bytes
    data_capacity_messages: int
    max_signal_id_bytes: int
    max_role_bytes: int
    max_schema_bytes: int
    max_payload_bytes: int
    ready_timeout_ms: int
    processing_timeout_ms: int
    shutdown_timeout_ms: int

class _SidecarMessage:
    def __init__(
        self,
        *,
        kind: str,
        stream_id: int,
        sequence_number: int,
        timestamp_ns: int,
        signal_id: str,
        payload: bytes,
        terminal: bool = False,
        role: str | None = None,
        schema: str | None = None,
    ) -> None: ...
    kind: str
    terminal: bool
    stream_id: int
    sequence_number: int
    timestamp_ns: int
    signal_id: str
    role: str | None
    schema: str | None
    payload: bytes

class _SidecarRead:
    status: str
    message: _SidecarMessage | None

class _SidecarSnapshot:
    sidecar_id: int
    state: str
    state_transitions: int
    data_enqueued_total: int
    data_received_total: int
    data_dropped_total: int
    protocol_failures_total: int
    timeouts_total: int
    forced_kills_total: int
    reaps_total: int
    def visited(self, state: str) -> bool: ...

class _SessionStartCancellation:
    def __init__(self) -> None: ...
    def request(self) -> None: ...
    def is_requested(self) -> bool: ...

class _AudioInputObservations:
    capacity_frames: int
    buffer_slots: int
    available_buffers: int
    accepted_total: int
    full_total: int
    invalid_total: int
    cancelled: bool
    closed: bool

class _AudioInput:
    source_id: SourceId
    stream_id: StreamId
    output: SourceOutput
    def try_write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
    ) -> None: ...
    def close(self) -> None: ...
    def observations(self) -> _AudioInputObservations: ...

class _SourceManifest:
    def __init__(
        self,
        source_type_id: str,
        outputs: list[_PortSpec],
        revision: int = 1,
        implementation_generation: int = 1,
    ) -> None: ...
    source_type_id: str
    revision: int
    implementation_generation: int

class _SourceEmission:
    @staticmethod
    def text(
        output_port: str,
        payload: str,
        signal: _SignalSpec,
        source_timestamp_ns: int | None = None,
        observed_timestamp_ns: int | None = None,
        duration_ns: int | None = None,
        source_generation: int = 1,
        discontinuity_epoch: int = 0,
        policy_epoch: int = 0,
        clock_domain_id: int = 1,
        terminal: bool = False,
    ) -> _SourceEmission: ...
    @staticmethod
    def bytes(
        output_port: str,
        payload: bytes,
        signal: _SignalSpec,
        source_timestamp_ns: int | None = None,
        observed_timestamp_ns: int | None = None,
        duration_ns: int | None = None,
        source_generation: int = 1,
        discontinuity_epoch: int = 0,
        policy_epoch: int = 0,
        clock_domain_id: int = 1,
        terminal: bool = False,
    ) -> _SourceEmission: ...

class _SourceOutputIdentity:
    output_port: str
    stream_id: StreamId

class _SourcePrepareContext:
    source_type_id: str
    session_id: RuntimeSessionId | None
    source_id: SourceId | None
    outputs: list[_SourceOutputIdentity]

class _SourceCancellation:
    cancelled: bool

class _RegisteredSource:
    source_type_id: str

class _OperatorManifest:
    def __init__(
        self,
        operator_id: str,
        inputs: list[_PortSpec],
        outputs: list[_PortSpec],
        revision: int = 1,
        implementation_generation: int = 1,
        queue_capacity_signals: int = 8,
        process_timeout_ms: int = 30_000,
        network_allowed: bool = False,
        filesystem_allowed: bool = False,
        drain_queued: bool = False,
        continue_on_failure: bool = False,
        terminal_roles: list[str] = [],
    ) -> None: ...
    operator_id: str

class _OperatorEmission:
    @staticmethod
    def audio(payload: object, signal: _SignalSpec) -> _OperatorEmission: ...
    @staticmethod
    def text(payload: str, signal: _SignalSpec) -> _OperatorEmission: ...
    @staticmethod
    def bytes(payload: bytes, signal: _SignalSpec) -> _OperatorEmission: ...

class _EndpointManifest:
    def __init__(
        self,
        operator_id: str,
        node_type_id: str,
        inputs: list[_PortSpec],
    ) -> None: ...
    operator_id: str
    node_type_id: str

class EndpointStartGate:
    is_open: bool

class EndpointPrepareContext:
    session_id: int
    endpoint_id: int
    connector_id: int | None
    route_id: int
    origin_kind: str
    source_id: int | None
    stream_id: int | None
    stem_id: int | None
    session_timeline_origin_ns: int
    configuration: dict[str, str]

class EndpointItem:
    kind: str
    audio: AudioFrame | None
    signal: _SignalEnvelope | None

class EndpointReceiver:
    def try_recv(self) -> EndpointItem | None: ...
    def is_abandoned(self) -> bool: ...
    def mark_discontinuity(self) -> None: ...
    def mark_worker_failure(self) -> None: ...

class EndpointPortInput:
    port_name: str
    signal: _SignalSpec
    media: _MediaCaps
    edge: _EdgeContract
    context: EndpointPrepareContext
    receiver: EndpointReceiver

class _RegisteredEndpoint:
    session_id: int
    operator_id: str
    node_type_id: str

class _OperatorPortContext:
    edge_id: int | None
    port_name: str
    direction: str
    capacity_signals: int
    signal: _SignalSpec
    media: _MediaCaps
    edge: _EdgeContract

class _OperatorPrepareContext:
    execution_partition: str
    inputs: list[_OperatorPortContext]
    outputs: list[_OperatorPortContext]

class Session:
    def __init__(
        self,
        *,
        recording_root: Path | None = None,
        trace_path: Path | None = None,
        trace_capacity_records: int = 256,
        sample_rate_hz: int = 48_000,
        channels: int = 1,
    ) -> None: ...
    @staticmethod
    def conformance(
        recording_root: Path,
        trace_path: Path | None = None,
        trace_capacity_records: int = 256,
    ) -> Session: ...
    id: int
    def capture(self, source: Source) -> Stem: ...
    def audio_input(
        self,
        sample_rate_hz: int,
        channels: int,
        capacity_frames: int = 8,
        frame_samples_per_channel: int = 480,
    ) -> _AudioInput: ...
    def pcm_source(
        self,
        sample_rate_hz: int,
        channels: int,
        capacity_frames: int = 8,
        frame_samples_per_channel: int = 480,
    ) -> _AudioInput: ...
    def source(
        self,
        source_type_id: str,
        configuration: dict[str, str],
    ) -> SourceInstance: ...
    def operator(
        self,
        operator_id: str,
        configuration: dict[str, str],
    ) -> OperatorInstance: ...
    def endpoint(self, descriptor: _EndpointDescriptor) -> Endpoint: ...
    def connector(
        self,
        operator_id: str,
        configuration: dict[str, str],
    ) -> Endpoint: ...
    def browser(self, receiver_uri: str) -> Endpoint: ...
    def polled_audio(self) -> Endpoint: ...
    def register_connector(
        self,
        manifest: _ConnectorManifest,
        factory: object,
    ) -> _RegisteredConnector: ...
    def register_connector_worker(
        self,
        manifest: _ConnectorManifest,
        factory: object,
        maximum_batch_items: int,
    ) -> _RegisteredConnector: ...
    def register_endpoint_provider(
        self,
        manifest: _EndpointManifest,
        factory: object,
    ) -> _RegisteredEndpoint: ...
    def register_source_provider(
        self,
        manifest: _SourceManifest,
        factory: object,
    ) -> _RegisteredSource: ...
    def register_operator_provider(
        self,
        manifest: _OperatorManifest,
        factory: object,
    ) -> None: ...
    def declare_connector(
        self,
        registered: _RegisteredConnector,
        configuration: _ConnectorConfiguration,
        edge: _EdgeContract,
    ) -> Endpoint: ...
    def declare_registered_endpoint(
        self,
        registered: _RegisteredEndpoint,
        configuration: dict[str, str],
        edge: _EdgeContract,
    ) -> Endpoint: ...
    def load_native_extension_library(
        self,
        path: Path,
    ) -> _NativeExtensionLibrary: ...
    def register_sidecar(self, spec: _SidecarProcessSpec) -> int: ...
    def relay(
        self,
        relay_url: str,
        relay_session_id: str,
        source_token: str,
    ) -> RelayPublisher: ...
    def subscribe_derived(
        self,
        stream: DerivedStream,
        signal: _SignalSpec,
        edge: _EdgeContract,
    ) -> BusSubscription: ...
    def subscribe_source_output(
        self,
        stream: SourceOutput,
        signal: _SignalSpec,
        edge: _EdgeContract,
    ) -> BusSubscription: ...
    def start(
        self,
        cancellation: _SessionStartCancellation | None = None,
    ) -> RunningSession: ...

class RunningSession:
    session_id: int
    lifecycle_state: str
    def poll_audio(self) -> AudioBatch | None: ...
    def wait_audio(self, timeout_ms: int = 100) -> AudioBatch | None: ...
    def poll_event(self) -> SessionEvent | None: ...
    def wait_event(self, timeout_ms: int = 100) -> SessionEvent | None: ...
    def poll_signal(self, subscription: BusSubscription) -> _SignalRead: ...
    def wait_signal(
        self,
        subscription: BusSubscription,
        timeout_ms: int = 100,
    ) -> _SignalRead: ...
    def close_signal(self, subscription: BusSubscription) -> None: ...
    def signal_metrics(
        self,
        subscription: BusSubscription,
    ) -> _SignalSubscriptionMetrics: ...
    def send_sidecar(self, sidecar_id: int, message: _SidecarMessage) -> None: ...
    def poll_sidecar(self, sidecar_id: int) -> _SidecarRead: ...
    def wait_sidecar(
        self,
        sidecar_id: int,
        timeout_ms: int = 100,
    ) -> _SidecarRead: ...
    def sidecar_snapshot(self, sidecar_id: int) -> _SidecarSnapshot: ...
    def metrics(self) -> SessionMetrics: ...
    def stop(self) -> StopResult: ...
    def cancel(self) -> StopResult: ...
