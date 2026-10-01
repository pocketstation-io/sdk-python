"""Lean artifacts keep capture usable and report the absent processor."""

from array import array

import pytest
from pocketstation import AudioFrame, Session
from pocketstation.aec import PlaybackReference, aec_available
from pocketstation.errors import SessionDeclarationError


def test_given_native_build_when_queried_then_availability_is_boolean() -> None:
    assert isinstance(aec_available(), bool)


@pytest.mark.skipif(aec_available(), reason="requires default lean artifact")
def test_given_lean_build_when_aec_is_requested_then_raw_audio_still_arrives() -> None:
    session = Session(frame_duration_ms=10)
    application = session.audio_input("application")
    reference = PlaybackReference.selected_application(application.output)
    with pytest.raises(SessionDeclarationError, match="AEC is unavailable"):
        session.echo_cancel(application.output, reference)
    application.output.send(session.polled_audio())
    with session.start() as running:
        application.try_write(array("f", [0.125]) * 480)
        frame = running.audio.read(timeout_s=1.0)
        assert isinstance(frame, AudioFrame)
        assert list(frame.samples.cast("f")) == [0.125] * 480
