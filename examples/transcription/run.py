"""Run real source-aware whisper.cpp transcription from an installed SDK."""

from __future__ import annotations

import argparse
import asyncio
import json
import wave
from array import array
from pathlib import Path

import pocketstation
import pocketstation.aio as pks_aio

from examples.transcription.whisper_cpp import (
    TRANSCRIPT_SIGNAL,
    WhisperCpp,
    WhisperCppConfiguration,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--whisper-cli", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--wav", type=Path, required=True)
    parser.add_argument("--record-to", type=Path, required=True)
    return parser.parse_args()


async def main() -> None:
    arguments = _arguments()
    result = await transcribe_wav(
        whisper_cli=arguments.whisper_cli,
        model=arguments.model,
        wav=arguments.wav,
        record_to=arguments.record_to,
    )
    print(json.dumps(result, indent=2))


async def transcribe_wav(
    *,
    whisper_cli: Path,
    model: Path,
    wav: Path,
    record_to: Path,
) -> dict[str, object]:
    """Transcribe one real WAV through Session audio input and recording."""
    with wave.open(str(wav), "rb") as source:
        if source.getsampwidth() != 2:
            raise ValueError("input WAV must contain 16-bit PCM")
        sample_rate_hz = source.getframerate()
        channels = source.getnchannels()
        source_frames = source.getnframes()
        pcm = array("h")
        pcm.frombytes(source.readframes(source_frames))
    samples = array("f", (value / 32_768 for value in pcm))
    frame_samples_per_channel = max(1, sample_rate_hz // 50)
    frame_values = frame_samples_per_channel * channels
    duration_s = source_frames / sample_rate_hz

    session = pks_aio.Session(
        recording_root=record_to,
        sample_rate_hz=sample_rate_hz,
        channels=channels,
    )
    audio = session.audio_input(
        "application-owned-speech",
        capacity_frames=32,
        frame_samples_per_channel=frame_samples_per_channel,
    )
    whisper = WhisperCpp(
        WhisperCppConfiguration(
            executable=whisper_cli,
            model=model,
            window_seconds=min(30, max(0.1, duration_s)),
        )
    )
    operator = session.register_operator(whisper.provider()).declare()
    audio.output.connect(operator.input("audio"))
    audio.output.record("application-owned-speech")
    subscription = session.subscribe(
        operator.output("transcript"), signal=TRANSCRIPT_SIGNAL
    )

    running = await session.start()
    try:
        for offset in range(0, len(samples), frame_values):
            frame = samples[offset : offset + frame_values]
            if len(frame) < frame_values:
                frame.extend([0.0] * (frame_values - len(frame)))
            await audio.write(frame, timeout_s=2)
            # A file has no capture clock. Yield finite pacing so this proof
            # exercises normal live ingestion instead of artificial burst loss.
            await asyncio.sleep(frame_samples_per_channel / sample_rate_hz / 10)
        await audio.close()
        result = await asyncio.wait_for(
            anext(running.signals(subscription).__aiter__()),
            timeout=whisper.configuration.process_timeout_s,
        )
        if not isinstance(result, pocketstation.SignalEnvelope):
            raise RuntimeError("transcription ended without a transcript")
        transcript = json.loads(str(result.payload))
    finally:
        outcome = await running.stop()
    if not outcome.success:
        raise RuntimeError(outcome)
    if not isinstance(transcript, dict):
        raise RuntimeError("transcription result must be a JSON object")
    return transcript


if __name__ == "__main__":
    asyncio.run(main())
