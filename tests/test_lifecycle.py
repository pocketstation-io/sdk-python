"""Stop, cancel, and bounded diagnostic trace lifecycle tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    EndpointFailureStage,
    Session,
    SessionComponentKind,
    SessionEvent,
    SessionFailureKind,
    SessionTerminalState,
    SessionTrace,
    SessionTraceConfiguration,
    SessionTraceRecordType,
    Source,
    TerminationDisposition,
)


def _running_conformance_session(tmp_path, *, trace_path=None):
    native = _native.Session.conformance(tmp_path, trace_path, 256)
    session = Session._from_native(native)
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    running = session.start()
    assert running.audio.read(timeout_s=1.0) is not None
    return running


def test_stop_and_cancel_have_distinct_typed_dispositions(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    stopped_running = _running_conformance_session(tmp_path / "stopped")
    cancelled_running = _running_conformance_session(tmp_path / "cancelled")
    assert stopped_running.session_id > 0
    assert cancelled_running.session_id > 0
    stopped = stopped_running.stop()
    cancelled = cancelled_running.cancel()
    stopped_events = tuple(stopped_running.events)
    cancelled_events = tuple(cancelled_running.events)

    declared = Session()
    assert declared.id > 0

    assert stopped.success
    assert stopped.disposition is TerminationDisposition.STOPPED
    assert cancelled.success
    assert cancelled.disposition is TerminationDisposition.CANCELLED
    assert stopped.session_state is SessionTerminalState.STOPPED
    assert cancelled.session_state is SessionTerminalState.STOPPED
    assert not stopped.runtime_worker_panicked
    assert not cancelled.runtime_worker_panicked
    assert stopped.terminal_event is not None
    assert stopped.terminal_event.terminal_state is SessionTerminalState.STOPPED
    assert cancelled.terminal_event is not None
    assert cancelled.terminal_event.terminal_state is SessionTerminalState.STOPPED
    assert stopped.terminal_event.failures == ()
    assert cancelled.terminal_event.failures == ()
    assert stopped.metrics is not None
    assert stopped.metrics_unavailable_reason is None
    assert stopped.metrics.event_queue.depth_count == 0
    assert cancelled.metrics is not None
    assert cancelled.metrics_unavailable_reason is None
    assert cancelled.metrics.event_queue.depth_count == 0
    assert stopped_events[-1] == stopped.terminal_event
    assert cancelled_events[-1] == cancelled.terminal_event
    assert stopped_running.events.is_closed
    assert cancelled_running.events.is_closed


def test_trace_round_trip_preserves_terminal_lifecycle_and_hash(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    trace_path = tmp_path / "session.trace"
    stop = _running_conformance_session(
        tmp_path / "recordings", trace_path=trace_path
    ).stop()

    assert stop.trace_error is None
    assert stop.trace is not None
    assert stop.trace.complete
    assert stop.trace.path == trace_path
    trace = SessionTrace.read(trace_path)
    validation = trace.validate()
    assert trace.session_id == validation.session_id
    assert trace.records_total == validation.records_validated_total
    assert trace.outcome.rolling_hash == stop.trace.rolling_hash
    assert validation.terminal_state is SessionTerminalState.STOPPED
    assert validation.source_failures_total == 0
    assert validation.endpoint_failures_total == 0
    assert len(trace.records) == trace.records_total
    assert trace.records[0].sequence_index == 0
    assert trace.records[0].type is SessionTraceRecordType.LIFECYCLE
    assert trace.records[-1].type is SessionTraceRecordType.TERMINAL
    assert trace.records[-1].terminal_state is SessionTerminalState.STOPPED


@pytest.mark.parametrize("path", ["", "   ", Path("\t")])
def test_trace_configuration_rejects_blank_path(path) -> None:
    with pytest.raises(ValueError, match="trace path cannot be empty"):
        SessionTraceConfiguration(path)


@pytest.mark.parametrize("capacity", [0, 1_000_001, True, 1.5])
def test_trace_configuration_rejects_capacity_outside_finite_bounds(
    tmp_path, capacity
) -> None:
    with pytest.raises(ValueError, match="integer between 1 and 1000000"):
        SessionTraceConfiguration(  # type: ignore[arg-type]
            tmp_path / "trace",
            capacity_records=capacity,
        )


@pytest.mark.parametrize("path", ["", "   ", Path("\t")])
def test_trace_reader_rejects_blank_path_before_native_io(path) -> None:
    with pytest.raises(ValueError, match="trace path cannot be empty"):
        SessionTrace.read(path)


def test_trace_configuration_accepts_capacity_bounds(tmp_path) -> None:
    assert (
        SessionTraceConfiguration(
            tmp_path / "lower.trace", capacity_records=1
        ).capacity_records
        == 1
    )
    assert (
        SessionTraceConfiguration(
            tmp_path / "upper.trace", capacity_records=1_000_000
        ).capacity_records
        == 1_000_000
    )


def test_terminal_event_keeps_fault_categories_and_owner_ids_separate() -> None:
    def failure(kind, stage, **identifiers):
        return SimpleNamespace(
            kind=kind,
            stage=stage,
            operation="finalize" if kind == "finalization" else None,
            error_class="fixture-failure",
            error_code="fixture.endpoint" if kind == "endpoint" else None,
            retryability="retryable" if kind == "endpoint" else None,
            component="Runtime" if kind == "finalization" else None,
            component_kind="runtime" if kind == "finalization" else None,
            message="endpoint failed" if kind == "endpoint" else None,
            stem_id=identifiers.get("stem_id"),
            route_id=identifiers.get("route_id"),
            endpoint_id=identifiers.get("endpoint_id"),
            operator_instance_id=None,
            sidecar_id=None,
            source_event_kind=None,
            source_platform=None,
            source_kind=None,
            source_stable_key=None,
            source_source_id=None,
            source_generation=None,
            source_recovery_requirement=None,
            source_failure_operation=None,
            source_failure_class=None,
            source_platform_status_code=None,
            source_backend_class=None,
        )

    failures = [
        failure("endpoint", "join-finalize", route_id=3, endpoint_id=4),
        failure("finalization", "finalize-endpoint"),
    ]
    event = SessionEvent._from_native(
        SimpleNamespace(
            kind="terminal",
            lifecycle_state="failed",
            terminal_state="failed",
            session_id=1,
            stem_id=None,
            route_id=None,
            endpoint_id=None,
            failures_total=2,
            failures=lambda: failures,
            source_event_kind=None,
        )
    )

    assert event.terminal_state is SessionTerminalState.FAILED
    assert event.failures[0].kind is SessionFailureKind.ENDPOINT
    assert event.failures[0].stage is EndpointFailureStage.JOIN_FINALIZE
    assert event.failures[0].route_id == 3
    assert event.failures[0].endpoint_id == 4
    assert event.failures[0].error_code == "fixture.endpoint"
    assert event.failures[0].retryability.value == "retryable"
    assert event.failures[1].kind is SessionFailureKind.FINALIZATION
    assert event.failures[1].component is not None
    assert event.failures[1].component.kind is SessionComponentKind.RUNTIME
    assert event.failures[1].component_diagnostic == "Runtime"
