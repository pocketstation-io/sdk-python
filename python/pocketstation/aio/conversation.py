"""Continuous voice composition over one running native Session."""

from __future__ import annotations

import asyncio
import inspect
from collections import OrderedDict, deque
from collections.abc import AsyncIterable, Awaitable, Callable
from dataclasses import dataclass
from time import monotonic_ns
from typing import TypeAlias, cast

from ..audio_input import OutputGeneration
from ..conversation import (
    ConversationConfig,
    ConversationContext,
    ConversationDisposition,
    ConversationEvent,
    ConversationMessage,
    ConversationOutcome,
    ConversationResponse,
    ConversationResponseChunk,
    ConversationRole,
    ConversationTurn,
    TranscriptUpdate,
)
from ..signal import BusSubscription, EndOfStream, SignalEnvelope
from .audio_input import AudioInput

ResponseItem: TypeAlias = str | ConversationResponse | ConversationResponseChunk
ResponseResult: TypeAlias = (
    ResponseItem
    | AsyncIterable[ResponseItem]
    | Awaitable[ResponseItem | AsyncIterable[ResponseItem]]
)
SynthesisResult: TypeAlias = AsyncIterable[object] | Awaitable[AsyncIterable[object]]


ResponseHandler: TypeAlias = Callable[
    [TranscriptUpdate, ConversationContext], ResponseResult
]
SynthesisHandler: TypeAlias = Callable[
    [ConversationResponseChunk, ConversationTurn], SynthesisResult
]
TranscriptDecoder: TypeAlias = Callable[[SignalEnvelope[str]], TranscriptUpdate | None]


@dataclass(frozen=True, slots=True)
class _TranscriptRecord:
    revision: int
    stable_prefix: str
    final: bool


class _TranscriptState:
    def __init__(self, capacity: int, maximum_characters: int) -> None:
        self._capacity = capacity
        self._maximum_characters = maximum_characters
        self._records: OrderedDict[str, _TranscriptRecord] = OrderedDict()

    def accept(self, update: TranscriptUpdate) -> None:
        if len(update.text) > self._maximum_characters:
            raise ValueError("transcript exceeded maximum_transcript_characters")
        previous = self._records.get(update.utterance_id)
        if previous is not None:
            if previous.final:
                raise ValueError("a final utterance cannot receive another revision")
            if update.revision <= previous.revision:
                raise ValueError("transcript revisions must increase")
            if not update.stable_prefix.startswith(previous.stable_prefix):
                raise ValueError("stable transcript text cannot change or shrink")
            self._records.move_to_end(update.utterance_id)
        elif len(self._records) >= self._capacity:
            oldest_id, oldest = next(iter(self._records.items()))
            if not oldest.final:
                raise RuntimeError("transcript_state_capacity is exhausted")
            del self._records[oldest_id]
        self._records[update.utterance_id] = _TranscriptRecord(
            revision=update.revision,
            stable_prefix=update.stable_prefix,
            final=update.final,
        )


@dataclass(slots=True)
class _Speculation:
    update: TranscriptUpdate
    task: asyncio.Task[tuple[ConversationResponseChunk, ...]]


@dataclass(slots=True)
class _Delivery:
    turn: ConversationTurn
    generation: OutputGeneration
    task: asyncio.Task[None]
    settled: bool = False
    interruption_counted: bool = False


class Conversation:
    """Coordinate transcript, response, synthesis, and generated audio work.

    The native Session continues to own Sources, routing, recording, and
    Connector delivery. This object owns only finite provider work and retained
    conversation state. Partial transcripts may prepare a response, but audio
    is not emitted until the transcript is final.
    """

    def __init__(
        self,
        *,
        transcripts: BusSubscription[str],
        respond: ResponseHandler,
        synthesize: SynthesisHandler,
        output: AudioInput,
        config: ConversationConfig | None = None,
        decode_transcript: TranscriptDecoder | None = None,
    ) -> None:
        if transcripts.session_id != int(output.output.session_id):
            raise ValueError("transcripts and output must belong to the same Session")
        self._transcripts = transcripts
        self._respond = respond
        self._synthesize = synthesize
        self._output = output
        self._config = ConversationConfig() if config is None else config
        self._decode_transcript = (
            _default_transcript_decoder
            if decode_transcript is None
            else decode_transcript
        )
        self._transcript_state = _TranscriptState(
            self._config.transcript_state_capacity,
            self._config.maximum_transcript_characters,
        )
        self._history: deque[ConversationMessage] = deque(
            maxlen=self._config.history_capacity
        )
        self._events: deque[ConversationEvent] = deque(
            maxlen=self._config.event_capacity
        )
        self._stop_requested = asyncio.Event()
        self._running = False
        self._has_run = False
        self._discontinuity_pending = False
        self._turns_started = 0
        self._turns_completed = 0
        self._turns_interrupted = 0
        self._transcript_updates_received = 0
        self._speculative_responses_started = 0
        self._speculative_responses_reused = 0
        self._output_generations_cancelled = 0
        self._output_frames_written = 0
        self._outcome: ConversationOutcome | None = None

    @property
    def config(self) -> ConversationConfig:
        return self._config

    @property
    def outcome(self) -> ConversationOutcome | None:
        return self._outcome

    @property
    def history(self) -> tuple[ConversationMessage, ...]:
        return tuple(self._history)

    @property
    def events(self) -> tuple[ConversationEvent, ...]:
        return tuple(self._events)

    def stop(self) -> None:
        """Request a normal stop at the next finite signal wait."""
        self._stop_requested.set()

    async def run(self, running: object) -> ConversationOutcome:
        """Run until the transcript endpoint closes or :meth:`stop` is called."""
        from .session import RunningSession

        if not isinstance(running, RunningSession):
            raise TypeError("running must be a pocketstation.aio.RunningSession")
        if self._running:
            raise RuntimeError("Conversation is already running")
        if self._has_run:
            raise RuntimeError("Conversation can run only once")
        if int(running.session_id) != self._transcripts.session_id:
            raise ValueError("running Session does not own this conversation")

        self._running = True
        self._has_run = True
        disposition = "completed"
        failure: str | None = None
        delivery: _Delivery | None = None
        speculation: _Speculation | None = None
        stream = running.signals(self._transcripts)
        started_providers: list[object] = []
        try:
            for provider in _unique_providers(self._respond, self._synthesize):
                await self._provider_lifecycle(provider, "start")
                started_providers.append(provider)
            while not self._stop_requested.is_set():
                if (
                    delivery is not None
                    and delivery.task.done()
                    and not delivery.settled
                ):
                    await delivery.task
                    delivery.settled = True
                result = await stream.read(timeout_s=self._config.signal_wait_timeout_s)
                if isinstance(result, EndOfStream):
                    break
                if result is None:
                    continue
                update = self._decode_transcript(result)
                if update is None:
                    continue
                self._transcript_state.accept(update)
                self._transcript_updates_received += 1
                self._event("transcript.updated", update=update)

                if delivery is not None and update.interrupts:
                    await self._interrupt_delivery(delivery)
                    delivery = None

                if not update.final:
                    if not update.text.strip():
                        continue
                    if speculation is not None and (
                        speculation.update.utterance_id != update.utterance_id
                        or speculation.update.text != update.text
                    ):
                        await self._cancel_speculation(speculation)
                        speculation = None
                    if speculation is None:
                        self._speculative_responses_started += 1
                        self._event("response.preparing", update=update)
                        speculation = _Speculation(
                            update=update,
                            task=asyncio.create_task(self._prepare_response(update)),
                        )
                    continue

                prepared: tuple[ConversationResponseChunk, ...] | None = None
                if speculation is not None:
                    if (
                        speculation.update.utterance_id == update.utterance_id
                        and speculation.update.text == update.text
                    ):
                        prepared = await speculation.task
                        self._speculative_responses_reused += 1
                        self._event("response.prepared", update=update)
                    else:
                        await self._cancel_speculation(speculation)
                    speculation = None

                turn = self._turn(result, update)
                self._turns_started += 1
                self._append_message("user", update.text, turn.id)
                self._event("turn.started", turn=turn, update=update)
                generation = self._output.begin_output()
                self._event(
                    "output.started",
                    turn=turn,
                    update=update,
                    generation=generation,
                )
                delivery = _Delivery(
                    turn=turn,
                    generation=generation,
                    task=asyncio.create_task(
                        self._deliver_response(turn, update, generation, prepared)
                    ),
                )
                await asyncio.sleep(0)

            if speculation is not None:
                await self._cancel_speculation(speculation)
            if delivery is not None:
                if self._stop_requested.is_set():
                    await self._interrupt_delivery(delivery)
                    disposition = "stopped"
                elif not delivery.settled:
                    await delivery.task
                    delivery.settled = True
            elif self._stop_requested.is_set():
                disposition = "stopped"
            await self._wait_output_drained(running)
        except asyncio.CancelledError:
            disposition = "cancelled"
            if speculation is not None:
                await self._cancel_speculation(speculation)
            if delivery is not None:
                await self._interrupt_delivery(delivery)
            raise
        except Exception as error:
            if speculation is not None:
                await self._cancel_speculation(speculation)
            if delivery is not None and not delivery.task.done():
                await self._interrupt_delivery(delivery)
            disposition = "failed"
            failure = f"{type(error).__name__}: {error}"
            self._event("conversation.failed", detail=failure)
        finally:
            for provider in reversed(started_providers):
                try:
                    await self._provider_lifecycle(provider, "aclose")
                except Exception as error:
                    disposition = "failed"
                    failure = f"provider close failed: {type(error).__name__}: {error}"
                    self._event("provider.close_failed", detail=failure)
            self._outcome = ConversationOutcome(
                disposition=cast(ConversationDisposition, disposition),
                turns_started=self._turns_started,
                turns_completed=self._turns_completed,
                turns_interrupted=self._turns_interrupted,
                transcript_updates_received=self._transcript_updates_received,
                speculative_responses_started=self._speculative_responses_started,
                speculative_responses_reused=self._speculative_responses_reused,
                output_generations_cancelled=self._output_generations_cancelled,
                output_frames_written=self._output_frames_written,
                history=tuple(self._history),
                events=tuple(self._events),
                failure=failure,
            )
            self._running = False
        return self._outcome

    async def _prepare_response(
        self,
        update: TranscriptUpdate,
    ) -> tuple[ConversationResponseChunk, ...]:
        chunks: list[ConversationResponseChunk] = []
        characters = 0
        async for chunk in self._response_chunks(update, committed=False):
            if chunk.tool_events:
                raise ValueError("a speculative response cannot request tool work")
            chunks.append(chunk)
            characters += len(chunk.text)
            self._check_response_bounds(len(chunks), characters, 0)
        if not any(chunk.text for chunk in chunks):
            raise ValueError("response provider produced no text")
        return tuple(chunks)

    async def _deliver_response(
        self,
        turn: ConversationTurn,
        update: TranscriptUpdate,
        generation: OutputGeneration,
        prepared: tuple[ConversationResponseChunk, ...] | None,
    ) -> None:
        response_started = monotonic_ns()
        response_text: list[str] = []
        response_chunks = 0
        response_characters = 0
        tool_events = 0
        frames = 0
        synthesis_started: int | None = None
        synthesis_deadline = (
            asyncio.get_running_loop().time() + self._config.synthesis_timeout_s
        )
        chunks: AsyncIterable[ConversationResponseChunk]
        if prepared is None:
            chunks = self._response_chunks(update, committed=True)
        else:
            chunks = _iter_prepared(prepared)

        async for chunk in chunks:
            response_chunks += 1
            response_characters += len(chunk.text)
            tool_events += len(chunk.tool_events)
            self._check_response_bounds(
                response_chunks,
                response_characters,
                tool_events,
            )
            response_text.append(chunk.text)
            self._event(
                "response.chunk",
                turn=turn,
                update=update,
                generation=generation,
            )
            for tool in chunk.tool_events:
                detail = f": {tool.detail}" if tool.detail else ""
                self._append_message(
                    "tool",
                    f"{tool.name}: {tool.outcome}{detail}",
                    turn.id,
                )
                self._event(
                    "tool.completed",
                    turn=turn,
                    update=update,
                    generation=generation,
                    detail=f"{tool.name}:{tool.outcome}",
                )
            if not chunk.text:
                continue
            if synthesis_started is None:
                synthesis_started = monotonic_ns()
                self._event(
                    "synthesis.started",
                    turn=turn,
                    update=update,
                    generation=generation,
                )
            produced = self._synthesize(chunk, turn)
            if inspect.isawaitable(produced):
                produced = await asyncio.wait_for(
                    produced,
                    timeout=self._remaining(synthesis_deadline, "synthesis"),
                )
            async for samples in _iterate_until(
                produced,
                synthesis_deadline,
                "synthesis",
            ):
                if not generation.active:
                    raise asyncio.CancelledError
                frames += 1
                if frames > self._config.maximum_output_frames_per_turn:
                    raise ValueError(
                        "synthesis exceeded maximum_output_frames_per_turn"
                    )
                await self._output.write(
                    samples,
                    discontinuity=self._discontinuity_pending,
                    generation=generation,
                    timeout_s=min(
                        self._config.output_write_timeout_s,
                        self._remaining(synthesis_deadline, "synthesis"),
                    ),
                )
                self._discontinuity_pending = False
                self._output_frames_written += 1

        text = "".join(response_text)
        if not text.strip():
            raise ValueError("response provider produced no text")
        self._event(
            "response.completed",
            turn=turn,
            update=update,
            generation=generation,
            duration_ns=monotonic_ns() - response_started,
        )
        self._event(
            "synthesis.completed",
            turn=turn,
            update=update,
            generation=generation,
            duration_ns=(
                None
                if synthesis_started is None
                else monotonic_ns() - synthesis_started
            ),
            detail=f"frames={frames}",
        )
        self._append_message("assistant", text, turn.id)
        self._turns_completed += 1
        self._event(
            "turn.completed",
            turn=turn,
            update=update,
            generation=generation,
            duration_ns=monotonic_ns() - response_started,
        )

    async def _response_chunks(
        self,
        update: TranscriptUpdate,
        *,
        committed: bool,
    ) -> AsyncIterable[ConversationResponseChunk]:
        deadline = asyncio.get_running_loop().time() + self._config.response_timeout_s
        produced = self._respond(
            update,
            ConversationContext(tuple(self._history), committed=committed),
        )
        if inspect.isawaitable(produced):
            produced = await asyncio.wait_for(
                produced,
                timeout=self._remaining(deadline, "response"),
            )
        if isinstance(produced, AsyncIterable):
            async for value in _iterate_until(produced, deadline, "response"):
                yield _response_chunk(value)
        else:
            yield _response_chunk(produced)

    def _check_response_bounds(
        self,
        chunks: int,
        characters: int,
        tool_events: int,
    ) -> None:
        if chunks > self._config.maximum_response_chunks_per_turn:
            raise ValueError("response exceeded maximum_response_chunks_per_turn")
        if characters > self._config.maximum_response_characters:
            raise ValueError("response exceeded maximum_response_characters")
        if tool_events > self._config.maximum_tool_events_per_turn:
            raise ValueError("response exceeded maximum_tool_events_per_turn")

    async def _interrupt_delivery(self, delivery: _Delivery) -> None:
        if delivery.generation.active:
            delivery.generation.cancel()
            self._output_generations_cancelled += 1
            self._discontinuity_pending = True
            self._event(
                "output.cancelled",
                turn=delivery.turn,
                generation=delivery.generation,
            )
        if not delivery.task.done():
            delivery.task.cancel()
            try:
                await asyncio.wait_for(
                    delivery.task,
                    timeout=self._config.cancellation_timeout_s,
                )
            except asyncio.CancelledError:
                pass
            except TimeoutError as error:
                raise TimeoutError(
                    "provider did not stop within cancellation_timeout_s"
                ) from error
            if not delivery.interruption_counted:
                self._turns_interrupted += 1
                delivery.interruption_counted = True
                self._event("turn.interrupted", turn=delivery.turn)

    async def _cancel_speculation(self, speculation: _Speculation) -> None:
        if speculation.task.done():
            await speculation.task
            return
        speculation.task.cancel()
        try:
            await asyncio.wait_for(
                speculation.task,
                timeout=self._config.cancellation_timeout_s,
            )
        except asyncio.CancelledError:
            self._event("response.preparation_cancelled", update=speculation.update)
        except TimeoutError as error:
            raise TimeoutError(
                "speculative response did not stop within cancellation_timeout_s"
            ) from error

    async def _provider_lifecycle(self, provider: object, method_name: str) -> None:
        method = getattr(provider, method_name, None)
        if method is None:
            return
        timeout_s = (
            self._config.provider_close_timeout_s
            if method_name == "aclose"
            else self._config.provider_start_timeout_s
        )
        if inspect.iscoroutinefunction(method):
            result = await asyncio.wait_for(method(), timeout=timeout_s)
        else:
            result = await asyncio.wait_for(
                asyncio.to_thread(method),
                timeout=timeout_s,
            )
        if inspect.isawaitable(result):
            await asyncio.wait_for(result, timeout=timeout_s)

    async def _wait_output_drained(self, running: object) -> None:
        from .session import RunningSession

        if not isinstance(running, RunningSession):
            raise TypeError("running must be a pocketstation.aio.RunningSession")
        deadline = (
            asyncio.get_running_loop().time() + self._config.output_drain_timeout_s
        )
        route_ids, endpoint_ids = self._output.output._delivery_targets()
        wait_s = 0.000_25
        while True:
            observations = await self._output.observations()
            metrics = await running.metrics()
            routes = tuple(
                route
                for route in metrics.routes
                if route.route_id in route_ids or route.endpoint_id in endpoint_ids
            )
            if any(
                route.frames_dropped_total > 0
                or route.endpoint.frames_dropped_total > 0
                or route.endpoint.failures_total > 0
                for route in routes
            ):
                raise RuntimeError(
                    "generated audio delivery failed before output drained"
                )
            routes_drained = bool(routes) and all(
                route.edge.queue_depth_frames == 0
                and route.edge.frames_delivered_total
                + (route.edge.discarded_output_frames_total or 0)
                >= self._output_frames_written
                for route in routes
            )
            buffers_reclaimed = (
                observations.available_buffers == observations.buffer_slots
            )
            no_declared_delivery = not route_ids and not endpoint_ids
            if routes_drained or (no_declared_delivery and buffers_reclaimed):
                self._event("output.drained")
                return
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(
                    "generated audio did not drain within output_drain_timeout_s"
                )
            await asyncio.sleep(min(wait_s, remaining))
            wait_s = min(wait_s * 2, 0.005)

    def _turn(
        self,
        envelope: SignalEnvelope[str],
        update: TranscriptUpdate,
    ) -> ConversationTurn:
        lineage = envelope.lineage
        return ConversationTurn(
            id=self._turns_started + 1,
            utterance_id=update.utterance_id,
            text=update.text,
            source_id=(
                update.source_id
                if update.source_id is not None
                else None
                if lineage is None
                else lineage.source_id
            ),
            stream_id=(
                update.stream_id
                if update.stream_id is not None
                else None
                if lineage is None
                else lineage.stream_id
            ),
            source_sequence=(
                update.source_sequence
                if update.source_sequence is not None
                else None
                if lineage is None
                else lineage.sequence_number
            ),
            source_timestamp_ns=(
                update.source_timestamp_ns
                if update.source_timestamp_ns is not None
                else envelope.timing.source_timestamp_ns
            ),
            audio_start_ns=update.audio_start_ns,
            audio_end_ns=update.audio_end_ns,
            received_timestamp_ns=monotonic_ns(),
        )

    def _append_message(self, role: str, content: str, turn_id: int) -> None:
        self._history.append(
            ConversationMessage(
                role=cast(ConversationRole, role),
                content=content,
                turn_id=turn_id,
                timestamp_ns=monotonic_ns(),
            )
        )

    def _event(
        self,
        kind: str,
        *,
        turn: ConversationTurn | None = None,
        update: TranscriptUpdate | None = None,
        generation: OutputGeneration | None = None,
        duration_ns: int | None = None,
        detail: str | None = None,
    ) -> None:
        self._events.append(
            ConversationEvent(
                kind=kind,
                timestamp_ns=monotonic_ns(),
                turn_id=None if turn is None else turn.id,
                utterance_id=(
                    update.utterance_id
                    if update is not None
                    else None
                    if turn is None
                    else turn.utterance_id
                ),
                transcript_revision=None if update is None else update.revision,
                output_generation_id=None if generation is None else generation.id,
                duration_ns=duration_ns,
                detail=detail,
            )
        )

    @staticmethod
    def _remaining(deadline: float, operation: str) -> float:
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise TimeoutError(f"{operation} exceeded its configured timeout")
        return remaining


def _default_transcript_decoder(
    envelope: SignalEnvelope[str],
) -> TranscriptUpdate | None:
    if not isinstance(envelope.payload, str):
        raise TypeError("conversation transcript signals must contain text")
    text = envelope.payload.strip()
    if not text:
        return None
    lineage = envelope.lineage
    source = "unknown" if lineage is None else str(lineage.source_id)
    sequence = 0 if lineage is None else lineage.sequence_number
    audio_start_ns = envelope.timing.source_timestamp_ns
    duration_ns = envelope.timing.duration_ns
    audio_end_ns = (
        None
        if audio_start_ns is None or duration_ns is None
        else audio_start_ns + duration_ns
    )
    return TranscriptUpdate(
        utterance_id=f"{source}:{sequence}",
        revision=1,
        text=text,
        stable_prefix=text,
        final=True,
        source_id=None if lineage is None else lineage.source_id,
        stream_id=None if lineage is None else lineage.stream_id,
        source_sequence=None if lineage is None else lineage.sequence_number,
        source_timestamp_ns=envelope.timing.source_timestamp_ns,
        audio_start_ns=audio_start_ns,
        audio_end_ns=audio_end_ns,
    )


def _response_chunk(value: object) -> ConversationResponseChunk:
    if isinstance(value, ConversationResponseChunk):
        return value
    if isinstance(value, ConversationResponse):
        return ConversationResponseChunk(value.text, value.tool_events)
    if isinstance(value, str):
        return ConversationResponseChunk(value)
    raise TypeError(
        "response provider must return text, ConversationResponse, "
        "ConversationResponseChunk, or an async iterable of those values"
    )


async def _iterate_until(
    values: AsyncIterable[object],
    deadline: float,
    operation: str,
) -> AsyncIterable[object]:
    iterator = aiter(values)
    try:
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(f"{operation} exceeded its configured timeout")
            try:
                yield await asyncio.wait_for(anext(iterator), timeout=remaining)
            except StopAsyncIteration:
                return
    finally:
        close = getattr(iterator, "aclose", None)
        if close is not None:
            result = close()
            if inspect.isawaitable(result):
                await result


async def _iter_prepared(
    chunks: tuple[ConversationResponseChunk, ...],
) -> AsyncIterable[ConversationResponseChunk]:
    for chunk in chunks:
        yield chunk


def _unique_providers(*providers: object) -> tuple[object, ...]:
    unique: list[object] = []
    identities: set[int] = set()
    for provider in providers:
        if id(provider) not in identities:
            unique.append(provider)
            identities.add(id(provider))
    return tuple(unique)


__all__ = [
    "Conversation",
    "ResponseHandler",
    "SynthesisHandler",
    "TranscriptDecoder",
]
