"""Exercise built-in cancellation through the real installed native Session."""

from __future__ import annotations

import json
import math
import random
from array import array
from dataclasses import FrozenInstanceError
from pathlib import Path
from time import monotonic, sleep

import pytest
from pocketstation import AudioFrame, Session
from pocketstation.aec import (
    EchoCancellationState,
    PlaybackReference,
    aec_available,
)
from pocketstation.errors import PocketStationError
from pocketstation.signal import STREAM_EOF, AudioProcessing

pytestmark = pytest.mark.skipif(
    not aec_available(), reason="requires explicit AEC build"
)


@pytest.mark.parametrize(("duration_ms", "channels"), [(10, 1), (20, 1), (10, 2)])
def test_given_echo_when_native_session_runs_then_cancelled_and_raw_stems_arrive(
    duration_ms: int, channels: int
) -> None:
    session = Session(frame_duration_ms=duration_ms, channels=channels)
    reference = session.audio_input("playback")
    microphone = session.audio_input("microphone")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    assert cleaned.microphone is microphone.output
    assert cleaned.reference.input is reference.output
    assert cleaned.reference_coverage == "caller-rendered-audio"
    initial = cleaned.observations()
    assert initial.state is EchoCancellationState.WAITING_FOR_REFERENCE
    endpoint = session.polled_audio()
    reference.output.send(endpoint)
    cleaned.audio.send(endpoint)
    rng = random.Random(4917)
    samples = duration_ms * 48
    previous = array("f", [0.0]) * (samples * channels)
    input_power = output_power = 0.0
    with session.start() as running:
        for index in range(300):
            playback = array("f")
            for _ in range(samples):
                value = rng.uniform(-0.1, 0.1)
                playback.extend([value] if channels == 1 else [value, -value])
            mic = array("f")
            for offset in range(0, len(previous), channels):
                echo = previous[offset] * (0.6 if channels == 1 else 0.5)
                mic.extend([echo] * channels)
            # Source time remains ordered even when callback arrival alternates.
            if index % 2:
                microphone.try_write(mic)
                reference.try_write(playback)
            else:
                reference.try_write(playback)
                microphone.try_write(mic)
            delivered: set[str] = set()
            for _ in range(2):
                frame = running.audio.read(timeout_s=1.0)
                assert isinstance(frame, AudioFrame), (frame, cleaned.observations())
                values = frame.samples.cast("f")
                if frame.source_id == reference.source_id:
                    assert "raw" not in delivered
                    assert list(values) == list(playback)
                    assert frame.processing is None
                    delivered.add("raw")
                else:
                    assert "processed" not in delivered
                    assert frame.stem_id == cleaned.audio.id
                    assert len(values) == len(mic)
                    assert all(math.isfinite(value) for value in values)
                    metadata = frame.processing
                    assert isinstance(metadata, AudioProcessing)
                    assert metadata.input_source_id == microphone.source_id
                    assert metadata.input_stream_id == microphone.output.stream_id
                    assert frame.source_id != metadata.input_source_id
                    assert not metadata.is_tail
                    assert metadata.padding_samples == 0
                    assert metadata.nominal_delay_samples == 432
                    delivered.add("processed")
                    if index >= 200:
                        output_power += sum(value * value for value in values)
            assert delivered == {"raw", "processed"}
            if index >= 200:
                input_power += sum(value * value for value in mic)
            previous = playback
        assert input_power > 1.0
        assert output_power < input_power * 0.5
        reference.close()
        microphone.close()
        assert running.stop().success
    observation = cleaned.observations()
    assert observation.processed_microphone_frames_total == 300
    assert observation.reference_source_id == reference.source_id
    assert observation.microphone_source_id == microphone.source_id
    assert observation.state is EchoCancellationState.STOPPED
    assert observation.last_error is None
    assert observation.maximum_processing_duration_ns > 0
    assert observation.output_frames_total == 300 + 40 // duration_ms
    assert observation.discarded_output_frames_total == 0
    assert observation.tail_frames_total == 40 // duration_ms
    assert observation.tail_padding_samples_total == 1920
    assert observation.discarded_tail_generations_total == 0
    assert observation.nominal_delay_samples == 432
    assert observation.drain_duration_ms == 40
    assert initial.processed_microphone_frames_total == 0
    with pytest.raises(FrozenInstanceError):
        observation.state = EchoCancellationState.FAILED  # type: ignore[misc]


def test_given_near_end_voice_when_reference_is_silent_then_voice_is_not_muted() -> (
    None
):
    session = Session(frame_duration_ms=10)
    reference = session.audio_input("playback")
    microphone = session.audio_input("voice")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.selected_application(reference.output)
    )
    assert cleaned.reference_coverage == "selected-application"
    cleaned.audio.send(session.polled_audio())
    input_power = output_power = 0.0
    with session.start() as running:
        for frame_index in range(100):
            voice = array(
                "f",
                (
                    0.2
                    * math.sin(2.0 * math.pi * 300 * (frame_index * 480 + i) / 48000)
                    for i in range(480)
                ),
            )
            reference.try_write(array("f", [0.0]) * 480)
            microphone.try_write(voice)
            frame = running.audio.read(timeout_s=1.0)
            assert isinstance(frame, AudioFrame), (frame, cleaned.observations())
            if frame_index >= 50:
                input_power += sum(value * value for value in voice)
                output_power += sum(value * value for value in frame.samples.cast("f"))
        reference.close()
        microphone.close()
        assert running.stop().success
    assert 0.5 < output_power / input_power < 2.0


def test_given_invalid_inputs_when_declaring_then_session_remains_usable() -> None:
    session = Session()
    other = Session()
    microphone = session.audio_input("voice")
    reference = session.audio_input("playback")
    foreign = other.audio_input("foreign")
    for selected in (microphone.output, foreign.output):
        with pytest.raises(PocketStationError, match="different"):
            session.echo_cancel(
                microphone.output, PlaybackReference.rendered_audio(selected)
            )
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.output_mix(reference.output)
    )
    assert cleaned.reference_coverage == "authorized-output-mix"
    cleaned.audio.send(session.polled_audio())
    microphone.close()
    reference.close()
    foreign.close()
    with session.start() as running:
        with pytest.raises(PocketStationError, match="started"):
            session.echo_cancel(
                microphone.output, PlaybackReference.rendered_audio(reference.output)
            )
        assert running.stop().success


def test_given_non_audio_when_selecting_reference_then_typed_error() -> None:
    with pytest.raises(TypeError, match="echo input"):
        PlaybackReference.rendered_audio(object())  # type: ignore[arg-type]


def test_given_app_only_when_session_runs_then_no_microphone_is_required() -> None:
    session = Session()
    app = session.audio_input("application")
    app.output.send(session.polled_audio())
    samples = array("f", [0.125]) * 960
    with session.start() as running:
        app.try_write(samples)
        frame = running.audio.read(timeout_s=1.0)
        assert isinstance(frame, AudioFrame)
        assert list(frame.samples.cast("f")) == list(samples)
        assert frame.processing is None
        app.close()
        assert running.stop().success


def test_given_absent_reference_when_queue_fills_then_failure_survives_stop() -> None:
    session = Session()
    microphone = session.audio_input("microphone")
    reference = session.audio_input("silent-reference")
    application = session.audio_input("independent-application")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    endpoint = session.polled_audio()
    cleaned.audio.send(endpoint)
    application.output.send(endpoint)
    capacity = cleaned.observations().queue_capacity_frames
    with session.start() as running:
        for index in range(capacity + 1):
            microphone.try_write(array("f", [0.1]) * 960)
            deadline = monotonic() + 2.0
            while True:
                observation = cleaned.observations()
                if (
                    observation.microphone_queue_depth_frames == index + 1
                    or observation.state is EchoCancellationState.FAILED
                ):
                    break
                assert monotonic() < deadline, observation
                sleep(0.001)
        failed = cleaned.observations()
        assert failed.state is EchoCancellationState.FAILED
        assert failed.last_error is not None
        assert failed.processed_microphone_frames_total == 0
        assert failed.microphone_queue_depth_frames <= capacity
        application.try_write(array("f", [0.25]) * 960)
        frame = running.audio.read(timeout_s=1.0)
        assert isinstance(frame, AudioFrame), (frame, cleaned.observations())
        assert frame.source_id == application.source_id
        assert list(frame.samples.cast("f")) == [0.25] * 960
        microphone.close()
        reference.close()
        application.close()
        assert not running.stop().success
    assert cleaned.observations().state is EchoCancellationState.FAILED
    assert cleaned.observations().last_error == failed.last_error


@pytest.mark.parametrize(
    ("duration_ms", "channels"), [(10, 1), (20, 1), (10, 2), (20, 2)]
)
def test_given_last_input_when_stopped_then_tail_retains_actual_input_provenance(
    tmp_path: Path, duration_ms: int, channels: int
) -> None:
    session = Session(
        frame_duration_ms=duration_ms, channels=channels, recording_root=tmp_path
    )
    reference = session.audio_input("playback")
    microphone = session.audio_input("microphone")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    endpoint = session.polled_audio()
    microphone.output.send(endpoint)
    cleaned.audio.send(endpoint)
    microphone.output.record("raw")
    cleaned.audio.record("processed")
    samples = duration_ms * 48
    voice = array("f", [0.0]) * (samples * channels)
    for channel in range(channels):
        voice[channel] = 0.35
        voice[(samples - 1) * channels + channel] = 0.25
    with session.start() as running:
        reference.try_write(array("f", [0.0]) * len(voice))
        microphone.try_write(voice)
        delivered = {}
        for _ in range(2):
            frame = running.audio.read(timeout_s=1.0)
            assert isinstance(frame, AudioFrame), cleaned.observations()
            delivered[frame.source_id] = frame
        raw = delivered[microphone.source_id]
        processed = next(
            frame
            for source_id, frame in delivered.items()
            if source_id != raw.source_id
        )
        metadata = processed.processing
        assert isinstance(metadata, AudioProcessing)
        assert raw.processing is None
        assert list(raw.samples.cast("f")) == list(voice)
        assert metadata.input_source_id == raw.source_id
        assert metadata.input_stream_id == raw.stream_id
        assert metadata.input_sequence_number == raw.sequence_number
        assert metadata.input_timestamp_ns == raw.timestamp_start_ns
        assert metadata.input_duration_ns == raw.duration_ns
        assert metadata.input_source_generation == raw.source_generation
        assert metadata.input_discontinuity_epoch == raw.discontinuity_epoch
        assert metadata.generation == cleaned.observations().processing_generation
        assert metadata.nominal_delay_samples == 432
        assert not metadata.is_tail
        assert metadata.tail_offset_samples == metadata.padding_samples == 0
        with pytest.raises(AttributeError):
            metadata.generation = 0  # type: ignore[misc]
        reference.close()
        microphone.close()
        assert running.stop().success
        assert running.audio.is_closed
        tails = []
        for _ in range(40 // duration_ms):
            tail = running.audio.read(timeout_s=1.0)
            assert isinstance(tail, AudioFrame), cleaned.observations()
            assert tail.processing is not None
            assert tail.processing.is_tail
            tails.append(tail)
        assert running.audio.read(timeout_s=0.0) is STREAM_EOF
        assert running.audio.read(timeout_s=0.0) is STREAM_EOF
    observations = cleaned.observations()
    tail_frames = 40 // duration_ms
    assert observations.output_frames_total == 1 + tail_frames
    assert observations.tail_frames_total == tail_frames
    assert observations.tail_padding_samples_total == 1920
    assert observations.processed_microphone_frames_total == 1
    assert observations.analyzed_reference_frames_total == 1
    assert observations.discarded_tail_generations_total == 0
    for index, tail in enumerate(tails):
        tail_metadata = tail.processing
        assert tail_metadata is not None
        assert tail_metadata.input_source_id == raw.source_id
        assert tail_metadata.input_sequence_number == raw.sequence_number
        assert tail_metadata.input_timestamp_ns == raw.timestamp_start_ns
        assert tail_metadata.generation == metadata.generation
        assert tail_metadata.padding_samples == samples
        assert tail_metadata.tail_offset_samples == index * samples
        assert tail.source_id == processed.source_id
        assert tail.sequence_number == processed.sequence_number + index + 1
        assert len(tail.samples.cast("f")) == samples * channels
    manifests = list(tmp_path.glob("*/events/processing-processed.jsonl"))
    assert len(manifests) == 1
    events = [json.loads(line) for line in manifests[0].read_text().splitlines()]
    assert len(events) == 1 + tail_frames
    assert not list(tmp_path.glob("*/events/processing-raw.jsonl"))
    for index, event in enumerate(events):
        assert event["input_source_id"] == raw.source_id
        assert event["input_sequence_number"] == raw.sequence_number
        assert event["input_timestamp_ns"] == raw.timestamp_start_ns
        assert event["generation"] == metadata.generation
        assert event["padding_samples"] == (samples if index else 0)
        assert event["tail_offset_samples"] == max(0, index - 1) * samples


def test_given_discontinuity_when_processing_resumes_then_generation_is_preserved() -> (
    None
):
    session = Session(frame_duration_ms=10)
    reference = session.audio_input("playback")
    microphone = session.audio_input("microphone")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    cleaned.audio.send(session.polled_audio())
    generations = []
    with session.start() as running:
        for index in range(12):
            reference.try_write(array("f", [0.0]) * 480, discontinuity=index == 10)
            microphone.try_write(array("f", [0.1]) * 480, discontinuity=index == 10)
            frame = running.audio.read(timeout_s=1.0)
            assert isinstance(frame, AudioFrame), cleaned.observations()
            assert frame.processing is not None
            generations.append(frame.processing.generation)
            assert frame.processing.input_discontinuity_epoch == (
                1 if index >= 10 else 0
            )
        assert generations[9] < generations[10] == generations[11]
        reference.close()
        microphone.close()
        assert running.stop().success
    observations = cleaned.observations()
    assert observations.processing_generation == generations[-1]
    assert observations.resets_total > 0
    assert observations.discarded_tail_generations_total > 0
