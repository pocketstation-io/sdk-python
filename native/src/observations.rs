use std::path::PathBuf;
use std::sync::mpsc::{sync_channel, SyncSender};
use std::thread;
use std::time::{Duration, Instant};

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use crate::errors::coded_reason;
use crate::relay::{OwnedRelayPublishOutcome, PythonRelayPublishOutcome};
use crate::session::SessionCommand;
use crate::sources::stable_source_parts;

#[pyclass(name = "RecordingDiscontinuity", frozen)]
pub(crate) struct PythonRecordingDiscontinuity {
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    label: String,
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    timestamp_start_ns: u64,
    #[pyo3(get)]
    timestamp_end_ns: u64,
    #[pyo3(get)]
    sequence_start: Option<u64>,
    #[pyo3(get)]
    sequence_end: Option<u64>,
}

#[pyclass(name = "RecordingStemOutcome", frozen)]
pub(crate) struct PythonRecordingStemOutcome {
    #[pyo3(get)]
    stem_name: String,
    #[pyo3(get)]
    frames_written_total: u64,
    #[pyo3(get)]
    stale_frames_total: u64,
    #[pyo3(get)]
    error: Option<String>,
    #[pyo3(get)]
    queue_capacity_frames: u64,
    #[pyo3(get)]
    queue_peak_frames: u64,
    #[pyo3(get)]
    frames_delivered_total: u64,
    #[pyo3(get)]
    frames_dropped_total: u64,
    #[pyo3(get)]
    queue_full_drops_total: u64,
    #[pyo3(get)]
    discontinuities_total: u64,
    discontinuities: Vec<Py<PythonRecordingDiscontinuity>>,
}

#[pymethods]
impl PythonRecordingStemOutcome {
    fn discontinuities(&self, py: Python<'_>) -> Vec<Py<PythonRecordingDiscontinuity>> {
        self.discontinuities
            .iter()
            .map(|value| value.clone_ref(py))
            .collect()
    }
}

#[pyclass(name = "RecordingOutcome", frozen)]
pub(crate) struct PythonRecordingOutcome {
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    group_id: String,
    #[pyo3(get)]
    complete: bool,
    #[pyo3(get)]
    state: String,
    #[pyo3(get)]
    completed_stems: usize,
    #[pyo3(get)]
    failed_stems: usize,
    #[pyo3(get)]
    session_directory: String,
    #[pyo3(get)]
    manifest_path: String,
    #[pyo3(get)]
    manifest_schema_version: u32,
    #[pyo3(get)]
    error_code: Option<String>,
    stems: Vec<Py<PythonRecordingStemOutcome>>,
}

#[pymethods]
impl PythonRecordingOutcome {
    fn stems(&self, py: Python<'_>) -> Vec<Py<PythonRecordingStemOutcome>> {
        self.stems.iter().map(|stem| stem.clone_ref(py)).collect()
    }
}

#[pyclass(name = "StopResult", frozen)]
pub(crate) struct PythonStopResult {
    #[pyo3(get)]
    pub(crate) success: bool,
    #[pyo3(get)]
    pub(crate) already_stopped: bool,
    #[pyo3(get)]
    pub(crate) disposition: String,
    #[pyo3(get)]
    pub(crate) runtime_worker_panicked: bool,
    #[pyo3(get)]
    pub(crate) capture_finalization_failures_total: u64,
    #[pyo3(get)]
    pub(crate) operator_finalization_failures_total: u64,
    #[pyo3(get)]
    pub(crate) endpoint_finalization_failures_total: u64,
    #[pyo3(get)]
    pub(crate) runtime_failures_total: u64,
    #[pyo3(get)]
    pub(crate) lineage_failures_total: u64,
    #[pyo3(get)]
    pub(crate) source_send_rejections_total: u64,
    #[pyo3(get)]
    pub(crate) runtime_events_total: u64,
    #[pyo3(get)]
    pub(crate) recording: Option<Py<PythonRecordingOutcome>>,
    #[pyo3(get)]
    pub(crate) trace: Option<Py<PythonSessionTraceRecorderOutcome>>,
    #[pyo3(get)]
    pub(crate) trace_error: Option<String>,
    #[pyo3(get)]
    pub(crate) terminal_event: Option<Py<PythonSessionEvent>>,
    pub(crate) relay: Vec<Py<PythonRelayPublishOutcome>>,
    pub(crate) sidecars: Vec<Py<crate::sidecar::PythonSidecarSnapshot>>,
}

#[pyclass(name = "_SessionFailure", frozen)]
pub(crate) struct PythonSessionFailure {
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    stage: Option<String>,
    #[pyo3(get)]
    operation: Option<String>,
    #[pyo3(get)]
    error_class: Option<String>,
    #[pyo3(get)]
    error_code: Option<String>,
    #[pyo3(get)]
    retryability: Option<String>,
    #[pyo3(get)]
    component: Option<String>,
    #[pyo3(get)]
    component_kind: Option<String>,
    #[pyo3(get)]
    message: Option<String>,
    #[pyo3(get)]
    stem_id: Option<u64>,
    #[pyo3(get)]
    route_id: Option<u64>,
    #[pyo3(get)]
    endpoint_id: Option<u64>,
    #[pyo3(get)]
    operator_instance_id: Option<u64>,
    #[pyo3(get)]
    sidecar_id: Option<u64>,
    #[pyo3(get)]
    source_event_kind: Option<String>,
    #[pyo3(get)]
    source_platform: Option<String>,
    #[pyo3(get)]
    source_kind: Option<String>,
    #[pyo3(get)]
    source_stable_key: Option<String>,
    #[pyo3(get)]
    source_source_id: Option<u64>,
    #[pyo3(get)]
    source_generation: Option<u32>,
    #[pyo3(get)]
    source_recovery_requirement: Option<String>,
    #[pyo3(get)]
    source_failure_operation: Option<String>,
    #[pyo3(get)]
    source_failure_class: Option<String>,
    #[pyo3(get)]
    source_platform_status_code: Option<i32>,
    #[pyo3(get)]
    source_backend_class: Option<String>,
}

#[pymethods]
impl PythonStopResult {
    fn relay_outcomes(&self, py: Python<'_>) -> Vec<Py<PythonRelayPublishOutcome>> {
        self.relay
            .iter()
            .map(|outcome| outcome.clone_ref(py))
            .collect()
    }

    fn sidecar_outcomes(&self, py: Python<'_>) -> Vec<Py<crate::sidecar::PythonSidecarSnapshot>> {
        self.sidecars
            .iter()
            .map(|outcome| outcome.clone_ref(py))
            .collect()
    }
}

#[pyclass(name = "SessionEvent", frozen)]
pub(crate) struct PythonSessionEvent {
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    lifecycle_state: Option<String>,
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    stem_id: Option<u64>,
    #[pyo3(get)]
    endpoint_id: Option<u64>,
    #[pyo3(get)]
    route_id: Option<u64>,
    #[pyo3(get)]
    failures_total: u64,
    #[pyo3(get)]
    terminal_state: Option<String>,
    #[pyo3(get)]
    source_event_kind: Option<String>,
    #[pyo3(get)]
    source_platform: Option<String>,
    #[pyo3(get)]
    source_kind: Option<String>,
    #[pyo3(get)]
    source_stable_key: Option<String>,
    #[pyo3(get)]
    source_source_id: Option<u64>,
    #[pyo3(get)]
    source_generation: Option<u32>,
    #[pyo3(get)]
    source_recovery_requirement: Option<String>,
    #[pyo3(get)]
    source_failure_operation: Option<String>,
    #[pyo3(get)]
    source_failure_class: Option<String>,
    #[pyo3(get)]
    source_platform_status_code: Option<i32>,
    #[pyo3(get)]
    source_backend_class: Option<String>,
    failures: Vec<Py<PythonSessionFailure>>,
}

#[pymethods]
impl PythonSessionEvent {
    fn failures(&self, py: Python<'_>) -> Vec<Py<PythonSessionFailure>> {
        self.failures
            .iter()
            .map(|failure| failure.clone_ref(py))
            .collect()
    }
}

#[pyclass(name = "_SessionSourceMetrics", frozen)]
pub(crate) struct PythonSessionSourceMetrics {
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    callback_buffers_total: u64,
    #[pyo3(get)]
    capture_frames_enqueued_total: u64,
    #[pyo3(get)]
    capture_pool_exhausted_total: u64,
    #[pyo3(get)]
    capture_dispatch_queue_full_total: u64,
    #[pyo3(get)]
    capture_invalid_buffer_total: u64,
    #[pyo3(get)]
    capture_oversized_buffer_total: u64,
    #[pyo3(get)]
    capture_stream_errors_total: u64,
    #[pyo3(get)]
    capture_timestamp_epoch_clamps_total: u64,
    #[pyo3(get)]
    frame_stream_delivered_frames_total: u64,
    #[pyo3(get)]
    frame_stream_dropped_newest_frames_total: u64,
    #[pyo3(get)]
    frames_discarded_before_start_total: u64,
    #[pyo3(get)]
    runtime_event_capacity_count: u64,
    #[pyo3(get)]
    runtime_event_maximum_event_owned_bytes: u64,
    #[pyo3(get)]
    runtime_event_maximum_buffered_owned_bytes: u64,
    #[pyo3(get)]
    runtime_event_depth_count: u64,
    #[pyo3(get)]
    runtime_event_depth_owned_bytes: u64,
    #[pyo3(get)]
    runtime_event_peak_depth_owned_bytes: u64,
    #[pyo3(get)]
    runtime_events_enqueued_total: u64,
    #[pyo3(get)]
    runtime_events_dropped_total: u64,
    #[pyo3(get)]
    runtime_events_dropped_oversized_total: u64,
    #[pyo3(get)]
    ingress_queue_capacity_frames: u64,
    #[pyo3(get)]
    ingress_queue_depth_frames: u64,
    #[pyo3(get)]
    ingress_queue_peak_frames: u64,
    #[pyo3(get)]
    ingress_frames_enqueued_total: u64,
    #[pyo3(get)]
    ingress_frames_delivered_total: u64,
    #[pyo3(get)]
    ingress_frames_rejected_full_total: u64,
    #[pyo3(get)]
    ingress_frames_rejected_cancelled_total: u64,
    #[pyo3(get)]
    ingress_frames_discarded_total: u64,
}

#[pyclass(name = "_ExternalSourceMetrics", frozen)]
pub(crate) struct PythonExternalSourceMetrics {
    #[pyo3(get)]
    source_instance_id: u64,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    emitted_total: u64,
    #[pyo3(get)]
    dropped_total: u64,
    #[pyo3(get)]
    failure_total: u64,
    #[pyo3(get)]
    cancellation_total: u64,
    #[pyo3(get)]
    discontinuity_total: u64,
    #[pyo3(get)]
    recovery_total: u64,
    #[pyo3(get)]
    policy_change_total: u64,
    #[pyo3(get)]
    ready: bool,
    #[pyo3(get)]
    joined: bool,
}

#[pyclass(name = "_OperatorInputMetrics", frozen)]
pub(crate) struct PythonOperatorInputMetrics {
    #[pyo3(get)]
    port_name: String,
    #[pyo3(get)]
    delivery: Py<PythonRouteDeliveryMetrics>,
}

#[pyclass(name = "_OperatorWorkerMetrics", frozen)]
pub(crate) struct PythonOperatorWorkerMetrics {
    #[pyo3(get)]
    input_attempted_total: u64,
    #[pyo3(get)]
    input_dropped_total: u64,
    #[pyo3(get)]
    processed_total: u64,
    #[pyo3(get)]
    output_emitted_total: u64,
    #[pyo3(get)]
    output_dropped_total: u64,
    #[pyo3(get)]
    output_nonterminal_total: u64,
    #[pyo3(get)]
    output_terminal_total: u64,
    #[pyo3(get)]
    process_failure_total: u64,
    #[pyo3(get)]
    timeout_total: u64,
    #[pyo3(get)]
    cancellation_total: u64,
    #[pyo3(get)]
    graceful_finish_total: u64,
    #[pyo3(get)]
    idle_poll_total: u64,
    #[pyo3(get)]
    ready: bool,
    #[pyo3(get)]
    joined: bool,
}

#[pyclass(name = "_OperatorMetrics", frozen)]
pub(crate) struct PythonOperatorMetrics {
    #[pyo3(get)]
    operator_instance_id: u64,
    #[pyo3(get)]
    input_delivery: Py<PythonRouteDeliveryMetrics>,
    #[pyo3(get)]
    worker: Py<PythonOperatorWorkerMetrics>,
    #[pyo3(get)]
    finalization_failures_total: u64,
    input_ports: Vec<Py<PythonOperatorInputMetrics>>,
}

#[pymethods]
impl PythonOperatorMetrics {
    fn input_ports(&self, py: Python<'_>) -> Vec<Py<PythonOperatorInputMetrics>> {
        self.input_ports
            .iter()
            .map(|input| input.clone_ref(py))
            .collect()
    }
}

#[pyclass(name = "_SignalQueueMetrics", frozen)]
pub(crate) struct PythonSignalQueueMetrics {
    #[pyo3(get)]
    capacity_signals: u64,
    #[pyo3(get)]
    max_payload_bytes: u64,
    #[pyo3(get)]
    maximum_buffered_payload_bytes: u64,
    #[pyo3(get)]
    depth_signals: u64,
    #[pyo3(get)]
    peak_depth_signals: u64,
    #[pyo3(get)]
    enqueued_total: u64,
    #[pyo3(get)]
    received_total: u64,
    #[pyo3(get)]
    dropped_total: u64,
}

#[pyclass(name = "_DerivedRouteMetrics", frozen)]
pub(crate) struct PythonDerivedRouteMetrics {
    #[pyo3(get)]
    route_id: u64,
    #[pyo3(get)]
    endpoint_id: u64,
    #[pyo3(get)]
    output: Py<PythonSignalQueueMetrics>,
    #[pyo3(get)]
    endpoint_observation_stage: String,
    #[pyo3(get)]
    endpoint_frames_received_total: u64,
    #[pyo3(get)]
    endpoint_frames_delivered_total: u64,
    #[pyo3(get)]
    endpoint_frames_dropped_total: u64,
    #[pyo3(get)]
    endpoint_discontinuities_total: u64,
    #[pyo3(get)]
    endpoint_failures_total: u64,
    #[pyo3(get)]
    endpoint_finalization_failures_total: u64,
}

#[pyclass(name = "_AudioReentryMetrics", frozen)]
pub(crate) struct PythonAudioReentryMetrics {
    #[pyo3(get)]
    operator_instance_id: u64,
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    queue_capacity_signals: u64,
    #[pyo3(get)]
    queue_depth_signals: u64,
    #[pyo3(get)]
    queue_peak_signals: u64,
    #[pyo3(get)]
    signals_enqueued_total: u64,
    #[pyo3(get)]
    signals_received_total: u64,
    #[pyo3(get)]
    signals_dropped_total: u64,
    #[pyo3(get)]
    pool_slots: u64,
    #[pyo3(get)]
    frame_capacity_samples: u64,
    #[pyo3(get)]
    maximum_buffered_audio_bytes: u64,
    #[pyo3(get)]
    normalized_total: u64,
    #[pyo3(get)]
    invalid_total: u64,
    #[pyo3(get)]
    shared_audio_rejected_total: u64,
    #[pyo3(get)]
    pool_exhausted_total: u64,
    #[pyo3(get)]
    ingress_rejected_total: u64,
    #[pyo3(get)]
    audio_frames_enqueued_total: u64,
    #[pyo3(get)]
    cancellation_total: u64,
    #[pyo3(get)]
    joined: bool,
}

#[pyclass(name = "_RouteDeliveryMetrics", frozen)]
pub(crate) struct PythonRouteDeliveryMetrics {
    #[pyo3(get)]
    queue_capacity_frames: u64,
    #[pyo3(get)]
    queue_depth_frames: u64,
    #[pyo3(get)]
    queue_peak_frames: u64,
    #[pyo3(get)]
    frames_enqueued_total: u64,
    #[pyo3(get)]
    frames_delivered_total: u64,
    #[pyo3(get)]
    frames_dropped_total: u64,
    #[pyo3(get)]
    overruns_total: u64,
    #[pyo3(get)]
    receiver_unavailable_drops_total: u64,
    #[pyo3(get)]
    queue_full_drops_total: u64,
    #[pyo3(get)]
    shared_reference_exhausted_drops_total: u64,
    #[pyo3(get)]
    branch_pool_exhausted_drops_total: u64,
    #[pyo3(get)]
    invalid_copy_policy_drops_total: u64,
    #[pyo3(get)]
    freeze_failed_drops_total: u64,
    #[pyo3(get)]
    discontinuities_total: u64,
    #[pyo3(get)]
    source_identity_discontinuities_total: u64,
    #[pyo3(get)]
    sequence_discontinuities_total: u64,
    #[pyo3(get)]
    timestamp_discontinuities_total: u64,
    #[pyo3(get)]
    lineage_epoch_discontinuities_total: u64,
    #[pyo3(get)]
    manually_reported_discontinuities_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_samples_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_invalid_order_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_p50_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_p95_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_p99_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_max_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_samples_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_missing_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_future_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p50_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p95_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p99_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_max_ns: u64,
    #[pyo3(get)]
    worker_failures_total: u64,
    #[pyo3(get)]
    shutdown_discarded_total: u64,
    #[pyo3(get)]
    discarded_output_frames_total: Option<u64>,
}

#[pyclass(name = "SessionMetrics", frozen)]
pub(crate) struct PythonSessionMetrics {
    #[pyo3(get)]
    event_capacity_count: u64,
    #[pyo3(get)]
    event_maximum_event_owned_bytes: u64,
    #[pyo3(get)]
    event_maximum_buffered_owned_bytes: u64,
    #[pyo3(get)]
    event_depth_count: u64,
    #[pyo3(get)]
    event_depth_owned_bytes: u64,
    #[pyo3(get)]
    event_peak_depth_count: u64,
    #[pyo3(get)]
    event_peak_depth_owned_bytes: u64,
    #[pyo3(get)]
    events_enqueued_total: u64,
    #[pyo3(get)]
    events_dropped_total: u64,
    #[pyo3(get)]
    events_dropped_oversized_total: u64,
    #[pyo3(get)]
    event_receiver_closed_total: u64,
    #[pyo3(get)]
    audio_registered_endpoints: u64,
    #[pyo3(get)]
    audio_queue_capacity_frames: u64,
    #[pyo3(get)]
    audio_queue_depth_frames: u64,
    #[pyo3(get)]
    audio_queue_peak_frames: u64,
    #[pyo3(get)]
    audio_queue_depth_invariant_failures_total: u64,
    #[pyo3(get)]
    audio_frames_received_total: u64,
    #[pyo3(get)]
    audio_frames_delivered_total: u64,
    #[pyo3(get)]
    audio_queue_full_drops_total: u64,
    #[pyo3(get)]
    audio_invalid_ownership_drops_total: u64,
    #[pyo3(get)]
    audio_discarded_output_frames_total: u64,
    #[pyo3(get)]
    audio_lease_capacity_count: u64,
    #[pyo3(get)]
    audio_outstanding_leases: u64,
    #[pyo3(get)]
    audio_lease_exhausted_total: u64,
    #[pyo3(get)]
    audio_batches_polled_total: u64,
    #[pyo3(get)]
    audio_frames_polled_total: u64,
    #[pyo3(get)]
    source_count: usize,
    #[pyo3(get)]
    external_source_count: usize,
    #[pyo3(get)]
    route_count: usize,
    #[pyo3(get)]
    operator_count: usize,
    #[pyo3(get)]
    derived_route_count: usize,
    #[pyo3(get)]
    audio_reentry_count: usize,
    #[pyo3(get)]
    routes: Vec<Py<PythonRouteMetrics>>,
    #[pyo3(get)]
    sources: Vec<Py<PythonSessionSourceMetrics>>,
    #[pyo3(get)]
    external_sources: Vec<Py<PythonExternalSourceMetrics>>,
    #[pyo3(get)]
    operators: Vec<Py<PythonOperatorMetrics>>,
    #[pyo3(get)]
    derived_routes: Vec<Py<PythonDerivedRouteMetrics>>,
    #[pyo3(get)]
    audio_reentries: Vec<Py<PythonAudioReentryMetrics>>,
}

#[pyclass(name = "RouteMetrics", frozen)]
pub(crate) struct PythonRouteMetrics {
    #[pyo3(get)]
    route_id: u64,
    #[pyo3(get)]
    endpoint_id: u64,
    #[pyo3(get)]
    endpoint_observation_stage: String,
    #[pyo3(get)]
    queue_capacity_frames: u64,
    #[pyo3(get)]
    queue_depth_frames: u64,
    #[pyo3(get)]
    queue_peak_frames: u64,
    #[pyo3(get)]
    frames_enqueued_total: u64,
    #[pyo3(get)]
    frames_attempted_total: u64,
    #[pyo3(get)]
    frames_delivered_total: u64,
    #[pyo3(get)]
    frames_dropped_total: u64,
    #[pyo3(get)]
    queue_full_drops_total: u64,
    #[pyo3(get)]
    overruns_total: u64,
    #[pyo3(get)]
    receiver_unavailable_drops_total: u64,
    #[pyo3(get)]
    shared_reference_exhausted_drops_total: u64,
    #[pyo3(get)]
    branch_pool_exhausted_drops_total: u64,
    #[pyo3(get)]
    invalid_copy_policy_drops_total: u64,
    #[pyo3(get)]
    freeze_failed_drops_total: u64,
    #[pyo3(get)]
    discontinuities_total: u64,
    #[pyo3(get)]
    source_identity_discontinuities_total: u64,
    #[pyo3(get)]
    sequence_discontinuities_total: u64,
    #[pyo3(get)]
    timestamp_discontinuities_total: u64,
    #[pyo3(get)]
    lineage_epoch_discontinuities_total: u64,
    #[pyo3(get)]
    manually_reported_discontinuities_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_samples_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_invalid_order_total: u64,
    #[pyo3(get)]
    enqueue_to_receive_p50_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_p95_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_p99_ns: u64,
    #[pyo3(get)]
    enqueue_to_receive_max_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_samples_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_missing_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_future_total: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p50_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p95_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_p99_ns: u64,
    #[pyo3(get)]
    source_timestamp_to_receive_max_ns: u64,
    #[pyo3(get)]
    worker_failures_total: u64,
    #[pyo3(get)]
    shutdown_discarded_total: u64,
    #[pyo3(get)]
    discarded_output_frames_total: u64,
    #[pyo3(get)]
    endpoint_frames_received_total: u64,
    #[pyo3(get)]
    endpoint_frames_delivered_total: u64,
    #[pyo3(get)]
    endpoint_frames_dropped_total: u64,
    #[pyo3(get)]
    endpoint_discontinuities_total: u64,
    #[pyo3(get)]
    endpoint_failures_total: u64,
    #[pyo3(get)]
    endpoint_finalization_failures_total: u64,
    #[pyo3(get)]
    drop_observation_interval: String,
    #[pyo3(get)]
    drop_rate_pct: f64,
    #[pyo3(get)]
    source_latency_measurement: String,
    #[pyo3(get)]
    source_latency_unit: String,
}

#[pyclass(name = "SessionTraceRecorderOutcome", frozen)]
pub(crate) struct PythonSessionTraceRecorderOutcome {
    #[pyo3(get)]
    path: String,
    #[pyo3(get)]
    records_attempted_total: u64,
    #[pyo3(get)]
    records_enqueued_total: u64,
    #[pyo3(get)]
    records_dropped_total: u64,
    #[pyo3(get)]
    records_written_total: u64,
    #[pyo3(get)]
    rolling_hash: u64,
    #[pyo3(get)]
    complete: bool,
}

#[pyclass(name = "_SessionTraceValidation", frozen)]
pub(crate) struct PythonSessionTraceValidation {
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    lifecycle: Vec<String>,
    #[pyo3(get)]
    terminal_state: String,
    #[pyo3(get)]
    source_failures_total: u64,
    #[pyo3(get)]
    endpoint_failures_total: u64,
    #[pyo3(get)]
    rollback_failures_total: u64,
    #[pyo3(get)]
    finalization_failures_total: u64,
    #[pyo3(get)]
    records_validated_total: u64,
}

#[pyclass(name = "SessionTraceRecord", frozen)]
pub(crate) struct PythonSessionTraceRecord {
    #[pyo3(get)]
    sequence_index: u64,
    #[pyo3(get)]
    observed_at_ns: u64,
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    lifecycle_state: Option<String>,
    #[pyo3(get)]
    terminal_state: Option<String>,
    #[pyo3(get)]
    stem_id: Option<u64>,
    #[pyo3(get)]
    route_id: Option<u64>,
    #[pyo3(get)]
    endpoint_id: Option<u64>,
    #[pyo3(get)]
    endpoint_stage: Option<String>,
    #[pyo3(get)]
    rollback_stage: Option<String>,
    #[pyo3(get)]
    finalization_stage: Option<String>,
    #[pyo3(get)]
    source_failures_total: Option<u64>,
    #[pyo3(get)]
    endpoint_failures_total: Option<u64>,
    #[pyo3(get)]
    rollback_failures_total: Option<u64>,
    #[pyo3(get)]
    finalization_failures_total: Option<u64>,
}

#[pyclass(name = "SessionTrace", frozen)]
pub(crate) struct PythonSessionTrace {
    trace: pocketstation::SessionTrace,
}

#[pymethods]
impl PythonSessionTrace {
    #[staticmethod]
    fn read(path: PathBuf) -> PyResult<Self> {
        pocketstation::SessionTrace::read(path)
            .map(|trace| Self { trace })
            .map_err(session_trace_validation_error)
    }

    #[getter]
    fn session_id(&self) -> u64 {
        self.trace.session_id().get()
    }

    #[getter]
    fn outcome(&self) -> PythonSessionTraceRecorderOutcome {
        PythonSessionTraceRecorderOutcome::from(self.trace.outcome().clone())
    }

    #[getter]
    fn records_total(&self) -> usize {
        self.trace.records().len()
    }

    fn records(&self) -> Vec<PythonSessionTraceRecord> {
        self.trace
            .records()
            .iter()
            .copied()
            .map(PythonSessionTraceRecord::from)
            .collect()
    }

    fn validate(&self) -> PyResult<PythonSessionTraceValidation> {
        self.trace
            .validate()
            .map(PythonSessionTraceValidation::from)
            .map_err(session_trace_validation_error)
    }
}

pub(crate) struct OwnedRecordingStemOutcome {
    stem_name: String,
    frames_written_total: u64,
    stale_frames_total: u64,
    error: Option<String>,
    queue_capacity_frames: u64,
    queue_peak_frames: u64,
    frames_delivered_total: u64,
    frames_dropped_total: u64,
    queue_full_drops_total: u64,
    discontinuities_total: u64,
    discontinuities: Vec<OwnedRecordingDiscontinuity>,
}

struct OwnedRecordingDiscontinuity {
    stem_id: u64,
    label: String,
    kind: String,
    timestamp_start_ns: u64,
    timestamp_end_ns: u64,
    sequence_start: Option<u64>,
    sequence_end: Option<u64>,
}

pub(crate) struct OwnedRecordingOutcome {
    session_id: u64,
    group_id: String,
    pub(crate) complete: bool,
    state: String,
    completed_stems: usize,
    failed_stems: usize,
    session_directory: String,
    manifest_path: String,
    manifest_schema_version: u32,
    error_code: Option<String>,
    pub(crate) stems: Vec<OwnedRecordingStemOutcome>,
}

pub(crate) struct OwnedStopResult {
    pub(crate) lifecycle_state: &'static str,
    pub(crate) success: bool,
    pub(crate) already_stopped: bool,
    pub(crate) disposition: String,
    pub(crate) runtime_worker_panicked: bool,
    pub(crate) capture_finalization_failures_total: u64,
    pub(crate) operator_finalization_failures_total: u64,
    pub(crate) endpoint_finalization_failures_total: u64,
    pub(crate) runtime_failures_total: u64,
    pub(crate) lineage_failures_total: u64,
    pub(crate) source_send_rejections_total: u64,
    pub(crate) runtime_events_total: u64,
    pub(crate) recording: Option<OwnedRecordingOutcome>,
    pub(crate) trace: Option<pocketstation::SessionTraceRecorderOutcome>,
    pub(crate) trace_error: Option<String>,
    pub(crate) terminal_event: Option<OwnedSessionEvent>,
    pub(crate) relay: Vec<OwnedRelayPublishOutcome>,
    pub(crate) sidecars: Vec<pocketstation::SessionSidecarMetrics>,
}

pub(crate) struct OwnedSessionEvent {
    pub(crate) kind: String,
    lifecycle_state: Option<String>,
    session_id: u64,
    stem_id: Option<u64>,
    endpoint_id: Option<u64>,
    route_id: Option<u64>,
    failures_total: u64,
    terminal_state: Option<String>,
    source_event_kind: Option<String>,
    source_platform: Option<String>,
    source_kind: Option<String>,
    source_stable_key: Option<String>,
    source_source_id: Option<u64>,
    source_generation: Option<u32>,
    source_recovery_requirement: Option<String>,
    source_failure_operation: Option<String>,
    source_failure_class: Option<String>,
    source_platform_status_code: Option<i32>,
    source_backend_class: Option<String>,
    failures: Vec<OwnedSessionFailure>,
}

#[derive(Default)]
struct OwnedSessionFailure {
    kind: String,
    stage: Option<String>,
    operation: Option<String>,
    error_class: Option<String>,
    error_code: Option<String>,
    retryability: Option<String>,
    component: Option<String>,
    component_kind: Option<String>,
    message: Option<String>,
    stem_id: Option<u64>,
    route_id: Option<u64>,
    endpoint_id: Option<u64>,
    operator_instance_id: Option<u64>,
    sidecar_id: Option<u64>,
    source_event_kind: Option<String>,
    source_platform: Option<String>,
    source_kind: Option<String>,
    source_stable_key: Option<String>,
    source_source_id: Option<u64>,
    source_generation: Option<u32>,
    source_recovery_requirement: Option<String>,
    source_failure_operation: Option<String>,
    source_failure_class: Option<String>,
    source_platform_status_code: Option<i32>,
    source_backend_class: Option<String>,
}

pub(crate) struct OwnedSessionMetrics {
    event_capacity_count: u64,
    event_maximum_event_owned_bytes: u64,
    event_maximum_buffered_owned_bytes: u64,
    event_depth_count: u64,
    event_depth_owned_bytes: u64,
    event_peak_depth_count: u64,
    event_peak_depth_owned_bytes: u64,
    events_enqueued_total: u64,
    events_dropped_total: u64,
    events_dropped_oversized_total: u64,
    event_receiver_closed_total: u64,
    audio_registered_endpoints: u64,
    audio_queue_capacity_frames: u64,
    audio_queue_depth_frames: u64,
    audio_queue_peak_frames: u64,
    audio_queue_depth_invariant_failures_total: u64,
    audio_frames_received_total: u64,
    audio_frames_delivered_total: u64,
    audio_queue_full_drops_total: u64,
    audio_invalid_ownership_drops_total: u64,
    audio_discarded_output_frames_total: u64,
    audio_lease_capacity_count: u64,
    audio_outstanding_leases: u64,
    audio_lease_exhausted_total: u64,
    audio_batches_polled_total: u64,
    audio_frames_polled_total: u64,
    pub(crate) source_count: usize,
    external_source_count: usize,
    pub(crate) route_count: usize,
    operator_count: usize,
    derived_route_count: usize,
    audio_reentry_count: usize,
    pub(crate) routes: Vec<OwnedRouteMetrics>,
    sources: Vec<pocketstation::SessionSourceMetrics>,
    external_sources: Vec<pocketstation::SessionExternalSourceMetrics>,
    operators: Vec<pocketstation::SessionOperatorMetrics>,
    derived_routes: Vec<pocketstation::SessionDerivedRouteMetrics>,
    audio_reentries: Vec<pocketstation::SessionAudioReentryMetrics>,
}

pub(crate) struct OwnedRouteMetrics {
    pub(crate) route_id: u64,
    endpoint_id: u64,
    endpoint_observation_stage: String,
    queue_capacity_frames: u64,
    queue_depth_frames: u64,
    queue_peak_frames: u64,
    frames_enqueued_total: u64,
    frames_attempted_total: u64,
    pub(crate) frames_delivered_total: u64,
    frames_dropped_total: u64,
    queue_full_drops_total: u64,
    overruns_total: u64,
    receiver_unavailable_drops_total: u64,
    shared_reference_exhausted_drops_total: u64,
    branch_pool_exhausted_drops_total: u64,
    invalid_copy_policy_drops_total: u64,
    freeze_failed_drops_total: u64,
    discontinuities_total: u64,
    source_identity_discontinuities_total: u64,
    sequence_discontinuities_total: u64,
    timestamp_discontinuities_total: u64,
    lineage_epoch_discontinuities_total: u64,
    manually_reported_discontinuities_total: u64,
    enqueue_to_receive_samples_total: u64,
    enqueue_to_receive_invalid_order_total: u64,
    enqueue_to_receive_p50_ns: u64,
    enqueue_to_receive_p95_ns: u64,
    enqueue_to_receive_p99_ns: u64,
    enqueue_to_receive_max_ns: u64,
    source_timestamp_to_receive_samples_total: u64,
    source_timestamp_to_receive_missing_total: u64,
    source_timestamp_to_receive_future_total: u64,
    source_timestamp_to_receive_p50_ns: u64,
    source_timestamp_to_receive_p95_ns: u64,
    source_timestamp_to_receive_p99_ns: u64,
    source_timestamp_to_receive_max_ns: u64,
    worker_failures_total: u64,
    shutdown_discarded_total: u64,
    discarded_output_frames_total: u64,
    pub(crate) endpoint_frames_received_total: u64,
    endpoint_frames_delivered_total: u64,
    endpoint_frames_dropped_total: u64,
    endpoint_discontinuities_total: u64,
    endpoint_failures_total: u64,
    endpoint_finalization_failures_total: u64,
    drop_rate_pct: f64,
}

pub(crate) fn request_event(
    commands: &SyncSender<SessionCommand>,
) -> PyResult<Option<OwnedSessionEvent>> {
    let (response, receiver) = sync_channel(1);
    commands
        .send(SessionCommand::PollEvent { response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not return an event"))?
        .map_err(PyRuntimeError::new_err)
}

pub(crate) fn request_event_wait(
    commands: &SyncSender<SessionCommand>,
    timeout: Duration,
) -> PyResult<Option<OwnedSessionEvent>> {
    let (response, receiver) = sync_channel(1);
    commands
        .send(SessionCommand::WaitEvent { timeout, response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not return an event"))?
        .map_err(PyRuntimeError::new_err)
}

pub(crate) fn request_metrics(
    commands: &SyncSender<SessionCommand>,
) -> PyResult<OwnedSessionMetrics> {
    let (response, receiver) = sync_channel(1);
    commands
        .send(SessionCommand::Metrics { response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not return metrics"))?
        .map_err(PyRuntimeError::new_err)
}

pub(crate) fn drain_terminal_event(
    running: &pocketstation::RunningSession,
) -> Option<OwnedSessionEvent> {
    let mut terminal = None;
    while let pocketstation::SessionEventReceive::Event(event) = running.try_recv_event() {
        let projected = owned_session_event(&event);
        if projected.kind == "terminal" {
            terminal = Some(projected);
        }
    }
    terminal
}

pub(crate) fn copy_event(
    running: &pocketstation::RunningSession,
) -> Result<Option<OwnedSessionEvent>, String> {
    match running.try_recv_event() {
        pocketstation::SessionEventReceive::Event(event) => Ok(Some(owned_session_event(&event))),
        pocketstation::SessionEventReceive::Empty => Ok(None),
        pocketstation::SessionEventReceive::Closed => {
            Err("native Session event queue is closed".to_owned())
        }
    }
}

pub(crate) fn copy_event_until(
    running: &pocketstation::RunningSession,
    timeout: Duration,
) -> Result<Option<OwnedSessionEvent>, String> {
    let deadline = Instant::now() + timeout;
    loop {
        match copy_event(running)? {
            Some(event) => return Ok(Some(event)),
            None if Instant::now() < deadline => thread::sleep(Duration::from_millis(1)),
            None => return Ok(None),
        }
    }
}

pub(crate) fn copy_metrics(
    running: &pocketstation::RunningSession,
) -> Result<OwnedSessionMetrics, String> {
    let snapshot = running
        .metrics_snapshot()
        .map_err(|error| error.to_string())?;
    let events = snapshot.event_queue();
    let audio = snapshot.polled_audio();
    let routes = (0..snapshot.route_count())
        .filter_map(|index| snapshot.route(index))
        .map(|route| {
            let endpoint = route.endpoint.unwrap_or_default();
            OwnedRouteMetrics {
                route_id: route.route_id.get(),
                endpoint_id: route.endpoint_id.get(),
                endpoint_observation_stage: endpoint_observation_stage_name(
                    route.endpoint_observation_stage,
                ),
                queue_capacity_frames: route.edge.queue_capacity_frames,
                queue_depth_frames: route.edge.queue_depth_frames,
                queue_peak_frames: route.edge.queue_peak_frames,
                frames_enqueued_total: route.edge.frames_enqueued_total,
                frames_attempted_total: route.edge.frames_attempted_total(),
                frames_delivered_total: route.edge.frames_delivered_total,
                frames_dropped_total: route.edge.frames_dropped_total,
                queue_full_drops_total: route.edge.queue_full_drops_total,
                overruns_total: route.edge.overruns_total,
                receiver_unavailable_drops_total: route.edge.receiver_unavailable_drops_total,
                shared_reference_exhausted_drops_total: route
                    .edge
                    .shared_reference_exhausted_drops_total,
                branch_pool_exhausted_drops_total: route.edge.branch_pool_exhausted_drops_total,
                invalid_copy_policy_drops_total: route.edge.invalid_copy_policy_drops_total,
                freeze_failed_drops_total: route.edge.freeze_failed_drops_total,
                discontinuities_total: route.edge.discontinuities_total,
                source_identity_discontinuities_total: route
                    .edge
                    .source_identity_discontinuities_total,
                sequence_discontinuities_total: route.edge.sequence_discontinuities_total,
                timestamp_discontinuities_total: route.edge.timestamp_discontinuities_total,
                lineage_epoch_discontinuities_total: route.edge.lineage_epoch_discontinuities_total,
                manually_reported_discontinuities_total: route
                    .edge
                    .manually_reported_discontinuities_total,
                enqueue_to_receive_samples_total: route.edge.enqueue_to_receive_samples_total,
                enqueue_to_receive_invalid_order_total: route
                    .edge
                    .enqueue_to_receive_invalid_order_total,
                enqueue_to_receive_p50_ns: route.edge.enqueue_to_receive_p50_ns,
                enqueue_to_receive_p95_ns: route.edge.enqueue_to_receive_p95_ns,
                enqueue_to_receive_p99_ns: route.edge.enqueue_to_receive_p99_ns,
                enqueue_to_receive_max_ns: route.edge.enqueue_to_receive_max_ns,
                source_timestamp_to_receive_samples_total: route
                    .edge
                    .source_timestamp_to_receive_samples_total,
                source_timestamp_to_receive_missing_total: route
                    .edge
                    .source_timestamp_to_receive_missing_total,
                source_timestamp_to_receive_future_total: route
                    .edge
                    .source_timestamp_to_receive_future_total,
                source_timestamp_to_receive_p50_ns: route.edge.source_timestamp_to_receive_p50_ns,
                source_timestamp_to_receive_p95_ns: route.edge.source_timestamp_to_receive_p95_ns,
                source_timestamp_to_receive_p99_ns: route.edge.source_timestamp_to_receive_p99_ns,
                source_timestamp_to_receive_max_ns: route.edge.source_timestamp_to_receive_max_ns,
                worker_failures_total: route.edge.worker_failures_total,
                shutdown_discarded_total: route.edge.shutdown_discarded_total,
                discarded_output_frames_total: running
                    .route_discarded_output_frames_total(route.route_id)
                    .unwrap_or(0),
                endpoint_frames_received_total: endpoint.frames_received_total,
                endpoint_frames_delivered_total: endpoint.frames_delivered_total,
                endpoint_frames_dropped_total: endpoint.frames_dropped_total,
                endpoint_discontinuities_total: endpoint.discontinuities_total,
                endpoint_failures_total: endpoint.failures_total,
                endpoint_finalization_failures_total: route.endpoint_finalization_failures_total,
                drop_rate_pct: route.drop_observations().drop_rate_pct(),
            }
        })
        .collect();
    let sources = (0..snapshot.source_count())
        .filter_map(|index| snapshot.source(index).copied())
        .collect();
    let external_sources = running.external_source_metrics().into_vec();
    let operators = running.operator_metrics().into_vec();
    let derived_routes = running.derived_route_metrics().into_vec();
    let audio_reentries = running.audio_reentry_metrics().into_vec();
    Ok(OwnedSessionMetrics {
        event_capacity_count: events.capacity_event_count,
        event_maximum_event_owned_bytes: events.maximum_event_owned_bytes,
        event_maximum_buffered_owned_bytes: events.maximum_buffered_owned_bytes,
        event_depth_count: events.depth_events,
        event_depth_owned_bytes: events.depth_owned_bytes,
        event_peak_depth_count: events.peak_depth_event_count,
        event_peak_depth_owned_bytes: events.peak_depth_owned_bytes,
        events_enqueued_total: events.events_enqueued_total,
        events_dropped_total: events.events_dropped_total,
        events_dropped_oversized_total: events.events_dropped_oversized_total,
        event_receiver_closed_total: events.receiver_closed_total,
        audio_registered_endpoints: audio.registered_endpoints,
        audio_queue_capacity_frames: audio.queue_capacity_frames,
        audio_queue_depth_frames: audio.queue_depth_frames,
        audio_queue_peak_frames: audio.queue_peak_frames,
        audio_queue_depth_invariant_failures_total: audio.queue_depth_invariant_failures_total,
        audio_frames_received_total: audio.frames_received_total,
        audio_frames_delivered_total: audio.frames_delivered_total,
        audio_queue_full_drops_total: audio.queue_full_drops_total,
        audio_invalid_ownership_drops_total: audio.invalid_ownership_drops_total,
        audio_discarded_output_frames_total: running.audio_discarded_output_frames_total(),
        audio_lease_capacity_count: audio.lease_capacity_count,
        audio_outstanding_leases: audio.outstanding_leases,
        audio_lease_exhausted_total: audio.lease_exhausted_total,
        audio_batches_polled_total: audio.batches_polled_total,
        audio_frames_polled_total: audio.frames_polled_total,
        source_count: snapshot.source_count(),
        external_source_count: external_sources.len(),
        route_count: snapshot.route_count(),
        operator_count: operators.len(),
        derived_route_count: derived_routes.len(),
        audio_reentry_count: audio_reentries.len(),
        routes,
        sources,
        external_sources,
        operators,
        derived_routes,
        audio_reentries,
    })
}

const fn lifecycle_state_name(state: pocketstation::SessionLifecycleState) -> &'static str {
    match state {
        pocketstation::SessionLifecycleState::Starting => "starting",
        pocketstation::SessionLifecycleState::Running => "running",
        pocketstation::SessionLifecycleState::Stopping => "stopping",
        pocketstation::SessionLifecycleState::Stopped => "stopped",
        pocketstation::SessionLifecycleState::Failed => "failed",
    }
}

const fn terminal_state_name(state: pocketstation::SessionTerminalState) -> &'static str {
    match state {
        pocketstation::SessionTerminalState::Stopped => "stopped",
        pocketstation::SessionTerminalState::Failed => "failed",
    }
}

const fn endpoint_failure_stage_name(stage: pocketstation::EndpointFailureStage) -> &'static str {
    match stage {
        pocketstation::EndpointFailureStage::Prepare => "prepare",
        pocketstation::EndpointFailureStage::CancelPreparation => "cancel-preparation",
        pocketstation::EndpointFailureStage::Start => "start",
        pocketstation::EndpointFailureStage::RequestStop => "request-stop",
        pocketstation::EndpointFailureStage::JoinFinalize => "join-finalize",
    }
}

fn rollback_stage_name(stage: impl std::fmt::Debug) -> String {
    match format!("{stage:?}").as_str() {
        "CancelOperator" => "cancel-operator",
        "CancelEndpointPreparation" => "cancel-endpoint-preparation",
        "FinalizeStartedEndpoint" => "finalize-started-endpoint",
        "StopOpenedCapture" => "stop-opened-capture",
        "DiscardRuntimeQueues" => "discard-runtime-queues",
        _ => "unrecognized-rollback-stage",
    }
    .to_owned()
}

fn finalization_stage_name(stage: impl std::fmt::Debug) -> String {
    match format!("{stage:?}").as_str() {
        "StopCapture" => "stop-capture",
        "DrainRuntime" => "drain-runtime",
        "DrainOperator" => "drain-operator",
        "RequestEndpointStop" => "request-endpoint-stop",
        "JoinEndpoint" => "join-endpoint",
        "FinalizeEndpoint" => "finalize-endpoint",
        "DrainSidecar" => "drain-sidecar",
        _ => "unrecognized-finalization-stage",
    }
    .to_owned()
}

fn endpoint_observation_stage_name(stage: impl std::fmt::Debug) -> String {
    match format!("{stage:?}").as_str() {
        "Unavailable" => "unavailable",
        "Live" => "live",
        "Finalized" => "finalized",
        _ => "unrecognized-endpoint-observation-stage",
    }
    .to_owned()
}

fn owned_session_event(event: &pocketstation::SessionEvent) -> OwnedSessionEvent {
    let mut output = empty_owned_session_event(event.session_id().get());
    match event.kind() {
        pocketstation::SessionEventKind::Lifecycle(state) => {
            output.lifecycle_state = Some(lifecycle_state_name(*state).to_owned());
        }
        pocketstation::SessionEventKind::Source(failure) => {
            "source_failure".clone_into(&mut output.kind);
            output.stem_id = Some(failure.stem_id().get());
            output.failures_total = 1;
            populate_source_runtime_event(&mut output, failure.event());
            output.failures.push(owned_source_failure(
                failure.stem_id().get(),
                failure.event(),
            ));
        }
        pocketstation::SessionEventKind::Endpoint(failure) => {
            "endpoint_failure".clone_into(&mut output.kind);
            output.endpoint_id = Some(failure.endpoint_id().get());
            output.route_id = Some(failure.route_id().get());
            output.failures_total = 1;
            output.failures.push(owned_endpoint_failure(
                failure.route_id().get(),
                failure.endpoint_id().get(),
                endpoint_failure_stage_name(failure.stage()).to_owned(),
                failure.failure(),
            ));
        }
        pocketstation::SessionEventKind::Rollback(failure) => {
            "rollback_failure".clone_into(&mut output.kind);
            output.failures_total = 1;
            output.failures.push(owned_control_failure(
                "rollback",
                Some(rollback_stage_name(failure.stage())),
                failure.failure(),
            ));
        }
        pocketstation::SessionEventKind::Finalization(failure) => {
            "finalization_failure".clone_into(&mut output.kind);
            output.failures_total = 1;
            output.failures.push(owned_control_failure(
                "finalization",
                Some(finalization_stage_name(failure.stage())),
                failure.failure(),
            ));
        }
        pocketstation::SessionEventKind::Terminal(outcome) => {
            "terminal".clone_into(&mut output.kind);
            let terminal_state = terminal_state_name(outcome.state()).to_owned();
            output.lifecycle_state = Some(terminal_state.clone());
            output.terminal_state = Some(terminal_state);
            output.failures_total = (outcome.source_failures().len()
                + outcome.endpoint_failures().len()
                + outcome.rollback_failures().len()
                + outcome.finalization_failures().len()) as u64;
            output.failures.extend(
                outcome
                    .source_failures()
                    .iter()
                    .map(|failure| owned_source_failure(failure.stem_id().get(), failure.event())),
            );
            output
                .failures
                .extend(outcome.endpoint_failures().iter().map(|failure| {
                    owned_endpoint_failure(
                        failure.route_id().get(),
                        failure.endpoint_id().get(),
                        endpoint_failure_stage_name(failure.stage()).to_owned(),
                        failure.failure(),
                    )
                }));
            output
                .failures
                .extend(outcome.rollback_failures().iter().map(|failure| {
                    owned_control_failure(
                        "rollback",
                        Some(rollback_stage_name(failure.stage())),
                        failure.failure(),
                    )
                }));
            output
                .failures
                .extend(outcome.finalization_failures().iter().map(|failure| {
                    owned_control_failure(
                        "finalization",
                        Some(finalization_stage_name(failure.stage())),
                        failure.failure(),
                    )
                }));
        }
    }
    output
}

fn empty_owned_session_event(session_id: u64) -> OwnedSessionEvent {
    OwnedSessionEvent {
        kind: "lifecycle".to_owned(),
        lifecycle_state: None,
        session_id,
        stem_id: None,
        endpoint_id: None,
        route_id: None,
        failures_total: 0,
        terminal_state: None,
        source_event_kind: None,
        source_platform: None,
        source_kind: None,
        source_stable_key: None,
        source_source_id: None,
        source_generation: None,
        source_recovery_requirement: None,
        source_failure_operation: None,
        source_failure_class: None,
        source_platform_status_code: None,
        source_backend_class: None,
        failures: Vec::new(),
    }
}

fn owned_source_failure(
    stem_id: u64,
    event: &pocketstation::SourceRuntimeEvent,
) -> OwnedSessionFailure {
    let mut projected = empty_owned_session_event(0);
    populate_source_runtime_event(&mut projected, event);
    OwnedSessionFailure {
        kind: "source".to_owned(),
        stem_id: Some(stem_id),
        source_event_kind: projected.source_event_kind,
        source_platform: projected.source_platform,
        source_kind: projected.source_kind,
        source_stable_key: projected.source_stable_key,
        source_source_id: projected.source_source_id,
        source_generation: projected.source_generation,
        source_recovery_requirement: projected.source_recovery_requirement,
        source_failure_operation: projected.source_failure_operation,
        source_failure_class: projected.source_failure_class,
        source_platform_status_code: projected.source_platform_status_code,
        source_backend_class: projected.source_backend_class,
        ..OwnedSessionFailure::default()
    }
}

fn owned_endpoint_failure(
    route_id: u64,
    endpoint_id: u64,
    stage: String,
    failure: &pocketstation::EndpointFailure,
) -> OwnedSessionFailure {
    let retryability = failure.retryability().map(|value| {
        match value {
            pocketstation::EndpointFailureRetryability::Never => "never",
            pocketstation::EndpointFailureRetryability::Retryable => "retryable",
            pocketstation::EndpointFailureRetryability::ReconfigurationRequired => {
                "retry-after-reconfiguration"
            }
        }
        .to_owned()
    });
    OwnedSessionFailure {
        kind: "endpoint".to_owned(),
        stage: Some(stage),
        error_class: Some("endpoint-failure".to_owned()),
        error_code: failure.code().map(str::to_owned),
        retryability,
        message: Some(failure.message().to_owned()),
        route_id: Some(route_id),
        endpoint_id: Some(endpoint_id),
        ..OwnedSessionFailure::default()
    }
}

fn owned_control_failure(
    kind: &str,
    stage: Option<String>,
    failure: &pocketstation::SessionControlFailure,
) -> OwnedSessionFailure {
    let mut owned = OwnedSessionFailure {
        kind: kind.to_owned(),
        stage,
        operation: Some(failure.operation().to_owned()),
        error_class: Some(failure.error_class().to_owned()),
        component: Some(format!("{:?}", failure.component())),
        ..OwnedSessionFailure::default()
    };
    match failure.component() {
        pocketstation::SessionComponentId::Source { stem_id } => {
            owned.component_kind = Some("source".to_owned());
            owned.stem_id = Some(stem_id.get());
        }
        pocketstation::SessionComponentId::Endpoint {
            route_id,
            endpoint_id,
        } => {
            owned.component_kind = Some("endpoint".to_owned());
            owned.route_id = Some(route_id.get());
            owned.endpoint_id = Some(endpoint_id.get());
        }
        pocketstation::SessionComponentId::Operator {
            operator_instance_id,
        } => {
            owned.component_kind = Some("operator".to_owned());
            owned.operator_instance_id = Some(operator_instance_id.value());
        }
        pocketstation::SessionComponentId::Sidecar { sidecar_id } => {
            owned.component_kind = Some("sidecar".to_owned());
            owned.sidecar_id = Some(sidecar_id);
        }
        pocketstation::SessionComponentId::Runtime => {
            owned.component_kind = Some("runtime".to_owned());
        }
    }
    owned
}

fn populate_source_runtime_event(
    output: &mut OwnedSessionEvent,
    event: &pocketstation::SourceRuntimeEvent,
) {
    let (event_kind, stable_id, generation, recovery_requirement, failure) = match event {
        pocketstation::SourceRuntimeEvent::SourceUnavailable {
            stable_id,
            generation,
            recovery_requirement,
            failure,
        } => (
            "source-unavailable",
            stable_id,
            generation,
            Some(match recovery_requirement {
                pocketstation::SourceRecoveryRequirement::ExplicitRediscoveryAndNewSession => {
                    "explicit-rediscovery-and-new-session"
                }
            }),
            failure,
        ),
        pocketstation::SourceRuntimeEvent::BackendFailure {
            stable_id,
            generation,
            failure,
        } => ("backend-failure", stable_id, generation, None, failure),
    };
    let (platform, kind, stable_key) = stable_source_parts(stable_id);
    output.source_event_kind = Some(event_kind.to_owned());
    output.source_platform = Some(platform.to_owned());
    output.source_kind = Some(kind.to_owned());
    output.source_stable_key = Some(stable_key.to_owned());
    output.source_source_id = Some(stable_id.source_id().get());
    output.source_generation = Some(generation.0);
    output.source_recovery_requirement = recovery_requirement.map(str::to_owned);
    output.source_failure_operation = Some(failure.operation.to_owned());
    match &failure.error_class {
        pocketstation::CaptureRuntimeFailureClass::SourceInstanceExited => {
            output.source_failure_class = Some("source-instance-exited".to_owned());
        }
        pocketstation::CaptureRuntimeFailureClass::PlatformStatus { status_code } => {
            output.source_failure_class = Some("platform-status".to_owned());
            output.source_platform_status_code = Some(*status_code);
        }
        pocketstation::CaptureRuntimeFailureClass::BackendClass { class } => {
            output.source_failure_class = Some("backend-class".to_owned());
            output.source_backend_class = Some(class.clone());
        }
    }
}

pub(crate) fn python_session_event(
    py: Python<'_>,
    event: OwnedSessionEvent,
) -> PyResult<PythonSessionEvent> {
    let failures = event
        .failures
        .into_iter()
        .map(|failure| {
            Py::new(
                py,
                PythonSessionFailure {
                    kind: failure.kind,
                    stage: failure.stage,
                    operation: failure.operation,
                    error_class: failure.error_class,
                    error_code: failure.error_code,
                    retryability: failure.retryability,
                    component: failure.component,
                    component_kind: failure.component_kind,
                    message: failure.message,
                    stem_id: failure.stem_id,
                    route_id: failure.route_id,
                    endpoint_id: failure.endpoint_id,
                    operator_instance_id: failure.operator_instance_id,
                    sidecar_id: failure.sidecar_id,
                    source_event_kind: failure.source_event_kind,
                    source_platform: failure.source_platform,
                    source_kind: failure.source_kind,
                    source_stable_key: failure.source_stable_key,
                    source_source_id: failure.source_source_id,
                    source_generation: failure.source_generation,
                    source_recovery_requirement: failure.source_recovery_requirement,
                    source_failure_operation: failure.source_failure_operation,
                    source_failure_class: failure.source_failure_class,
                    source_platform_status_code: failure.source_platform_status_code,
                    source_backend_class: failure.source_backend_class,
                },
            )
        })
        .collect::<PyResult<Vec<_>>>()?;
    Ok(PythonSessionEvent {
        kind: event.kind,
        lifecycle_state: event.lifecycle_state,
        session_id: event.session_id,
        stem_id: event.stem_id,
        endpoint_id: event.endpoint_id,
        route_id: event.route_id,
        failures_total: event.failures_total,
        terminal_state: event.terminal_state,
        source_event_kind: event.source_event_kind,
        source_platform: event.source_platform,
        source_kind: event.source_kind,
        source_stable_key: event.source_stable_key,
        source_source_id: event.source_source_id,
        source_generation: event.source_generation,
        source_recovery_requirement: event.source_recovery_requirement,
        source_failure_operation: event.source_failure_operation,
        source_failure_class: event.source_failure_class,
        source_platform_status_code: event.source_platform_status_code,
        source_backend_class: event.source_backend_class,
        failures,
    })
}

impl From<pocketstation::EdgeObservations> for PythonRouteDeliveryMetrics {
    fn from(edge: pocketstation::EdgeObservations) -> Self {
        Self {
            queue_capacity_frames: edge.queue_capacity_frames,
            queue_depth_frames: edge.queue_depth_frames,
            queue_peak_frames: edge.queue_peak_frames,
            frames_enqueued_total: edge.frames_enqueued_total,
            frames_delivered_total: edge.frames_delivered_total,
            frames_dropped_total: edge.frames_dropped_total,
            overruns_total: edge.overruns_total,
            receiver_unavailable_drops_total: edge.receiver_unavailable_drops_total,
            queue_full_drops_total: edge.queue_full_drops_total,
            shared_reference_exhausted_drops_total: edge.shared_reference_exhausted_drops_total,
            branch_pool_exhausted_drops_total: edge.branch_pool_exhausted_drops_total,
            invalid_copy_policy_drops_total: edge.invalid_copy_policy_drops_total,
            freeze_failed_drops_total: edge.freeze_failed_drops_total,
            discontinuities_total: edge.discontinuities_total,
            source_identity_discontinuities_total: edge.source_identity_discontinuities_total,
            sequence_discontinuities_total: edge.sequence_discontinuities_total,
            timestamp_discontinuities_total: edge.timestamp_discontinuities_total,
            lineage_epoch_discontinuities_total: edge.lineage_epoch_discontinuities_total,
            manually_reported_discontinuities_total: edge.manually_reported_discontinuities_total,
            enqueue_to_receive_samples_total: edge.enqueue_to_receive_samples_total,
            enqueue_to_receive_invalid_order_total: edge.enqueue_to_receive_invalid_order_total,
            enqueue_to_receive_p50_ns: edge.enqueue_to_receive_p50_ns,
            enqueue_to_receive_p95_ns: edge.enqueue_to_receive_p95_ns,
            enqueue_to_receive_p99_ns: edge.enqueue_to_receive_p99_ns,
            enqueue_to_receive_max_ns: edge.enqueue_to_receive_max_ns,
            source_timestamp_to_receive_samples_total: edge
                .source_timestamp_to_receive_samples_total,
            source_timestamp_to_receive_missing_total: edge
                .source_timestamp_to_receive_missing_total,
            source_timestamp_to_receive_future_total: edge.source_timestamp_to_receive_future_total,
            source_timestamp_to_receive_p50_ns: edge.source_timestamp_to_receive_p50_ns,
            source_timestamp_to_receive_p95_ns: edge.source_timestamp_to_receive_p95_ns,
            source_timestamp_to_receive_p99_ns: edge.source_timestamp_to_receive_p99_ns,
            source_timestamp_to_receive_max_ns: edge.source_timestamp_to_receive_max_ns,
            worker_failures_total: edge.worker_failures_total,
            shutdown_discarded_total: edge.shutdown_discarded_total,
            discarded_output_frames_total: None,
        }
    }
}

impl From<pocketstation::SessionSourceMetrics> for PythonSessionSourceMetrics {
    fn from(source: pocketstation::SessionSourceMetrics) -> Self {
        Self {
            stem_id: source.stem_id.get(),
            callback_buffers_total: source.capture.backend.callback_buffers_total,
            capture_frames_enqueued_total: source.capture.backend.frames_enqueued_total,
            capture_pool_exhausted_total: source.capture.backend.pool_exhausted_total,
            capture_dispatch_queue_full_total: source.capture.backend.dispatch_queue_full_total,
            capture_invalid_buffer_total: source.capture.backend.invalid_buffer_total,
            capture_oversized_buffer_total: source.capture.backend.oversized_buffer_total,
            capture_stream_errors_total: source.capture.backend.stream_errors_total,
            capture_timestamp_epoch_clamps_total: source
                .capture
                .backend
                .timestamp_epoch_clamps_total,
            frame_stream_delivered_frames_total: source.capture.frame_stream.delivered_frames,
            frame_stream_dropped_newest_frames_total: source
                .capture
                .frame_stream
                .dropped_newest_frames,
            frames_discarded_before_start_total: source
                .capture
                .frame_stream
                .frames_discarded_before_start_total,
            runtime_event_capacity_count: source.capture.runtime_events.capacity_event_count,
            runtime_event_maximum_event_owned_bytes: source
                .capture
                .runtime_events
                .maximum_event_owned_bytes,
            runtime_event_maximum_buffered_owned_bytes: source
                .capture
                .runtime_events
                .maximum_buffered_owned_bytes,
            runtime_event_depth_count: source.capture.runtime_events.depth_events,
            runtime_event_depth_owned_bytes: source.capture.runtime_events.depth_owned_bytes,
            runtime_event_peak_depth_owned_bytes: source
                .capture
                .runtime_events
                .peak_depth_owned_bytes,
            runtime_events_enqueued_total: source.capture.runtime_events.events_enqueued_total,
            runtime_events_dropped_total: source.capture.runtime_events.events_dropped_total,
            runtime_events_dropped_oversized_total: source
                .capture
                .runtime_events
                .events_dropped_oversized_total,
            ingress_queue_capacity_frames: source.ingress.queue_capacity_frames,
            ingress_queue_depth_frames: source.ingress.queue_depth_frames,
            ingress_queue_peak_frames: source.ingress.queue_peak_frames,
            ingress_frames_enqueued_total: source.ingress.frames_enqueued_total,
            ingress_frames_delivered_total: source.ingress.frames_delivered_total,
            ingress_frames_rejected_full_total: source.ingress.frames_rejected_full_total,
            ingress_frames_rejected_cancelled_total: source.ingress.frames_rejected_cancelled_total,
            ingress_frames_discarded_total: source.ingress.frames_discarded_total,
        }
    }
}

impl From<pocketstation::SessionExternalSourceMetrics> for PythonExternalSourceMetrics {
    fn from(source: pocketstation::SessionExternalSourceMetrics) -> Self {
        Self {
            source_instance_id: source.source_instance_id.value(),
            source_id: source.source_id.get(),
            emitted_total: source.runtime.emitted_total,
            dropped_total: source.runtime.dropped_total,
            failure_total: source.runtime.failure_total,
            cancellation_total: source.runtime.cancellation_total,
            discontinuity_total: source.runtime.discontinuity_total,
            recovery_total: source.runtime.recovery_total,
            policy_change_total: source.runtime.policy_change_total,
            ready: source.runtime.ready,
            joined: source.runtime.joined,
        }
    }
}

fn python_operator_metrics(
    py: Python<'_>,
    operator: pocketstation::SessionOperatorMetrics,
) -> PyResult<Py<PythonOperatorMetrics>> {
    let input_ports = operator
        .input_ports
        .iter()
        .map(|input| {
            Py::new(
                py,
                PythonOperatorInputMetrics {
                    port_name: input.port_name.clone(),
                    delivery: Py::new(py, PythonRouteDeliveryMetrics::from(input.edge))?,
                },
            )
        })
        .collect::<PyResult<Vec<_>>>()?;
    let worker = operator.worker;
    Py::new(
        py,
        PythonOperatorMetrics {
            operator_instance_id: operator.operator_instance_id.value(),
            input_delivery: Py::new(
                py,
                PythonRouteDeliveryMetrics::from(operator.input_delivery),
            )?,
            worker: Py::new(
                py,
                PythonOperatorWorkerMetrics {
                    input_attempted_total: worker.input_attempted_total,
                    input_dropped_total: worker.input_dropped_total,
                    processed_total: worker.processed_total,
                    output_emitted_total: worker.output_emitted_total,
                    output_dropped_total: worker.output_dropped_total,
                    output_nonterminal_total: worker.output_nonterminal_total,
                    output_terminal_total: worker.output_terminal_total,
                    process_failure_total: worker.process_failure_total,
                    timeout_total: worker.timeout_total,
                    cancellation_total: worker.cancellation_total,
                    graceful_finish_total: worker.graceful_finish_total,
                    idle_poll_total: worker.idle_poll_total,
                    ready: worker.ready,
                    joined: worker.joined,
                },
            )?,
            finalization_failures_total: operator.finalization_failures_total,
            input_ports,
        },
    )
}

fn python_derived_route_metrics(
    py: Python<'_>,
    route: pocketstation::SessionDerivedRouteMetrics,
) -> PyResult<Py<PythonDerivedRouteMetrics>> {
    let endpoint = route.endpoint.unwrap_or_default();
    Py::new(
        py,
        PythonDerivedRouteMetrics {
            route_id: route.route_id.get(),
            endpoint_id: route.endpoint_id.get(),
            output: Py::new(
                py,
                PythonSignalQueueMetrics {
                    capacity_signals: route.output.capacity_signals,
                    max_payload_bytes: route.output.max_payload_bytes,
                    maximum_buffered_payload_bytes: route.output.maximum_buffered_payload_bytes,
                    depth_signals: route.output.depth_signals,
                    peak_depth_signals: route.output.peak_depth_signals,
                    enqueued_total: route.output.enqueued_total,
                    received_total: route.output.received_total,
                    dropped_total: route.output.dropped_total,
                },
            )?,
            endpoint_observation_stage: endpoint_observation_stage_name(
                route.endpoint_observation_stage,
            ),
            endpoint_frames_received_total: endpoint.frames_received_total,
            endpoint_frames_delivered_total: endpoint.frames_delivered_total,
            endpoint_frames_dropped_total: endpoint.frames_dropped_total,
            endpoint_discontinuities_total: endpoint.discontinuities_total,
            endpoint_failures_total: endpoint.failures_total,
            endpoint_finalization_failures_total: route.endpoint_finalization_failures_total,
        },
    )
}

impl From<pocketstation::SessionAudioReentryMetrics> for PythonAudioReentryMetrics {
    fn from(reentry: pocketstation::SessionAudioReentryMetrics) -> Self {
        Self {
            operator_instance_id: reentry.operator_instance_id().value(),
            stem_id: reentry.stem_id().get(),
            queue_capacity_signals: reentry.queue_capacity_signals(),
            queue_depth_signals: reentry.queue_depth_signals(),
            queue_peak_signals: reentry.queue_peak_signals(),
            signals_enqueued_total: reentry.signals_enqueued_total(),
            signals_received_total: reentry.signals_received_total(),
            signals_dropped_total: reentry.signals_dropped_total(),
            pool_slots: reentry.pool_slots(),
            frame_capacity_samples: reentry.frame_capacity_samples(),
            maximum_buffered_audio_bytes: reentry.maximum_buffered_audio_bytes(),
            normalized_total: reentry.normalized_total(),
            invalid_total: reentry.invalid_total(),
            shared_audio_rejected_total: reentry.shared_audio_rejected_total(),
            pool_exhausted_total: reentry.pool_exhausted_total(),
            ingress_rejected_total: reentry.ingress_rejected_total(),
            audio_frames_enqueued_total: reentry.audio_frames_enqueued_total(),
            cancellation_total: reentry.cancellation_total(),
            joined: reentry.joined(),
        }
    }
}

impl From<pocketstation::SessionTraceRecorderOutcome> for PythonSessionTraceRecorderOutcome {
    fn from(outcome: pocketstation::SessionTraceRecorderOutcome) -> Self {
        Self {
            path: outcome.path.display().to_string(),
            records_attempted_total: outcome.records_attempted_total,
            records_enqueued_total: outcome.records_enqueued_total,
            records_dropped_total: outcome.records_dropped_total,
            records_written_total: outcome.records_written_total,
            rolling_hash: outcome.rolling_hash,
            complete: outcome.is_complete(),
        }
    }
}

impl From<pocketstation::SessionTraceValidation> for PythonSessionTraceValidation {
    fn from(validation: pocketstation::SessionTraceValidation) -> Self {
        Self {
            session_id: validation.session_id.get(),
            lifecycle: validation
                .lifecycle
                .iter()
                .map(|state| lifecycle_state_name(*state).to_owned())
                .collect(),
            terminal_state: terminal_state_name(validation.terminal.state).to_owned(),
            source_failures_total: validation.terminal.source_failures_total,
            endpoint_failures_total: validation.terminal.endpoint_failures_total,
            rollback_failures_total: validation.terminal.rollback_failures_total,
            finalization_failures_total: validation.terminal.finalization_failures_total,
            records_validated_total: validation.records_validated_total,
        }
    }
}

impl From<pocketstation::SessionTraceRecord> for PythonSessionTraceRecord {
    fn from(record: pocketstation::SessionTraceRecord) -> Self {
        let mut output = Self {
            sequence_index: record.sequence_index,
            observed_at_ns: record.observed_at_ns,
            session_id: record.session_id.get(),
            kind: String::new(),
            lifecycle_state: None,
            terminal_state: None,
            stem_id: None,
            route_id: None,
            endpoint_id: None,
            endpoint_stage: None,
            rollback_stage: None,
            finalization_stage: None,
            source_failures_total: None,
            endpoint_failures_total: None,
            rollback_failures_total: None,
            finalization_failures_total: None,
        };
        match record.kind {
            pocketstation::SessionTraceRecordKind::Lifecycle { state } => {
                output.kind = "lifecycle".to_owned();
                output.lifecycle_state = Some(lifecycle_state_name(state).to_owned());
            }
            pocketstation::SessionTraceRecordKind::SourceFailure { stem_id } => {
                output.kind = "source-failure".to_owned();
                output.stem_id = Some(stem_id.get());
            }
            pocketstation::SessionTraceRecordKind::EndpointFailure {
                route_id,
                endpoint_id,
                stage_code,
            } => {
                output.kind = "endpoint-failure".to_owned();
                output.route_id = Some(route_id.get());
                output.endpoint_id = Some(endpoint_id.get());
                output.endpoint_stage = endpoint_trace_stage_name(stage_code).map(str::to_owned);
            }
            pocketstation::SessionTraceRecordKind::RollbackFailure { stage } => {
                output.kind = "rollback-failure".to_owned();
                output.rollback_stage = Some(rollback_stage_name(stage));
            }
            pocketstation::SessionTraceRecordKind::FinalizationFailure { stage } => {
                output.kind = "finalization-failure".to_owned();
                output.finalization_stage = Some(finalization_stage_name(stage));
            }
            pocketstation::SessionTraceRecordKind::Terminal {
                state,
                source_failures_total,
                endpoint_failures_total,
                rollback_failures_total,
                finalization_failures_total,
            } => {
                output.kind = "terminal".to_owned();
                output.terminal_state = Some(terminal_state_name(state).to_owned());
                output.source_failures_total = Some(source_failures_total);
                output.endpoint_failures_total = Some(endpoint_failures_total);
                output.rollback_failures_total = Some(rollback_failures_total);
                output.finalization_failures_total = Some(finalization_failures_total);
            }
        }
        output
    }
}

const fn endpoint_trace_stage_name(stage_code: u8) -> Option<&'static str> {
    match stage_code {
        1 => Some("prepare"),
        2 => Some("cancel-preparation"),
        3 => Some("start"),
        4 => Some("request-stop"),
        5 => Some("join-finalize"),
        _ => None,
    }
}

fn session_trace_validation_error(error: pocketstation::SessionTraceValidationError) -> PyErr {
    let code = match &error {
        pocketstation::SessionTraceValidationError::Io(_) => "trace.io",
        pocketstation::SessionTraceValidationError::InvalidMagic => "trace.invalid_magic",
        pocketstation::SessionTraceValidationError::UnsupportedVersion => {
            "trace.unsupported_version"
        }
        pocketstation::SessionTraceValidationError::InvalidLayout => "trace.invalid_layout",
        pocketstation::SessionTraceValidationError::Truncated => "trace.truncated",
        pocketstation::SessionTraceValidationError::InvalidChecksum => "trace.invalid_checksum",
        pocketstation::SessionTraceValidationError::IncompleteTrace => "trace.incomplete",
        pocketstation::SessionTraceValidationError::SequenceGap => "trace.sequence_gap",
        pocketstation::SessionTraceValidationError::SessionMismatch => "trace.session_mismatch",
        pocketstation::SessionTraceValidationError::TimestampRegression => {
            "trace.timestamp_regression"
        }
        pocketstation::SessionTraceValidationError::InvalidLifecycleTransition => {
            "trace.invalid_lifecycle_transition"
        }
        pocketstation::SessionTraceValidationError::MissingTerminal => "trace.missing_terminal",
        pocketstation::SessionTraceValidationError::TerminalMismatch => "trace.terminal_mismatch",
        pocketstation::SessionTraceValidationError::RecordAfterTerminal => {
            "trace.record_after_terminal"
        }
        pocketstation::SessionTraceValidationError::UnknownRecordType => {
            "trace.unknown_record_type"
        }
    };
    PyRuntimeError::new_err(coded_reason(code, error.to_string()))
}

pub(crate) fn python_session_metrics(
    py: Python<'_>,
    metrics: OwnedSessionMetrics,
) -> PyResult<PythonSessionMetrics> {
    let sources = metrics
        .sources
        .into_iter()
        .map(|source| Py::new(py, PythonSessionSourceMetrics::from(source)))
        .collect::<PyResult<Vec<_>>>()?;
    let external_sources = metrics
        .external_sources
        .into_iter()
        .map(|source| Py::new(py, PythonExternalSourceMetrics::from(source)))
        .collect::<PyResult<Vec<_>>>()?;
    let operators = metrics
        .operators
        .into_iter()
        .map(|operator| python_operator_metrics(py, operator))
        .collect::<PyResult<Vec<_>>>()?;
    let derived_routes = metrics
        .derived_routes
        .into_iter()
        .map(|route| python_derived_route_metrics(py, route))
        .collect::<PyResult<Vec<_>>>()?;
    let audio_reentries = metrics
        .audio_reentries
        .into_iter()
        .map(|reentry| Py::new(py, PythonAudioReentryMetrics::from(reentry)))
        .collect::<PyResult<Vec<_>>>()?;
    let routes = metrics
        .routes
        .into_iter()
        .map(|route| {
            Py::new(
                py,
                PythonRouteMetrics {
                    route_id: route.route_id,
                    endpoint_id: route.endpoint_id,
                    endpoint_observation_stage: route.endpoint_observation_stage,
                    queue_capacity_frames: route.queue_capacity_frames,
                    queue_depth_frames: route.queue_depth_frames,
                    queue_peak_frames: route.queue_peak_frames,
                    frames_enqueued_total: route.frames_enqueued_total,
                    frames_attempted_total: route.frames_attempted_total,
                    frames_delivered_total: route.frames_delivered_total,
                    frames_dropped_total: route.frames_dropped_total,
                    queue_full_drops_total: route.queue_full_drops_total,
                    overruns_total: route.overruns_total,
                    receiver_unavailable_drops_total: route.receiver_unavailable_drops_total,
                    shared_reference_exhausted_drops_total: route
                        .shared_reference_exhausted_drops_total,
                    branch_pool_exhausted_drops_total: route.branch_pool_exhausted_drops_total,
                    invalid_copy_policy_drops_total: route.invalid_copy_policy_drops_total,
                    freeze_failed_drops_total: route.freeze_failed_drops_total,
                    discontinuities_total: route.discontinuities_total,
                    source_identity_discontinuities_total: route
                        .source_identity_discontinuities_total,
                    sequence_discontinuities_total: route.sequence_discontinuities_total,
                    timestamp_discontinuities_total: route.timestamp_discontinuities_total,
                    lineage_epoch_discontinuities_total: route.lineage_epoch_discontinuities_total,
                    manually_reported_discontinuities_total: route
                        .manually_reported_discontinuities_total,
                    enqueue_to_receive_samples_total: route.enqueue_to_receive_samples_total,
                    enqueue_to_receive_invalid_order_total: route
                        .enqueue_to_receive_invalid_order_total,
                    enqueue_to_receive_p50_ns: route.enqueue_to_receive_p50_ns,
                    enqueue_to_receive_p95_ns: route.enqueue_to_receive_p95_ns,
                    enqueue_to_receive_p99_ns: route.enqueue_to_receive_p99_ns,
                    enqueue_to_receive_max_ns: route.enqueue_to_receive_max_ns,
                    source_timestamp_to_receive_samples_total: route
                        .source_timestamp_to_receive_samples_total,
                    source_timestamp_to_receive_missing_total: route
                        .source_timestamp_to_receive_missing_total,
                    source_timestamp_to_receive_future_total: route
                        .source_timestamp_to_receive_future_total,
                    source_timestamp_to_receive_p50_ns: route.source_timestamp_to_receive_p50_ns,
                    source_timestamp_to_receive_p95_ns: route.source_timestamp_to_receive_p95_ns,
                    source_timestamp_to_receive_p99_ns: route.source_timestamp_to_receive_p99_ns,
                    source_timestamp_to_receive_max_ns: route.source_timestamp_to_receive_max_ns,
                    worker_failures_total: route.worker_failures_total,
                    shutdown_discarded_total: route.shutdown_discarded_total,
                    discarded_output_frames_total: route.discarded_output_frames_total,
                    endpoint_frames_received_total: route.endpoint_frames_received_total,
                    endpoint_frames_delivered_total: route.endpoint_frames_delivered_total,
                    endpoint_frames_dropped_total: route.endpoint_frames_dropped_total,
                    endpoint_discontinuities_total: route.endpoint_discontinuities_total,
                    endpoint_failures_total: route.endpoint_failures_total,
                    endpoint_finalization_failures_total: route
                        .endpoint_finalization_failures_total,
                    drop_observation_interval: "route-lifetime-to-snapshot".to_owned(),
                    drop_rate_pct: route.drop_rate_pct,
                    source_latency_measurement: "source-monotonic-timestamp-to-route-receive"
                        .to_owned(),
                    source_latency_unit: "nanoseconds".to_owned(),
                },
            )
        })
        .collect::<PyResult<Vec<_>>>()?;
    Ok(PythonSessionMetrics {
        event_capacity_count: metrics.event_capacity_count,
        event_maximum_event_owned_bytes: metrics.event_maximum_event_owned_bytes,
        event_maximum_buffered_owned_bytes: metrics.event_maximum_buffered_owned_bytes,
        event_depth_count: metrics.event_depth_count,
        event_depth_owned_bytes: metrics.event_depth_owned_bytes,
        event_peak_depth_count: metrics.event_peak_depth_count,
        event_peak_depth_owned_bytes: metrics.event_peak_depth_owned_bytes,
        events_enqueued_total: metrics.events_enqueued_total,
        events_dropped_total: metrics.events_dropped_total,
        events_dropped_oversized_total: metrics.events_dropped_oversized_total,
        event_receiver_closed_total: metrics.event_receiver_closed_total,
        audio_registered_endpoints: metrics.audio_registered_endpoints,
        audio_queue_capacity_frames: metrics.audio_queue_capacity_frames,
        audio_queue_depth_frames: metrics.audio_queue_depth_frames,
        audio_queue_peak_frames: metrics.audio_queue_peak_frames,
        audio_queue_depth_invariant_failures_total: metrics
            .audio_queue_depth_invariant_failures_total,
        audio_frames_received_total: metrics.audio_frames_received_total,
        audio_frames_delivered_total: metrics.audio_frames_delivered_total,
        audio_queue_full_drops_total: metrics.audio_queue_full_drops_total,
        audio_invalid_ownership_drops_total: metrics.audio_invalid_ownership_drops_total,
        audio_discarded_output_frames_total: metrics.audio_discarded_output_frames_total,
        audio_lease_capacity_count: metrics.audio_lease_capacity_count,
        audio_outstanding_leases: metrics.audio_outstanding_leases,
        audio_lease_exhausted_total: metrics.audio_lease_exhausted_total,
        audio_batches_polled_total: metrics.audio_batches_polled_total,
        audio_frames_polled_total: metrics.audio_frames_polled_total,
        source_count: metrics.source_count,
        external_source_count: metrics.external_source_count,
        route_count: metrics.route_count,
        operator_count: metrics.operator_count,
        derived_route_count: metrics.derived_route_count,
        audio_reentry_count: metrics.audio_reentry_count,
        routes,
        sources,
        external_sources,
        operators,
        derived_routes,
        audio_reentries,
    })
}

pub(crate) fn owned_recording_outcome(
    running: &pocketstation::RunningSession,
) -> Option<OwnedRecordingOutcome> {
    let outcome = running.recording_outcome()?;
    let stems = outcome
        .stems
        .iter()
        .map(|stem| {
            let discontinuities = stem
                .gap_ranges
                .iter()
                .map(|record| OwnedRecordingDiscontinuity {
                    stem_id: record.stem_id,
                    label: record.label.clone(),
                    kind: match format!("{:?}", record.kind).as_str() {
                        "TimestampGap" => "timestamp-gap",
                        "SequenceGap" => "sequence-gap",
                        "OverlapRejected" => "overlap-rejected",
                        _ => "unrecognized-discontinuity",
                    }
                    .to_owned(),
                    timestamp_start_ns: record.timestamp_start_ns,
                    timestamp_end_ns: record.timestamp_end_ns,
                    sequence_start: record.sequence_start,
                    sequence_end: record.sequence_end,
                })
                .collect();
            OwnedRecordingStemOutcome {
                stem_name: stem.label.clone(),
                frames_written_total: stem.written_frames,
                stale_frames_total: stem.stale_frames,
                error: stem.error.clone(),
                queue_capacity_frames: stem.edge_observations.queue_capacity_frames,
                queue_peak_frames: stem.edge_observations.queue_peak_frames,
                frames_delivered_total: stem.edge_observations.frames_delivered_total,
                frames_dropped_total: stem.edge_observations.frames_dropped_total,
                queue_full_drops_total: stem.edge_observations.queue_full_drops_total,
                discontinuities_total: stem.edge_observations.discontinuities_total,
                discontinuities,
            }
        })
        .collect();
    Some(OwnedRecordingOutcome {
        session_id: running.session_id().get(),
        group_id: pocketstation::DEFAULT_MULTISTEM_RECORDING_GROUP_ID.to_owned(),
        complete: outcome.state == pocketstation::SessionRecordingState::Complete,
        state: format!("{:?}", outcome.state).to_lowercase(),
        completed_stems: outcome.completed_stems,
        failed_stems: outcome.failed_stems,
        session_directory: outcome.session_dir.display().to_string(),
        manifest_path: outcome
            .session_dir
            .join(pocketstation::SESSION_RECORDING_MANIFEST_FILE_NAME)
            .display()
            .to_string(),
        manifest_schema_version: pocketstation::SESSION_RECORDING_MANIFEST_SCHEMA_VERSION,
        error_code: pocketstation::session_recording_outcome_error_code(outcome)
            .map(|code| code.as_str().to_owned()),
        stems,
    })
}

pub(crate) fn python_recording_outcome(
    py: Python<'_>,
    outcome: OwnedRecordingOutcome,
) -> PyResult<Py<PythonRecordingOutcome>> {
    let stems = outcome
        .stems
        .into_iter()
        .map(|stem| {
            let discontinuities = stem
                .discontinuities
                .into_iter()
                .map(|value| {
                    Py::new(
                        py,
                        PythonRecordingDiscontinuity {
                            stem_id: value.stem_id,
                            label: value.label,
                            kind: value.kind,
                            timestamp_start_ns: value.timestamp_start_ns,
                            timestamp_end_ns: value.timestamp_end_ns,
                            sequence_start: value.sequence_start,
                            sequence_end: value.sequence_end,
                        },
                    )
                })
                .collect::<PyResult<Vec<_>>>()?;
            Py::new(
                py,
                PythonRecordingStemOutcome {
                    stem_name: stem.stem_name,
                    frames_written_total: stem.frames_written_total,
                    stale_frames_total: stem.stale_frames_total,
                    error: stem.error,
                    queue_capacity_frames: stem.queue_capacity_frames,
                    queue_peak_frames: stem.queue_peak_frames,
                    frames_delivered_total: stem.frames_delivered_total,
                    frames_dropped_total: stem.frames_dropped_total,
                    queue_full_drops_total: stem.queue_full_drops_total,
                    discontinuities_total: stem.discontinuities_total,
                    discontinuities,
                },
            )
        })
        .collect::<PyResult<Vec<_>>>()?;
    Py::new(
        py,
        PythonRecordingOutcome {
            session_id: outcome.session_id,
            group_id: outcome.group_id,
            complete: outcome.complete,
            state: outcome.state,
            completed_stems: outcome.completed_stems,
            failed_stems: outcome.failed_stems,
            session_directory: outcome.session_directory,
            manifest_path: outcome.manifest_path,
            manifest_schema_version: outcome.manifest_schema_version,
            error_code: outcome.error_code,
            stems,
        },
    )
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonRecordingDiscontinuity>()?;
    module.add_class::<PythonRecordingStemOutcome>()?;
    module.add_class::<PythonRecordingOutcome>()?;
    module.add_class::<PythonStopResult>()?;
    module.add_class::<PythonSessionFailure>()?;
    module.add_class::<PythonSessionEvent>()?;
    module.add_class::<PythonSessionMetrics>()?;
    module.add_class::<PythonRouteMetrics>()?;
    module.add_class::<PythonSessionSourceMetrics>()?;
    module.add_class::<PythonExternalSourceMetrics>()?;
    module.add_class::<PythonRouteDeliveryMetrics>()?;
    module.add_class::<PythonOperatorInputMetrics>()?;
    module.add_class::<PythonOperatorWorkerMetrics>()?;
    module.add_class::<PythonOperatorMetrics>()?;
    module.add_class::<PythonSignalQueueMetrics>()?;
    module.add_class::<PythonDerivedRouteMetrics>()?;
    module.add_class::<PythonAudioReentryMetrics>()?;
    module.add_class::<PythonSessionTraceRecorderOutcome>()?;
    module.add_class::<PythonSessionTraceValidation>()?;
    module.add_class::<PythonSessionTraceRecord>()?;
    module.add_class::<PythonSessionTrace>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use pocketstation::{
        CaptureRuntimeFailure, CaptureRuntimeFailureClass, Platform, SourceGeneration, SourceKind,
        SourceRecoveryRequirement, SourceRuntimeEvent, StableSourceId,
    };

    #[test]
    fn source_disappearance_survives_the_native_projection() {
        let stable_id =
            StableSourceId::new(Platform::Windows, SourceKind::Application, "aumid:fixture");
        let expected_source_id = stable_id.source_id().get();
        let event = SourceRuntimeEvent::SourceUnavailable {
            stable_id,
            generation: SourceGeneration(7),
            recovery_requirement: SourceRecoveryRequirement::ExplicitRediscoveryAndNewSession,
            failure: CaptureRuntimeFailure {
                operation: "capture",
                error_class: CaptureRuntimeFailureClass::PlatformStatus { status_code: -42 },
            },
        };
        let mut projected = empty_owned_session_event(1);
        populate_source_runtime_event(&mut projected, &event);

        assert_eq!(
            projected.source_event_kind.as_deref(),
            Some("source-unavailable")
        );
        assert_eq!(projected.source_platform.as_deref(), Some("windows"));
        assert_eq!(projected.source_kind.as_deref(), Some("application"));
        assert_eq!(
            projected.source_stable_key.as_deref(),
            Some("aumid:fixture")
        );
        assert_eq!(projected.source_source_id, Some(expected_source_id));
        assert_eq!(projected.source_generation, Some(7));
        assert_eq!(
            projected.source_recovery_requirement.as_deref(),
            Some("explicit-rediscovery-and-new-session")
        );
        assert_eq!(
            projected.source_failure_operation.as_deref(),
            Some("capture")
        );
        assert_eq!(
            projected.source_failure_class.as_deref(),
            Some("platform-status")
        );
        assert_eq!(projected.source_platform_status_code, Some(-42));
    }
}
