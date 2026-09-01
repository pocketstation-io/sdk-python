from __future__ import annotations

from array import array
from threading import Event
from time import monotonic

import pocketstation as pks


class CollectingConnector(pks.Connector):
    def __init__(self, name: str) -> None:
        self.name = name
        self.started_total = 0
        self.stopped_total = 0
        self.received: list[pks.AudioFrame] = []
        self.delivered = Event()

    def start(self) -> None:
        self.started_total += 1

    def send(self, frame: pks.AudioFrame) -> None:
        self.received.append(frame)
        self.delivered.set()

    def stop(self) -> None:
        self.stopped_total += 1


def test_given_one_connector_when_two_stems_send_then_one_lifecycle_receives_both() -> (
    None
):
    destination = CollectingConnector("broadcast")
    session = pks.Session()
    application = session.audio_input("application", frame_samples_per_channel=4)
    microphone = session.audio_input("microphone", frame_samples_per_channel=4)
    application.output.send_to(destination)
    microphone.output.send_to(destination)

    running = session.start()
    application.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    microphone.write(array("f", [0.5, 0.6, 0.7, 0.8]))
    deadline = monotonic() + 1.0
    while len(destination.received) < 2 and monotonic() < deadline:
        destination.delivered.wait(0.01)
    outcome = running.stop()

    assert outcome.success
    assert destination.started_total == 1
    assert destination.stopped_total == 1
    assert {frame.source_id for frame in destination.received} == {
        application.source_id,
        microphone.source_id,
    }


def test_given_two_connectors_when_one_stem_sends_then_lifecycles_are_independent() -> (
    None
):
    primary = CollectingConnector("primary")
    backup = CollectingConnector("backup")
    session = pks.Session()
    application = session.audio_input("application", frame_samples_per_channel=4)
    application.output.send_to(primary)
    application.output.send_to(backup)

    running = session.start()
    application.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    assert primary.delivered.wait(1.0)
    assert backup.delivered.wait(1.0)
    outcome = running.stop()

    assert outcome.success
    assert primary.started_total == primary.stopped_total == 1
    assert backup.started_total == backup.stopped_total == 1
    assert len(primary.received) == len(backup.received) == 1


def test_given_start_failure_when_session_starts_then_provider_is_closed() -> None:
    class FailingConnector(pks.Connector):
        def __init__(self) -> None:
            self.stopped_total = 0

        def start(self) -> None:
            raise RuntimeError("provider unavailable")

        def send(self, frame: pks.AudioFrame) -> None:
            raise AssertionError(f"unexpected frame {frame.sequence_number}")

        def stop(self) -> None:
            self.stopped_total += 1

    destination = FailingConnector()
    session = pks.Session()
    audio = session.audio_input("application", frame_samples_per_channel=4)
    audio.output.send_to(destination)

    running = session.start()
    outcome = running.stop()

    assert not outcome.success
    assert destination.stopped_total == 1


def test_given_callbacks_when_two_stems_send_then_one_lifecycle_receives_both() -> None:
    started_total = 0
    stopped_total = 0
    received: list[pks.AudioFrame] = []
    delivered = Event()

    def start() -> None:
        nonlocal started_total
        started_total += 1

    def send(frame: pks.AudioFrame) -> None:
        received.append(frame)
        if len(received) == 2:
            delivered.set()

    def stop() -> None:
        nonlocal stopped_total
        stopped_total += 1

    destination = pks.Connector(start=start, send=send, stop=stop)
    session = pks.Session()
    application = session.audio_input("application", frame_samples_per_channel=4)
    microphone = session.audio_input("microphone", frame_samples_per_channel=4)
    application.output.send_to(destination)
    microphone.output.send_to(destination)

    running = session.start()
    application.write(array("f", [0.1, 0.2, 0.3, 0.4]))
    microphone.write(array("f", [0.5, 0.6, 0.7, 0.8]))
    assert delivered.wait(1.0)
    outcome = running.stop()

    assert outcome.success
    assert started_total == stopped_total == 1
    assert {frame.source_id for frame in received} == {
        application.source_id,
        microphone.source_id,
    }


def test_given_lifecycle_callback_without_send_then_creation_fails() -> None:
    try:
        pks.Connector(start=lambda: None)
    except TypeError as error:
        assert str(error) == "send is required when lifecycle callbacks are provided"
    else:
        raise AssertionError("Connector accepted lifecycle callbacks without send")
