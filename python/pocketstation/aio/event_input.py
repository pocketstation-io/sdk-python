"""Bounded typed-event input for asyncio frameworks and application callbacks."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from time import monotonic_ns
from typing import TYPE_CHECKING, Any

from ..errors import EventInputClosedError, EventInputFullError
from ..graph import Multiplicity, PortSpec, SignalSpec, SourceOutput
from ..source_authoring import SourceEmission, SourceManifest
from .source_authoring import SourceProvider

if TYPE_CHECKING:
    from .session import Session

_OUTPUT_PORT = "events"


@dataclass(frozen=True, slots=True)
class EventInputObservations:
    """Current capacity and delivery counters for one event input."""

    capacity_events: int
    depth_events: int
    accepted_total: int
    full_total: int
    closed: bool


@dataclass(frozen=True, slots=True)
class _QueuedEvent:
    payload: bytes
    timestamp_ns: int


class EventInput:
    """Push framework events into a normal PocketStation typed Source."""

    def __init__(
        self,
        session: Session,
        name: str,
        *,
        signal: SignalSpec[bytes],
        capacity_events: int,
        maximum_event_bytes: int,
    ) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        if not 1 <= capacity_events <= 65_536:
            raise ValueError("capacity_events must be between 1 and 65536")
        if not 1 <= maximum_event_bytes <= 1_048_576:
            raise ValueError("maximum_event_bytes must be between 1 and 1048576")

        self.name = name
        self.signal = signal
        self.capacity_events = capacity_events
        self.maximum_event_bytes = maximum_event_bytes
        self._queue: asyncio.Queue[_QueuedEvent | None] = asyncio.Queue(capacity_events)
        self._accepted_total = 0
        self._full_total = 0
        self._closed = False

        async def emissions(
            _configuration: Mapping[str, str],
        ) -> AsyncIterator[SourceEmission]:
            while True:
                queued = await self._queue.get()
                try:
                    if queued is None:
                        return
                    yield SourceEmission.bytes(
                        _OUTPUT_PORT,
                        queued.payload,
                        signal=signal,
                        source_timestamp_ns=queued.timestamp_ns,
                        observed_timestamp_ns=queued.timestamp_ns,
                    )
                finally:
                    self._queue.task_done()

        provider = SourceProvider.from_async_iterable(
            SourceManifest(
                _source_type_id(name),
                outputs=(
                    PortSpec.output(
                        _OUTPUT_PORT,
                        signal,
                        multiplicity=Multiplicity.MANY,
                    ),
                ),
            ),
            emissions,
        )
        instance = session.register_source(provider).declare()
        self.output: SourceOutput = instance.output(_OUTPUT_PORT)

    def try_write(
        self,
        event: Mapping[str, Any],
        *,
        timestamp_ns: int | None = None,
    ) -> None:
        """Serialize and enqueue one JSON event without waiting."""
        if self._closed:
            raise EventInputClosedError("event input is closed", "event_input.closed")
        payload = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > self.maximum_event_bytes:
            raise ValueError(
                f"event is {len(payload)} bytes; maximum is {self.maximum_event_bytes}"
            )
        queued = _QueuedEvent(
            payload=payload,
            timestamp_ns=monotonic_ns() if timestamp_ns is None else timestamp_ns,
        )
        try:
            self._queue.put_nowait(queued)
        except asyncio.QueueFull as error:
            self._full_total += 1
            raise EventInputFullError(
                "event input is full", "event_input.full"
            ) from error
        self._accepted_total += 1

    async def aclose(self) -> None:
        """Stop accepting events after previously accepted events drain."""
        if self._closed:
            return
        self._closed = True
        await self._queue.put(None)

    def observations(self) -> EventInputObservations:
        return EventInputObservations(
            capacity_events=self.capacity_events,
            depth_events=self._queue.qsize(),
            accepted_total=self._accepted_total,
            full_total=self._full_total,
            closed=self._closed,
        )


def _source_type_id(name: str) -> str:
    normalized = "-".join(name.strip().lower().replace("_", "-").split())
    if not normalized or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-"
        for character in normalized
    ):
        raise ValueError("name must contain only letters, numbers, spaces, '_' or '-'")
    return f"io.pocketstation.source.event-input.{normalized}.v1"


__all__ = ["EventInput", "EventInputObservations"]
