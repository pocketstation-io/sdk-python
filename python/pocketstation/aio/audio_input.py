"""Asyncio API for bounded application-owned PCM input."""

from __future__ import annotations

import asyncio
from time import monotonic

from ..audio_input import (
    AudioInputConfig,
    AudioInputObservations,
    OutputGeneration,
)
from ..audio_input import (
    PcmSource as SyncPcmSource,
)
from ..errors import AudioInputFullError
from ..graph import SourceOutput


class PcmSource:
    """Async writer over the same native Session-owned PCM source."""

    def __init__(self, source: SyncPcmSource) -> None:
        self._source = source

    @property
    def config(self) -> AudioInputConfig:
        return self._source.config

    @property
    def source_id(self) -> int:
        return self._source.source_id

    @property
    def stream_id(self) -> int:
        return self._source.stream_id

    @property
    def output(self) -> SourceOutput:
        return self._source.output

    def begin_output(self) -> OutputGeneration:
        return self._source.begin_output()

    async def try_write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
        generation: OutputGeneration | None = None,
    ) -> None:
        """Attempt one immediate write into Core's finite preallocated pool.

        The native operation never waits for capacity. It either accepts the
        frame or reports ``Full``, ``Closed``, ``Cancelled``, or an invalid
        buffer, so dispatching every write through the thread pool would add
        scheduling overhead without making the operation more asynchronous.
        """
        self._source.try_write(
            samples,
            discontinuity=discontinuity,
            generation=generation,
        )

    async def close(self) -> None:
        """Close the native input immediately after its accepted frames drain."""
        self._source.close()

    async def observations(self) -> AudioInputObservations:
        """Read one immediate point-in-time snapshot from Core."""
        return self._source.observations()


class AudioInput(PcmSource):
    """Write application-owned PCM to a bounded native Source with asyncio."""

    async def write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
        generation: OutputGeneration | None = None,
        timeout_s: float = 1.0,
    ) -> None:
        """Wait finitely for one native buffer without growing a Python queue."""
        if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
            raise TypeError("timeout_s must be a number")
        if not 0 <= timeout_s <= 60:
            raise ValueError("timeout_s must be between 0 and 60")
        deadline = monotonic() + float(timeout_s)
        wait_s = 0.000_25
        while True:
            try:
                await self.try_write(
                    samples,
                    discontinuity=discontinuity,
                    generation=generation,
                )
                return
            except AudioInputFullError:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise
                await asyncio.sleep(min(wait_s, remaining))
                wait_s = min(wait_s * 2, 0.005)


__all__ = ["AudioInput", "PcmSource"]
