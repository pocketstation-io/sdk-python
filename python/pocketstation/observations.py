"""Typed, immutable observations from the canonical native Session."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast

from ._native import RecordingDiscontinuity as _NativeRecordingDiscontinuity
from ._native import RecordingOutcome as _NativeRecordingOutcome
from ._native import RecordingStemOutcome as _NativeRecordingStemOutcome
from ._native import RelayPublishOutcome as _NativeRelayPublishOutcome
from ._native import RouteMetrics as _NativeRouteMetrics
from ._native import SessionEvent as _NativeSessionEvent
from ._native import SessionMetrics as _NativeSessionMetrics
from ._native import SessionTrace as _NativeSessionTrace
from ._native import SessionTraceRecorderOutcome as _NativeTraceRecorderOutcome
from ._native import StopResult as _NativeStopResult
from ._native import _AudioReentryMetrics as _NativeAudioReentryMetrics
from ._native import _DerivedRouteMetrics as _NativeDerivedRouteMetrics
from ._native import _EdgeMetrics as _NativeEdgeMetrics
from ._native import _ExternalSourceMetrics as _NativeExternalSourceMetrics
from ._native import _OperatorInputMetrics as _NativeOperatorInputMetrics
from ._native import _OperatorMetrics as _NativeOperatorMetrics
from ._native import _OperatorWorkerMetrics as _NativeOperatorWorkerMetrics
from ._native import _SessionFailure as _NativeSessionFailure
from ._native import _SessionSourceMetrics as _NativeSessionSourceMetrics
from ._native import _SessionTraceValidation as _NativeTraceValidation
from ._native import _TypedEdgeMetrics as _NativeTypedEdgeMetrics
from .errors import PocketStationError, _native_call
from .sidecar import SidecarSnapshot
from .sources import SourceRuntimeEvent
from .streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)


class SessionEventType(StrEnum):
    """Stable variants of the authoritative Session event stream."""

    LIFECYCLE = "lifecycle"
    SOURCE_FAILURE = "source_failure"
    ENDPOINT_FAILURE = "endpoint_failure"
    ROLLBACK_FAILURE = "rollback_failure"
    FINALIZATION_FAILURE = "finalization_failure"
    TERMINAL = "terminal"


class SessionLifecycleState(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class SessionTerminalState(StrEnum):
    STOPPED = "stopped"
    FAILED = "failed"


class SessionFailureKind(StrEnum):
    SOURCE = "source"
    ENDPOINT = "endpoint"
    ROLLBACK = "rollback"
    FINALIZATION = "finalization"


class EndpointFailureStage(StrEnum):
    PREPARE = "prepare"
    CANCEL_PREPARATION = "cancel-preparation"
    START = "start"
    REQUEST_STOP = "request-stop"
    JOIN_FINALIZE = "join-finalize"


class EndpointFailureRetryability(StrEnum):
    NEVER = "never"
    RETRYABLE = "retryable"
    RECONFIGURATION_REQUIRED = "retry-after-reconfiguration"


class SessionRollbackStage(StrEnum):
    CANCEL_OPERATOR = "cancel-operator"
    CANCEL_ENDPOINT_PREPARATION = "cancel-endpoint-preparation"
    FINALIZE_STARTED_ENDPOINT = "finalize-started-endpoint"
    STOP_OPENED_CAPTURE = "stop-opened-capture"
    DISCARD_RUNTIME_QUEUES = "discard-runtime-queues"


class SessionFinalizationStage(StrEnum):
    STOP_CAPTURE = "stop-capture"
    DRAIN_RUNTIME = "drain-runtime"
    DRAIN_OPERATOR = "drain-operator"
    REQUEST_ENDPOINT_STOP = "request-endpoint-stop"
    JOIN_ENDPOINT = "join-endpoint"
    FINALIZE_ENDPOINT = "finalize-endpoint"
    DRAIN_SIDECAR = "drain-sidecar"


class EndpointObservationStage(StrEnum):
    UNAVAILABLE = "unavailable"
    LIVE = "live"
    FINALIZED = "finalized"


class TerminationDisposition(StrEnum):
    STOPPED = "stopped"
    CANCELLED = "cancelled"
    ALREADY_STOPPED = "already-stopped"


class RecordingState(StrEnum):
    RECORDING = "recording"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


class RecordingDiscontinuityKind(StrEnum):
    TIMESTAMP_GAP = "timestamp-gap"
    SEQUENCE_GAP = "sequence-gap"
    OVERLAP_REJECTED = "overlap-rejected"


class RouteObservationInterval(StrEnum):
    ROUTE_LIFETIME_TO_SNAPSHOT = "route-lifetime-to-snapshot"


class RouteLatencyBoundary(StrEnum):
    SOURCE_TIMESTAMP_TO_ROUTE_RECEIVE = "source-monotonic-timestamp-to-route-receive"


class RouteLatencyUnit(StrEnum):
    NANOSECONDS = "nanoseconds"


FailureStage = EndpointFailureStage | SessionRollbackStage | SessionFinalizationStage


def _failure_stage(kind: SessionFailureKind, value: str | None) -> FailureStage | None:
    if value is None:
        return None
    if kind is SessionFailureKind.ENDPOINT:
        return EndpointFailureStage(value)
    if kind is SessionFailureKind.ROLLBACK:
        return SessionRollbackStage(value)
    if kind is SessionFailureKind.FINALIZATION:
        return SessionFinalizationStage(value)
    return None


@dataclass(frozen=True, slots=True)
class SessionFailure:
    """One typed source, endpoint, rollback, or finalization failure."""

    kind: SessionFailureKind
    stage: FailureStage | None
    operation: str | None
    error_class: str | None
    error_code: str | None
    retryability: EndpointFailureRetryability | None
    component: str | None
    message: str | None
    stem_id: int | None
    route_id: int | None
    endpoint_id: int | None
    operator_instance_id: int | None
    sidecar_id: int | None
    source: SourceRuntimeEvent | None

    @classmethod
    def _from_native(cls, failure: _NativeSessionFailure) -> SessionFailure:
        kind = SessionFailureKind(failure.kind)
        retryability = getattr(failure, "retryability", None)
        return cls(
            kind=kind,
            stage=_failure_stage(kind, failure.stage),
            operation=failure.operation,
            error_class=failure.error_class,
            error_code=getattr(failure, "error_code", None),
            retryability=(
                None
                if retryability is None
                else EndpointFailureRetryability(retryability)
            ),
            component=failure.component,
            message=failure.message,
            stem_id=failure.stem_id,
            route_id=failure.route_id,
            endpoint_id=failure.endpoint_id,
            operator_instance_id=failure.operator_instance_id,
            sidecar_id=failure.sidecar_id,
            source=SourceRuntimeEvent._from_native(cast(_NativeSessionEvent, failure)),
        )


@dataclass(frozen=True, slots=True)
class SessionEvent:
    """One immutable projection of an authoritative native Session event."""

    kind: SessionEventType
    lifecycle_state: SessionLifecycleState | None
    session_id: int
    stem_id: int | None
    endpoint_id: int | None
    route_id: int | None
    failures: tuple[SessionFailure, ...]
    terminal_state: SessionTerminalState | None
    source: SourceRuntimeEvent | None

    @property
    def failures_total(self) -> int:
        return len(self.failures)

    @classmethod
    def _from_native(cls, event: _NativeSessionEvent) -> SessionEvent:
        lifecycle_state = (
            None
            if event.lifecycle_state is None
            else SessionLifecycleState(event.lifecycle_state)
        )
        terminal_state = (
            None
            if event.terminal_state is None
            else SessionTerminalState(event.terminal_state)
        )
        failures = tuple(
            SessionFailure._from_native(failure) for failure in event.failures()
        )
        if event.failures_total != len(failures):
            raise PocketStationError(
                "native Session event failure count is inconsistent",
                "session.invalid_event",
            )
        return cls(
            kind=SessionEventType(event.kind),
            lifecycle_state=lifecycle_state,
            session_id=event.session_id,
            stem_id=event.stem_id,
            endpoint_id=event.endpoint_id,
            route_id=event.route_id,
            failures=failures,
            terminal_state=terminal_state,
            source=SourceRuntimeEvent._from_native(event),
        )


@dataclass(frozen=True, slots=True)
class EventQueueMetrics:
    capacity_count: int
    maximum_event_owned_bytes: int
    maximum_buffered_owned_bytes: int
    depth_count: int
    depth_owned_bytes: int
    peak_depth_count: int
    peak_depth_owned_bytes: int
    enqueued_total: int
    dropped_total: int
    dropped_oversized_total: int
    receiver_closed_total: int


@dataclass(frozen=True, slots=True)
class PolledAudioMetrics:
    registered_endpoints: int
    queue_capacity_frames: int
    queue_depth_frames: int
    queue_peak_frames: int
    queue_depth_invariant_failures_total: int
    frames_received_total: int
    frames_delivered_total: int
    queue_full_drops_total: int
    invalid_ownership_drops_total: int
    lease_capacity_count: int
    outstanding_leases: int
    lease_exhausted_total: int
    batches_polled_total: int
    frames_polled_total: int


@dataclass(frozen=True, slots=True)
class LatencyHistogram:
    samples_total: int
    invalid_order_total: int
    missing_total: int
    future_total: int
    p50_ns: int
    p95_ns: int
    p99_ns: int
    max_ns: int


@dataclass(frozen=True, slots=True)
class EdgeMetrics:
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
    enqueue_to_receive: LatencyHistogram
    source_timestamp_to_receive: LatencyHistogram
    worker_failures_total: int
    shutdown_discarded_total: int

    @classmethod
    def _from_native(cls, value: _NativeEdgeMetrics) -> EdgeMetrics:
        return cls(
            queue_capacity_frames=value.queue_capacity_frames,
            queue_depth_frames=value.queue_depth_frames,
            queue_peak_frames=value.queue_peak_frames,
            frames_enqueued_total=value.frames_enqueued_total,
            frames_delivered_total=value.frames_delivered_total,
            frames_dropped_total=value.frames_dropped_total,
            overruns_total=value.overruns_total,
            receiver_unavailable_drops_total=value.receiver_unavailable_drops_total,
            queue_full_drops_total=value.queue_full_drops_total,
            shared_reference_exhausted_drops_total=value.shared_reference_exhausted_drops_total,
            branch_pool_exhausted_drops_total=value.branch_pool_exhausted_drops_total,
            invalid_copy_policy_drops_total=value.invalid_copy_policy_drops_total,
            freeze_failed_drops_total=value.freeze_failed_drops_total,
            discontinuities_total=value.discontinuities_total,
            source_identity_discontinuities_total=value.source_identity_discontinuities_total,
            sequence_discontinuities_total=value.sequence_discontinuities_total,
            timestamp_discontinuities_total=value.timestamp_discontinuities_total,
            lineage_epoch_discontinuities_total=value.lineage_epoch_discontinuities_total,
            manually_reported_discontinuities_total=value.manually_reported_discontinuities_total,
            enqueue_to_receive=LatencyHistogram(
                samples_total=value.enqueue_to_receive_samples_total,
                invalid_order_total=value.enqueue_to_receive_invalid_order_total,
                missing_total=0,
                future_total=0,
                p50_ns=value.enqueue_to_receive_p50_ns,
                p95_ns=value.enqueue_to_receive_p95_ns,
                p99_ns=value.enqueue_to_receive_p99_ns,
                max_ns=value.enqueue_to_receive_max_ns,
            ),
            source_timestamp_to_receive=LatencyHistogram(
                samples_total=value.source_timestamp_to_receive_samples_total,
                invalid_order_total=0,
                missing_total=value.source_timestamp_to_receive_missing_total,
                future_total=value.source_timestamp_to_receive_future_total,
                p50_ns=value.source_timestamp_to_receive_p50_ns,
                p95_ns=value.source_timestamp_to_receive_p95_ns,
                p99_ns=value.source_timestamp_to_receive_p99_ns,
                max_ns=value.source_timestamp_to_receive_max_ns,
            ),
            worker_failures_total=value.worker_failures_total,
            shutdown_discarded_total=value.shutdown_discarded_total,
        )


@dataclass(frozen=True, slots=True)
class EndpointMetrics:
    observation_stage: EndpointObservationStage
    frames_received_total: int
    frames_delivered_total: int
    frames_dropped_total: int
    discontinuities_total: int
    failures_total: int
    finalization_failures_total: int


@dataclass(frozen=True, slots=True)
class RouteMetrics:
    route_id: int
    endpoint_id: int
    edge: EdgeMetrics
    endpoint: EndpointMetrics
    frames_attempted_total: int
    observation_interval: RouteObservationInterval
    drop_rate_pct: float
    source_latency_boundary: RouteLatencyBoundary
    source_latency_unit: RouteLatencyUnit

    @property
    def queue_capacity_frames(self) -> int:
        return self.edge.queue_capacity_frames

    @property
    def frames_delivered_total(self) -> int:
        return self.edge.frames_delivered_total

    @property
    def frames_dropped_total(self) -> int:
        return self.edge.frames_dropped_total

    @classmethod
    def _from_native(cls, value: _NativeRouteMetrics) -> RouteMetrics:
        edge = EdgeMetrics._from_native(cast(_NativeEdgeMetrics, value))
        return cls(
            route_id=value.route_id,
            endpoint_id=value.endpoint_id,
            edge=edge,
            endpoint=EndpointMetrics(
                observation_stage=EndpointObservationStage(
                    value.endpoint_observation_stage
                ),
                frames_received_total=value.endpoint_frames_received_total,
                frames_delivered_total=value.endpoint_frames_delivered_total,
                frames_dropped_total=value.endpoint_frames_dropped_total,
                discontinuities_total=value.endpoint_discontinuities_total,
                failures_total=value.endpoint_failures_total,
                finalization_failures_total=value.endpoint_finalization_failures_total,
            ),
            frames_attempted_total=value.frames_attempted_total,
            observation_interval=RouteObservationInterval(
                value.drop_observation_interval
            ),
            drop_rate_pct=value.drop_rate_pct,
            source_latency_boundary=RouteLatencyBoundary(value.source_latency_boundary),
            source_latency_unit=RouteLatencyUnit(value.source_latency_unit),
        )


@dataclass(frozen=True, slots=True)
class SourceMetrics:
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
    runtime_event_queue: EventQueueMetrics
    ingress_queue_capacity_frames: int
    ingress_queue_depth_frames: int
    ingress_queue_peak_frames: int
    ingress_frames_enqueued_total: int
    ingress_frames_delivered_total: int
    ingress_frames_rejected_full_total: int
    ingress_frames_rejected_cancelled_total: int
    ingress_frames_discarded_total: int

    @classmethod
    def _from_native(cls, value: _NativeSessionSourceMetrics) -> SourceMetrics:
        return cls(
            stem_id=value.stem_id,
            callback_buffers_total=value.callback_buffers_total,
            capture_frames_enqueued_total=value.capture_frames_enqueued_total,
            capture_pool_exhausted_total=value.capture_pool_exhausted_total,
            capture_dispatch_queue_full_total=value.capture_dispatch_queue_full_total,
            capture_invalid_buffer_total=value.capture_invalid_buffer_total,
            capture_oversized_buffer_total=value.capture_oversized_buffer_total,
            capture_stream_errors_total=value.capture_stream_errors_total,
            capture_timestamp_epoch_clamps_total=value.capture_timestamp_epoch_clamps_total,
            frame_stream_delivered_frames_total=value.frame_stream_delivered_frames_total,
            frame_stream_dropped_newest_frames_total=value.frame_stream_dropped_newest_frames_total,
            frames_discarded_before_start_total=value.frames_discarded_before_start_total,
            runtime_event_queue=EventQueueMetrics(
                capacity_count=value.runtime_event_capacity_count,
                maximum_event_owned_bytes=value.runtime_event_maximum_event_owned_bytes,
                maximum_buffered_owned_bytes=value.runtime_event_maximum_buffered_owned_bytes,
                depth_count=value.runtime_event_depth_count,
                depth_owned_bytes=value.runtime_event_depth_owned_bytes,
                peak_depth_count=0,
                peak_depth_owned_bytes=value.runtime_event_peak_depth_owned_bytes,
                enqueued_total=value.runtime_events_enqueued_total,
                dropped_total=value.runtime_events_dropped_total,
                dropped_oversized_total=value.runtime_events_dropped_oversized_total,
                receiver_closed_total=0,
            ),
            ingress_queue_capacity_frames=value.ingress_queue_capacity_frames,
            ingress_queue_depth_frames=value.ingress_queue_depth_frames,
            ingress_queue_peak_frames=value.ingress_queue_peak_frames,
            ingress_frames_enqueued_total=value.ingress_frames_enqueued_total,
            ingress_frames_delivered_total=value.ingress_frames_delivered_total,
            ingress_frames_rejected_full_total=value.ingress_frames_rejected_full_total,
            ingress_frames_rejected_cancelled_total=value.ingress_frames_rejected_cancelled_total,
            ingress_frames_discarded_total=value.ingress_frames_discarded_total,
        )


@dataclass(frozen=True, slots=True)
class ExternalSourceMetrics:
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

    @classmethod
    def _from_native(cls, value: _NativeExternalSourceMetrics) -> ExternalSourceMetrics:
        return cls(**{name: getattr(value, name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True, slots=True)
class TypedEdgeMetrics:
    capacity_signals: int
    max_payload_bytes: int
    maximum_buffered_payload_bytes: int
    depth_signals: int
    peak_depth_signals: int
    enqueued_total: int
    received_total: int
    dropped_total: int

    @classmethod
    def _from_native(cls, value: _NativeTypedEdgeMetrics) -> TypedEdgeMetrics:
        return cls(**{name: getattr(value, name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True, slots=True)
class OperatorWorkerMetrics:
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

    @classmethod
    def _from_native(cls, value: _NativeOperatorWorkerMetrics) -> OperatorWorkerMetrics:
        return cls(**{name: getattr(value, name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True, slots=True)
class OperatorInputMetrics:
    port_name: str
    edge: EdgeMetrics

    @classmethod
    def _from_native(cls, value: _NativeOperatorInputMetrics) -> OperatorInputMetrics:
        return cls(port_name=value.port_name, edge=EdgeMetrics._from_native(value.edge))


@dataclass(frozen=True, slots=True)
class OperatorMetrics:
    operator_instance_id: int
    input_edge: EdgeMetrics
    worker: OperatorWorkerMetrics
    finalization_failures_total: int
    input_ports: tuple[OperatorInputMetrics, ...]

    @classmethod
    def _from_native(cls, value: _NativeOperatorMetrics) -> OperatorMetrics:
        return cls(
            operator_instance_id=value.operator_instance_id,
            input_edge=EdgeMetrics._from_native(value.input_edge),
            worker=OperatorWorkerMetrics._from_native(value.worker),
            finalization_failures_total=value.finalization_failures_total,
            input_ports=tuple(
                OperatorInputMetrics._from_native(port) for port in value.input_ports()
            ),
        )


@dataclass(frozen=True, slots=True)
class DerivedRouteMetrics:
    route_id: int
    endpoint_id: int
    output: TypedEdgeMetrics
    endpoint: EndpointMetrics

    @classmethod
    def _from_native(cls, value: _NativeDerivedRouteMetrics) -> DerivedRouteMetrics:
        return cls(
            route_id=value.route_id,
            endpoint_id=value.endpoint_id,
            output=TypedEdgeMetrics._from_native(value.output),
            endpoint=EndpointMetrics(
                observation_stage=EndpointObservationStage(
                    value.endpoint_observation_stage
                ),
                frames_received_total=value.endpoint_frames_received_total,
                frames_delivered_total=value.endpoint_frames_delivered_total,
                frames_dropped_total=value.endpoint_frames_dropped_total,
                discontinuities_total=value.endpoint_discontinuities_total,
                failures_total=value.endpoint_failures_total,
                finalization_failures_total=value.endpoint_finalization_failures_total,
            ),
        )


@dataclass(frozen=True, slots=True)
class AudioReentryMetrics:
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

    @classmethod
    def _from_native(cls, value: _NativeAudioReentryMetrics) -> AudioReentryMetrics:
        return cls(**{name: getattr(value, name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True, slots=True)
class SessionMetrics:
    event_queue: EventQueueMetrics
    polled_audio: PolledAudioMetrics
    sources: tuple[SourceMetrics, ...]
    external_sources: tuple[ExternalSourceMetrics, ...]
    routes: tuple[RouteMetrics, ...]
    operators: tuple[OperatorMetrics, ...]
    derived_routes: tuple[DerivedRouteMetrics, ...]
    audio_reentries: tuple[AudioReentryMetrics, ...]

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def route_count(self) -> int:
        return len(self.routes)

    @property
    def audio_queue_capacity_frames(self) -> int:
        return self.polled_audio.queue_capacity_frames

    @property
    def audio_queue_full_drops_total(self) -> int:
        return self.polled_audio.queue_full_drops_total

    @classmethod
    def _from_native(cls, value: _NativeSessionMetrics) -> SessionMetrics:
        result = cls(
            event_queue=EventQueueMetrics(
                capacity_count=value.event_capacity_count,
                maximum_event_owned_bytes=value.event_maximum_event_owned_bytes,
                maximum_buffered_owned_bytes=value.event_maximum_buffered_owned_bytes,
                depth_count=value.event_depth_count,
                depth_owned_bytes=value.event_depth_owned_bytes,
                peak_depth_count=value.event_peak_depth_count,
                peak_depth_owned_bytes=value.event_peak_depth_owned_bytes,
                enqueued_total=value.events_enqueued_total,
                dropped_total=value.events_dropped_total,
                dropped_oversized_total=value.events_dropped_oversized_total,
                receiver_closed_total=value.event_receiver_closed_total,
            ),
            polled_audio=PolledAudioMetrics(
                registered_endpoints=value.audio_registered_endpoints,
                queue_capacity_frames=value.audio_queue_capacity_frames,
                queue_depth_frames=value.audio_queue_depth_frames,
                queue_peak_frames=value.audio_queue_peak_frames,
                queue_depth_invariant_failures_total=value.audio_queue_depth_invariant_failures_total,
                frames_received_total=value.audio_frames_received_total,
                frames_delivered_total=value.audio_frames_delivered_total,
                queue_full_drops_total=value.audio_queue_full_drops_total,
                invalid_ownership_drops_total=value.audio_invalid_ownership_drops_total,
                lease_capacity_count=value.audio_lease_capacity_count,
                outstanding_leases=value.audio_outstanding_leases,
                lease_exhausted_total=value.audio_lease_exhausted_total,
                batches_polled_total=value.audio_batches_polled_total,
                frames_polled_total=value.audio_frames_polled_total,
            ),
            sources=tuple(SourceMetrics._from_native(item) for item in value.sources),
            external_sources=tuple(
                ExternalSourceMetrics._from_native(item)
                for item in value.external_sources
            ),
            routes=tuple(RouteMetrics._from_native(item) for item in value.routes),
            operators=tuple(
                OperatorMetrics._from_native(item) for item in value.operators
            ),
            derived_routes=tuple(
                DerivedRouteMetrics._from_native(item) for item in value.derived_routes
            ),
            audio_reentries=tuple(
                AudioReentryMetrics._from_native(item) for item in value.audio_reentries
            ),
        )
        expected = (
            value.source_count,
            value.external_source_count,
            value.route_count,
            value.operator_count,
            value.derived_route_count,
            value.audio_reentry_count,
        )
        actual = (
            len(result.sources),
            len(result.external_sources),
            len(result.routes),
            len(result.operators),
            len(result.derived_routes),
            len(result.audio_reentries),
        )
        if actual != expected:
            raise PocketStationError(
                "native Session metrics counts are inconsistent",
                "session.invalid_metrics_snapshot",
            )
        return result


@dataclass(frozen=True, slots=True)
class RecordingDiscontinuity:
    stem_id: int
    label: str
    kind: RecordingDiscontinuityKind
    timestamp_start_ns: int
    timestamp_end_ns: int
    sequence_start: int | None
    sequence_end: int | None

    @classmethod
    def _from_native(
        cls, value: _NativeRecordingDiscontinuity
    ) -> RecordingDiscontinuity:
        return cls(
            stem_id=value.stem_id,
            label=value.label,
            kind=RecordingDiscontinuityKind(value.kind),
            timestamp_start_ns=value.timestamp_start_ns,
            timestamp_end_ns=value.timestamp_end_ns,
            sequence_start=value.sequence_start,
            sequence_end=value.sequence_end,
        )


@dataclass(frozen=True, slots=True)
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
    discontinuities: tuple[RecordingDiscontinuity, ...]

    @classmethod
    def _from_native(cls, value: _NativeRecordingStemOutcome) -> RecordingStemOutcome:
        return cls(
            stem_name=value.stem_name,
            frames_written_total=value.frames_written_total,
            stale_frames_total=value.stale_frames_total,
            error=value.error,
            queue_capacity_frames=value.queue_capacity_frames,
            queue_peak_frames=value.queue_peak_frames,
            frames_delivered_total=value.frames_delivered_total,
            frames_dropped_total=value.frames_dropped_total,
            queue_full_drops_total=value.queue_full_drops_total,
            discontinuities_total=value.discontinuities_total,
            discontinuities=tuple(
                RecordingDiscontinuity._from_native(record)
                for record in value.discontinuities()
            ),
        )


@dataclass(frozen=True, slots=True)
class RecordingOutcome:
    state: RecordingState
    completed_stems: int
    failed_stems: int
    session_directory: Path
    error_code: str | None
    stems: tuple[RecordingStemOutcome, ...]

    @property
    def complete(self) -> bool:
        return self.state is RecordingState.COMPLETE

    @classmethod
    def _from_native(cls, value: _NativeRecordingOutcome) -> RecordingOutcome:
        result = cls(
            state=RecordingState(value.state),
            completed_stems=value.completed_stems,
            failed_stems=value.failed_stems,
            session_directory=Path(value.session_directory),
            error_code=value.error_code,
            stems=tuple(
                RecordingStemOutcome._from_native(stem) for stem in value.stems()
            ),
        )
        if result.complete != value.complete:
            raise PocketStationError(
                "native recording terminal state is inconsistent",
                "recording.invalid_outcome",
            )
        return result


@dataclass(frozen=True, slots=True)
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

    @classmethod
    def _from_native(cls, value: _NativeRelayPublishOutcome) -> RelayPublishOutcome:
        return cls(**{name: getattr(value, name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True, slots=True)
class SessionTraceConfiguration:
    """Finite native trace configuration attached when the Session starts."""

    path: Path
    capacity_records: int = 256

    def __init__(self, path: str | Path, capacity_records: int = 256) -> None:
        if (
            isinstance(capacity_records, bool)
            or not isinstance(capacity_records, int)
            or capacity_records <= 0
        ):
            raise ValueError("capacity_records must be a positive integer")
        object.__setattr__(self, "path", Path(path))
        object.__setattr__(self, "capacity_records", capacity_records)


@dataclass(frozen=True, slots=True)
class SessionTraceRecorderOutcome:
    path: Path
    records_attempted_total: int
    records_enqueued_total: int
    records_dropped_total: int
    records_written_total: int
    rolling_hash: int
    complete: bool

    @classmethod
    def _from_native(
        cls, value: _NativeTraceRecorderOutcome
    ) -> SessionTraceRecorderOutcome:
        return cls(
            path=Path(value.path),
            records_attempted_total=value.records_attempted_total,
            records_enqueued_total=value.records_enqueued_total,
            records_dropped_total=value.records_dropped_total,
            records_written_total=value.records_written_total,
            rolling_hash=value.rolling_hash,
            complete=value.complete,
        )


@dataclass(frozen=True, slots=True)
class SessionTraceValidation:
    session_id: int
    lifecycle: tuple[SessionLifecycleState, ...]
    terminal_state: SessionTerminalState
    source_failures_total: int
    endpoint_failures_total: int
    rollback_failures_total: int
    finalization_failures_total: int
    records_validated_total: int

    @classmethod
    def _from_native(cls, value: _NativeTraceValidation) -> SessionTraceValidation:
        return cls(
            session_id=value.session_id,
            lifecycle=tuple(SessionLifecycleState(state) for state in value.lifecycle),
            terminal_state=SessionTerminalState(value.terminal_state),
            source_failures_total=value.source_failures_total,
            endpoint_failures_total=value.endpoint_failures_total,
            rollback_failures_total=value.rollback_failures_total,
            finalization_failures_total=value.finalization_failures_total,
            records_validated_total=value.records_validated_total,
        )


class SessionTrace:
    """Validated reader for one finite native Session trace artifact."""

    def __init__(self, native: _NativeSessionTrace) -> None:
        self._native = native

    @classmethod
    def read(cls, path: str | Path) -> SessionTrace:
        return cls(_native_call(lambda: _NativeSessionTrace.read(Path(path))))

    @property
    def session_id(self) -> int:
        return self._native.session_id

    @property
    def records_total(self) -> int:
        return self._native.records_total

    @property
    def outcome(self) -> SessionTraceRecorderOutcome:
        return SessionTraceRecorderOutcome._from_native(self._native.outcome)

    def validate(self) -> SessionTraceValidation:
        return SessionTraceValidation._from_native(_native_call(self._native.validate))


@dataclass(frozen=True, slots=True)
class StopResult:
    success: bool
    already_stopped: bool
    disposition: TerminationDisposition
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
    relay_outcomes: tuple[RelayPublishOutcome, ...]
    sidecar_outcomes: tuple[SidecarSnapshot, ...]

    @classmethod
    def _from_native(cls, value: _NativeStopResult) -> StopResult:
        return cls(
            success=value.success,
            already_stopped=value.already_stopped,
            disposition=TerminationDisposition(value.disposition),
            runtime_worker_panicked=value.runtime_worker_panicked,
            capture_finalization_failures_total=value.capture_finalization_failures_total,
            operator_finalization_failures_total=value.operator_finalization_failures_total,
            endpoint_finalization_failures_total=value.endpoint_finalization_failures_total,
            runtime_failures_total=value.runtime_failures_total,
            lineage_failures_total=value.lineage_failures_total,
            source_send_rejections_total=value.source_send_rejections_total,
            runtime_events_total=value.runtime_events_total,
            recording=(
                None
                if value.recording is None
                else RecordingOutcome._from_native(value.recording)
            ),
            trace=(
                None
                if value.trace is None
                else SessionTraceRecorderOutcome._from_native(value.trace)
            ),
            trace_error=value.trace_error,
            terminal_event=(
                None
                if value.terminal_event is None
                else SessionEvent._from_native(value.terminal_event)
            ),
            relay_outcomes=tuple(
                RelayPublishOutcome._from_native(outcome)
                for outcome in value.relay_outcomes()
            ),
            sidecar_outcomes=tuple(
                SidecarSnapshot._from_native(outcome)
                for outcome in value.sidecar_outcomes()
            ),
        )


class EventStream:
    """Exclusive bounded view of authoritative native Session events.

    Iteration waits in the native worker while the GIL is released. It creates
    no Python queue, polling thread, or unbounded event buffer.
    """

    def __init__(
        self,
        *,
        poll_event: Callable[[], SessionEvent | None],
        wait_event: Callable[[int], SessionEvent | None],
        is_closed: Callable[[], bool],
    ) -> None:
        self._poll_event = poll_event
        self._wait_event = wait_event
        self._is_closed = is_closed
        self._state = _ReaderState()

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._is_closed()

    def poll(self) -> SessionEvent | None:
        token = self._state.claim("event_read")
        try:
            return None if self.is_closed else self._poll_event()
        finally:
            self._state.release(token)

    def read(self, *, timeout_s: float = 1.0) -> SessionEvent | None:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("event_read")
        try:
            return None if self.is_closed else self._wait_event(timeout_ms)
        finally:
            self._state.release(token)

    def __iter__(self) -> Iterator[SessionEvent]:
        return self.iter_events()

    def iter_events(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> Iterator[SessionEvent]:
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        def iterate() -> Iterator[SessionEvent]:
            token = self._state.claim("events")
            try:
                while not self.is_closed:
                    event = self._wait_event(timeout_ms)
                    if event is not None:
                        yield event
            finally:
                self._state.release(token)

        return iterate()


__all__ = [
    "AudioReentryMetrics",
    "DerivedRouteMetrics",
    "EdgeMetrics",
    "EndpointFailureRetryability",
    "EndpointFailureStage",
    "EndpointMetrics",
    "EndpointObservationStage",
    "EventQueueMetrics",
    "EventStream",
    "ExternalSourceMetrics",
    "LatencyHistogram",
    "OperatorInputMetrics",
    "OperatorMetrics",
    "OperatorWorkerMetrics",
    "PolledAudioMetrics",
    "RecordingDiscontinuity",
    "RecordingDiscontinuityKind",
    "RecordingOutcome",
    "RecordingState",
    "RecordingStemOutcome",
    "RelayPublishOutcome",
    "RouteLatencyBoundary",
    "RouteLatencyUnit",
    "RouteMetrics",
    "RouteObservationInterval",
    "SessionEvent",
    "SessionEventType",
    "SessionFailure",
    "SessionFailureKind",
    "SessionFinalizationStage",
    "SessionLifecycleState",
    "SessionMetrics",
    "SessionRollbackStage",
    "SessionTerminalState",
    "SessionTrace",
    "SessionTraceConfiguration",
    "SessionTraceRecorderOutcome",
    "SessionTraceValidation",
    "SourceMetrics",
    "StopResult",
    "TerminationDisposition",
    "TypedEdgeMetrics",
]
