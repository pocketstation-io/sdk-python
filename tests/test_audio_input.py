"""Application-owned PCM ingress contracts."""

from __future__ import annotations

from array import array

import pytest
from pocketstation._api import (
    AudioInputBufferError,
    AudioInputCancelledError,
    AudioInputClosedError,
    AudioInputConfig,
    AudioInputError,
    AudioInputFullError,
    Session,
    SourceId,
    StreamId,
)


@pytest.mark.parametrize("name", ["", " ", "\t"])
def test_audio_input_rejects_empty_names(name: str) -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        AudioInputConfig(name=name)


@pytest.mark.parametrize(
    "samples",
    [
        array("d", [0.0] * 4),
        array("f", [0.0] * 2),
        memoryview(array("f", [0.0] * 8))[::2],
    ],
)
def test_audio_input_rejects_wrong_or_noncontiguous_buffers(samples: object) -> None:
    source = Session().audio_input("owned", frame_samples_per_channel=4)

    with pytest.raises(AudioInputBufferError) as failure:
        source.try_write(samples)

    assert failure.value.code == "audio_input.invalid_buffer"


def test_pcm_source_exposes_typed_identity_and_exact_finite_capacity() -> None:
    session = Session()
    source = session.pcm_source(
        AudioInputConfig(
            name="generated",
            capacity_frames=1,
            frame_samples_per_channel=4,
        )
    )
    samples = array("f", [0.0] * 4)

    assert isinstance(source.source_id, int)
    assert isinstance(source.stream_id, int)
    assert SourceId(source.source_id) == source.source_id
    assert StreamId(source.stream_id) == source.stream_id

    source.try_write(samples)
    with pytest.raises(AudioInputFullError) as full:
        source.try_write(samples)
    assert full.value.code == "audio_input.full"

    observations = source.observations()
    assert observations.capacity_frames == 1
    # The queue has one slot and Core owns one additional in-flight buffer so
    # the producer never allocates while a queued frame is being consumed.
    assert observations.buffer_slots == observations.capacity_frames + 1
    assert observations.available_buffers == (
        observations.buffer_slots - observations.capacity_frames
    )
    assert observations.accepted_total == 1
    assert observations.full_total == 1


def test_audio_input_close_and_session_cancellation_have_distinct_outcomes() -> None:
    samples = array("f", [0.0] * 4)

    closed = Session().audio_input("closed", frame_samples_per_channel=4)
    closed.close()
    with pytest.raises(AudioInputClosedError) as closed_failure:
        closed.try_write(samples)
    assert closed_failure.value.code == "audio_input.closed"
    assert closed.observations().closed

    session = Session()
    cancelled = session.audio_input("cancelled", frame_samples_per_channel=4)
    cancelled.output.send(session.polled_audio())
    running = session.start()
    assert running.cancel().success

    with pytest.raises(AudioInputCancelledError) as cancelled_failure:
        cancelled.try_write(samples)
    assert cancelled_failure.value.code == "audio_input.cancelled"
    assert cancelled.observations().cancelled


def test_audio_input_recovers_its_exact_preallocated_slot_after_delivery() -> None:
    session = Session()
    audio = session.audio_input(
        "owned",
        capacity_frames=1,
        frame_samples_per_channel=4,
    )
    audio.output.send(session.polled_audio())
    running = session.start()
    samples = array("f", [0.25, -0.25, 0.5, -0.5])

    audio.try_write(samples, discontinuity=True)
    frame = running.audio.read(timeout_s=1.0)

    assert frame is not None
    assert frame.source_id == audio.source_id
    assert frame.stream_id == audio.stream_id
    assert frame.discontinuity_epoch == 1
    observations = audio.observations()
    assert observations.available_buffers == observations.buffer_slots

    audio.try_write(samples)
    second = running.audio.read(timeout_s=1.0)
    assert second is not None
    assert second.sequence_number == frame.sequence_number + 1
    assert second.discontinuity_epoch == frame.discontinuity_epoch
    assert running.stop().success


def test_given_replaced_output_when_read_then_only_active_pcm_is_returned() -> None:
    session = Session()
    output = session.audio_input(
        "generated",
        capacity_frames=4,
        frame_samples_per_channel=4,
    )
    output.output.send(session.polled_audio())
    running = session.start()
    first = output.begin_output()

    output.try_write(array("f", [-0.5] * 4), generation=first)
    output.try_write(array("f", [-0.25] * 4), generation=first)
    first.cancel()
    assert not first.active
    with pytest.raises(AudioInputError) as inactive:
        output.try_write(array("f", [-0.75] * 4), generation=first)
    assert inactive.value.code == "audio_input.output_inactive"

    replacement = output.begin_output()
    output.try_write(array("f", [0.5] * 4), generation=replacement)
    frame = running.audio.read(timeout_s=1.0)

    assert frame is not None
    assert frame.output_generation_id == replacement.id
    assert memoryview(frame.samples).cast("f")[0] == pytest.approx(0.5)
    assert running.audio.read(timeout_s=0.01) is None
    assert output.observations().inactive_output_writes_total == 1
    assert running.stop().success
