"""Run the real Python → Rust connector → relay path for aggregate E2E."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from array import array
from pathlib import Path
from time import sleep
from typing import Any

import pocketstation as pks


def emit(message_type: str, **fields: Any) -> None:
    print(json.dumps({"type": message_type, **fields}, sort_keys=True), flush=True)


def _tone(frequency_hz: float, *, sample_count: int = 480) -> array[float]:
    return array(
        "f",
        (
            0.2 * math.sin(2.0 * math.pi * frequency_hz * index / 48_000)
            for index in range(sample_count)
        ),
    )


def _write_application_inputs(
    application: pks.AudioInput,
    microphone: pks.AudioInput,
    *,
    active_seconds: float,
) -> None:
    """Feed two finite Core inputs at their declared 10 ms cadence."""
    application_frame = _tone(440.0)
    microphone_frame = _tone(660.0)
    frame_count = max(1, math.ceil(active_seconds / 0.01))
    for _ in range(frame_count):
        application.write(application_frame)
        microphone.write(microphone_frame)
        sleep(0.01)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-plane-url", required=True)
    parser.add_argument("--relay-url", required=True)
    parser.add_argument("--recording-root", type=Path, required=True)
    parser.add_argument("--active-seconds", type=float, default=2.0)
    application_selector = parser.add_mutually_exclusive_group()
    application_selector.add_argument("--application-name")
    application_selector.add_argument("--application-process-id", type=int)
    arguments = parser.parse_args()
    if arguments.active_seconds <= 0:
        parser.error("--active-seconds must be positive")
    use_application_audio_inputs = (
        os.environ.get("PKS_E2E_APPLICATION_AUDIO_INPUT", "") == "1"
    )
    if (
        arguments.application_name is None
        and arguments.application_process_id is None
        and not use_application_audio_inputs
        and not hasattr(pks._native.Session, "conformance")
    ):
        emit("failure", code="relay.conformance_fixture_unavailable")
        return 2

    remote: pks.RelaySession | None = None
    running: pks.RunningSession | None = None
    try:
        remote = pks.RelaySession.create(
            control_plane_url=arguments.control_plane_url,
            relay_url=arguments.relay_url,
        )
        application_audio: pks.AudioInput | None = None
        microphone_audio: pks.AudioInput | None = None
        application: pks.Stem | pks.SourceOutput
        microphone: pks.Stem | pks.SourceOutput
        if use_application_audio_inputs:
            if (
                arguments.application_name is not None
                or arguments.application_process_id is not None
            ):
                raise RuntimeError(
                    "application-owned PCM fixture cannot be combined with "
                    "physical capture"
                )
            session = pks.Session(recording_root=arguments.recording_root)
            application_audio = session.audio_input("application")
            microphone_audio = session.audio_input("microphone")
            application = application_audio.output
            microphone = microphone_audio.output
            source_mode = "conformance-fixture"
            input_mode = "application-audio-input"
        elif (
            arguments.application_name is None
            and arguments.application_process_id is None
        ):
            session = pks.Session._from_native(
                pks._native.Session.conformance(arguments.recording_root)
            )
            application_source = pks.Source.application("PocketStation Python Fixture")
            source_mode = "conformance-fixture"
            input_mode = "capture-source"
        elif arguments.application_process_id is not None:
            session = pks.Session(recording_root=arguments.recording_root)
            application_source = pks.Source.application_process_id(
                arguments.application_process_id
            )
            source_mode = "physical"
            input_mode = "capture-source"
        else:
            assert arguments.application_name is not None
            matches = tuple(
                source
                for source in pks.discover_sources()
                if source.name == arguments.application_name
                and source.stable_id.kind is pks.SourceKind.APPLICATION
            )
            if len(matches) != 1:
                raise RuntimeError(
                    "expected one application named "
                    f"{arguments.application_name!r}, found {len(matches)}"
                )
            session = pks.Session(recording_root=arguments.recording_root)
            application_source = pks.Source.from_discovered(matches[0])
            source_mode = "physical"
            input_mode = "capture-source"
        if not use_application_audio_inputs:
            application = session.capture(application_source)
            microphone = session.capture(pks.Source.microphone_default())
        publisher = session.relay(remote)
        routes = (
            application.publish(publisher, "application"),
            microphone.publish(publisher, "microphone"),
        )
        application.record("application")
        microphone.record("microphone")

        running = session.start()
        if application_audio is not None and microphone_audio is not None:
            # Relay declares publication readiness only after every named bus
            # has produced RTP. Prime a finite 100 ms per bus before waiting
            # for the invitation; one 10 ms PCM frame is not enough to form
            # the configured Opus packet. The remaining feed starts after the
            # browser is attached so its delivery is observable.
            application_frame = _tone(440.0)
            microphone_frame = _tone(660.0)
            for index in range(10):
                discontinuity = index == 0
                application_audio.write(
                    application_frame,
                    discontinuity=discontinuity,
                )
                microphone_audio.write(
                    microphone_frame,
                    discontinuity=discontinuity,
                )
                sleep(0.01)
        invitation = remote.wait_for_publisher_and_invitation(
            timeout_seconds=15.0,
            poll_interval_seconds=0.05,
        )
        emit(
            "invitation",
            session_id=str(remote.session_id),
            join_code=invitation.join_code,
            join_url=invitation.join_url,
            buses=[route.bus_id for route in routes],
            route_ids=[route.route_id for route in routes],
            source_mode=source_mode,
            input_mode=input_mode,
        )

        receiver = remote.wait_for_receiver(
            timeout_seconds=20.0,
            poll_interval_seconds=0.05,
        )
        emit(
            "receiver-active",
            session_id=str(remote.session_id),
            source_active=receiver.snapshot.source_active,
            subscription_count=receiver.snapshot.subscription_count,
        )
        if application_audio is not None and microphone_audio is not None:
            _write_application_inputs(
                application_audio,
                microphone_audio,
                active_seconds=arguments.active_seconds,
            )
        else:
            sleep(arguments.active_seconds)

        stop = running.stop()
        running = None
        recording = stop.recording
        relay_outcome_values = stop.relay_outcomes
        relay_outcomes = [
            {
                "bus_id": outcome.bus_id,
                "frames_received_total": outcome.frames_received_total,
                "rtp_packets_sent_total": outcome.rtp_packets_sent_total,
                "rtp_payload_bytes_sent_total": outcome.rtp_payload_bytes_sent_total,
                "ingress_queue_drops_total": outcome.ingress_queue_drops_total,
                "publisher_stale_drops_total": outcome.publisher_stale_drops_total,
                "failures_total": outcome.failures_total,
                "error": outcome.error,
            }
            for outcome in relay_outcome_values
        ]
        recording_stem_values = () if recording is None else recording.stems
        recording_stems = (
            []
            if recording is None
            else [
                {
                    "stem_name": stem.stem_name,
                    "frames_written_total": stem.frames_written_total,
                    "frames_dropped_total": stem.frames_dropped_total,
                    "discontinuities_total": stem.discontinuities_total,
                    "error": stem.error,
                }
                for stem in recording_stem_values
            ]
        )
        expected_buses = {"application", "microphone"}
        success = (
            stop.success
            and recording is not None
            and recording.complete
            and {stem.stem_name for stem in recording_stem_values} == expected_buses
            and all(stem.frames_written_total > 0 for stem in recording_stem_values)
            and {outcome.bus_id for outcome in relay_outcome_values} == expected_buses
            and all(
                outcome.frames_received_total > 0
                and outcome.rtp_packets_sent_total > 0
                and outcome.failures_total == 0
                and outcome.error is None
                for outcome in relay_outcome_values
            )
        )
        remote.close()
        remote = None
        emit(
            "final",
            success=success,
            recording_complete=recording is not None and recording.complete,
            recording_stems=recording_stems,
            relay_outcomes=relay_outcomes,
        )
        return 0 if success else 3
    except BaseException as error:
        emit(
            "failure",
            error_type=type(error).__name__,
            code=getattr(error, "code", "relay.e2e_failure"),
        )
        return 1
    finally:
        if running is not None:
            try:
                running.cancel()
            except BaseException:
                pass
        if remote is not None:
            try:
                remote.close()
            except BaseException:
                pass


if __name__ == "__main__":
    sys.exit(main())
