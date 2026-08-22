from __future__ import annotations

import asyncio
import json
from array import array
from dataclasses import dataclass

import pocketstation.aio as pks_aio
import pytest
from pocketstation_examples import (
    FasterWhisper,
    FasterWhisperConfiguration,
)


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
