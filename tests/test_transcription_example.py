from __future__ import annotations

import asyncio
import json
import os
import sys
from array import array
from dataclasses import dataclass
from pathlib import Path

import pocketstation.aio as pks_aio
import pytest

from examples.transcription import (
    FasterWhisper,
    FasterWhisperConfiguration,
    WhisperCpp,
    WhisperCppConfiguration,
)


def test_whisper_example_declares_a_bounded_source_aware_operator(
    tmp_path: Path,
) -> None:
    executable = tmp_path / "whisper-cli"
    model = tmp_path / "model.bin"
    executable.touch()
    model.touch()
    configuration = WhisperCppConfiguration(
        executable=executable,
        model=model,
        window_seconds=2,
        process_timeout_s=10,
        queue_capacity_signals=128,
    )
    whisper = WhisperCpp(configuration)

    assert whisper.manifest.inputs[0].name == "audio"
    assert whisper.manifest.inputs[0].signal.is_audio
    assert whisper.manifest.outputs[0].name == "transcript"
    assert whisper.manifest.outputs[0].signal.role == "transcript.final"
    assert whisper.manifest.queue_capacity_signals == 128
    assert whisper.manifest.filesystem_allowed


def test_faster_whisper_can_forbid_model_downloads() -> None:
    transcription = FasterWhisper(
        FasterWhisperConfiguration(
            model="/opt/models/whisper-base-ct2",
            allow_model_download=False,
        ),
        model_factory=lambda _configuration: _Model(),
    )

    assert not transcription.manifest.network_allowed
    assert transcription.manifest.filesystem_allowed


@dataclass(frozen=True)
class _Segment:
    start: float = 0.0
    end: float = 0.1
    text: str = " pocket station"


@dataclass(frozen=True)
class _Info:
    language: str = "en"
    language_probability: float = 0.99


class _Model:
    def transcribe(self, audio, *, beam_size, language, vad_filter):
        assert len(audio) == 4_800
        assert beam_size == 1
        assert language == "en"
        assert vad_filter
        return iter((_Segment(),)), _Info()


@pytest.mark.asyncio
async def test_faster_whisper_is_the_concise_source_aware_python_path() -> None:
    transcription = FasterWhisper(
        FasterWhisperConfiguration(
            model="tiny.en",
            language="en",
            beam_size=1,
            window_seconds=0.1,
        ),
        model_factory=lambda _configuration: _Model(),
        _audio_converter=lambda window: list(window.samples),
    )
    session = pks_aio.Session()
    audio = session.audio_input(
        "remote-call",
        frame_samples_per_channel=480,
    )
    transcripts = transcription.attach(session, audio.output)

    running = await session.start()
    try:
        for _ in range(10):
            await audio.write(array("f", [0.0] * 480))
            await asyncio.sleep(0.001)
        envelope = await asyncio.wait_for(
            anext(running.signals(transcripts).__aiter__()),
            timeout=5.0,
        )
    finally:
        stop = await running.stop()
    transcript = json.loads(str(envelope.payload))
    assert transcript["source_id"] == audio.source_id
    assert transcript["stream_id"] == audio.stream_id
    assert transcript["text"] == "pocket station"
    assert stop.success


@pytest.mark.asyncio
async def test_real_whisper_process_preserves_source_identity(tmp_path: Path) -> None:
    executable_value = os.environ.get("POCKETSTATION_WHISPER_CLI")
    model_value = os.environ.get("POCKETSTATION_WHISPER_MODEL")
    wav_value = os.environ.get("POCKETSTATION_WHISPER_WAV")
    if not executable_value or not model_value or not wav_value:
        pytest.skip("real whisper paths were not supplied")

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "examples.transcription.run",
        "--whisper-cli",
        executable_value,
        "--model",
        model_value,
        "--wav",
        wav_value,
        "--record-to",
        str(tmp_path / "recordings"),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
    assert process.returncode == 0, stderr.decode(errors="replace")
    transcript = json.loads(stdout)
    assert transcript["source_id"] > 0
    assert transcript["stream_id"] > 0
    assert transcript["sequence_start"] == 0
    assert transcript["sequence_end"] >= transcript["sequence_start"]
    assert transcript["discontinuity_epoch"] == 0
    assert "pocket station" in transcript["text"].lower()
    stems = list((tmp_path / "recordings").glob("session-*/stems/*.wav"))
    assert len(stems) == 1
