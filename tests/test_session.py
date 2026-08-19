"""Synchronous public Session contract tests."""

from __future__ import annotations

import pytest

from pocketstation import PocketStationError, Session, Source


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
