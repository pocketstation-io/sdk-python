"""Strict static consumer for the installed PocketStation package."""

from __future__ import annotations

from array import array
from typing import assert_type

from pocketstation.aec import EchoCancellationObservations, PlaybackReference
from pocketstation.audio_input import AudioInput
from pocketstation.graph import Endpoint, Stem
from pocketstation.identity import RouteId
from pocketstation.observations import StopResult
from pocketstation.session import RunningSession, Session
from pocketstation.signal import AudioProcessing
from pocketstation.streams import AudioFrame, AudioReadResult, AudioStream


def verify_installed_session() -> None:
    session = Session(frame_duration_ms=10)
    source = session.audio_input(
        "installed-typing",
        capacity_frames=2,
        frame_samples_per_channel=480,
    )
    destination = session.polled_audio()
    route_id = source.output.send(destination)
    running = session.start()
    source.write(array("f", [0.0]) * 480)
    frame = running.audio.read(timeout_s=1.0)
    result = running.stop()

    assert_type(source, AudioInput)
    assert_type(destination, Endpoint)
    assert_type(route_id, RouteId)
    assert_type(running, RunningSession)
    assert_type(running.audio, AudioStream)
    assert_type(frame, AudioReadResult)
    assert_type(result, StopResult)
    if isinstance(frame, AudioFrame):
        assert_type(frame.processing, AudioProcessing | None)


def verify_installed_echo() -> None:
    session = Session(frame_duration_ms=10)
    microphone = session.audio_input("microphone")
    playback = session.audio_input("playback")
    reference = PlaybackReference.rendered_audio(playback.output)
    cleaned = session.echo_cancel(microphone.output, reference)
    assert_type(cleaned.audio, Stem)
    assert_type(cleaned.reference, PlaybackReference)
    assert_type(cleaned.observations(), EchoCancellationObservations)
