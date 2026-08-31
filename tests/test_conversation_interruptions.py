from __future__ import annotations

import asyncio
from array import array
from collections.abc import AsyncIterator
from pathlib import Path
from threading import Event

import pocketstation.aio as pocketstation
import pytest
from conversation_support import (
    TRANSCRIPT_SIGNAL,
    transcript_operator,
    transcript_source,
    transcript_source_after,
)
from pocketstation.conversation import (
    ConversationConfig,
    ConversationContext,
    ConversationResponseChunk,
    ConversationTurn,
    TranscriptUpdate,
)


@pytest.mark.asyncio
async def test_given_new_turn_when_response_is_active_then_provider_is_cancelled(
    tmp_path: Path,
) -> None:
    session = pocketstation.Session(recording_root=tmp_path)
    source = session.register_source(transcript_source("obsolete", "current")).declare()
    operator = session.register_operator(transcript_operator()).declare()
    source.output("transcript").connect(operator.input("transcript"))
    transcripts = session.subscribe(
        operator.output("transcript"),
        signal=TRANSCRIPT_SIGNAL,
    )
    output = session.audio_input(
        "assistant",
        capacity_frames=1,
        frame_samples_per_channel=480,
    )
    output.output.record("assistant")
    output.output.send(session.polled_audio())
    cancelled = asyncio.Event()

    async def respond(
        turn: TranscriptUpdate,
        _context: ConversationContext,
    ) -> str:
        if turn.text == "obsolete":
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                cancelled.set()
                raise
        return f"answer:{turn.text}"

    async def synthesize(
        response: ConversationResponseChunk,
        _turn: ConversationTurn,
    ) -> AsyncIterator[array[float]]:
        assert response.text == "answer:current"
        yield array("f", [0.25] * 480)

    conversation = session.conversation(
        transcripts=transcripts,
        respond=respond,
        synthesize=synthesize,
        output=output,
        config=ConversationConfig(cancellation_timeout_s=1),
    )
    running = await session.start()
    frame_task = asyncio.create_task(running.audio.read(timeout_s=1))
    outcome = await conversation.run(running)
    frame = await frame_task
    await output.close()
    stopped = await running.stop()

    assert cancelled.is_set()
    assert outcome.success
    assert outcome.turns_started == 2
    assert outcome.turns_interrupted == 1
    assert outcome.turns_completed == 1
    assert outcome.output_frames_written == 1
    assert outcome.history[-1].content == "answer:current"
    assert frame is not None
    assert frame.discontinuity_epoch == 1
    assert stopped.success, stopped


@pytest.mark.asyncio
async def test_given_run_cancel_when_provider_active_then_lifecycle_closes() -> None:
    session = pocketstation.Session()
    source = session.register_source(transcript_source("wait for me")).declare()
    operator = session.register_operator(transcript_operator()).declare()
    source.output("transcript").connect(operator.input("transcript"))
    transcripts = session.subscribe(
        operator.output("transcript"),
        signal=TRANSCRIPT_SIGNAL,
    )
    output = session.audio_input("assistant", frame_samples_per_channel=480)
    output.output.send(session.polled_audio())
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def respond(
        _turn: TranscriptUpdate,
        _context: ConversationContext,
    ) -> str:
        started.set()
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            cancelled.set()
            raise
        raise AssertionError("active response provider was not cancelled")

    async def synthesize(
        _response: ConversationResponseChunk,
        _turn: ConversationTurn,
    ) -> AsyncIterator[array[float]]:
        yield array("f", [0.0] * 480)

    conversation = session.conversation(
        transcripts=transcripts,
        respond=respond,
        synthesize=synthesize,
        output=output,
        config=ConversationConfig(cancellation_timeout_s=1),
    )
    running = await session.start()
    task = asyncio.create_task(conversation.run(running))
    await asyncio.wait_for(started.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await output.close()
    stopped = await running.stop()

    assert cancelled.is_set()
    assert conversation.outcome is not None
    assert conversation.outcome.disposition == "cancelled"
    assert conversation.outcome.turns_interrupted == 1
    assert conversation.outcome.output_frames_written == 0
    assert stopped.success


@pytest.mark.asyncio
async def test_given_queued_output_when_interrupted_then_only_replacement_is_read(
    tmp_path: Path,
) -> None:
    session = pocketstation.Session(recording_root=tmp_path)
    old_frame_queued = Event()
    source = session.register_source(
        transcript_source_after("old", "new", ready=old_frame_queued)
    ).declare()
    operator = session.register_operator(transcript_operator()).declare()
    source.output("transcript").connect(operator.input("transcript"))
    transcripts = session.subscribe(
        operator.output("transcript"),
        signal=TRANSCRIPT_SIGNAL,
    )
    output = session.audio_input(
        "assistant",
        capacity_frames=2,
        frame_samples_per_channel=480,
    )
    output.output.send(session.polled_audio())

    async def respond(
        update: TranscriptUpdate,
        _context: ConversationContext,
    ) -> str:
        return update.text

    async def synthesize(
        chunk: ConversationResponseChunk,
        _turn: ConversationTurn,
    ) -> AsyncIterator[array[float]]:
        if chunk.text == "old":
            yield array("f", [-0.5] * 480)
            old_frame_queued.set()
            await asyncio.sleep(30)
        else:
            assert old_frame_queued.is_set()
            yield array("f", [0.5] * 480)

    conversation = session.conversation(
        transcripts=transcripts,
        respond=respond,
        synthesize=synthesize,
        output=output,
        config=ConversationConfig(cancellation_timeout_s=1),
    )
    running = await session.start()
    outcome = await conversation.run(running)
    frame = await running.audio.read(timeout_s=1)
    metrics = await running.metrics()
    await output.close()
    stopped = await running.stop()

    assert outcome.success
    assert outcome.output_generations_cancelled == 1
    assert outcome.turns_interrupted == 1
    assert frame is not None
    assert memoryview(frame.samples).cast("f")[0] == pytest.approx(0.5)
    assert frame.output_generation_id is not None
    assert await running.audio.read(timeout_s=0.01) is None
    discarded_output_frames_total = (
        metrics.polled_audio.discarded_output_frames_total
        + sum(route.edge.discarded_output_frames_total or 0 for route in metrics.routes)
    )
    assert discarded_output_frames_total >= 1
    assert stopped.success
