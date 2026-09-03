"""Declare Python graph routes for the Rust ``Session`` to compile."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypeVar, cast

from ._native import DerivedStream as _NativeDerivedStream
from ._native import Endpoint as _NativeEndpoint
from ._native import OperatorInput as _NativeOperatorInput
from ._native import OperatorInstance as _NativeOperatorInstance
from ._native import Session as _NativeSession
from ._native import SourceInstance as _NativeSourceInstance
from ._native import SourceOutput as _NativeSourceOutput
from ._native import Stem as _NativeStem
from ._native import _EndpointDescriptor as _NativeEndpointDescriptor
from ._native import _MediaCaps as _NativeMediaCaps
from ._native import _PortSpec as _NativePortSpec
from ._native import _RouteSettings as _NativeRouteSettings
from ._native import _SignalSpec as _NativeSignalSpec
from .errors import _native_call
from .identity import (
    ConnectorId,
    EndpointId,
    OperatorInstanceId,
    RouteId,
    RuntimeSessionId,
    SourceId,
    SourceInstanceId,
    StemId,
    StreamId,
)

if TYPE_CHECKING:
    from .aio.connector import Connector as AsyncConnector
    from .connector import Connector as SyncConnector
    from .relay import RelayPublisher, RelayRoute
    from .signal import BusSubscription, SignalAudioPayload

    _ConnectorTarget: TypeAlias = SyncConnector | AsyncConnector
else:
    _ConnectorTarget: TypeAlias = object

_DestinationResolver: TypeAlias = Callable[[object], "Endpoint"]

_PayloadT = TypeVar("_PayloadT")
_PayloadT_co = TypeVar("_PayloadT_co", covariant=True)


class SignalKind(StrEnum):
    ANY = "any"
    PCM_AUDIO = "pcm-audio"
    ENCODED_AUDIO = "encoded-audio"
    TEXT = "text"
    EVENT = "event"
    METRICS = "metrics"
    CONTROL = "control"
    BINARY = "binary"
    CUSTOM = "custom"


class Codec(StrEnum):
    OPUS = "opus"
    AAC = "aac"
    MP3 = "mp3"
    G711_ULAW = "g711-ulaw"
    G711_ALAW = "g711-alaw"
    WEBM_OPUS = "webm-opus"


class TextFormat(StrEnum):
    UTF8 = "utf8"
    JSON = "json"
    MARKDOWN = "markdown"


class EventFormat(StrEnum):
    JSON = "json"
    PROTOBUF = "protobuf"
    FLATBUFFERS = "flatbuffers"
    CBOR = "cbor"


class BinaryFormat(StrEnum):
    RAW = "raw"
    PROTOBUF = "protobuf"
    FLATBUFFERS = "flatbuffers"
    CBOR = "cbor"


SignalFormat: TypeAlias = Codec | TextFormat | EventFormat | BinaryFormat


@dataclass(frozen=True, slots=True)
class SignalSpec(Generic[_PayloadT_co]):
    """Stable language-neutral signal identity, role, and schema."""

    kind: SignalKind
    format: SignalFormat | None = None
    custom_id: str | None = None
    role: str | None = None
    schema: str | None = None
    _native: _NativeSignalSpec = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativeSignalSpec(
                self.kind.value,
                None if self.format is None else self.format.value,
                self.custom_id,
                self.role,
                self.schema,
            )
        )
        object.__setattr__(self, "_native", native)

    @classmethod
    def _from_native(cls, native: _NativeSignalSpec) -> SignalSpec[object]:
        kind = SignalKind(native.kind)
        format_value: SignalFormat | None = None
        if native.format is not None:
            if kind is SignalKind.ENCODED_AUDIO:
                format_value = Codec(native.format)
            elif kind is SignalKind.TEXT:
                format_value = TextFormat(native.format)
            elif kind is SignalKind.EVENT:
                format_value = EventFormat(native.format)
            elif kind is SignalKind.BINARY:
                format_value = BinaryFormat(native.format)
            else:
                raise AssertionError(
                    f"Rust signal {kind.value!r} exposed an unexpected format"
                )
        return cls(
            kind,
            format_value,
            native.custom_id,
            native.role,
            native.schema,
        )

    @classmethod
    def any(
        cls, *, role: str | None = None, schema: str | None = None
    ) -> SignalSpec[object]:
        return cls(SignalKind.ANY, role=role, schema=schema)

    @classmethod
    def audio(
        cls, *, role: str | None = None, schema: str | None = None
    ) -> SignalSpec[SignalAudioPayload]:
        return cast(
            "SignalSpec[SignalAudioPayload]",
            cls(SignalKind.PCM_AUDIO, role=role, schema=schema),
        )

    @classmethod
    def encoded_audio(
        cls,
        codec: Codec,
        *,
        role: str | None = None,
        schema: str | None = None,
    ) -> SignalSpec[bytes]:
        return cast(
            SignalSpec[bytes],
            cls(SignalKind.ENCODED_AUDIO, codec, role=role, schema=schema),
        )

    @classmethod
    def text(
        cls,
        format: TextFormat = TextFormat.UTF8,
        *,
        role: str | None = None,
        schema: str | None = None,
    ) -> SignalSpec[str]:
        return cast(
            SignalSpec[str], cls(SignalKind.TEXT, format, role=role, schema=schema)
        )

    @classmethod
    def event(
        cls,
        format: EventFormat = EventFormat.JSON,
        *,
        role: str | None = None,
        schema: str | None = None,
    ) -> SignalSpec[bytes]:
        return cast(
            SignalSpec[bytes],
            cls(SignalKind.EVENT, format, role=role, schema=schema),
        )

    @classmethod
    def metrics(
        cls, *, role: str | None = None, schema: str | None = None
    ) -> SignalSpec[object]:
        return cls(SignalKind.METRICS, role=role, schema=schema)

    @classmethod
    def control(
        cls, *, role: str | None = None, schema: str | None = None
    ) -> SignalSpec[object]:
        return cls(SignalKind.CONTROL, role=role, schema=schema)

    @classmethod
    def binary(
        cls,
        format: BinaryFormat = BinaryFormat.RAW,
        *,
        role: str | None = None,
        schema: str | None = None,
    ) -> SignalSpec[bytes]:
        return cast(
            SignalSpec[bytes],
            cls(SignalKind.BINARY, format, role=role, schema=schema),
        )

    @classmethod
    def custom(
        cls,
        signal_id: str,
        *,
        role: str | None = None,
        schema: str | None = None,
    ) -> SignalSpec[object]:
        return cls(
            SignalKind.CUSTOM,
            custom_id=signal_id,
            role=role,
            schema=schema,
        )

    @property
    def wire_id(self) -> str:
        return self._native.wire_id

    @property
    def is_audio(self) -> bool:
        return self._native.is_audio

    def is_compatible_with(self, other: SignalSpec[object]) -> bool:
        return self._native.is_compatible_with(other._native)


class MediaKind(StrEnum):
    AUDIO_PCM = "audio-pcm"
    AUDIO_ENCODED = "audio-encoded"
    TEXT = "text"
    EVENT = "event"
    METRICS = "metrics"
    CONTROL = "control"
    BINARY = "binary"
    ANY = "any"


class ChannelLayout(StrEnum):
    MONO = "mono"
    STEREO = "stereo"
    ANY = "any"

    @property
    def channel_count(self) -> int | None:
        if self is ChannelLayout.MONO:
            return 1
        if self is ChannelLayout.STEREO:
            return 2
        return None


class SampleFormat(StrEnum):
    F32_INTERLEAVED = "f32-interleaved"


@dataclass(frozen=True, slots=True)
class AudioCaps:
    """Physical PCM constraints; ``None`` means the Rust wildcard."""

    sample_rate_hz: int | None = None
    frame_samples: int | None = None
    channel_layout: ChannelLayout = ChannelLayout.ANY
    format: SampleFormat = SampleFormat.F32_INTERLEAVED


MediaFormat: TypeAlias = Codec | BinaryFormat


@dataclass(frozen=True, slots=True)
class MediaCaps:
    """Exact Rust media representation projected as an immutable value."""

    kind: MediaKind
    audio_caps: AudioCaps | None = None
    format: MediaFormat | None = None
    _native: _NativeMediaCaps = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        audio = self.audio_caps
        native = _native_call(
            lambda: _NativeMediaCaps(
                self.kind.value,
                None if self.format is None else self.format.value,
                None if audio is None else audio.sample_rate_hz,
                None if audio is None else audio.frame_samples,
                None if audio is None else audio.channel_layout.value,
            )
        )
        object.__setattr__(self, "_native", native)

    @classmethod
    def _from_native(cls, native: _NativeMediaCaps) -> MediaCaps:
        return _media_from_native(native)

    @classmethod
    def audio(cls, caps: AudioCaps | None = None) -> MediaCaps:
        return cls(MediaKind.AUDIO_PCM, audio_caps=caps or AudioCaps())

    @classmethod
    def encoded_audio(cls, codec: Codec) -> MediaCaps:
        return cls(MediaKind.AUDIO_ENCODED, format=codec)

    @classmethod
    def text(cls) -> MediaCaps:
        return cls(MediaKind.TEXT)

    @classmethod
    def event(cls) -> MediaCaps:
        return cls(MediaKind.EVENT)

    @classmethod
    def metrics(cls) -> MediaCaps:
        return cls(MediaKind.METRICS)

    @classmethod
    def control(cls) -> MediaCaps:
        return cls(MediaKind.CONTROL)

    @classmethod
    def binary(cls, format: BinaryFormat = BinaryFormat.RAW) -> MediaCaps:
        return cls(MediaKind.BINARY, format=format)

    @classmethod
    def any(cls) -> MediaCaps:
        return cls(MediaKind.ANY)

    @classmethod
    def for_signal(cls, signal: SignalSpec[object]) -> MediaCaps:
        """Select wildcard media requirements for a signal."""
        if signal.kind is SignalKind.PCM_AUDIO:
            return cls.audio()
        if signal.kind is SignalKind.ENCODED_AUDIO:
            if not isinstance(signal.format, Codec):
                raise ValueError("encoded-audio SignalSpec requires a Codec")
            return cls.encoded_audio(signal.format)
        if signal.kind is SignalKind.TEXT:
            return cls.text()
        if signal.kind is SignalKind.EVENT:
            return cls.event()
        if signal.kind is SignalKind.METRICS:
            return cls.metrics()
        if signal.kind is SignalKind.CONTROL:
            return cls.control()
        if signal.kind is SignalKind.BINARY:
            format = signal.format
            return cls.binary(
                format if isinstance(format, BinaryFormat) else BinaryFormat.RAW
            )
        return cls.any()

    def is_compatible_with(self, other: MediaCaps) -> bool:
        return self._native.is_compatible_with(other._native)

    def negotiate(self, other: MediaCaps) -> MediaCaps | None:
        """Return Core's narrow compatible media requirements, if any."""
        native = self._native.negotiate(other._native)
        return None if native is None else type(self)._from_native(native)

    def supports_signal(self, signal: SignalSpec[object]) -> bool:
        return self._native.supports_signal(signal._native)


class PortDirection(StrEnum):
    INPUT = "input"
    OUTPUT = "output"


class Multiplicity(StrEnum):
    ONE = "one"
    MANY = "many"


@dataclass(frozen=True, slots=True)
class PortSpec:
    """Named typed graph port validated by the Rust ``PortSpec`` owner."""

    name: str
    direction: PortDirection
    signal: SignalSpec[object]
    media: MediaCaps
    multiplicity: Multiplicity = Multiplicity.ONE
    required: bool = True
    _native: _NativePortSpec = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativePortSpec(
                self.name,
                self.direction.value,
                self.signal._native,
                self.media._native,
                self.multiplicity.value,
                self.required,
            )
        )
        object.__setattr__(self, "_native", native)

    @classmethod
    def input(
        cls,
        name: str,
        signal: SignalSpec[object],
        *,
        media: MediaCaps | None = None,
        multiplicity: Multiplicity = Multiplicity.ONE,
        required: bool = True,
    ) -> PortSpec:
        """Declare an input port and infer its normal media requirements."""
        return cls(
            name,
            PortDirection.INPUT,
            signal,
            media or MediaCaps.for_signal(signal),
            multiplicity,
            required,
        )

    @classmethod
    def output(
        cls,
        name: str,
        signal: SignalSpec[object],
        *,
        media: MediaCaps | None = None,
        multiplicity: Multiplicity = Multiplicity.ONE,
        required: bool = True,
    ) -> PortSpec:
        """Declare an output port and infer its normal media requirements."""
        return cls(
            name,
            PortDirection.OUTPUT,
            signal,
            media or MediaCaps.for_signal(signal),
            multiplicity,
            required,
        )


class ClockDomain(StrEnum):
    CAPTURE = "capture"
    PLAYBACK = "playback"
    NETWORK = "network"
    INHERITED = "inherited"
    WALLCLOCK = "wallclock"

    @property
    def is_realtime(self) -> bool:
        return self in {ClockDomain.CAPTURE, ClockDomain.PLAYBACK}


class BackpressurePolicy(StrEnum):
    DROP_NEWEST = "drop-newest"
    DROP_OLDEST = "drop-oldest"
    BOUNDED_QUEUE = "bounded-queue"
    BLOCK_FORBIDDEN = "block-forbidden"


class DeliverySemantics(StrEnum):
    BEST_EFFORT_REALTIME = "best-effort-realtime"
    ORDERED = "ordered"
    EXACTLY_ONCE_NOT_REALTIME = "exactly-once-not-realtime"


class LossPolicy(StrEnum):
    CONCEAL_FOR_AUDIO = "conceal-for-audio"
    MUST_DELIVER_OR_FAIL = "must-deliver-or-fail"
    DROP_ALLOWED = "drop-allowed"


class CopyPolicy(StrEnum):
    MOVE_EXCLUSIVE = "move-exclusive"
    SHARE_READ_ONLY = "share-read-only"
    COPY_TO_BRANCH_POOL = "copy-to-branch-pool"


class RouteObservability(StrEnum):
    OFF = "off"
    COUNTERS = "counters"
    FULL = "full"

    @property
    def rank(self) -> int:
        return {
            RouteObservability.OFF: 0,
            RouteObservability.COUNTERS: 1,
            RouteObservability.FULL: 2,
        }[self]


@dataclass(frozen=True, slots=True, eq=False)
class DeliveryPolicy:
    """Choose how a route behaves when delivery slows or fails."""

    _native: _NativeRouteSettings = field(repr=False, compare=False)

    @classmethod
    def realtime_audio(cls) -> DeliveryPolicy:
        return cls(_NativeRouteSettings.realtime_audio())

    @classmethod
    def bounded_async(cls) -> DeliveryPolicy:
        return cls(_NativeRouteSettings.bounded_async())

    @property
    def clock(self) -> ClockDomain:
        return ClockDomain(self._native.clock)

    @property
    def latency_budget_ms(self) -> int | None:
        return self._native.latency_budget_ms

    @property
    def jitter_budget_ms(self) -> int | None:
        return self._native.jitter_budget_ms

    @property
    def backpressure(self) -> BackpressurePolicy:
        return BackpressurePolicy(self._native.backpressure)

    @property
    def delivery(self) -> DeliverySemantics:
        return DeliverySemantics(self._native.delivery)

    @property
    def loss(self) -> LossPolicy:
        return LossPolicy(self._native.loss)

    @property
    def copy_policy(self) -> CopyPolicy:
        return CopyPolicy(self._native.copy_policy)

    @property
    def observability(self) -> RouteObservability:
        return RouteObservability(self._native.observability)

    @property
    def max_payload_bytes(self) -> int | None:
        return self._native.max_payload_bytes

    def with_backpressure(self, policy: BackpressurePolicy) -> DeliveryPolicy:
        return type(self)(
            _native_call(lambda: self._native.with_backpressure(policy.value))
        )

    def with_copy_policy(self, policy: CopyPolicy) -> DeliveryPolicy:
        return type(self)(
            _native_call(lambda: self._native.with_copy_policy(policy.value))
        )

    def with_jitter_budget_ms(self, budget_ms: int | None) -> DeliveryPolicy:
        return type(self)(self._native.with_jitter_budget_ms(budget_ms))

    def with_max_payload_bytes(self, maximum_bytes: int) -> DeliveryPolicy:
        return type(self)(
            _native_call(lambda: self._native.with_max_payload_bytes(maximum_bytes))
        )

    def _values(self) -> tuple[object, ...]:
        return (
            self.clock,
            self.latency_budget_ms,
            self.jitter_budget_ms,
            self.backpressure,
            self.delivery,
            self.loss,
            self.copy_policy,
            self.observability,
            self.max_payload_bytes,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DeliveryPolicy) and self._values() == other._values()

    def __hash__(self) -> int:
        return hash(self._values())


@dataclass(frozen=True, slots=True, eq=False)
class RouteSettings:
    """Choose the media accepted by a route and how that route delivers it."""

    _native: _NativeRouteSettings = field(repr=False, compare=False)

    @classmethod
    def realtime_audio(cls) -> RouteSettings:
        return cls(_NativeRouteSettings.realtime_audio())

    @classmethod
    def bounded_async(cls) -> RouteSettings:
        return cls(_NativeRouteSettings.bounded_async())

    @property
    def media(self) -> MediaCaps:
        return _media_from_native(self._native.media)

    @property
    def clock(self) -> ClockDomain:
        return ClockDomain(self._native.clock)

    @property
    def latency_budget_ms(self) -> int | None:
        return self._native.latency_budget_ms

    @property
    def jitter_budget_ms(self) -> int | None:
        return self._native.jitter_budget_ms

    @property
    def backpressure(self) -> BackpressurePolicy:
        return BackpressurePolicy(self._native.backpressure)

    @property
    def delivery(self) -> DeliverySemantics:
        return DeliverySemantics(self._native.delivery)

    @property
    def loss(self) -> LossPolicy:
        return LossPolicy(self._native.loss)

    @property
    def copy_policy(self) -> CopyPolicy:
        return CopyPolicy(self._native.copy_policy)

    @property
    def observability(self) -> RouteObservability:
        return RouteObservability(self._native.observability)

    @property
    def max_payload_bytes(self) -> int | None:
        return self._native.max_payload_bytes

    @property
    def delivery_policy(self) -> DeliveryPolicy:
        return DeliveryPolicy(self._native)

    def with_media(self, media: MediaCaps) -> RouteSettings:
        return type(self)(self._native.with_media(media._native))

    def with_delivery_policy(self, policy: DeliveryPolicy) -> RouteSettings:
        return type(self)(policy._native.with_media(self.media._native))

    def with_backpressure(self, policy: BackpressurePolicy) -> RouteSettings:
        return type(self)(
            _native_call(lambda: self._native.with_backpressure(policy.value))
        )

    def with_copy_policy(self, policy: CopyPolicy) -> RouteSettings:
        return type(self)(
            _native_call(lambda: self._native.with_copy_policy(policy.value))
        )

    def with_jitter_budget_ms(self, budget_ms: int | None) -> RouteSettings:
        return type(self)(self._native.with_jitter_budget_ms(budget_ms))

    def with_max_payload_bytes(self, maximum_bytes: int) -> RouteSettings:
        return type(self)(
            _native_call(lambda: self._native.with_max_payload_bytes(maximum_bytes))
        )

    def _values(self) -> tuple[object, ...]:
        return (self.media, self.delivery_policy)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RouteSettings) and self._values() == other._values()

    def __hash__(self) -> int:
        return hash(self._values())


def _select_route_settings(
    route_settings: RouteSettings | None,
    default: RouteSettings,
) -> RouteSettings:
    return route_settings or default


ConfigurationInput: TypeAlias = Mapping[str, str] | Iterable[tuple[str, str]]


def _configuration_items(values: ConfigurationInput) -> tuple[tuple[str, str], ...]:
    entries = tuple(values.items() if isinstance(values, Mapping) else values)
    seen: set[str] = set()
    for key, _value in entries:
        if key in seen:
            raise ValueError(f"duplicate configuration key {key!r}")
        seen.add(key)
    return tuple(sorted(entries))


@dataclass(frozen=True, slots=True, init=False)
class OperatorConfiguration:
    values: tuple[tuple[str, str], ...]

    def __init__(self, values: ConfigurationInput = ()) -> None:
        object.__setattr__(self, "values", _configuration_items(values))

    def with_value(self, key: str, value: str) -> OperatorConfiguration:
        return type(self)(dict((*self.values, (key, value))))

    def _as_dict(self) -> dict[str, str]:
        return dict(self.values)


@dataclass(frozen=True, slots=True, init=False)
class SourceConfiguration:
    values: tuple[tuple[str, str], ...]

    def __init__(self, values: ConfigurationInput = ()) -> None:
        object.__setattr__(self, "values", _configuration_items(values))

    def with_value(self, key: str, value: str) -> SourceConfiguration:
        return type(self)(dict((*self.values, (key, value))))

    def _as_dict(self) -> dict[str, str]:
        return dict(self.values)


@dataclass(frozen=True, slots=True, init=False)
class EndpointConfiguration:
    values: tuple[tuple[str, str], ...]

    def __init__(self, values: ConfigurationInput = ()) -> None:
        object.__setattr__(self, "values", _configuration_items(values))

    def with_value(self, key: str, value: str) -> EndpointConfiguration:
        return type(self)(dict((*self.values, (key, value))))

    def _as_dict(self) -> dict[str, str]:
        return dict(self.values)


@dataclass(frozen=True, slots=True)
class Operator:
    """Open operator declaration; implementation registration is a later gate."""

    operator_id: str
    configuration: OperatorConfiguration = field(default_factory=OperatorConfiguration)


@dataclass(frozen=True, slots=True)
class EndpointDescriptor:
    """Open endpoint declaration lowered and validated by the Rust Session."""

    node_type_id: str
    operator_id: str
    configuration: EndpointConfiguration = field(default_factory=EndpointConfiguration)
    route_settings: RouteSettings | None = None
    _native: _NativeEndpointDescriptor = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        native = _native_call(
            lambda: _NativeEndpointDescriptor(
                self.node_type_id,
                self.operator_id,
                self.configuration._as_dict(),
                None if self.route_settings is None else self.route_settings._native,
            )
        )
        object.__setattr__(self, "_native", native)


class Endpoint:
    """Opaque Session-scoped destination handle."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeEndpoint) -> None:
        self._native = native

    @property
    def id(self) -> EndpointId:
        return EndpointId(self._native.id)

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def connector_id(self) -> ConnectorId | None:
        value = self._native.connector_id
        return None if value is None else ConnectorId(value)


class OperatorInput:
    """One explicit named input on a Session-owned operator instance."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeOperatorInput) -> None:
        self._native = native

    @property
    def port_name(self) -> str:
        return self._native.port_name


class OperatorInstance:
    """Session-scoped operator instance with explicit named ports."""

    __slots__ = ("_destination", "_native")

    def __init__(
        self,
        native: _NativeOperatorInstance,
        destination: _DestinationResolver,
    ) -> None:
        self._native = native
        self._destination = destination

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def instance_id(self) -> OperatorInstanceId:
        return OperatorInstanceId(self._native.instance_id)

    def input(self, port_name: str) -> OperatorInput:
        return _native_call(lambda: OperatorInput(self._native.input(port_name)))

    def output(self, port_name: str) -> DerivedStream:
        return _native_call(
            lambda: DerivedStream(self._native.output(port_name), self._destination)
        )


class _RoutableStream:
    __slots__ = ("_destination", "_endpoint_ids", "_route_ids")

    _native: _NativeStem | _NativeDerivedStream | _NativeSourceOutput
    _destination: _DestinationResolver
    _endpoint_ids: set[int]
    _route_ids: set[int]

    def send(self, endpoint: Endpoint, *, input_port: str | None = None) -> RouteId:
        route_id = RouteId(
            _native_call(
                lambda: (
                    self._native.send(endpoint._native)
                    if input_port is None
                    else self._native.send_to(endpoint._native, input_port)
                )
            )
        )
        self._route_ids.add(int(route_id))
        self._endpoint_ids.add(int(endpoint.id))
        return route_id

    def send_to(
        self,
        connector: _ConnectorTarget,
        *,
        input_port: str | None = None,
    ) -> RouteId:
        """Route to one Connector using this stream's owning Session.

        This is the concise one-destination form. Use
        ``Session.register_connector(...).declare(...)`` when one Connector
        implementation needs multiple configurations or explicit
        route settings.
        """
        return self.send(
            self._destination(connector),
            input_port=input_port,
        )

    def connect(self, input: OperatorInput) -> RouteId:
        route_id = RouteId(_native_call(lambda: self._native.connect(input._native)))
        self._route_ids.add(int(route_id))
        return route_id

    def _delivery_targets(self) -> tuple[frozenset[int], frozenset[int]]:
        """Return declarations needed for a finite delivery-completion wait."""
        return frozenset(self._route_ids), frozenset(self._endpoint_ids)

    def through(
        self,
        operator: Operator,
        *,
        input_port: str | None = None,
        output_port: str | None = None,
    ) -> DerivedStream:
        return _native_call(
            lambda: DerivedStream(
                self._native.through(
                    operator.operator_id,
                    operator.configuration._as_dict(),
                    input_port,
                    output_port,
                ),
                self._destination,
            )
        )


class Stem(_RoutableStream):
    """Independent source-aware PCM stream declared on a Session."""

    __slots__ = ("_native",)
    _native: _NativeStem

    def __init__(self, native: _NativeStem, destination: _DestinationResolver) -> None:
        self._native = native
        self._destination = destination
        self._route_ids = set()
        self._endpoint_ids = set()

    @property
    def id(self) -> StemId:
        return StemId(self._native.id)

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    def record(self, stem_name: str) -> Endpoint:
        endpoint = _native_call(lambda: Endpoint(self._native.record(stem_name)))
        self._endpoint_ids.add(int(endpoint.id))
        return endpoint

    def publish(self, publisher: RelayPublisher, bus_id: str) -> RelayRoute:
        """Publish this stem as one named bus through the Rust connector."""
        from .relay import RelayPublisher, RelayRoute

        if not isinstance(publisher, RelayPublisher):
            raise TypeError("publisher must be a RelayPublisher")
        route_id = _native_call(lambda: self._native.publish(publisher._native, bus_id))
        self._route_ids.add(route_id)
        return RelayRoute(bus_id=bus_id, route_id=RouteId(route_id))


class DerivedStream(_RoutableStream):
    """Named operator output that remains owned by the Rust Session draft."""

    __slots__ = ("_native",)
    _native: _NativeDerivedStream

    def __init__(
        self,
        native: _NativeDerivedStream,
        destination: _DestinationResolver,
    ) -> None:
        self._native = native
        self._destination = destination
        self._route_ids = set()
        self._endpoint_ids = set()

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def operator_instance_id(self) -> OperatorInstanceId:
        return OperatorInstanceId(self._native.operator_instance_id)

    @property
    def output_port(self) -> str | None:
        return self._native.output_port

    def output(self, port_name: str) -> DerivedStream:
        return _native_call(
            lambda: type(self)(self._native.output(port_name), self._destination)
        )

    def reenter_audio(self) -> Stem:
        """Return generated PCM through Core without a Python audio callback."""
        return _native_call(
            lambda: Stem(self._native.reenter_audio(), self._destination)
        )


class SourceInstance:
    """Open registered source declaration scoped to one Session."""

    __slots__ = ("_destination", "_native")

    def __init__(
        self,
        native: _NativeSourceInstance,
        destination: _DestinationResolver,
    ) -> None:
        self._native = native
        self._destination = destination

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def instance_id(self) -> SourceInstanceId:
        return SourceInstanceId(self._native.instance_id)

    @property
    def source_id(self) -> SourceId:
        return SourceId(self._native.source_id)

    def output(self, port_name: str) -> SourceOutput:
        return _native_call(
            lambda: SourceOutput(self._native.output(port_name), self._destination)
        )


class SourceOutput(_RoutableStream):
    """One named output from an externally registered source instance."""

    __slots__ = ("_native",)
    _native: _NativeSourceOutput

    def __init__(
        self,
        native: _NativeSourceOutput,
        destination: _DestinationResolver,
    ) -> None:
        self._native = native
        self._destination = destination
        self._route_ids = set()
        self._endpoint_ids = set()

    @property
    def session_id(self) -> RuntimeSessionId:
        return RuntimeSessionId(self._native.session_id)

    @property
    def source_instance_id(self) -> SourceInstanceId:
        return SourceInstanceId(self._native.source_instance_id)

    @property
    def source_id(self) -> SourceId:
        return SourceId(self._native.source_id)

    @property
    def stream_id(self) -> StreamId:
        return StreamId(self._native.stream_id)

    @property
    def output_port(self) -> str:
        return self._native.output_port

    def record(self, stem_name: str) -> Endpoint:
        endpoint = _native_call(lambda: Endpoint(self._native.record(stem_name)))
        self._endpoint_ids.add(int(endpoint.id))
        return endpoint

    def publish(self, publisher: RelayPublisher, bus_id: str) -> RelayRoute:
        """Publish this source output as one named Relay AudioBus."""
        from .relay import RelayPublisher, RelayRoute

        if not isinstance(publisher, RelayPublisher):
            raise TypeError("publisher must be a RelayPublisher")
        route_id = _native_call(lambda: self._native.publish(publisher._native, bus_id))
        self._route_ids.add(route_id)
        return RelayRoute(bus_id=bus_id, route_id=RouteId(route_id))


class _GraphSessionDeclarations:
    """One shared sync/async policy for immediate Rust draft declarations."""

    _native: _NativeSession

    def _destination_for_stream(self, connector: object) -> Endpoint:
        """Call the concrete sync or asyncio Session declaration method."""
        return cast(Endpoint, cast(Any, self).destination(connector))

    @property
    def id(self) -> RuntimeSessionId:
        """Return the stable identity allocated by the Rust Session."""
        return RuntimeSessionId(self._native.id)

    def source(
        self,
        source_type_id: str,
        configuration: SourceConfiguration | None = None,
    ) -> SourceInstance:
        """Declare one instance of an open, externally registered source."""
        values = SourceConfiguration() if configuration is None else configuration
        return _native_call(
            lambda: SourceInstance(
                self._native.source(source_type_id, values._as_dict()),
                self._destination_for_stream,
            )
        )

    def operator(self, operator: Operator) -> OperatorInstance:
        """Declare one open operator instance with named ports."""
        return _native_call(
            lambda: OperatorInstance(
                self._native.operator(
                    operator.operator_id,
                    operator.configuration._as_dict(),
                ),
                self._destination_for_stream,
            )
        )

    def endpoint(self, descriptor: EndpointDescriptor) -> Endpoint:
        """Declare one open Endpoint descriptor on the Session draft."""
        return _native_call(lambda: Endpoint(self._native.endpoint(descriptor._native)))

    def browser(self, receiver_uri: str) -> Endpoint:
        """Declare the frozen browser or remote-receiver Endpoint."""
        return _native_call(lambda: Endpoint(self._native.browser(receiver_uri)))

    def subscribe(
        self,
        stream: DerivedStream | SourceOutput,
        *,
        signal: SignalSpec[_PayloadT],
        route_settings: RouteSettings | None = None,
    ) -> BusSubscription[_PayloadT]:
        """Declare one bounded, exclusive typed-signal subscription.

        The subscription is an Endpoint in the Rust Session.
        Python owns no additional queue, router, or background pump.
        """
        from .signal import BusSubscription

        settings = _select_route_settings(
            route_settings,
            RouteSettings.bounded_async().with_media(_media_for_signal(signal)),
        )
        if isinstance(stream, DerivedStream):
            native = _native_call(
                lambda: self._native.subscribe_derived(
                    stream._native,
                    signal._native,
                    settings._native,
                )
            )
        elif isinstance(stream, SourceOutput):
            native = _native_call(
                lambda: self._native.subscribe_source_output(
                    stream._native,
                    signal._native,
                    settings._native,
                )
            )
        else:
            raise TypeError("stream must be a DerivedStream or SourceOutput")
        return BusSubscription(native)


def _media_from_native(native: _NativeMediaCaps) -> MediaCaps:
    kind = MediaKind(native.kind)
    if kind is MediaKind.AUDIO_PCM:
        caps = AudioCaps(
            sample_rate_hz=native.sample_rate_hz,
            frame_samples=native.frame_samples,
            channel_layout=ChannelLayout(native.channel_layout or "any"),
        )
        return MediaCaps(kind, audio_caps=caps)
    if kind is MediaKind.AUDIO_ENCODED:
        format = native.format
        if format is None:
            raise AssertionError("Rust encoded-audio media omitted its codec")
        return MediaCaps(kind, format=Codec(format))
    if kind is MediaKind.BINARY:
        format = native.format
        if format is None:
            raise AssertionError("Rust binary media omitted its format")
        return MediaCaps(kind, format=BinaryFormat(format))
    return MediaCaps(kind)


def _media_for_signal(signal: SignalSpec[object]) -> MediaCaps:
    if signal.kind is SignalKind.PCM_AUDIO:
        return MediaCaps.audio()
    if signal.kind is SignalKind.ENCODED_AUDIO:
        if not isinstance(signal.format, Codec):
            raise AssertionError("encoded-audio SignalSpec omitted its codec")
        return MediaCaps.encoded_audio(signal.format)
    if signal.kind is SignalKind.TEXT:
        return MediaCaps.text()
    if signal.kind is SignalKind.EVENT:
        return MediaCaps.event()
    if signal.kind is SignalKind.METRICS:
        return MediaCaps.metrics()
    if signal.kind is SignalKind.CONTROL:
        return MediaCaps.control()
    if signal.kind is SignalKind.BINARY:
        format = (
            signal.format
            if isinstance(signal.format, BinaryFormat)
            else BinaryFormat.RAW
        )
        return MediaCaps.binary(format)
    return MediaCaps.any()


__all__ = [
    "AudioCaps",
    "BackpressurePolicy",
    "BinaryFormat",
    "ChannelLayout",
    "ClockDomain",
    "Codec",
    "CopyPolicy",
    "DeliveryPolicy",
    "DeliverySemantics",
    "DerivedStream",
    "Endpoint",
    "EndpointConfiguration",
    "EndpointDescriptor",
    "EventFormat",
    "LossPolicy",
    "MediaCaps",
    "MediaKind",
    "Multiplicity",
    "Operator",
    "OperatorConfiguration",
    "OperatorInput",
    "OperatorInstance",
    "PortDirection",
    "PortSpec",
    "RouteObservability",
    "RouteSettings",
    "SampleFormat",
    "SignalKind",
    "SignalSpec",
    "SourceConfiguration",
    "SourceInstance",
    "SourceOutput",
    "Stem",
    "TextFormat",
]
