"""Synchronous public Session contract tests."""

from __future__ import annotations

from array import array

import pytest
from pocketstation._api import (
    PocketStationError,
    Session,
    SessionLifecycleState,
    Source,
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


@pytest.mark.parametrize("frame_duration_ms", [10, 20])
def test_given_supported_frame_duration_when_session_declared_then_it_is_accepted(
    frame_duration_ms: int,
) -> None:
    assert Session(frame_duration_ms=frame_duration_ms)


def test_given_unsupported_frame_duration_when_declared_then_it_is_rejected() -> None:
    with pytest.raises(PocketStationError, match="must be 10 or 20") as failure:
        Session(frame_duration_ms=15)
    assert failure.value.code == "session.invalid_frame_duration"


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
    assert Source.system_audio()
    assert Source.microphone_id("device-42")


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
