"""The asyncio Session declares the same native cancellation operation."""

from __future__ import annotations

import asyncio
from array import array

from pocketstation import AudioFrame, aio
from pocketstation.aec import EchoCancellationState, PlaybackReference
from pocketstation.signal import STREAM_EOF


async def test_given_async_session_when_echo_runs_then_stop_is_observed() -> None:
    session = aio.Session(frame_duration_ms=10)
    reference = session.audio_input("playback")
    microphone = session.audio_input("microphone")
    cleaned = session.echo_cancel(
        microphone.output, PlaybackReference.rendered_audio(reference.output)
    )
    cleaned.audio.send(session.polled_audio())
    async with await session.start() as running:
        for _ in range(10):
            await reference.try_write(array("f", [0.0]) * 480)
            await microphone.try_write(array("f", [0.1]) * 480)
            frame = await running.audio.read(timeout_s=1.0)
            assert isinstance(frame, AudioFrame)
            assert frame.stem_id == cleaned.audio.id
            assert len(frame.samples.cast("f")) == 480
            assert frame.processing is not None
            assert frame.processing.input_source_id == microphone.source_id
            assert not frame.processing.is_tail
        await reference.close()
        await microphone.close()
        final_read = asyncio.create_task(running.audio.read(timeout_s=1.0))
        await asyncio.sleep(0)
        assert (await running.stop()).success
        assert running.audio.is_closed
        for index in range(4):
            tail = (
                await final_read
                if index == 0
                else await running.audio.read(timeout_s=1.0)
            )
            assert isinstance(tail, AudioFrame), cleaned.observations()
            assert tail.processing is not None
            assert tail.processing.is_tail
            assert tail.processing.input_source_id == microphone.source_id
            assert tail.processing.padding_samples == 480
            assert tail.processing.tail_offset_samples == index * 480
        assert await running.audio.read(timeout_s=0.0) is STREAM_EOF
    observation = cleaned.observations()
    assert observation.state is EchoCancellationState.STOPPED
    assert observation.processed_microphone_frames_total == 10
    assert observation.microphone_source_id == microphone.source_id
    assert observation.reference_source_id == reference.source_id
    assert observation.output_frames_total == 14
    assert observation.tail_frames_total == 4
    assert observation.tail_padding_samples_total == 1920
