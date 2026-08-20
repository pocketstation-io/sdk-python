"""Synchronous public Session contract tests."""

from __future__ import annotations

from array import array

import pytest
from pocketstation import (
    PocketStationError,
    Session,
    SessionLifecycleState,
    Source,
    _native,
)


def test_given_app_and_mic_when_routed_then_native_session_owns_routes(tmp_path):
    session = Session(recording_root=tmp_path)
    application = session.capture(Source.application("PocketStation Fixture"))
    microphone = session.capture(Source.microphone_default())
    audio = session.polled_audio()

    application_route = application.send(audio)
    microphone_route = microphone.send(audio)
    application.record("application")
    microphone.record("microphone")

    assert application.id != microphone.id
    assert application_route != microphone_route


@pytest.mark.parametrize("name", ["", " ", "\t"])
def test_given_empty_application_name_when_declared_then_rejected(name):
    with pytest.raises(PocketStationError, match="must not be empty") as failure:
        Source.application(name)
    assert failure.value.code == "session.invalid_selector"


def test_given_selector_family_when_declared_then_each_shape_is_available():
    assert Source.application_bundle_id("com.spotify.client")
    assert Source.application_process_id(42)
    assert Source.application_stable_id("macos", "bundle:com.spotify.client")
    assert Source.application_process_instance(
        42,
        "macos",
        "bundle:com.spotify.client",
    )
    assert Source.microphone_id("device-42")
    assert Source.system_mix()


def test_given_invalid_process_or_platform_when_declared_then_rejected():
    with pytest.raises(PocketStationError, match="non-zero"):
        Source.application_process_id(0)
    with pytest.raises(PocketStationError, match="platform must be"):
        Source.application_stable_id("plan9", "app:42")


def test_given_session_after_start_attempt_when_reused_then_rejected():
    session = Session()

    with pytest.raises(PocketStationError):
        session.start()

    with pytest.raises(PocketStationError, match="already started") as failure:
        session.capture(Source.microphone_default())
    assert failure.value.code == "session.draft_frozen"


def test_running_session_projects_native_lifecycle_state() -> None:
    session = Session()
    audio = session.audio_input("owned", frame_samples_per_channel=4)
    audio.output.send(session.polled_audio())

    running = session.start()
    assert running.state is SessionLifecycleState.RUNNING
    assert not running.is_stopped
    audio.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    assert running.stop().success
    assert running.state is SessionLifecycleState.STOPPED
    assert running.is_stopped


def test_system_mix_runs_through_the_canonical_capture_backend(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    session = Session._from_native(_native.Session.conformance(tmp_path, None, 256))
    system_mix = session.capture(Source.system_mix())
    system_mix.send(session.polled_audio())

    running = session.start()
    frame = running.audio.read(timeout_s=1.0)
    stop = running.stop()

    assert frame is not None
    assert frame.stem_id == system_mix.id
    assert stop.success
