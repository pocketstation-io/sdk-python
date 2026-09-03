"""Real Session conformance for bounded typed-signal subscriptions."""

from __future__ import annotations

from pathlib import Path
from time import monotonic

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    STREAM_EOF,
    BackpressurePolicy,
    BinaryFormat,
    Operator,
    PocketStationError,
    Session,
    SignalAudioPayload,
    SignalEnvelope,
    SignalSpec,
    Source,
    TextFormat,
    aio,
)

AUDIO_OPERATOR = "org.pocketstation.python.conformance.audio-pass-through.v1"
TEXT_OPERATOR = "org.pocketstation.python.conformance.audio-to-text.v1"
BYTES_OPERATOR = "org.pocketstation.python.conformance.audio-to-bytes.v1"


def _native_conformance_session(recording_root: Path):
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    return _native.Session.conformance(recording_root)


def _declared_session(recording_root: Path, *, asynchronous: bool = False):
    native = _native_conformance_session(recording_root)
    session = (
        aio.Session._from_native(native)
        if asynchronous
        else Session._from_native(native)
    )
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    application.send(session.polled_audio())

    audio = microphone.through(
        Operator(AUDIO_OPERATOR),
        input_port="audio-in",
        output_port="audio-out",
    )
    text = microphone.through(
        Operator(TEXT_OPERATOR),
        input_port="audio-in",
        output_port="text-out",
    )
    binary = microphone.through(
        Operator(BYTES_OPERATOR),
        input_port="audio-in",
        output_port="bytes-out",
    )
    return session, {
        "audio": session.subscribe(audio, signal=SignalSpec.audio()),
        "text": session.subscribe(text, signal=SignalSpec.text()),
        "bytes": session.subscribe(
            binary,
            signal=SignalSpec.binary(BinaryFormat.RAW),
        ),
    }


def _read_envelope(stream, timeout_s: float = 2.0) -> SignalEnvelope:
    deadline = monotonic() + timeout_s
    while monotonic() < deadline:
        value = stream.read(timeout_s=0.1)
        if isinstance(value, SignalEnvelope):
            return value
        assert value is not STREAM_EOF
    raise AssertionError("typed signal did not arrive before the bounded deadline")


def test_real_session_delivers_audio_text_and_bytes_with_complete_provenance(
    tmp_path: Path,
) -> None:
    session, subscriptions = _declared_session(tmp_path)
    running = session.start()
    audio_stream = running.signals(subscriptions["audio"])
    text_stream = running.signals(subscriptions["text"])
    bytes_stream = running.signals(subscriptions["bytes"])

    audio = _read_envelope(audio_stream)
    text = _read_envelope(text_stream)
    binary = _read_envelope(bytes_stream)
    audio_payload = audio.payload
    assert isinstance(audio_payload, SignalAudioPayload)
    snapshot = audio_payload.samples_f32le

    assert audio.signal == SignalSpec.audio()
    assert audio.lineage is not None
    assert audio.lineage.clock.id == audio.lineage.clock_id
    assert audio.lineage.clock.kind == "process-monotonic"
    assert audio.lineage.clock.origin == "process-start"
    assert audio.lineage.clock.tick_rate_hz == 1_000_000_000
    assert audio.derivation is not None
    assert audio.derivation.upstream_lineage == audio.lineage
    assert audio_payload.source_id == audio.lineage.source_id
    assert audio_payload.stream_id == audio.lineage.stream_id
    assert audio_payload.sequence_number == audio.lineage.sequence_number
    assert audio_payload.samples.readonly
    assert audio_payload.sample_count > 0

    assert text.signal == SignalSpec.text(TextFormat.UTF8)
    assert isinstance(text.payload, str)
    assert text.lineage is not None
    assert f"source={text.lineage.source_id}" in text.payload
    assert text.derivation is not None
    assert text.derivation.operator_id == TEXT_OPERATOR

    assert binary.signal == SignalSpec.binary(BinaryFormat.RAW)
    assert isinstance(binary.payload, bytes)
    assert len(binary.payload) == 8
    assert binary.lineage is not None
    assert int.from_bytes(binary.payload, "little") == binary.lineage.sequence_number
    assert binary.derivation is not None
    assert binary.derivation.operator_id == BYTES_OPERATOR

    assert running.signals(subscriptions["audio"]) is audio_stream
    streams = {
        "audio": audio_stream,
        "text": text_stream,
        "bytes": bytes_stream,
    }
    for name, subscription in subscriptions.items():
        assert (
            subscription.route_settings.backpressure is BackpressurePolicy.BOUNDED_QUEUE
        )
        assert subscription.route_settings.max_payload_bytes == 1_048_576
        metrics = streams[name].metrics()
        assert metrics.capacity_signals > 0
        assert metrics.max_payload_bytes == 1_048_576
        assert metrics.maximum_buffered_payload_bytes == (
            metrics.capacity_signals * metrics.max_payload_bytes
        )
        assert metrics.enqueued_total >= metrics.received_total > 0
        assert metrics.dropped_total >= 0
    assert running.stop().success
    assert audio_stream.read(timeout_s=0.0) is STREAM_EOF
    assert text_stream.read(timeout_s=0.0) is STREAM_EOF
    assert bytes_stream.read(timeout_s=0.0) is STREAM_EOF
    assert audio_payload.samples_f32le == snapshot


def test_subscription_close_is_idempotent_and_does_not_stop_other_routes(
    tmp_path: Path,
) -> None:
    session, subscriptions = _declared_session(tmp_path)
    running = session.start()
    text_stream = running.signals(subscriptions["text"])
    bytes_stream = running.signals(subscriptions["bytes"])

    text_stream.close()
    text_stream.close()
    assert text_stream.poll() is STREAM_EOF
    assert isinstance(_read_envelope(bytes_stream), SignalEnvelope)
    assert running.stop().success


def test_external_source_outputs_have_the_same_subscription_declaration() -> None:
    session = Session()
    source = session.source("org.example.source.typed.v1")
    subscription = session.subscribe(
        source.output("events"),
        signal=SignalSpec.text(TextFormat.JSON),
    )

    assert subscription.session_id == session.id
    assert subscription.signal == SignalSpec.text(TextFormat.JSON)
    assert subscription.route_settings.media.supports_signal(subscription.signal)
    assert subscription.route_id > 0


def test_running_session_rejects_a_foreign_subscription(tmp_path: Path) -> None:
    session, _ = _declared_session(tmp_path / "local")
    _, foreign = _declared_session(tmp_path / "foreign")
    running = session.start()
    try:
        with pytest.raises(PocketStationError) as failure:
            running.signals(foreign["text"]).poll()
        assert failure.value.code == "session.invalid_route"
    finally:
        assert running.stop().success


@pytest.mark.asyncio
async def test_async_real_session_preserves_the_same_signal_contract(
    tmp_path: Path,
) -> None:
    session, subscriptions = _declared_session(tmp_path, asynchronous=True)
    running = await session.start()
    stream = running.signals(subscriptions["text"])
    deadline = monotonic() + 2.0
    envelope = None
    while monotonic() < deadline:
        value = await stream.read(timeout_s=0.1)
        if isinstance(value, SignalEnvelope):
            envelope = value
            break
        assert value is not STREAM_EOF

    assert envelope is not None
    assert isinstance(envelope.payload, str)
    assert envelope.lineage is not None
    assert envelope.derivation is not None
    assert (await running.stop()).success
    assert await stream.read(timeout_s=0.0) is STREAM_EOF
