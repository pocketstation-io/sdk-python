"""Extract source-aware context from finalized recordings without recapturing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import _native
from ._native import RecordingClipWindow as _NativeClipWindow
from .errors import RecordingClipError, _native_call
from .identity import ClockDomainId, RuntimeSessionId, SourceId, StemId
from .observations import RecordingDiscontinuity


def _u64(value: int, label: str, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 2**64:
        raise RecordingClipError(f"{label} must be an unsigned 64-bit integer", code)
    return value


@dataclass(frozen=True, slots=True, init=False)
class RecordingClipWindow:
    """A nonempty half-open Session interval in ns, limited by Core to 120 seconds."""

    start_ns: int
    end_ns: int
    _native: _NativeClipWindow = field(repr=False, compare=False)

    def __init__(self, start_ns: int, end_ns: int) -> None:
        code = "recording.clip_invalid_window"
        value = _native_call(
            lambda: _native.RecordingClipWindow(
                _u64(start_ns, "start_ns", code), _u64(end_ns, "end_ns", code)
            )
        )
        object.__setattr__(self, "start_ns", value.start_ns)
        object.__setattr__(self, "end_ns", value.end_ns)
        object.__setattr__(self, "_native", value)

    @classmethod
    def _from_native(cls, value: _NativeClipWindow) -> RecordingClipWindow:
        result = object.__new__(cls)
        object.__setattr__(result, "start_ns", value.start_ns)
        object.__setattr__(result, "end_ns", value.end_ns)
        object.__setattr__(result, "_native", value)
        return result

    @classmethod
    def around(
        cls, start_ns: int, end_ns: int, before_ns: int, after_ns: int
    ) -> RecordingClipWindow:
        """Add context, clamping before-context at zero and rejecting overflow."""
        code = "recording.clip_invalid_window"
        return cls._from_native(
            _native_call(
                lambda: _native.RecordingClipWindow.around(
                    _u64(start_ns, "start_ns", code),
                    _u64(end_ns, "end_ns", code),
                    _u64(before_ns, "before_ns", code),
                    _u64(after_ns, "after_ns", code),
                )
            )
        )


@dataclass(frozen=True, slots=True)
class RecordedStem:
    """Persisted source identity, interleaved format and normalized recording origin."""

    label: str
    session_id: RuntimeSessionId
    source_id: SourceId
    stem_id: StemId
    clock_id: ClockDomainId
    source_generation: int
    permission_epoch: int
    sample_rate_hz: int
    channels: int
    first_timestamp_ns: int
    final_timestamp_ns: int

    @classmethod
    def _from_native(cls, value: _native.RecordedStem) -> RecordedStem:
        return cls(
            value.label,
            RuntimeSessionId(value.session_id),
            SourceId(value.source_id),
            StemId(value.stem_id),
            ClockDomainId(value.clock_id),
            value.source_generation,
            value.permission_epoch,
            value.sample_rate_hz,
            value.channels,
            value.first_timestamp_ns,
            value.final_timestamp_ns,
        )


@dataclass(frozen=True, slots=True)
class RecordingClip:
    """Exact float32 WAV bytes, actual sample bounds and original gap observations."""

    wav: bytes
    stem: RecordedStem
    requested: RecordingClipWindow
    actual: RecordingClipWindow
    first_sample_frame: int
    sample_frames: int
    discontinuities: tuple[RecordingDiscontinuity, ...]

    @classmethod
    def _from_native(cls, value: _native.RecordingClip) -> RecordingClip:
        return cls(
            value.wav,
            RecordedStem._from_native(value.stem),
            RecordingClipWindow._from_native(value.requested),
            RecordingClipWindow._from_native(value.actual),
            value.first_sample_frame,
            value.sample_frames,
            tuple(
                RecordingDiscontinuity._from_native(gap)
                for gap in value.discontinuities()
            ),
        )


class RecordedAudio:
    """Read authorized finalized recordings, releasing the GIL during I/O.

    Core verifies the manifest and selected WAV on each read. The caller owns
    directory authorization. Limits are 120 seconds/32 MiB per clip and 1 GiB
    per selected source. Started blocking I/O cannot be forcibly cancelled.
    """

    __slots__ = ("_native",)

    def __init__(self, directory: str | Path, session_id: RuntimeSessionId) -> None:
        self._native = _native_call(
            lambda: _native.RecordedAudio(
                Path(directory),
                _u64(session_id, "session_id", "recording.clip_invalid_recording"),
            )
        )

    @classmethod
    def open(cls, directory: str | Path, session_id: RuntimeSessionId) -> RecordedAudio:
        """Verify a complete recording belongs to this exact runtime Session."""
        return cls(directory, session_id)

    @property
    def stems(self) -> tuple[RecordedStem, ...]:
        return tuple(RecordedStem._from_native(value) for value in self._native.stems())

    def read_clip(self, stem_id: StemId, window: RecordingClipWindow) -> RecordingClip:
        """Extract this exact stem; preserve channels and reported discontinuities."""
        if not isinstance(window, RecordingClipWindow):
            raise TypeError("window must be RecordingClipWindow")
        value = _native_call(
            lambda: self._native.read_clip(
                _u64(stem_id, "stem_id", "recording.clip_unknown_stem"), window._native
            )
        )
        return RecordingClip._from_native(value)


__all__ = [
    "RecordedAudio",
    "RecordedStem",
    "RecordingClip",
    "RecordingClipError",
    "RecordingClipWindow",
]
