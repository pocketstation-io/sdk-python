"""Run the real Python → Rust connector → relay path for aggregate E2E."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import threading
from array import array
from collections.abc import Iterator
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Any, cast

import pocketstation._api as pks
import pocketstation._native as native

if TYPE_CHECKING:
    from tests.transcription.wav_input import WavInput

SDK_ROOT = Path(__file__).resolve().parents[1]
if str(SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(SDK_ROOT))


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


def _wav_frames(source: WavInput) -> Iterator[array[float]]:
    frame_values = source.frame_samples_per_channel * source.channels
    for offset in range(0, len(source.samples), frame_values):
        frame = source.samples[offset : offset + frame_values]
        if len(frame) < frame_values:
            frame.extend([0.0] * (frame_values - len(frame)))
        yield frame


def _write_fixture_frames(
    application: pks.AudioInput,
    microphone: pks.AudioInput,
    application_frames: Iterator[array[float]],
    microphone_frames: Iterator[array[float]],
    *,
    frame_duration_s: float,
    maximum_frames: int | None = None,
) -> int:
    written = 0
    application_open = True
    microphone_open = True
    while application_open or microphone_open:
        application_frame = next(application_frames, None)
        microphone_frame = next(microphone_frames, None)
        application_open = application_frame is not None
        microphone_open = microphone_frame is not None
        if not application_open and not microphone_open:
            break
        if application_frame is not None:
            application.write(application_frame, discontinuity=written == 0)
        if microphone_frame is not None:
            microphone.write(microphone_frame, discontinuity=written == 0)
        written += 1
        sleep(frame_duration_s)
        if maximum_frames is not None and written >= maximum_frames:
            break
    return written


def _collect_transcripts(
    stream: pks.SignalStream[str],
    received: list[dict[str, object]],
    failures: list[BaseException],
) -> None:
    try:
        while True:
            envelope = stream.read(timeout_s=1.0)
            if envelope is None:
                continue
            if isinstance(envelope, pks.EndOfStream):
                return
            value = json.loads(str(envelope.payload))
            if not isinstance(value, dict):
                raise RuntimeError("transcript payload must be a JSON object")
            if value.get("text"):
                received.append(value)
    except BaseException as error:
        failures.append(error)


def main() -> int:
    from pocketstation_demo import (
        TRANSCRIPT_SIGNAL,
        FasterWhisper,
        FasterWhisperConfiguration,
    )

    from tests.transcription.wav_input import read_pcm16_wav

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
    transcription_model = os.environ.get("PKS_E2E_TRANSCRIPTION_MODEL")
    transcription_application_wav = os.environ.get(
        "PKS_E2E_TRANSCRIPTION_APPLICATION_WAV"
    )
    transcription_microphone_wav = os.environ.get(
        "PKS_E2E_TRANSCRIPTION_MICROPHONE_WAV"
    )
    transcription_values = (
        transcription_model,
        transcription_application_wav,
        transcription_microphone_wav,
    )
    if any(transcription_values) and not all(transcription_values):
        parser.error(
            "transcription E2E requires model, application WAV, and microphone WAV"
        )
    use_transcription = transcription_model is not None
    use_application_audio_inputs = (
        os.environ.get("PKS_E2E_APPLICATION_AUDIO_INPUT", "") == "1"
        or use_transcription
    )
    if (
        arguments.application_name is None
        and arguments.application_process_id is None
        and not use_application_audio_inputs
        and not hasattr(native.Session, "conformance")
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
        application_fixture: WavInput | None = None
        microphone_fixture: WavInput | None = None
        application_frames: Iterator[array[float]] | None = None
        microphone_frames: Iterator[array[float]] | None = None
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
            if use_transcription:
                assert transcription_application_wav is not None
                assert transcription_microphone_wav is not None
                application_fixture = read_pcm16_wav(
                    Path(transcription_application_wav)
                )
                microphone_fixture = read_pcm16_wav(Path(transcription_microphone_wav))
                application_contract = (
                    application_fixture.sample_rate_hz,
                    application_fixture.channels,
                    application_fixture.frame_samples_per_channel,
                )
                microphone_contract = (
                    microphone_fixture.sample_rate_hz,
                    microphone_fixture.channels,
                    microphone_fixture.frame_samples_per_channel,
                )
                if application_contract != microphone_contract:
                    raise RuntimeError(
                        "transcription fixtures must share one Session media contract"
                    )
                session = pks.Session(
                    recording_root=arguments.recording_root,
                    sample_rate_hz=application_fixture.sample_rate_hz,
                    channels=application_fixture.channels,
                )
                application_audio = session.audio_input(
                    "application",
                    capacity_frames=32,
                    frame_samples_per_channel=(
                        application_fixture.frame_samples_per_channel
                    ),
                )
                microphone_audio = session.audio_input(
                    "microphone",
                    capacity_frames=32,
                    frame_samples_per_channel=(
                        microphone_fixture.frame_samples_per_channel
                    ),
                )
                application_frames = _wav_frames(application_fixture)
                microphone_frames = _wav_frames(microphone_fixture)
            else:
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
                native.Session.conformance(arguments.recording_root)
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

        transcript_subscription: pks.BusSubscription[str] | None = None
        if use_transcription:
            assert transcription_model is not None
            transcription_window_seconds = float(
                os.environ.get("PKS_E2E_TRANSCRIPTION_WINDOW_SECONDS", "2")
            )
            transcription_queue_capacity = int(
                os.environ.get("PKS_E2E_TRANSCRIPTION_QUEUE_CAPACITY", "1024")
            )
            transcriber = FasterWhisper(
                FasterWhisperConfiguration(
                    model=transcription_model,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=4,
                    allow_model_download=False,
                    beam_size=1,
                    window_seconds=transcription_window_seconds,
                    queue_capacity_signals=transcription_queue_capacity,
                    maximum_sources=2,
                    create_timeout_s=60,
                    inference_timeout_s=60,
                )
            )
            operator = session.register_operator(transcriber.sync_provider()).declare()
            operator_input = operator.input("audio")
            application.connect(operator_input)
            microphone.connect(operator_input)
            transcript_subscription = session.subscribe(
                operator.output("transcript"),
                signal=TRANSCRIPT_SIGNAL,
            )

        running = session.start()
        transcript_values: list[dict[str, object]] = []
        transcript_failures: list[BaseException] = []
        transcript_thread: threading.Thread | None = None
        if transcript_subscription is not None:
            transcript_thread = threading.Thread(
                target=_collect_transcripts,
                args=(
                    running.signals(transcript_subscription),
                    transcript_values,
                    transcript_failures,
                ),
                name="pocketstation-transcript-consumer",
                daemon=False,
            )
            transcript_thread.start()
        if application_audio is not None and microphone_audio is not None:
            # Relay declares publication readiness only after every named bus
            # has produced RTP. Prime a finite 100 ms per bus before waiting
            # for the invitation; one 10 ms PCM frame is not enough to form
            # the configured Opus packet. The remaining feed starts after the
            # browser is attached so its delivery is observable.
            if application_frames is not None and microphone_frames is not None:
                assert application_fixture is not None
                _write_fixture_frames(
                    application_audio,
                    microphone_audio,
                    application_frames,
                    microphone_frames,
                    frame_duration_s=(
                        application_fixture.frame_samples_per_channel
                        / application_fixture.sample_rate_hz
                    ),
                    maximum_frames=10,
                )
            else:
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
            source_active=receiver.snapshot.ready,
            subscription_count=receiver.snapshot.subscription_count,
        )
        if application_audio is not None and microphone_audio is not None:
            if application_frames is not None and microphone_frames is not None:
                assert application_fixture is not None
                _write_fixture_frames(
                    application_audio,
                    microphone_audio,
                    application_frames,
                    microphone_frames,
                    frame_duration_s=(
                        application_fixture.frame_samples_per_channel
                        / application_fixture.sample_rate_hz
                    ),
                )
                application_audio.close()
                microphone_audio.close()
            else:
                _write_application_inputs(
                    application_audio,
                    microphone_audio,
                    active_seconds=arguments.active_seconds,
                )
        else:
            sleep(arguments.active_seconds)

        stop = running.stop()
        running = None
        if transcript_thread is not None:
            transcript_thread.join(timeout=5)
            if transcript_thread.is_alive():
                raise RuntimeError("transcript consumer did not stop")
            if transcript_failures:
                raise RuntimeError(
                    f"transcript consumer failed: {transcript_failures[0]}"
                )
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
                "cancelled_output_frames_total": outcome.cancelled_output_frames_total,
                "cancelled_output_samples_total": (
                    outcome.cancelled_output_samples_total
                ),
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
        transcript_source_ids = {
            cast(int, value["source_id"])
            for value in transcript_values
            if isinstance(value.get("source_id"), int) and value.get("text")
        }
        expected_transcript_source_ids = (
            set()
            if application_audio is None or microphone_audio is None
            else {
                int(application_audio.source_id),
                int(microphone_audio.source_id),
            }
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
            and (
                not use_transcription
                or transcript_source_ids == expected_transcript_source_ids
            )
        )
        if use_transcription:
            emit(
                "transcription",
                sources=sorted(transcript_source_ids),
                expected_sources=sorted(expected_transcript_source_ids),
                windows_total=len(transcript_values),
                transcripts=transcript_values,
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
            message=str(error),
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
