"""Static-only checks for signal payload and runtime identity preservation."""

from typing import assert_type

from pocketstation.aec import (
    EchoCancellationObservations,
    EchoCancellationState,
    EchoCancelledAudio,
    NativePlaybackReference,
    PlaybackReference,
)
from pocketstation.aio import Session as AsyncSession
from pocketstation.aio.connector import Connector as AsyncConnector
from pocketstation.connector import Connector
from pocketstation.graph import SignalSpec, SourceOutput, Stem
from pocketstation.identity import (
    ClockDomainId,
    ConnectorId,
    EndpointId,
    RouteId,
    RuntimeSessionId,
    SourceId,
    StemId,
    StreamId,
)
from pocketstation.session import RunningSession, Session
from pocketstation.signal import AudioProcessing, BusSubscription, SignalAudioPayload
from pocketstation.streams import AudioFrame


def verify_signal_types(
    session: Session,
    source: SourceOutput,
    connector: Connector,
    async_connector: AsyncConnector,
) -> None:
    audio_spec = SignalSpec.audio()
    text_spec = SignalSpec.text()
    assert_type(audio_spec, SignalSpec[SignalAudioPayload])
    assert_type(text_spec, SignalSpec[str])

    audio_subscription = session.subscribe(source, signal=audio_spec)
    text_subscription = session.subscribe(source, signal=text_spec)
    assert_type(audio_subscription, BusSubscription[SignalAudioPayload])
    assert_type(text_subscription, BusSubscription[str])
    assert_type(audio_subscription.session_id, RuntimeSessionId)
    assert_type(audio_subscription.route_id, RouteId)
    assert_type(source.send_to(connector), RouteId)
    assert_type(source.send_to(async_connector), RouteId)


def verify_runtime_identities(running: RunningSession, frame: AudioFrame) -> None:
    assert_type(running.session_id, RuntimeSessionId)
    assert_type(frame.session_id, RuntimeSessionId)
    assert_type(frame.stream_id, StreamId)
    assert_type(frame.source_id, SourceId)
    assert_type(frame.stem_id, StemId)
    assert_type(frame.clock_id, ClockDomainId)
    assert_type(frame.endpoint_id, EndpointId)
    assert_type(frame.connector_id, ConnectorId | None)
    assert_type(frame.route_id, RouteId)
    assert_type(frame.processing, AudioProcessing | None)
    if frame.processing is not None:
        assert_type(frame.processing.input_source_id, SourceId)
        assert_type(frame.processing.input_stream_id, StreamId)
        assert_type(frame.processing.is_tail, bool)


def verify_echo_types(
    session: Session | AsyncSession, microphone: Stem, reference: SourceOutput
) -> None:
    cleaned = session.echo_cancel(
        microphone, PlaybackReference.selected_application(reference)
    )
    assert_type(cleaned, EchoCancelledAudio)
    assert_type(cleaned.audio, Stem)
    assert_type(cleaned.reference, PlaybackReference)
    observation = cleaned.observations()
    assert_type(observation, EchoCancellationObservations)
    assert_type(observation.state, EchoCancellationState)
    assert_type(observation.qualified_algorithmic_delay_samples, int | None)
    assert_type(observation.microphone_source_id, SourceId | None)
    assert_type(observation.tail_padding_samples_total, int)
    assert_type(observation.nominal_delay_samples, int)


def verify_native_echo_types(session: Session | AsyncSession, microphone: Stem) -> None:
    reference = NativePlaybackReference.output("exact-output-device")
    assert_type(reference.playback_device_id, str)
    assert_type(session.native_aec(microphone, reference), None)
