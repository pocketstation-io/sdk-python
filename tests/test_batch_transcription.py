from __future__ import annotations

import asyncio
import json
import os
from array import array
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

import pocketstation._api as pocketstation
import pocketstation.aio as pks_aio
import pytest
from pocketstation_examples import FasterWhisper, FasterWhisperConfiguration

from tests.transcription.run_source_aware import transcribe_sources
from tests.transcription.wav_input import read_pcm16_wav


@dataclass(frozen=True)
class _Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class _Info:
    language: str = "en"
    language_probability: float = 1.0


class _SourceModel:
    calls: int = 0

    def transcribe(self, audio, *, beam_size, language, vad_filter):
        self.calls += 1
        text = "application source" if sum(audio) > 0 else "microphone source"
        return iter((_Segment(0.0, 0.1, text),)), _Info()


@pytest.mark.asyncio
async def test_one_bounded_model_preserves_two_source_identities(
    tmp_path: Path,
) -> None:
    model = _SourceModel()
    model_creations = 0

    def create_model(_configuration: FasterWhisperConfiguration) -> _SourceModel:
        nonlocal model_creations
        model_creations += 1
        return model

    transcriber = FasterWhisper(
        FasterWhisperConfiguration(
            model="test-model",
            allow_model_download=False,
            language="en",
            beam_size=1,
            window_seconds=0.1,
            maximum_sources=2,
        ),
        model_factory=create_model,
        _audio_converter=lambda window: list(window.samples),
    )
    assert (
        transcriber.manifest.inputs[0].multiplicity is pocketstation.Multiplicity.MANY
    )

    session = pks_aio.Session(recording_root=tmp_path)
    application = session.audio_input(
        "application", capacity_frames=16, frame_samples_per_channel=480
    )
    microphone = session.audio_input(
        "microphone", capacity_frames=16, frame_samples_per_channel=480
    )
    subscription = transcriber.attach_many(
        session,
        (application.output, microphone.output),
    )
    application.output.record("application")
    microphone.output.record("microphone")

    running = await session.start()
    try:
        for _ in range(10):
            await application.write(array("f", [0.1] * 480))
            await microphone.write(array("f", [-0.1] * 480))
            await asyncio.sleep(0.01)
        stream = running.signals(subscription)
        received: dict[int, dict[str, object]] = {}
        deadline = monotonic() + 5
        while len(received) < 2:
            if monotonic() >= deadline:
                raise TimeoutError("transcription did not emit both source identities")
            envelope = await stream.read(timeout_s=1)
            if envelope is None:
                continue
            if isinstance(envelope, pocketstation.EndOfStream):
                metrics = await running.metrics()
                terminal = await running.stop()
                raise RuntimeError(
                    "transcription ended before both sources; "
                    f"model_calls={model.calls}, sources={metrics.external_sources!r}, "
                    f"operators={metrics.operators!r}, terminal={terminal!r}"
                )
            assert isinstance(envelope, pocketstation.SignalEnvelope)
            value = json.loads(str(envelope.payload))
            received[int(value["source_id"])] = value
        await application.close()
        await microphone.close()
    finally:
        outcome = await running.stop()

    assert model_creations == 1
    assert model.calls == 2
    assert set(received) == {application.source_id, microphone.source_id}
    assert received[application.source_id]["text"] == "application source"
    assert received[microphone.source_id]["text"] == "microphone source"
    assert all(value["sequence_start"] == 0 for value in received.values())
    assert all(value["sequence_end"] == 9 for value in received.values())
    assert all(value["clock_id"] == 1 for value in received.values())
    assert outcome.success
    assert outcome.recording is not None and outcome.recording.complete


@pytest.mark.asyncio
async def test_real_faster_whisper_transcribes_two_upstream_fixtures(
    tmp_path: Path,
) -> None:
    model = os.environ.get("PKS_REAL_TRANSCRIPTION_MODEL")
    application_wav = os.environ.get("PKS_REAL_TRANSCRIPTION_APPLICATION_WAV")
    microphone_wav = os.environ.get("PKS_REAL_TRANSCRIPTION_MICROPHONE_WAV")
    if not model or not application_wav or not microphone_wav:
        pytest.skip("real model and source fixtures are supplied by the Lab gate")

    result = await transcribe_sources(
        application=read_pcm16_wav(Path(application_wav)),
        microphone=read_pcm16_wav(Path(microphone_wav)),
        record_to=tmp_path,
        model=model,
        model_revision=None,
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        window_seconds=2,
        timeout_s=60,
        allow_model_download=False,
    )

    assert result["recording_complete"] is True
    assert set(result["recording_stems"]) == {"application", "microphone"}
    assert result["application_source_id"] != result["microphone_source_id"]
    transcripts = result["transcripts"]
    assert isinstance(transcripts, dict)
    application = transcripts["application"]
    microphone = transcripts["microphone"]
    assert application["source_id"] == result["application_source_id"]
    assert microphone["source_id"] == result["microphone_source_id"]
    assert "country" in str(application["text"]).lower()
    assert str(microphone["text"]).strip()
    assert application["inference_duration_ns"] > 0
    assert microphone["inference_duration_ns"] > 0
