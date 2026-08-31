"""Typed Session-owned process sidecars using PocketStation's PKSS protocol."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import TypeAlias

from ._native import _SidecarMessage as _NativeSidecarMessage
from ._native import _SidecarProcessSpec as _NativeSidecarProcessSpec
from ._native import _SidecarRead as _NativeSidecarRead
from ._native import _SidecarSnapshot as _NativeSidecarSnapshot
from .errors import SidecarProtocolError
from .signal import STREAM_EOF, EndOfStream
from .streams import (
    _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    _iteration_timeout_milliseconds,
    _ReaderState,
    _timeout_milliseconds,
)


class SidecarMessageKind(StrEnum):
    """Frozen PKSS 1.0 message kinds."""

    SIGNAL = "signal"
    READY = "ready"
    ERROR = "error"
    CANCEL = "cancel"
    CLOSE = "close"
    HELLO = "hello"
    MANIFEST = "manifest"
    CONFIGURE = "configure"
    OBSERVATION = "observation"
    CLOSED = "closed"


class SidecarState(StrEnum):
    """Session-owned native child lifecycle states."""

    SPAWNED = "spawned"
    HELLO = "hello"
    MANIFEST = "manifest"
    CONFIGURE = "configure"
    READY = "ready"
    RUNNING = "running"
    CANCELLING = "cancelling"
    CLOSING = "closing"
    CLOSED = "closed"
    REAPED = "reaped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class SidecarProtocolLimits:
    """Finite PKSS field and payload bounds measured in bytes."""

    max_signal_id_bytes: int = 256
    max_role_bytes: int = 256
    max_schema_bytes: int = 1_024
    max_payload_bytes: int = 1_048_576

    def __post_init__(self) -> None:
        for name, value in (
            ("max_signal_id_bytes", self.max_signal_id_bytes),
            ("max_role_bytes", self.max_role_bytes),
            ("max_schema_bytes", self.max_schema_bytes),
            ("max_payload_bytes", self.max_payload_bytes),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True, slots=True)
class SidecarDeadlines:
    """Native lifecycle deadlines measured in seconds."""

    ready_s: float = 5.0
    processing_s: float = 5.0
    shutdown_s: float = 2.0

    def __post_init__(self) -> None:
        for name, value in (
            ("ready_s", self.ready_s),
            ("processing_s", self.processing_s),
            ("shutdown_s", self.shutdown_s),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")
            if float(value) <= 0.0:
                raise ValueError(f"{name} must be greater than zero")

    def _milliseconds(self) -> tuple[int, int, int]:
        return (
            max(1, round(float(self.ready_s) * 1_000)),
            max(1, round(float(self.processing_s) * 1_000)),
            max(1, round(float(self.shutdown_s) * 1_000)),
        )


@dataclass(frozen=True, slots=True)
class SidecarProcessSpec:
    """One bounded child declaration spawned transactionally by ``Session``.

    ``stdout`` is reserved for PKSS. The native host owns pipes, handshake,
    deadlines, close/cancel, kill, wait, and reap. No shell is involved.
    """

    id: int
    program: str | Path
    arguments: tuple[str, ...] = ()
    configuration: bytes = b""
    data_capacity_messages: int = 64
    protocol_limits: SidecarProtocolLimits = field(
        default_factory=SidecarProtocolLimits
    )
    deadlines: SidecarDeadlines = field(default_factory=SidecarDeadlines)

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("id must be a positive integer")
        if not str(self.program):
            raise ValueError("program must not be empty")
        if any(not isinstance(argument, str) for argument in self.arguments):
            raise TypeError("arguments must contain only strings")
        if not isinstance(self.configuration, bytes):
            raise TypeError("configuration must be bytes")
        if (
            isinstance(self.data_capacity_messages, bool)
            or not isinstance(self.data_capacity_messages, int)
            or self.data_capacity_messages <= 0
        ):
            raise ValueError("data_capacity_messages must be a positive integer")

    def _to_native(self) -> _NativeSidecarProcessSpec:
        ready_ms, processing_ms, shutdown_ms = self.deadlines._milliseconds()
        limits = self.protocol_limits
        return _NativeSidecarProcessSpec(
            self.id,
            Path(self.program),
            list(self.arguments),
            self.configuration,
            self.data_capacity_messages,
            limits.max_signal_id_bytes,
            limits.max_role_bytes,
            limits.max_schema_bytes,
            limits.max_payload_bytes,
            ready_ms,
            processing_ms,
            shutdown_ms,
        )


@dataclass(frozen=True, slots=True)
class SidecarHandle:
    """A Session-scoped reference to one registered sidecar."""

    id: int
    session_id: int


@dataclass(frozen=True, slots=True)
class SidecarMessage:
    """One owned PKSS message with finite payload bytes."""

    kind: SidecarMessageKind
    stream_id: int
    sequence_number: int
    timestamp_ns: int
    signal_id: str
    payload: bytes
    terminal: bool = False
    role: str | None = None
    schema: str | None = None

    @classmethod
    def signal(
        cls,
        payload: bytes,
        *,
        signal_id: str,
        stream_id: int,
        sequence_number: int,
        timestamp_ns: int,
        role: str | None = None,
        schema: str | None = None,
        terminal: bool = False,
    ) -> SidecarMessage:
        """Build the only message kind accepted by the bounded data queue."""
        return cls(
            kind=SidecarMessageKind.SIGNAL,
            stream_id=stream_id,
            sequence_number=sequence_number,
            timestamp_ns=timestamp_ns,
            signal_id=signal_id,
            payload=payload,
            terminal=terminal,
            role=role,
            schema=schema,
        )

    def _to_native(self) -> _NativeSidecarMessage:
        return _NativeSidecarMessage(
            kind=self.kind.value,
            stream_id=self.stream_id,
            sequence_number=self.sequence_number,
            timestamp_ns=self.timestamp_ns,
            signal_id=self.signal_id,
            payload=self.payload,
            terminal=self.terminal,
            role=self.role,
            schema=self.schema,
        )

    @classmethod
    def _from_native(cls, value: _NativeSidecarMessage) -> SidecarMessage:
        return cls(
            kind=SidecarMessageKind(value.kind),
            stream_id=value.stream_id,
            sequence_number=value.sequence_number,
            timestamp_ns=value.timestamp_ns,
            signal_id=value.signal_id,
            payload=value.payload,
            terminal=value.terminal,
            role=value.role,
            schema=value.schema,
        )


@dataclass(frozen=True, slots=True)
class SidecarSnapshot:
    """Native process lifecycle and finite queue counters for one child."""

    sidecar_id: int
    state: SidecarState
    state_transitions: int
    data_enqueued_total: int
    data_received_total: int
    data_dropped_total: int
    protocol_failures_total: int
    timeouts_total: int
    forced_kills_total: int
    reaps_total: int

    @classmethod
    def _from_native(cls, value: _NativeSidecarSnapshot) -> SidecarSnapshot:
        return cls(
            sidecar_id=value.sidecar_id,
            state=SidecarState(value.state),
            state_transitions=value.state_transitions,
            data_enqueued_total=value.data_enqueued_total,
            data_received_total=value.data_received_total,
            data_dropped_total=value.data_dropped_total,
            protocol_failures_total=value.protocol_failures_total,
            timeouts_total=value.timeouts_total,
            forced_kills_total=value.forced_kills_total,
            reaps_total=value.reaps_total,
        )

    def visited(self, state: SidecarState) -> bool:
        position = list(SidecarState).index(state)
        return self.state_transitions & (1 << position) != 0


SidecarReadResult: TypeAlias = SidecarMessage | EndOfStream | None


class SidecarStream:
    """One-reader stream over the native bounded incoming PKSS queue."""

    def __init__(
        self,
        *,
        poll_message: Callable[[], _NativeSidecarRead],
        wait_message: Callable[[int], _NativeSidecarRead],
        is_session_stopped: Callable[[], bool],
    ) -> None:
        self._poll_message = poll_message
        self._wait_message = wait_message
        self._is_session_stopped = is_session_stopped
        self._state = _ReaderState()
        self._closed = False

    @property
    def reader_mode(self) -> str | None:
        return self._state.mode

    @property
    def is_closed(self) -> bool:
        return self._closed or self._is_session_stopped()

    def poll(self) -> SidecarReadResult:
        token = self._state.claim("sidecar_read")
        try:
            return STREAM_EOF if self.is_closed else self._decode(self._poll_message())
        finally:
            self._state.release(token)

    def read(self, *, timeout_s: float = 1.0) -> SidecarReadResult:
        timeout_ms = _timeout_milliseconds(timeout_s)
        token = self._state.claim("sidecar_read")
        try:
            return (
                STREAM_EOF
                if self.is_closed
                else self._decode(self._wait_message(timeout_ms))
            )
        finally:
            self._state.release(token)

    def __iter__(self) -> Iterator[SidecarMessage]:
        return self.messages()

    def messages(
        self,
        *,
        wait_timeout_s: float = _DEFAULT_ITERATION_TIMEOUT_SECONDS,
    ) -> Iterator[SidecarMessage]:
        timeout_ms = _iteration_timeout_milliseconds(wait_timeout_s)

        def iterate() -> Iterator[SidecarMessage]:
            token = self._state.claim("sidecar")
            try:
                while not self.is_closed:
                    result = self._decode(self._wait_message(timeout_ms))
                    if isinstance(result, EndOfStream):
                        break
                    if result is not None:
                        yield result
            finally:
                self._state.release(token)

        return iterate()

    def _decode(self, value: _NativeSidecarRead) -> SidecarReadResult:
        if value.status == "item":
            if value.message is None:
                raise SidecarProtocolError(
                    "native sidecar read omitted its message",
                    "sidecar.invalid_read",
                )
            return SidecarMessage._from_native(value.message)
        if value.status == "empty":
            return None
        if value.status == "closed":
            self._closed = True
            return STREAM_EOF
        raise SidecarProtocolError(
            f"native sidecar read has unknown state {value.status!r}",
            "sidecar.invalid_read",
        )


class SidecarConnection:
    """Running Session view of one registered sidecar."""

    def __init__(
        self,
        *,
        handle: SidecarHandle,
        send_message: Callable[[_NativeSidecarMessage], None],
        poll_message: Callable[[], _NativeSidecarRead],
        wait_message: Callable[[int], _NativeSidecarRead],
        snapshot: Callable[[], _NativeSidecarSnapshot],
        is_session_stopped: Callable[[], bool],
    ) -> None:
        self.handle = handle
        self._send_message = send_message
        self._snapshot = snapshot
        self.messages = SidecarStream(
            poll_message=poll_message,
            wait_message=wait_message,
            is_session_stopped=is_session_stopped,
        )

    def send(self, message: SidecarMessage) -> None:
        """Try one immediate native bounded enqueue; never waits for capacity."""
        self._send_message(message._to_native())

    def snapshot(self) -> SidecarSnapshot:
        return SidecarSnapshot._from_native(self._snapshot())


__all__ = [
    "SidecarConnection",
    "SidecarDeadlines",
    "SidecarHandle",
    "SidecarMessage",
    "SidecarMessageKind",
    "SidecarProcessSpec",
    "SidecarProtocolLimits",
    "SidecarReadResult",
    "SidecarSnapshot",
    "SidecarState",
    "SidecarStream",
]
