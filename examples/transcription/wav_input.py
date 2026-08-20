"""Finite PCM WAV input for executable transcription examples."""

from __future__ import annotations

import asyncio
import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

import pocketstation.aio as pks_aio


@dataclass(frozen=True, slots=True)
class WavInput:
    sample_rate_hz: int
    channels: int
    source_frames: int
    samples: array[float]

    @property
    def duration_s(self) -> float:
        return self.source_frames / self.sample_rate_hz

    @property
    def frame_samples_per_channel(self) -> int:
        return max(1, self.sample_rate_hz // 50)


def read_pcm16_wav(path: Path) -> WavInput:
    with wave.open(str(path), "rb") as source:
        if source.getsampwidth() != 2:
            raise ValueError("input WAV must contain 16-bit PCM")
        sample_rate_hz = source.getframerate()
        channels = source.getnchannels()
        source_frames = source.getnframes()
        pcm = array("h")
        pcm.frombytes(source.readframes(source_frames))
    return WavInput(
        sample_rate_hz=sample_rate_hz,
        channels=channels,
        source_frames=source_frames,
        samples=array("f", (value / 32_768 for value in pcm)),
    )


async def feed_live(
    audio: pks_aio.AudioInput,
    source: WavInput,
    *,
    timeout_s: float = 2.0,
    pacing_ratio: float = 0.1,
) -> None:
    frame_values = source.frame_samples_per_channel * source.channels
    for offset in range(0, len(source.samples), frame_values):
        frame = source.samples[offset : offset + frame_values]
        if len(frame) < frame_values:
            frame.extend([0.0] * (frame_values - len(frame)))
        await audio.write(frame, timeout_s=timeout_s)
        await asyncio.sleep(
            source.frame_samples_per_channel / source.sample_rate_hz * pacing_ratio
        )
    await audio.close()


__all__ = ["WavInput", "feed_live", "read_pcm16_wav"]
