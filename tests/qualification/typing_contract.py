"""Static-only checks for signal payload and runtime identity preservation."""

from typing import assert_type

import pocketstation


def verify_signal_types(
    session: pocketstation.Session,
    source: pocketstation.SourceOutput,
) -> None:
    audio_spec = pocketstation.SignalSpec.audio()
    text_spec = pocketstation.SignalSpec.text()
    assert_type(audio_spec, pocketstation.SignalSpec[pocketstation.SignalAudioPayload])
    assert_type(text_spec, pocketstation.SignalSpec[str])

    audio_subscription = session.subscribe(source, signal=audio_spec)
    text_subscription = session.subscribe(source, signal=text_spec)
    assert_type(
        audio_subscription,
        pocketstation.BusSubscription[pocketstation.SignalAudioPayload],
    )
    assert_type(text_subscription, pocketstation.BusSubscription[str])


def verify_runtime_identities(
    running: pocketstation.RunningSession,
    frame: pocketstation.AudioFrame,
) -> None:
    assert_type(running.session_id, pocketstation.RuntimeSessionId)
    assert_type(frame.session_id, pocketstation.RuntimeSessionId)
    assert_type(frame.stream_id, pocketstation.StreamId)
    assert_type(frame.source_id, pocketstation.SourceId)
    assert_type(frame.stem_id, pocketstation.StemId)
    assert_type(frame.clock_id, pocketstation.ClockDomainId)
    assert_type(frame.endpoint_id, pocketstation.EndpointId)
    assert_type(frame.connector_id, pocketstation.ConnectorId | None)
    assert_type(frame.route_id, pocketstation.RouteId)
