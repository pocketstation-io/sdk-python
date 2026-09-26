"""Strict static consumer for the installed PocketStation package."""

from __future__ import annotations

from array import array
from typing import assert_type

from pocketstation.audio_input import AudioInput
from pocketstation.graph import Endpoint
from pocketstation.identity import RouteId
from pocketstation.observations import StopResult
from pocketstation.session import RunningSession, Session
from pocketstation.streams import AudioReadResult, AudioStream


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
