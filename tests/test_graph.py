"""Typed graph declarations owned by the Rust Session."""

from __future__ import annotations

import pytest
from pocketstation._api import (
    AudioCaps,
    BackpressurePolicy,
    BinaryFormat,
    ChannelLayout,
    ClockDomain,
    Codec,
    CopyPolicy,
    DeliverySemantics,
    EdgeContract,
    EdgeObservabilityLevel,
    EndpointConfiguration,
    EndpointDescriptor,
    EventFormat,
    LossPolicy,
    MediaCaps,
    Multiplicity,
    Operator,
    OperatorConfiguration,
    PocketStationError,
    PortDirection,
    PortSpec,
    Session,
    SessionStartError,
    SignalSpec,
    Source,
    SourceConfiguration,
    TextFormat,
    aio,
)


@pytest.mark.parametrize(
    ("signal", "wire_id", "is_audio"),
    [
        (SignalSpec.any(), "pks.signal.any.v1", False),
        (SignalSpec.audio(), "pks.signal.pcm-audio.v1", True),
        (
            SignalSpec.encoded_audio(Codec.OPUS),
            "pks.signal.encoded.opus.v1",
            True,
        ),
        (SignalSpec.text(TextFormat.JSON), "pks.signal.text.json.v1", False),
        (SignalSpec.event(EventFormat.CBOR), "pks.signal.event.cbor.v1", False),
        (SignalSpec.metrics(), "pks.signal.metrics.v1", False),
        (SignalSpec.control(), "pks.signal.control.v1", False),
        (
            SignalSpec.binary(BinaryFormat.FLATBUFFERS),
            "pks.signal.binary.flatbuffers.v1",
            False,
        ),
        (
            SignalSpec.custom("org.example.embedding.v1"),
            "org.example.embedding.v1",
            False,
        ),
    ],
)
def test_signal_specs_preserve_rust_wire_identity(
    signal: SignalSpec,
    wire_id: str,
    is_audio: bool,
) -> None:
    assert signal.wire_id == wire_id
    assert signal.is_audio is is_audio


def test_signal_role_schema_and_compatibility_remain_open_and_typed() -> None:
    partial = SignalSpec.text(
        TextFormat.JSON,
        role="transcript.partial",
        schema="https://example.test/transcript.schema.json",
    )
    final = SignalSpec.text(TextFormat.JSON, role="transcript.final")

    assert partial.role == "transcript.partial"
    assert partial.schema == "https://example.test/transcript.schema.json"
    assert partial.is_compatible_with(final)
    assert SignalSpec.any().is_compatible_with(SignalSpec.audio())
    assert not partial.is_compatible_with(SignalSpec.audio())


@pytest.mark.parametrize(
    "factory",
    [
        lambda: SignalSpec.custom(""),
        lambda: SignalSpec.text(role=""),
        lambda: SignalSpec.event(schema=""),
    ],
)
def test_invalid_signal_contracts_return_stable_rust_error(factory) -> None:
    with pytest.raises(PocketStationError) as failure:
        factory()
    assert failure.value.code == "graph.invalid_contract"


def test_media_caps_and_port_specs_are_rust_validated() -> None:
    exact = MediaCaps.audio(
        AudioCaps(
            sample_rate_hz=48_000,
            frame_samples=960,
            channel_layout=ChannelLayout.MONO,
        )
    )
    wildcard = MediaCaps.audio()
    stereo = MediaCaps.audio(
        AudioCaps(
            sample_rate_hz=48_000,
            frame_samples=960,
            channel_layout=ChannelLayout.STEREO,
        )
    )

    assert wildcard.is_compatible_with(exact)
    assert not exact.is_compatible_with(stereo)
    assert MediaCaps.any().negotiate(exact) == exact
    assert wildcard.negotiate(exact) == exact
    assert exact.negotiate(MediaCaps.text()) is None
    assert exact.supports_signal(SignalSpec.audio())
    assert ChannelLayout.MONO.channel_count == 1
    assert ChannelLayout.STEREO.channel_count == 2
    assert ChannelLayout.ANY.channel_count is None
    port = PortSpec(
        "audio-in",
        PortDirection.INPUT,
        SignalSpec.audio(),
        exact,
        Multiplicity.MANY,
        required=True,
    )
    assert port.name == "audio-in"
    with pytest.raises(PocketStationError) as failure:
        PortSpec(
            "bad",
            PortDirection.INPUT,
            SignalSpec.text(),
            exact,
        )
    assert failure.value.code == "graph.invalid_contract"


def test_port_helpers_infer_media_without_hiding_explicit_contracts() -> None:
    text = SignalSpec.text(role="request")
    input_port = PortSpec.input("input", text)
    output_port = PortSpec.output(
        "output",
        text,
        media=MediaCaps.text(),
        multiplicity=Multiplicity.MANY,
    )

    assert input_port.direction is PortDirection.INPUT
    assert input_port.media.kind.value == "text"
    assert output_port.direction is PortDirection.OUTPUT
    assert output_port.media.kind.value == "text"
    assert output_port.multiplicity is Multiplicity.MANY


def test_edge_presets_and_modifiers_preserve_bounded_contracts() -> None:
    realtime = EdgeContract.realtime_audio()
    assert realtime.clock is ClockDomain.CAPTURE
    assert realtime.backpressure is BackpressurePolicy.DROP_NEWEST
    assert realtime.delivery is DeliverySemantics.ORDERED
    assert realtime.loss is LossPolicy.CONCEAL_FOR_AUDIO
    assert realtime.copy_policy is CopyPolicy.SHARE_READ_ONLY
    assert realtime.observability is EdgeObservabilityLevel.COUNTERS
    assert realtime.max_payload_bytes is None
    assert realtime.clock.is_realtime
    assert not ClockDomain.INHERITED.is_realtime
    assert EdgeObservabilityLevel.FULL.rank > realtime.observability.rank

    bounded = EdgeContract.bounded_async()
    assert bounded.clock is ClockDomain.INHERITED
    assert bounded.backpressure is BackpressurePolicy.BOUNDED_QUEUE
    assert bounded.delivery is DeliverySemantics.ORDERED
    assert bounded.loss is LossPolicy.MUST_DELIVER_OR_FAIL
    assert bounded.max_payload_bytes == 1_048_576

    changed = (
        bounded.with_backpressure(BackpressurePolicy.DROP_OLDEST)
        .with_copy_policy(CopyPolicy.COPY_TO_BRANCH_POOL)
        .with_jitter_budget_ms(25)
        .with_max_payload_bytes(4096)
    )
    assert changed.backpressure is BackpressurePolicy.DROP_OLDEST
    assert changed.copy_policy is CopyPolicy.COPY_TO_BRANCH_POOL
    assert changed.jitter_budget_ms == 25
    assert changed.max_payload_bytes == 4096
    assert bounded.backpressure is BackpressurePolicy.BOUNDED_QUEUE


def test_configuration_values_are_immutable_snapshots() -> None:
    original = {"model": "small"}
    operator = OperatorConfiguration(original)
    source = SourceConfiguration(original)
    endpoint = EndpointConfiguration(original)
    original["model"] = "large"

    assert operator.values == (("model", "small"),)
    assert source.values == (("model", "small"),)
    assert endpoint.values == (("model", "small"),)
    assert operator.with_value("model", "large").values == (("model", "large"),)


@pytest.mark.parametrize(
    "configuration_type",
    (OperatorConfiguration, SourceConfiguration, EndpointConfiguration),
)
def test_configuration_rejects_duplicate_keys(configuration_type) -> None:
    with pytest.raises(ValueError, match="duplicate configuration key 'mode'"):
        configuration_type((("mode", "first"), ("mode", "second")))


def test_graph_declarations_lower_immediately_to_one_rust_session(tmp_path) -> None:
    session = Session(recording_root=tmp_path)
    application = session.capture(Source.application("PocketStation Fixture"))
    microphone = session.capture(Source.microphone_default())
    operator = session.operator(
        Operator(
            "org.example.transcriber.v1",
            OperatorConfiguration({"language": "en"}),
        )
    )
    connector = session.connector(
        "org.example.connector.v1",
        EndpointConfiguration({"region": "local"}),
    )
    browser = session.browser("https://receiver.example.test")
    endpoint = session.endpoint(
        EndpointDescriptor(
            "org.example.endpoint-node.v1",
            "org.example.endpoint.v1",
            EndpointConfiguration({"mode": "events"}),
            EdgeContract.bounded_async(),
        )
    )

    first_route = application.connect(operator.input("audio-in"))
    output = operator.output("transcript")
    second_route = output.send(connector, input_port="events")
    assert application.session_id == session.id
    assert microphone.session_id == session.id
    assert operator.session_id == session.id
    assert connector.session_id == session.id
    assert browser.session_id == session.id
    assert endpoint.session_id == session.id
    assert output.output_port == "transcript"
    assert first_route != second_route


def test_open_external_source_declaration_and_routes_are_session_owned() -> None:
    session = Session()
    source = session.source(
        "org.example.source.external.v1",
        SourceConfiguration({"uri": "fixture://source"}),
    )
    output = source.output("audio-out")
    operator = session.operator(Operator("org.example.operator.v1"))

    route = output.connect(operator.input("audio-in"))
    assert source.session_id == session.id
    assert output.session_id == session.id
    assert output.output_port == "audio-out"
    assert route > 0


def test_cross_session_graph_handles_are_rejected_by_rust() -> None:
    first = Session()
    second = Session()
    stem = first.capture(Source.microphone_default())
    foreign_endpoint = second.polled_audio()
    foreign_input = second.operator(Operator("org.example.operator.v1")).input(
        "audio-in"
    )

    with pytest.raises(PocketStationError) as endpoint_failure:
        stem.send(foreign_endpoint)
    with pytest.raises(PocketStationError) as input_failure:
        stem.connect(foreign_input)
    assert endpoint_failure.value.code.startswith("session.")
    assert input_failure.value.code.startswith("session.")


def test_unknown_operator_is_rejected_by_the_canonical_compiler() -> None:
    session = Session()
    microphone = session.capture(Source.microphone_default())
    derived = microphone.through(Operator("org.example.missing.v1"))
    derived.send(session.polled_audio())

    with pytest.raises(PocketStationError) as failure:
        session.start()
    assert failure.value.code == "session.compile_failed"
    assert "operator org.example.missing.v1 is not registered" in str(failure.value)
    assert isinstance(failure.value, SessionStartError)
    assert failure.value.diagnostic is not None
    assert failure.value.diagnostic.code == "compile.unknown_async_operator"
    assert failure.value.diagnostic.operator_id == "org.example.missing.v1"


def test_sync_and_async_sessions_share_the_same_graph_declaration_surface() -> None:
    sync_session = Session()
    async_session = aio.Session()

    for session in (sync_session, async_session):
        assert session.id > 0
        declared = session.operator(Operator("org.example.operator.v1"))
        assert declared.session_id == session.id
        assert session.connector("org.example.connector.v1").session_id == session.id
