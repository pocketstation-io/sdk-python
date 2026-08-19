"""Asyncio projection of bounded application-owned PCM input."""

from __future__ import annotations

import asyncio

from ..audio_input import (
    AudioInputConfig,
    AudioInputObservations,
)
from ..audio_input import (
    PcmSource as SyncPcmSource,
)
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

    async def try_write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
    ) -> None:
        await asyncio.to_thread(
            self._source.try_write,
            samples,
            discontinuity=discontinuity,
        )

    async def close(self) -> None:
        await asyncio.to_thread(self._source.close)

    async def observations(self) -> AudioInputObservations:
        return await asyncio.to_thread(self._source.observations)


class AudioInput(PcmSource):
    """Intent-first asyncio input over the canonical bounded native source."""

    async def write(
        self,
        samples: object,
        *,
        discontinuity: bool = False,
    ) -> None:
        await self.try_write(samples, discontinuity=discontinuity)


__all__ = ["AudioInput", "PcmSource"]
