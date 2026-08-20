"""Run source-aware faster-whisper transcription from an installed SDK."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import pocketstation
import pocketstation.aio as pks_aio

from examples.transcription.faster_whisper import (
    FasterWhisper,
    FasterWhisperConfiguration,
)
from examples.transcription.wav_input import feed_live, read_pcm16_wav


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="base")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--compute-type", default="default")
    parser.add_argument("--language")
    parser.add_argument("--wav", type=Path, required=True)
    parser.add_argument("--record-to", type=Path, required=True)
    return parser.parse_args()


async def main() -> None:
    arguments = _arguments()
    result = await transcribe_wav(
        model=arguments.model,
        device=arguments.device,
        compute_type=arguments.compute_type,
        language=arguments.language,
        wav=arguments.wav,
        record_to=arguments.record_to,
    )
    print(json.dumps(result, indent=2))


async def transcribe_wav(
    *,
    model: str,
    device: str,
    compute_type: str,
    language: str | None,
    wav: Path,
    record_to: Path,
) -> dict[str, object]:
    """Transcribe one WAV through the public Session and Python model API."""
    source = read_pcm16_wav(wav)
    session = pks_aio.Session(
        recording_root=record_to,
        sample_rate_hz=source.sample_rate_hz,
        channels=source.channels,
    )
    audio = session.audio_input(
        "application-owned-speech",
        capacity_frames=32,
        frame_samples_per_channel=source.frame_samples_per_channel,
    )
    transcriber = FasterWhisper(
        FasterWhisperConfiguration(
            model=model,
            device=device,
            compute_type=compute_type,
            language=language,
            window_seconds=min(30, max(0.1, source.duration_s)),
        )
    )
    transcripts = transcriber.attach(session, audio.output)
    audio.output.record("application-owned-speech")

    running = await session.start()
    try:
        await feed_live(audio, source)
        envelope = await asyncio.wait_for(
            anext(running.signals(transcripts).__aiter__()),
            timeout=transcriber.configuration.inference_timeout_s,
        )
        if not isinstance(envelope, pocketstation.SignalEnvelope):
            raise RuntimeError("transcription ended without a transcript")
        transcript = json.loads(str(envelope.payload))
    finally:
        outcome = await running.stop()
    if not outcome.success:
        raise RuntimeError(outcome)
    if not isinstance(transcript, dict):
        raise RuntimeError("transcription result must be a JSON object")
    return transcript


if __name__ == "__main__":
    asyncio.run(main())
