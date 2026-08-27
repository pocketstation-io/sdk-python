"""Read immutable typed signals delivered by Rust Session endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar, cast

from ._native import BusSubscription as _NativeBusSubscription
from ._native import ClockDomainDescriptor
from ._native import _SignalAudioPayload as _NativeSignalAudioPayload
from ._native import _SignalDerivation as _NativeSignalDerivation
from ._native import _SignalEnvelope as _NativeSignalEnvelope
from ._native import _SignalLineage as _NativeSignalLineage
from ._native import _SignalSubscriptionMetrics as _NativeSignalSubscriptionMetrics
from ._native import _SignalTiming as _NativeSignalTiming
from .graph import EdgeContract, SignalSpec
from .identity import (
    ClockDomainId,
    ConnectorId,
    RuntimeSessionId,
    SourceId,
    StreamId,
)

_PayloadT = TypeVar("_PayloadT")
_PayloadT_co = TypeVar("_PayloadT_co", covariant=True)


@dataclass(frozen=True, slots=True)
class SignalTiming:
    """Clock observations preserved on one routed signal."""

    source_timestamp_ns: int | None
    observed_timestamp_ns: int
    session_timestamp_ns: int | None
    duration_ns: int | None

    @classmethod
    def _from_native(cls, value: _NativeSignalTiming) -> SignalTiming:
        return cls(
            source_timestamp_ns=value.source_timestamp_ns,
            observed_timestamp_ns=value.observed_timestamp_ns,
            session_timestamp_ns=value.session_timestamp_ns,
            duration_ns=value.duration_ns,
        )


@dataclass(frozen=True, slots=True)
class SignalLineage:
    """Source and stream identity that survives graph and language boundaries."""

    session_id: RuntimeSessionId
    stream_id: StreamId
    source_id: SourceId
    clock_id: ClockDomainId
    clock: ClockDomainDescriptor
    sequence_number: int
    source_generation: int
    discontinuity_epoch: int
    policy_epoch: int

    @classmethod
    def _from_native(cls, value: _NativeSignalLineage) -> SignalLineage:
        return cls(
            session_id=RuntimeSessionId(value.session_id),
            stream_id=StreamId(value.stream_id),
            source_id=SourceId(value.source_id),
            clock_id=ClockDomainId(value.clock_id),
            clock=value.clock,
            sequence_number=value.sequence_number,
            source_generation=value.source_generation,
            discontinuity_epoch=value.discontinuity_epoch,
            policy_epoch=value.policy_epoch,
        )


@dataclass(frozen=True, slots=True)
class SignalDerivation:
    """Operator provenance attached to a derived signal."""

    upstream_lineage: SignalLineage
    upstream_timing: SignalTiming
    operator_id: str
    operator_revision: int
    operator_generation: int
    connector_id: ConnectorId | None

    @classmethod
    def _from_native(cls, value: _NativeSignalDerivation) -> SignalDerivation:
        return cls(
            upstream_lineage=SignalLineage._from_native(value.upstream_lineage),
            upstream_timing=SignalTiming._from_native(value.upstream_timing),
            operator_id=value.operator_id,
            operator_revision=value.operator_revision,
            operator_generation=value.operator_generation,
            connector_id=(
                None if value.connector_id is None else ConnectorId(value.connector_id)
            ),
        )


@dataclass(frozen=True, slots=True)
class SignalAudioPayload:
    """Owned immutable interleaved f32 PCM payload."""

    samples_f32le: bytes
    sample_count: int
    sample_rate_hz: int
    channel_count: int
    stream_id: StreamId
    source_id: SourceId
    sequence_number: int
    timestamp_ns: int

    @classmethod
    def _from_native(cls, value: _NativeSignalAudioPayload) -> SignalAudioPayload:
        return cls(
            samples_f32le=value.samples_f32le,
            sample_count=value.sample_count,
            sample_rate_hz=value.sample_rate_hz,
            channel_count=value.channel_count,
            stream_id=StreamId(value.stream_id),
            source_id=SourceId(value.source_id),
            sequence_number=value.sequence_number,
            timestamp_ns=value.timestamp_ns,
        )

    @property
    def samples(self) -> memoryview:
        """Read-only bytes view; conversion to floats stays caller-controlled."""
        return memoryview(self.samples_f32le)

    @property
    def sample_format(self) -> str:
        return "f32le"


SignalPayload: TypeAlias = SignalAudioPayload | str | bytes


@dataclass(frozen=True, slots=True)
class SignalSubscriptionMetrics:
    """Unit-bearing finite edge and saturation observations."""

    capacity_signals: int
    max_payload_bytes: int
    maximum_buffered_payload_bytes: int
    depth_signals: int
    peak_depth_signals: int
    enqueued_total: int
    received_total: int
    dropped_total: int

    @classmethod
    def _from_native(
        cls,
        value: _NativeSignalSubscriptionMetrics,
    ) -> SignalSubscriptionMetrics:
        return cls(
            capacity_signals=value.capacity_signals,
            max_payload_bytes=value.max_payload_bytes,
            maximum_buffered_payload_bytes=value.maximum_buffered_payload_bytes,
            depth_signals=value.depth_signals,
            peak_depth_signals=value.peak_depth_signals,
            enqueued_total=value.enqueued_total,
            received_total=value.received_total,
            dropped_total=value.dropped_total,
        )


@dataclass(frozen=True, slots=True)
class SignalEnvelope(Generic[_PayloadT_co]):
    """One owned payload with its exact signal, timing, lineage, and derivation."""

    signal: SignalSpec[_PayloadT_co]
    timing: SignalTiming
    lineage: SignalLineage | None
    derivation: SignalDerivation | None
    payload: _PayloadT_co

    @classmethod
    def _from_native(
        cls, value: _NativeSignalEnvelope
    ) -> SignalEnvelope[SignalPayload]:
        if value.payload_kind == "audio":
            if value.audio is None:
                raise RuntimeError("native audio signal omitted its payload")
            payload: SignalPayload = SignalAudioPayload._from_native(value.audio)
        elif value.payload_kind == "text":
            if value.text is None:
                raise RuntimeError("native text signal omitted its payload")
            payload = value.text
        elif value.payload_kind == "bytes":
            if value.bytes is None:
                raise RuntimeError("native bytes signal omitted its payload")
            payload = value.bytes
        else:
            raise RuntimeError(
                f"native signal has unknown payload kind {value.payload_kind!r}"
            )
        return SignalEnvelope[SignalPayload](
            signal=cast(
                SignalSpec[SignalPayload], SignalSpec._from_native(value.signal)
            ),
            timing=SignalTiming._from_native(value.timing),
            lineage=(
                None
                if value.lineage is None
                else SignalLineage._from_native(value.lineage)
            ),
            derivation=(
                None
                if value.derivation is None
                else SignalDerivation._from_native(value.derivation)
            ),
            payload=payload,
        )


class BusSubscription(Generic[_PayloadT_co]):
    """Session-scoped receipt for one bounded typed ``AudioBus`` route."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeBusSubscription) -> None:
        self._native = native

    @property
    def id(self) -> int:
        return self._native.id

    @property
    def session_id(self) -> int:
        return self._native.session_id

    @property
    def route_id(self) -> int:
        return self._native.route_id

    @property
    def signal(self) -> SignalSpec[_PayloadT_co]:
        return cast(
            SignalSpec[_PayloadT_co], SignalSpec._from_native(self._native.signal)
        )

    @property
    def edge(self) -> EdgeContract:
        return EdgeContract(self._native.edge)


class EndOfStream:
    """Stable singleton returned by explicit reads after native endpoint EOF."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "STREAM_EOF"


STREAM_EOF = EndOfStream()
SignalReadResult: TypeAlias = SignalEnvelope[_PayloadT] | EndOfStream | None


__all__ = [
    "STREAM_EOF",
    "BusSubscription",
    "EndOfStream",
    "SignalAudioPayload",
    "SignalDerivation",
    "SignalEnvelope",
    "SignalLineage",
    "SignalPayload",
    "SignalReadResult",
    "SignalSpec",
    "SignalSubscriptionMetrics",
    "SignalTiming",
]
