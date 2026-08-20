from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

from examples.transcription import WhisperCpp, WhisperCppConfiguration


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
