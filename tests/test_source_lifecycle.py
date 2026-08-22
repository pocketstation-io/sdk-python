from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    Platform,
    RunningSession,
    Session,
    Source,
    SourceFailureClass,
    SourceKind,
    SourceRecoveryRequirement,
    SourceRuntimeEvent,
    SourceRuntimeEventKind,
)
from pocketstation.observations import SessionEvent


def _native_source_event():
    source = dict(
        source_event_kind="source-unavailable",
        source_platform="windows",
        source_kind="application",
        source_stable_key="aumid:fixture",
        source_source_id=42,
        source_generation=7,
        source_recovery_requirement="explicit-rediscovery-and-new-session",
        source_failure_operation="capture",
        source_failure_class="platform-status",
        source_platform_status_code=-42,
        source_backend_class=None,
    )
    failure = SimpleNamespace(
        kind="source",
        stage=None,
        operation=None,
        error_class=None,
        component=None,
        message=None,
        stem_id=3,
        route_id=None,
        endpoint_id=None,
        operator_instance_id=None,
        sidecar_id=None,
        **source,
    )
    return SimpleNamespace(
        kind="source_failure",
        lifecycle_state=None,
        terminal_state=None,
        session_id=9,
        stem_id=3,
        endpoint_id=None,
        route_id=None,
        failures_total=1,
        failures=lambda: [failure],
        **source,
    )


def test_source_disappearance_is_a_typed_immutable_session_event() -> None:
    event = SessionEvent._from_native(_native_source_event())

    assert isinstance(event.source, SourceRuntimeEvent)
    assert event.source.kind is SourceRuntimeEventKind.SOURCE_UNAVAILABLE
    assert event.source.stable_id.platform is Platform.WINDOWS
    assert event.source.stable_id.kind is SourceKind.APPLICATION
    assert event.source.stable_id.source_id == 42
    assert event.source.generation == 7
    assert (
        event.source.recovery_requirement
        is SourceRecoveryRequirement.EXPLICIT_REDISCOVERY_AND_NEW_SESSION
    )
    assert event.source.failure_class is SourceFailureClass.PLATFORM_STATUS
    assert event.source.platform_status_code == -42
    with pytest.raises(FrozenInstanceError):
        event.source.generation = 8


def test_non_source_session_event_has_no_fabricated_source_payload() -> None:
    native = _native_source_event()
    native.kind = "lifecycle"
    native.lifecycle_state = "running"
    native.source_event_kind = None
    native.failures_total = 0
    native.failures = lambda: []

    event = SessionEvent._from_native(native)

    assert event.lifecycle_state == "running"
    assert event.source is None


def test_application_and_microphone_lower_through_canonical_session_path(
    tmp_path,
) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    native = _native.Session.conformance(tmp_path)
    session = Session._from_native(native)
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)

    with session.start() as running:
        assert isinstance(running, RunningSession)
        observed_stems = set()
        while len(observed_stems) < 2:
            frame = running.audio.read(timeout_s=1.0)
            assert frame is not None
            observed_stems.add(frame.stem_id)

    assert len(observed_stems) == 2
