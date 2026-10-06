"""Native device AEC is an explicit microphone request, independent of the engine."""

from __future__ import annotations

import pytest
from pocketstation import Session, Source
from pocketstation.aec import NativePlaybackReference, PlaybackReference, aec_available
from pocketstation.errors import PocketStationError


def test_exact_output_reference_rejects_invalid_ids() -> None:
    reference = NativePlaybackReference.output("render-device-42")
    assert reference.playback_device_id == "render-device-42"
    for invalid in ("", " ", "\t"):
        with pytest.raises(
            PocketStationError, match="playback device ID must not be empty"
        ):
            NativePlaybackReference.output(invalid)
    with pytest.raises(TypeError, match="must be a string"):
        NativePlaybackReference.output(42)  # type: ignore[arg-type]


def test_native_request_is_explicit_and_rejects_invalid_or_duplicate_microphones() -> (
    None
):
    session = Session()
    microphone = session.capture(Source.microphone_default())
    application = session.capture(Source.system_audio())
    foreign = Session().capture(Source.microphone_default())
    reference = NativePlaybackReference.output("render-device-42")

    with pytest.raises(TypeError, match="captured Stem"):
        session.native_aec(microphone.id, reference)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="NativePlaybackReference"):
        session.native_aec(microphone, "render-device-42")  # type: ignore[arg-type]
    with pytest.raises(PocketStationError):
        session.native_aec(application, reference)
    with pytest.raises(PocketStationError):
        session.native_aec(foreign, reference)

    assert session.native_aec(microphone, reference) is None
    with pytest.raises(PocketStationError):
        session.native_aec(microphone, reference)
    # A native request does not require the portable engine in a lean build.
    assert isinstance(aec_available(), bool)


def test_native_and_portable_requests_cannot_process_the_same_microphone_twice() -> (
    None
):
    if not aec_available():
        pytest.skip("portable AEC requires the explicitly enabled artifact")
    reference = NativePlaybackReference.output("render-device-42")
    first = Session()
    microphone = first.capture(Source.microphone_default())
    playback = first.capture(Source.system_audio())
    first.native_aec(microphone, reference)
    with pytest.raises(PocketStationError):
        first.echo_cancel(microphone, PlaybackReference.output_mix(playback))

    second = Session()
    microphone = second.capture(Source.microphone_default())
    playback = second.capture(Source.system_audio())
    second.echo_cancel(microphone, PlaybackReference.output_mix(playback))
    with pytest.raises(PocketStationError):
        second.native_aec(microphone, reference)


def test_async_session_uses_the_same_native_declaration() -> None:
    from pocketstation.aio import Session as AsyncSession

    session = AsyncSession()
    microphone = session.capture(Source.microphone_default())
    reference = NativePlaybackReference.output("render-device-42")
    assert session.native_aec(microphone, reference) is None
    with pytest.raises(PocketStationError):
        session.native_aec(microphone, reference)
