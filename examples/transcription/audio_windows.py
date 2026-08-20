"""Finite source-aware PCM windows shared by transcription examples."""

from __future__ import annotations

import sys
from array import array
from dataclasses import dataclass, field

import pocketstation


@dataclass(slots=True)
class AudioWindow:
    sample_rate_hz: int
    channel_count: int
    source_id: int
    stream_id: int
    sequence_start: int
    sequence_end: int
    discontinuity_epoch: int
    samples: array[float] = field(default_factory=lambda: array("f"))

    @property
    def duration_ms(self) -> int:
        return round(
            len(self.samples) * 1_000 / (self.sample_rate_hz * self.channel_count)
        )


class AudioWindowBuffer:
    """Bounded per-source accumulator that splits on format discontinuity."""

    def __init__(self, *, window_seconds: float, maximum_sources: int) -> None:
        self._window_seconds = window_seconds
        self._maximum_sources = maximum_sources
        self._windows: dict[tuple[int, int], AudioWindow] = {}

    def push(
        self,
        envelope: pocketstation.SignalEnvelope[object],
    ) -> tuple[AudioWindow, ...]:
        payload = envelope.payload
        if not isinstance(payload, pocketstation.SignalAudioPayload):
            raise TypeError("transcription accepts only PCM audio signals")
        lineage = envelope.lineage
        if lineage is None:
            raise ValueError("transcription requires source-aware audio lineage")

        key = (payload.source_id, payload.stream_id)
        window = self._windows.get(key)
        incompatible = window is not None and (
            window.sample_rate_hz != payload.sample_rate_hz
            or window.channel_count != payload.channel_count
            or window.discontinuity_epoch != lineage.discontinuity_epoch
        )
        completed: list[AudioWindow] = []
        if incompatible and window is not None:
            if window.samples:
                completed.append(window)
            del self._windows[key]
            window = None
        if window is None:
            if len(self._windows) >= self._maximum_sources:
                raise RuntimeError("maximum concurrent transcription sources exceeded")
            window = AudioWindow(
                sample_rate_hz=payload.sample_rate_hz,
                channel_count=payload.channel_count,
                source_id=payload.source_id,
                stream_id=payload.stream_id,
                sequence_start=payload.sequence_number,
                sequence_end=payload.sequence_number,
                discontinuity_epoch=lineage.discontinuity_epoch,
            )
            self._windows[key] = window

        samples = array("f")
        samples.frombytes(payload.samples_f32le)
        if sys.byteorder != "little":
            samples.byteswap()
        if len(samples) != payload.sample_count:
            raise ValueError("audio payload size does not match sample_count")
        window.samples.extend(samples)
        window.sequence_end = payload.sequence_number

        target_samples = int(
            window.sample_rate_hz * window.channel_count * self._window_seconds
        )
        while len(window.samples) >= target_samples:
            completed.append(
                AudioWindow(
                    sample_rate_hz=window.sample_rate_hz,
                    channel_count=window.channel_count,
                    source_id=window.source_id,
                    stream_id=window.stream_id,
                    sequence_start=window.sequence_start,
                    sequence_end=window.sequence_end,
                    discontinuity_epoch=window.discontinuity_epoch,
                    samples=array("f", window.samples[:target_samples]),
                )
            )
            del window.samples[:target_samples]
            window.sequence_start = payload.sequence_number
        return tuple(completed)

    def flush(self) -> tuple[AudioWindow, ...]:
        completed = tuple(window for window in self._windows.values() if window.samples)
        self._windows.clear()
        return completed

    def clear(self) -> None:
        self._windows.clear()


def mono_16khz(window: AudioWindow) -> array[float]:
    return resample(
        downmix(window.samples, window.channel_count),
        window.sample_rate_hz,
    )


def downmix(samples: array[float], channels: int) -> array[float]:
    if channels == 1:
        return array("f", samples)
    return array(
        "f",
        (
            sum(samples[index : index + channels]) / channels
            for index in range(0, len(samples), channels)
        ),
    )


def resample(
    samples: array[float], source_rate_hz: int, target_rate_hz: int = 16_000
) -> array[float]:
    if source_rate_hz == target_rate_hz:
        return samples
    output_count = round(len(samples) * target_rate_hz / source_rate_hz)
    if not samples or output_count == 0:
        return array("f")
    if len(samples) == 1:
        return array("f", [samples[0]] * output_count)
    scale = source_rate_hz / target_rate_hz
    output = array("f")
    for output_index in range(output_count):
        position = min(output_index * scale, len(samples) - 1)
        lower = int(position)
        upper = min(lower + 1, len(samples) - 1)
        fraction = position - lower
        output.append(samples[lower] + (samples[upper] - samples[lower]) * fraction)
    return output


__all__ = ["AudioWindow", "AudioWindowBuffer", "mono_16khz"]
