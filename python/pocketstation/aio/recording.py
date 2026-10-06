"""Async scheduling over the same native finalized-recording reader."""

from __future__ import annotations

import asyncio
from pathlib import Path

from ..identity import RuntimeSessionId, StemId
from ..recording import AudioHistory as _AudioHistory
from ..recording import (
    AudioHistoryObservations,
    RecordedStem,
    RecordingClip,
    RecordingClipWindow,
)
from ..recording import RecordedAudio as _RecordedAudio


class RecordedAudio:
    """Read off the event loop. Cancellation cannot abort already started I/O."""

    __slots__ = ("_reader",)

    def __init__(self, reader: _RecordedAudio) -> None:
        self._reader = reader

    @classmethod
    async def open(
        cls, directory: str | Path, session_id: RuntimeSessionId
    ) -> RecordedAudio:
        return cls(await asyncio.to_thread(_RecordedAudio.open, directory, session_id))

    @property
    def stems(self) -> tuple[RecordedStem, ...]:
        return self._reader.stems

    async def read_clip(
        self, stem_id: StemId, window: RecordingClipWindow
    ) -> RecordingClip:
        return await asyncio.to_thread(self._reader.read_clip, stem_id, window)


__all__ = ["RecordedAudio"]


class AudioHistory:
    """Run live-history reads off the event loop. Started work is not abortable."""

    __slots__ = ("_reader",)

    def __init__(self, reader: _AudioHistory) -> None:
        self._reader = reader

    async def get_stems(self) -> tuple[RecordedStem, ...]:
        return await asyncio.to_thread(lambda: self._reader.stems)

    async def read_clip(
        self, stem_id: StemId, window: RecordingClipWindow
    ) -> RecordingClip:
        return await asyncio.to_thread(self._reader.read_clip, stem_id, window)

    async def clear(self) -> None:
        await asyncio.to_thread(self._reader.clear)

    async def observations(self) -> AudioHistoryObservations:
        return await asyncio.to_thread(self._reader.observations)


__all__ += ["AudioHistory"]
