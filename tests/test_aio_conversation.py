from __future__ import annotations

from array import array
from collections.abc import AsyncIterator
from pathlib import Path

import pocketstation.aio as pocketstation
import pytest
from conversation_support import (
    TRANSCRIPT_SIGNAL,
    transcript_operator,
    transcript_source,
)
from pocketstation.conversation import (
    ConversationConfig,
    ConversationContext,
    ConversationResponse,
    ConversationResponseChunk,
    ConversationTurn,
    ToolEvent,
    TranscriptUpdate,
)
from pocketstation.signal import SignalEnvelope


@pytest.mark.asyncio
async def test_given_conversation_when_run_then_one_session_owns_bounded_audio(
    tmp_path: Path,
) -> None:
    session = pocketstation.Session(recording_root=tmp_path)
    source = session.register_source(transcript_source("ship the answer")).declare()
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
    output.output.record("assistant")
    provider_events: list[str] = []
    received_source_ids: list[int | None] = []

    class Responder:
        async def start(self) -> None:
            provider_events.append("responder.started")

        async def __call__(
            self,
            turn: TranscriptUpdate,
            context: ConversationContext,
        ) -> ConversationResponse:
            assert turn.text == "ship the answer"
            assert context.history[-1].role == "user"
            received_source_ids.append(turn.source_id)
            return ConversationResponse(
                "completed",
                tool_events=(ToolEvent("lookup", "completed", "local"),),
            )

        async def aclose(self) -> None:
            provider_events.append("responder.closed")

    class Synthesizer:
        async def start(self) -> None:
            provider_events.append("synthesizer.started")

        async def __call__(
            self,
            _response: ConversationResponseChunk,
            _turn: ConversationTurn,
        ) -> AsyncIterator[array[float]]:
            async def frames() -> AsyncIterator[array[float]]:
                yield array("f", [0.1] * 480)
                yield array("f", [0.2] * 480)

            return frames()

        async def aclose(self) -> None:
            provider_events.append("synthesizer.closed")

    conversation = session.conversation(
        transcripts=transcripts,
        respond=Responder(),
        synthesize=Synthesizer(),
        output=output,
    )
    running = await session.start()
    outcome = await conversation.run(running)
    await output.close()
    stopped = await running.stop()

    assert outcome.success
    assert outcome.turns_started == 1
    assert outcome.turns_completed == 1
    assert outcome.output_frames_written == 2
    assert received_source_ids == [source.source_id]
    assert provider_events == [
        "responder.started",
        "synthesizer.started",
        "synthesizer.closed",
        "responder.closed",
    ]
    assert [message.role for message in outcome.history] == [
        "user",
        "tool",
        "assistant",
    ]
    assert {event.kind for event in outcome.events} >= {
        "turn.started",
        "response.completed",
        "tool.completed",
        "turn.completed",
    }
    assert stopped.success, (
        f"endpoint_finalization_failures="
        f"{stopped.endpoint_finalization_failures_total}; "
        f"runtime_failures={stopped.runtime_failures_total}; "
        f"source_send_rejections={stopped.source_send_rejections_total}; "
        f"recording={stopped.recording!r}; "
        f"terminal_event={stopped.terminal_event!r}"
    )
    assert stopped.recording is not None and stopped.recording.complete
    with pytest.raises(RuntimeError, match="only once"):
        await conversation.run(running)


@pytest.mark.asyncio
async def test_given_synthesis_limit_when_exceeded_then_conversation_fails(
    tmp_path: Path,
) -> None:
    session = pocketstation.Session(recording_root=tmp_path)
    source = session.register_source(transcript_source("too much audio")).declare()
    operator = session.register_operator(transcript_operator()).declare()
    source.output("transcript").connect(operator.input("transcript"))
    transcripts = session.subscribe(
        operator.output("transcript"),
        signal=TRANSCRIPT_SIGNAL,
    )
    output = session.audio_input("assistant", frame_samples_per_channel=480)
    output.output.send(session.polled_audio())

    async def respond(
        _turn: TranscriptUpdate,
        _context: ConversationContext,
    ) -> str:
        return "bounded response"

    async def synthesize(
        _response: ConversationResponseChunk,
        _turn: ConversationTurn,
    ) -> AsyncIterator[array[float]]:
        yield array("f", [0.1] * 480)
        yield array("f", [0.2] * 480)

    conversation = session.conversation(
        transcripts=transcripts,
        respond=respond,
        synthesize=synthesize,
        output=output,
        config=ConversationConfig(maximum_output_frames_per_turn=1),
    )
    running = await session.start()
    outcome = await conversation.run(running)
    frame = await running.audio.read(timeout_s=1)
    await output.close()
    stopped = await running.stop()

    assert frame is not None
    assert not outcome.success
    assert outcome.disposition == "failed"
    assert outcome.output_frames_written == 1
    assert outcome.failure is not None
    assert "maximum_output_frames_per_turn" in outcome.failure
    assert stopped.success


@pytest.mark.asyncio
async def test_given_revisable_transcript_when_final_then_prepared_chunks_stream(
    tmp_path: Path,
) -> None:
    session = pocketstation.Session(recording_root=tmp_path)
    source = session.register_source(
        transcript_source("partial-1", "partial-2", "final")
    ).declare()
    operator = session.register_operator(transcript_operator()).declare()
    source.output("transcript").connect(operator.input("transcript"))
    transcripts = session.subscribe(
        operator.output("transcript"),
        signal=TRANSCRIPT_SIGNAL,
    )
    output = session.audio_input("assistant", frame_samples_per_channel=480)
    output.output.send(session.polled_audio())
    final_seen = False
    response_inputs: list[tuple[str, bool]] = []
    synthesis_chunks: list[str] = []

    def decode(envelope: SignalEnvelope[str]) -> TranscriptUpdate:
        nonlocal final_seen
        lineage = envelope.lineage
        updates = {
            "partial-1": (1, "hello", "hello", False),
            "partial-2": (2, "hello there", "hello", False),
            "final": (3, "hello there", "hello there", True),
        }
        revision, text, stable_prefix, final = updates[envelope.payload]
        final_seen = final_seen or final
        return TranscriptUpdate(
            utterance_id="speech-1",
            revision=revision,
            text=text,
            stable_prefix=stable_prefix,
            final=final,
            source_id=None if lineage is None else lineage.source_id,
            stream_id=None if lineage is None else lineage.stream_id,
            source_sequence=None if lineage is None else lineage.sequence_number,
            source_timestamp_ns=envelope.timing.source_timestamp_ns,
        )

    async def respond(
        update: TranscriptUpdate,
        context: ConversationContext,
    ) -> AsyncIterator[ConversationResponseChunk]:
        response_inputs.append((update.text, context.committed))

        async def chunks() -> AsyncIterator[ConversationResponseChunk]:
            yield ConversationResponseChunk("answer: ")
            yield ConversationResponseChunk(update.text)

        return chunks()

    async def synthesize(
        chunk: ConversationResponseChunk,
        _turn: ConversationTurn,
    ) -> AsyncIterator[array[float]]:
        assert final_seen
        synthesis_chunks.append(chunk.text)
        yield array("f", [0.1] * 480)

    conversation = session.conversation(
        transcripts=transcripts,
        respond=respond,
        synthesize=synthesize,
        output=output,
        decode_transcript=decode,
    )
    running = await session.start()
    outcome = await conversation.run(running)
    first = await running.audio.read(timeout_s=1)
    second = await running.audio.read(timeout_s=1)
    await output.close()
    stopped = await running.stop()

    assert outcome.success
    assert outcome.transcript_updates_received == 3
    assert outcome.speculative_responses_started == 2
    assert outcome.speculative_responses_reused == 1
    assert response_inputs == [("hello", False), ("hello there", False)]
    assert synthesis_chunks == ["answer: ", "hello there"]
    assert first is not None and second is not None
    assert stopped.success
