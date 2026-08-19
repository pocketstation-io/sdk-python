"""Bounded application-owned PCM input for a PocketStation Session."""

from __future__ import annotations

from dataclasses import dataclass

from ._native import _AudioInput as _NativeAudioInput
from ._native import _AudioInputObservations as _NativeAudioInputObservations
from .errors import _native_call
from .graph import SourceOutput


@dataclass(frozen=True, slots=True)
class AudioInputConfig:
    """Finite PCM contract shared by the convenient and advanced APIs."""

    name: str
    sample_rate_hz: int = 48_000
    channels: int = 1
    capacity_frames: int = 8
    frame_samples_per_channel: int = 480

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")


@dataclass(frozen=True, slots=True)
class AudioInputObservations:
    """Point-in-time bounded-buffer and terminal-state observations."""

    capacity_frames: int
    buffer_slots: int
    available_buffers: int
    accepted_total: int
    full_total: int
    invalid_total: int
    cancelled: bool
    closed: bool

    @classmethod
    def _from_native(
        cls,
        native: _NativeAudioInputObservations,
    ) -> AudioInputObservations:
        return cls(
            capacity_frames=native.capacity_frames,
            buffer_slots=native.buffer_slots,
            available_buffers=native.available_buffers,
            accepted_total=native.accepted_total,
            full_total=native.full_total,
            invalid_total=native.invalid_total,
            cancelled=native.cancelled,
            closed=native.closed,
        )


class PcmSource:
    """Advanced explicit ownership of one Session source output and PCM writer."""

    def __init__(self, native: _NativeAudioInput, config: AudioInputConfig) -> None:
        self._native = native
        self._config = config
        self._output = SourceOutput(native.output)

    @property
    def config(self) -> AudioInputConfig:
        return self._config

    @property
    def source_id(self) -> int:
        return self._native.source_id

    @property
    def stream_id(self) -> int:
        return self._native.stream_id

    @property
    def output(self) -> SourceOutput:
        return self._output

    def try_write(self, samples: object, *, discontinuity: bool = False) -> None:
        """Copy one C-contiguous float32 frame into a preallocated Core buffer."""
        _native_call(
            lambda: self._native.try_write(samples, discontinuity=discontinuity)
        )

    def close(self) -> None:
        """Close after accepted frames drain; subsequent writes fail explicitly."""
        _native_call(self._native.close)

    def observations(self) -> AudioInputObservations:
        return AudioInputObservations._from_native(
            _native_call(self._native.observations)
        )


class AudioInput(PcmSource):
    """Intent-first input for audio already owned by the embedding application."""

    def write(self, samples: object, *, discontinuity: bool = False) -> None:
        """Submit one complete frame without blocking or growing the queue."""
        self.try_write(samples, discontinuity=discontinuity)


__all__ = [
    "AudioInput",
    "AudioInputConfig",
    "AudioInputObservations",
    "PcmSource",
]
