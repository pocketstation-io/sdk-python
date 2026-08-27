"""Bounded application-owned PCM input for a PocketStation Session."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic, sleep

from ._native import _AudioInput as _NativeAudioInput
from ._native import _AudioInputObservations as _NativeAudioInputObservations
from ._native import _OutputGeneration as _NativeOutputGeneration
from .errors import AudioInputBufferError, AudioInputFullError, _native_call
from .graph import Endpoint, SourceOutput
from .identity import SourceId, StreamId


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
    discarded_output_frames_total: int
    cancelled_output_writes_total: int
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
            discarded_output_frames_total=native.discarded_output_frames_total,
            cancelled_output_writes_total=native.cancelled_output_writes_total,
            cancelled=native.cancelled,
            closed=native.closed,
        )


class OutputGeneration:
    """Keeps replaceable PCM attached to one output operation."""

    def __init__(self, native: _NativeOutputGeneration) -> None:
        self._native = native

    @property
    def id(self) -> int:
        return self._native.id

    @property
    def active(self) -> bool:
        return self._native.active

    def cancel(self) -> None:
        """Cancel pending PCM without stopping capture or the Session."""
        _native_call(self._native.cancel)


class PcmSource:
    """Advanced explicit ownership of one Session source output and PCM writer."""

    def __init__(
        self,
        native: _NativeAudioInput,
        config: AudioInputConfig,
        destination: Callable[[object], Endpoint],
    ) -> None:
        self._native = native
        self._config = config
        self._output = SourceOutput(native.output, destination)

    @property
    def config(self) -> AudioInputConfig:
        return self._config

    @property
    def source_id(self) -> SourceId:
        return SourceId(self._native.source_id)

    @property
    def stream_id(self) -> StreamId:
        return StreamId(self._native.stream_id)

    @property
    def output(self) -> SourceOutput:
        return self._output

    def begin_output(self) -> OutputGeneration:
        return OutputGeneration(_native_call(self._native.begin_output))

    def try_write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
        generation: OutputGeneration | None = None,
    ) -> None:
        """Copy one C-contiguous float32 frame into a preallocated Core buffer."""
        try:
            _native_call(
                lambda: self._native.try_write(
                    samples,
                    discontinuity=discontinuity,
                    generation=None if generation is None else generation._native,
                )
            )
        except BufferError as error:
            # PyO3 rejects an incompatible buffer format before entering the
            # native method, so it cannot attach PocketStation's coded error.
            # Keep that binding detail out of the public SDK contract.
            raise AudioInputBufferError(
                "samples must be a C-contiguous float32 buffer",
                "audio_input.invalid_buffer",
            ) from error

    def close(self) -> None:
        """Close after accepted frames drain; subsequent writes fail explicitly."""
        _native_call(self._native.close)

    def observations(self) -> AudioInputObservations:
        return AudioInputObservations._from_native(
            _native_call(self._native.observations)
        )


class AudioInput(PcmSource):
    """Intent-first input for audio already owned by the embedding application."""

    def write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
        generation: OutputGeneration | None = None,
        timeout_s: float = 1.0,
    ) -> None:
        """Wait finitely for one preallocated native buffer.

        This convenience method never grows a Python queue. Advanced callers
        that need an immediate ``Full`` outcome should use :meth:`try_write`.
        """
        _write_with_timeout(
            self,
            samples,
            discontinuity=discontinuity,
            generation=generation,
            timeout_s=timeout_s,
        )


def _write_with_timeout(
    source: PcmSource,
    samples: object,
    *,
    discontinuity: bool,
    generation: OutputGeneration | None,
    timeout_s: float,
) -> None:
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s must be a number")
    if not 0 <= timeout_s <= 60:
        raise ValueError("timeout_s must be between 0 and 60")
    deadline = monotonic() + float(timeout_s)
    wait_s = 0.000_25
    while True:
        try:
            source.try_write(
                samples,
                discontinuity=discontinuity,
                generation=generation,
            )
            return
        except AudioInputFullError:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise
            sleep(min(wait_s, remaining))
            wait_s = min(wait_s * 2, 0.005)


__all__ = [
    "AudioInput",
    "AudioInputConfig",
    "AudioInputObservations",
    "OutputGeneration",
    "PcmSource",
]
