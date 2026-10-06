"""Installed native reader over normal Session PCM ingress, not a device mock."""

from __future__ import annotations

import asyncio
import json
import struct
from array import array
from dataclasses import replace
from pathlib import Path

import pytest
from pocketstation import RecordedAudio, RecordingClipWindow, Session
from pocketstation.aio.recording import RecordedAudio as AsyncRecordedAudio
from pocketstation.identity import RuntimeSessionId, StemId
from pocketstation.observations import RecordingState
from pocketstation.recording import RecordingClipError


def pcm(wav: bytes) -> tuple[float, ...]:
    """Decode the generated WAV data chunk for independent bit/sample assertions."""
    assert wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"
    offset = 12
    while offset + 8 <= len(wav):
        tag, size = struct.unpack_from("<4sI", wav, offset)
        offset += 8
        if tag == b"data":
            return struct.unpack_from(f"<{size // 4}f", wav, offset)
        offset += size + size % 2
    raise AssertionError("no data chunk")


@pytest.fixture
def recorded(tmp_path: Path):
    session = Session(recording_root=tmp_path, channels=2, frame_duration_ms=20)
    application = session.audio_input("application", capacity_frames=16)
    microphone = session.audio_input("microphone", capacity_frames=16)
    application.output.record("application")
    microphone.output.record("microphone")
    running = session.start()
    try:
        for index in range(8):
            samples = array("f")
            for frame in range(960):
                value = (index * 960 + frame) / 10000
                samples.extend((value, -value))
            application.write(samples, timeout_s=1.0)
            microphone.write(array("f", [0.125] * 1920), timeout_s=1.0)
        application.close()
        microphone.close()
    finally:
        stop = running.stop()
    assert stop.success and stop.recording is not None
    assert stop.recording.complete
    assert all(stem.frames_written_total == 8 for stem in stop.recording.stems)
    assert all(stem.frames_dropped_total == 0 for stem in stop.recording.stems)
    reader = RecordedAudio.open(stop.recording.session_directory, running.session_id)
    return reader, stop.recording, application.source_id


def test_clip_keeps_exact_stereo_samples_and_source_identity(recorded) -> None:
    reader, outcome, source_id = recorded
    stems = {stem.label: stem for stem in reader.stems}
    assert set(stems) == {"application", "microphone"}
    stem = stems["application"]
    assert stem.source_id == source_id
    assert stem.session_id == outcome.session_id
    assert (stem.sample_rate_hz, stem.channels) == (48000, 2)
    origin = stem.first_timestamp_ns
    window = RecordingClipWindow.around(
        origin + 60_000_000, origin + 100_000_000, 20_000_000, 20_000_000
    )
    clip = reader.read_clip(stem.stem_id, window)
    assert (clip.first_sample_frame, clip.sample_frames) == (1920, 3840)
    assert pcm(clip.wav)[:4] == tuple(array("f", [0.192, -0.192, 0.1921, -0.1921]))
    assert pcm(clip.wav)[-2:] == tuple(array("f", [0.5759, -0.5759]))
    assert clip.discontinuities == ()
    assert outcome.read_clip(stem.stem_id, window).wav == clip.wav
    mic = stems["microphone"]
    assert set(
        pcm(
            reader.read_clip(
                mic.stem_id,
                RecordingClipWindow(mic.first_timestamp_ns, mic.final_timestamp_ns),
            ).wav
        )
    ) == {0.125}


def test_sample_rounding_and_explicit_recording_bounds(recorded) -> None:
    reader, _, _ = recorded
    stem = reader.stems[0]
    origin = stem.first_timestamp_ns
    clip = reader.read_clip(
        stem.stem_id, RecordingClipWindow(origin + 20834, origin + 41665)
    )
    assert (clip.first_sample_frame, clip.sample_frames) == (1, 1)
    assert (clip.actual.start_ns, clip.actual.end_ns) == (
        origin + 20833,
        origin + 41666,
    )
    clipped = reader.read_clip(
        stem.stem_id, RecordingClipWindow(0, stem.final_timestamp_ns + 1_000_000_000)
    )
    assert clipped.actual.start_ns == origin and clipped.sample_frames == 7680
    with pytest.raises(RecordingClipError) as failure:
        reader.read_clip(
            stem.stem_id,
            RecordingClipWindow(
                stem.final_timestamp_ns + 1, stem.final_timestamp_ns + 2
            ),
        )
    assert failure.value.code == "recording.clip_no_audio"


@pytest.mark.parametrize(
    "start,end", [(0, 0), (3, 2), (-1, 1), (True, 1), (0, 120_000_000_001), (0, 2**64)]
)
def test_window_failures_have_core_error_codes(start, end) -> None:
    with pytest.raises(RecordingClipError) as failure:
        RecordingClipWindow(start, end)
    assert failure.value.code == "recording.clip_invalid_window"


def test_u64_windows_and_explicit_context_are_lossless() -> None:
    origin = 2**53 + 17
    window = RecordingClipWindow.around(origin, origin + 100, 3, 5)
    assert (window.start_ns, window.end_ns) == (origin - 3, origin + 105)
    assert RecordingClipWindow.around(2, 4, 9, 0).start_ns == 0
    with pytest.raises(RecordingClipError):
        RecordingClipWindow.around(2**64 - 3, 2**64 - 1, 0, 9)


def test_wrong_owner_unknown_stem_and_incomplete_receipt_fail_closed(recorded) -> None:
    reader, outcome, _ = recorded
    with pytest.raises(RecordingClipError) as wrong:
        RecordedAudio.open(
            outcome.session_directory, RuntimeSessionId(outcome.session_id + 1)
        )
    assert wrong.value.code == "recording.clip_invalid_recording"
    stem = reader.stems[0]
    window = RecordingClipWindow(stem.first_timestamp_ns, stem.final_timestamp_ns)
    with pytest.raises(RecordingClipError) as unknown:
        reader.read_clip(StemId(2**64 - 1), window)
    assert unknown.value.code == "recording.clip_unknown_stem"
    with pytest.raises(RecordingClipError) as incomplete:
        replace(outcome, state=RecordingState.INCOMPLETE).read_clip(
            stem.stem_id, window
        )
    assert incomplete.value.code == "recording.clip_invalid_recording"


@pytest.mark.parametrize("changed", ["manifest", "wav"])
def test_modified_recording_never_returns_success(recorded, changed: str) -> None:
    reader, outcome, _ = recorded
    stem = reader.stems[0]
    if changed == "manifest":
        outcome.manifest_path.write_bytes(outcome.manifest_path.read_bytes() + b" ")
    else:
        wav = outcome.session_directory / "stems" / f"{stem.label}.wav"
        data = bytearray(wav.read_bytes())
        data[-1] ^= 1
        wav.write_bytes(data)
    with pytest.raises(RecordingClipError) as failure:
        reader.read_clip(
            stem.stem_id,
            RecordingClipWindow(stem.first_timestamp_ns, stem.final_timestamp_ns),
        )
    assert failure.value.code.startswith("recording.clip_")


def test_async_reader_uses_the_same_core_bytes_without_blocking_loop(recorded) -> None:
    sync, outcome, _ = recorded
    stem = sync.stems[0]
    window = RecordingClipWindow(stem.first_timestamp_ns, stem.final_timestamp_ns)

    async def run():
        reader = await AsyncRecordedAudio.open(
            outcome.session_directory, outcome.session_id
        )
        ticks = 0

        async def heartbeat():
            nonlocal ticks
            for _ in range(20):
                await asyncio.sleep(0)
                ticks += 1

        results, _ = await asyncio.gather(
            asyncio.gather(*(reader.read_clip(stem.stem_id, window) for _ in range(4))),
            heartbeat(),
        )
        assert ticks == 20
        assert all(
            clip.wav == sync.read_clip(stem.stem_id, window).wav for clip in results
        )

    asyncio.run(run())


def test_manifest_large_integer_projection_is_exact(recorded) -> None:
    """Serialized integer fixture over real WAVs; not physical-clock evidence."""
    _, outcome, _ = recorded
    manifest = json.loads(outcome.manifest_path.read_text())
    high = 2**53 + 17
    manifest["session_id"] = high
    for stem in manifest["stems"]:
        stem["session_id"] = high
        stem["source_id"] += high
        stem["stem_id"] += high
        stem["permission_epoch"] = high
        stem["first_timestamp_ns"] += high
        stem["final_timestamp_ns"] += high
    outcome.manifest_path.write_text(json.dumps(manifest))
    reader = RecordedAudio.open(outcome.session_directory, RuntimeSessionId(high))
    stem = reader.stems[0]
    assert stem.session_id == high and stem.permission_epoch == high
    assert stem.source_id > high and stem.stem_id > high
    clip = reader.read_clip(
        stem.stem_id,
        RecordingClipWindow(
            stem.first_timestamp_ns + 1, stem.first_timestamp_ns + 20_000_000
        ),
    )
    assert clip.stem == stem and clip.actual.start_ns == stem.first_timestamp_ns
