"""Finite source-aware PCM windows for the example transcription provider."""

from __future__ import annotations

import sys
from array import array
from dataclasses import dataclass, field

from pocketstation.signal import SignalAudioPayload, SignalEnvelope


@dataclass(slots=True)
class AudioWindow:
    sample_rate_hz: int
    channel_count: int
    session_id: int
    source_id: int
    stream_id: int
    clock_id: int
    source_generation: int
    policy_epoch: int
    sequence_start: int
    sequence_end: int
    discontinuity_epoch: int
    timestamp_start_ns: int
    timestamp_end_ns: int
    source_timestamp_start_ns: int | None
    source_timestamp_end_ns: int | None
    session_timestamp_start_ns: int | None
    session_timestamp_end_ns: int | None
    discontinuity_reasons: tuple[str, ...] = ()
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
        envelope: SignalEnvelope[object],
    ) -> tuple[AudioWindow, ...]:
        payload = envelope.payload
        if not isinstance(payload, SignalAudioPayload):
            raise TypeError("transcription accepts only PCM audio signals")
        lineage = envelope.lineage
        if lineage is None:
            raise ValueError("transcription requires source-aware audio lineage")

        key = (payload.source_id, payload.stream_id)
        window = self._windows.get(key)
        reasons: list[str] = []
        if window is not None:
            if window.sample_rate_hz != payload.sample_rate_hz:
                reasons.append("sample-rate-change")
            if window.channel_count != payload.channel_count:
                reasons.append("channel-count-change")
            if window.clock_id != lineage.clock_id:
                reasons.append("clock-change")
            if window.source_generation != lineage.source_generation:
                reasons.append("source-generation-change")
            if window.policy_epoch != lineage.policy_epoch:
                reasons.append("policy-epoch-change")
            if window.discontinuity_epoch != lineage.discontinuity_epoch:
                reasons.append("discontinuity-epoch-change")
            if payload.sequence_number != window.sequence_end + 1:
                reasons.append("sequence-gap")
        completed: list[AudioWindow] = []
        if reasons and window is not None:
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
                session_id=lineage.session_id,
                source_id=payload.source_id,
                stream_id=payload.stream_id,
                clock_id=lineage.clock_id,
                source_generation=lineage.source_generation,
                policy_epoch=lineage.policy_epoch,
                sequence_start=payload.sequence_number,
                sequence_end=payload.sequence_number,
                discontinuity_epoch=lineage.discontinuity_epoch,
                timestamp_start_ns=payload.timestamp_ns,
                timestamp_end_ns=payload.timestamp_ns,
                source_timestamp_start_ns=envelope.timing.source_timestamp_ns,
                source_timestamp_end_ns=envelope.timing.source_timestamp_ns,
                session_timestamp_start_ns=envelope.timing.session_timestamp_ns,
                session_timestamp_end_ns=envelope.timing.session_timestamp_ns,
                discontinuity_reasons=tuple(reasons),
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
        duration_ns = envelope.timing.duration_ns or round(
            payload.sample_count
            / (payload.sample_rate_hz * payload.channel_count)
            * 1_000_000_000
        )
        window.timestamp_end_ns = payload.timestamp_ns + duration_ns
        if envelope.timing.source_timestamp_ns is not None:
            window.source_timestamp_end_ns = (
                envelope.timing.source_timestamp_ns + duration_ns
            )
        if envelope.timing.session_timestamp_ns is not None:
            window.session_timestamp_end_ns = (
                envelope.timing.session_timestamp_ns + duration_ns
            )

        target_samples = int(
            window.sample_rate_hz * window.channel_count * self._window_seconds
        )
        # Keep complete input frames together. A window may exceed the target
        # by at most one declared input frame, which preserves exact sequence
        # and timing ranges instead of assigning one frame to two windows.
        if len(window.samples) >= target_samples:
            completed.append(window)
            del self._windows[key]
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
