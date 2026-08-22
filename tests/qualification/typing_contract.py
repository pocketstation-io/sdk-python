"""Static-only checks for signal payload and runtime identity preservation."""

from typing import assert_type

from pocketstation.aio.connector import Connector as AsyncConnector
from pocketstation.connector import Connector
from pocketstation.graph import SignalSpec, SourceOutput
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
from pocketstation.signal import BusSubscription, SignalAudioPayload
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
