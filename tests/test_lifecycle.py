"""Stop, cancel, and bounded diagnostic trace lifecycle tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pocketstation import (
    EndpointFailureStage,
    Session,
    SessionEvent,
    SessionFailureKind,
    SessionTerminalState,
    SessionTrace,
    SessionTraceConfiguration,
    Source,
    TerminationDisposition,
    _native,
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

    declared = Session()
    assert declared.id > 0

    assert stopped.success
    assert stopped.disposition is TerminationDisposition.STOPPED
    assert cancelled.success
    assert cancelled.disposition is TerminationDisposition.CANCELLED
    assert not stopped.runtime_worker_panicked
    assert not cancelled.runtime_worker_panicked
    assert stopped.terminal_event is not None
    assert stopped.terminal_event.terminal_state is SessionTerminalState.STOPPED
    assert cancelled.terminal_event is not None
    assert cancelled.terminal_event.terminal_state is SessionTerminalState.STOPPED
    assert stopped.terminal_event.failures == ()
    assert cancelled.terminal_event.failures == ()


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


def test_trace_configuration_rejects_unbounded_or_zero_capacity(tmp_path) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        SessionTraceConfiguration(tmp_path / "trace", capacity_records=0)
    with pytest.raises(ValueError, match="positive integer"):
        SessionTraceConfiguration(tmp_path / "trace", capacity_records=1.5)  # type: ignore[arg-type]


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
