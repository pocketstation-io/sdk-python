"""Example-owned OpenAI Realtime adapter for the voice debugging demo."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import sys
from array import array
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from math import sqrt
from time import monotonic_ns
from typing import Any
from urllib.parse import urlencode

import pocketstation.aio as pks
from pocketstation.aio.event_input import EventInput
from pocketstation.audio_input import OutputGeneration
from pocketstation.errors import (
    AudioInputFullError,
    EventInputFullError,
)
from pocketstation.signal import BusSubscription, SignalEnvelope
from websockets.asyncio.client import ClientConnection, connect

_MODEL_SAMPLE_RATE_HZ = 24_000
_SESSION_SAMPLE_RATE_HZ = 48_000
_SESSION_FRAME_SAMPLES = 480
_MAX_EVENT_BYTES = 262_144
_MAX_INPUT_QUEUE_FRAMES = 64
_MAX_OUTPUT_QUEUE_CHUNKS = 32
_MAX_RETAINED_EVENTS = 65_536
_MAX_RETAINED_VOICED_FRAMES = 12_000


@dataclass(frozen=True, slots=True)
class RealtimeVoiceConfig:
    """Finite OpenAI Realtime connection and buffering settings."""

    model: str = "gpt-realtime-2.1"
    voice: str = "marin"
    instructions: str = (
        "Answer clearly and in enough detail that the user can interrupt you."
    )
    connect_timeout_s: float = 10.0
    close_timeout_s: float = 5.0
    input_queue_frames: int = _MAX_INPUT_QUEUE_FRAMES
    output_queue_chunks: int = _MAX_OUTPUT_QUEUE_CHUNKS

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.voice.strip():
            raise ValueError("model and voice must not be empty")
        if not self.instructions.strip():
            raise ValueError("instructions must not be empty")
        for name, value in (
            ("connect_timeout_s", self.connect_timeout_s),
            ("close_timeout_s", self.close_timeout_s),
        ):
            if isinstance(value, bool) or not 0 < value <= 60:
                raise ValueError(f"{name} must be greater than 0 and at most 60")
        for name, value, maximum in (
            ("input_queue_frames", self.input_queue_frames, 4_096),
            ("output_queue_chunks", self.output_queue_chunks, 1_024),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if not 1 <= value <= maximum:
                raise ValueError(f"{name} must be between 1 and {maximum}")


@dataclass(frozen=True, slots=True)
class RealtimeVoiceObservations:
    """Finite provider and PocketStation boundary counters."""

    input_frames_sent: int
    input_frames_dropped: int
    output_chunks_received: int
    output_chunks_dropped: int
    output_frames_written: int
    output_generations_cancelled: int
    provider_errors: int
    event_input_drops: int


@dataclass(slots=True)
class _RouteTimeline:
    label: str
    first_sequence: int | None = None
    last_sequence: int | None = None
    sequence_gaps: int = 0
    maximum_route_delay_ns: int = 0
    discontinuities: set[int] = field(default_factory=set)
    voiced_frames: deque[tuple[int, int]] = field(
        default_factory=lambda: deque(maxlen=_MAX_RETAINED_VOICED_FRAMES)
    )


@dataclass(frozen=True, slots=True)
class _OutputChunk:
    response_id: str
    generation: OutputGeneration
    pcm16le: bytes
    done: bool = False


@dataclass(slots=True)
class _ResponseOutput:
    response_id: str
    generation: OutputGeneration
    item_id: str | None = None


class _Pcm24To48:
    def __init__(self) -> None:
        self._previous: float | None = None
        self._pending = array("f")

    def append(self, pcm16le: bytes) -> tuple[array[float], ...]:
        samples = _pcm16le(pcm16le)
        for value in samples:
            current = float(value) / 32_768.0
            if self._previous is not None:
                self._pending.append(self._previous)
                self._pending.append((self._previous + current) * 0.5)
            self._previous = current
        return self._take_frames()

    def finish(self) -> tuple[array[float], ...]:
        if self._previous is not None:
            self._pending.extend((self._previous, self._previous))
            self._previous = None
        remainder = len(self._pending) % _SESSION_FRAME_SAMPLES
        if remainder:
            self._pending.extend([0.0] * (_SESSION_FRAME_SAMPLES - remainder))
        return self._take_frames()

    def _take_frames(self) -> tuple[array[float], ...]:
        frames: list[array[float]] = []
        while len(self._pending) >= _SESSION_FRAME_SAMPLES:
            frames.append(array("f", self._pending[:_SESSION_FRAME_SAMPLES]))
            del self._pending[:_SESSION_FRAME_SAMPLES]
        return tuple(frames)


class OpenAIRealtimeVoice:
    """Move one PocketStation microphone stem through OpenAI Realtime.

    PocketStation owns capture, media identity, bounded fan-out, recording,
    Relay publication, generated-audio ingestion, and sender-side cancellation.
    This example adapter owns only the provider WebSocket and PCM conversion.
    """

    def __init__(
        self,
        *,
        api_key: str,
        microphone_route_id: int,
        output: pks.AudioInput,
        events: EventInput,
        route_labels: Mapping[int, str],
        config: RealtimeVoiceConfig | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        self._api_key = api_key
        self._microphone_route_id = microphone_route_id
        self._output = output
        self._events = events
        self._route_labels = dict(route_labels)
        self._config = RealtimeVoiceConfig() if config is None else config
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue(
            self._config.input_queue_frames
        )
        self._output_queue: asyncio.Queue[_OutputChunk | None] = asyncio.Queue(
            self._config.output_queue_chunks
        )
        self._input_enabled = asyncio.Event()
        self._ready = asyncio.Event()
        self._socket: ClientConnection | None = None
        self._tasks: list[asyncio.Task[None]] = []
        self._response: _ResponseOutput | None = None
        self._failure: BaseException | None = None
        self._timelines: dict[int, _RouteTimeline] = {}
        self._event_records: deque[dict[str, Any]] = deque(maxlen=_MAX_RETAINED_EVENTS)
        self._input_frames_sent = 0
        self._input_frames_dropped = 0
        self._output_chunks_received = 0
        self._output_chunks_dropped = 0
        self._output_frames_written = 0
        self._output_generations_cancelled = 0
        self._provider_errors = 0
        self._event_input_drops = 0
        self._started = False
        self._closed = False

    @property
    def observations(self) -> RealtimeVoiceObservations:
        return RealtimeVoiceObservations(
            input_frames_sent=self._input_frames_sent,
            input_frames_dropped=self._input_frames_dropped,
            output_chunks_received=self._output_chunks_received,
            output_chunks_dropped=self._output_chunks_dropped,
            output_frames_written=self._output_frames_written,
            output_generations_cancelled=self._output_generations_cancelled,
            provider_errors=self._provider_errors,
            event_input_drops=self._event_input_drops,
        )

    async def connect(self) -> None:
        """Open and configure one finite provider connection."""
        if self._socket is not None:
            raise RuntimeError("OpenAI Realtime connection is already open")
        query = urlencode({"model": self._config.model})
        self._socket = await connect(
            f"wss://api.openai.com/v1/realtime?{query}",
            additional_headers={"Authorization": f"Bearer {self._api_key}"},
            compression=None,
            open_timeout=self._config.connect_timeout_s,
            close_timeout=self._config.close_timeout_s,
            ping_interval=20,
            ping_timeout=20,
            max_size=_MAX_EVENT_BYTES,
            max_queue=16,
            write_limit=32_768,
        )
        self._tasks.append(
            asyncio.create_task(self._receive(), name="pks-openai-receive")
        )
        await self._send(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "instructions": self._config.instructions,
                    "output_modalities": ["audio"],
                    "audio": {
                        "input": {
                            "format": {
                                "type": "audio/pcm",
                                "rate": _MODEL_SAMPLE_RATE_HZ,
                            },
                            "transcription": {"model": "gpt-live-transcribe"},
                            "turn_detection": {
                                "type": "server_vad",
                                "create_response": True,
                                "interrupt_response": True,
                            },
                        },
                        "output": {
                            "format": {
                                "type": "audio/pcm",
                                "rate": _MODEL_SAMPLE_RATE_HZ,
                            },
                            "voice": self._config.voice,
                        },
                    },
                },
            }
        )
        await asyncio.wait_for(
            self._ready.wait(), timeout=self._config.connect_timeout_s
        )
        if self._failure is not None:
            raise RuntimeError("OpenAI Realtime setup failed") from self._failure

    async def start(
        self,
        running: pks.RunningSession,
        event_log: BusSubscription[bytes],
    ) -> None:
        """Start bounded media and event workers for one running Session."""
        if self._socket is None:
            raise RuntimeError("connect() must complete before start()")
        if self._started:
            raise RuntimeError("OpenAI Realtime media workers already started")
        if int(running.session_id) != event_log.session_id:
            raise ValueError("event_log and running must belong to one Session")
        self._started = True
        self._tasks.extend(
            (
                asyncio.create_task(self._read_audio(running), name="pks-openai-media"),
                asyncio.create_task(self._send_audio(), name="pks-openai-input"),
                asyncio.create_task(self._write_output(), name="pks-openai-output"),
                asyncio.create_task(
                    self._read_events(running, event_log), name="pks-openai-events"
                ),
            )
        )

    def enable_input(self) -> None:
        """Begin forwarding microphone frames after the receiver is ready."""
        if not self._started:
            raise RuntimeError("start() must complete before enable_input()")
        self._input_enabled.set()
        self._event("pocketstation.input.enabled")

    async def wait(self) -> None:
        """Wait until the provider connection closes or fails."""
        if not self._tasks:
            raise RuntimeError("connect() must complete before wait()")
        await self._tasks[0]
        if self._failure is not None:
            raise RuntimeError("OpenAI Realtime connection failed") from self._failure

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._response is not None and self._response.generation.active:
            self._response.generation.cancel()
            self._output_generations_cancelled += 1
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        if self._socket is not None:
            await self._socket.close(code=1000)
            await self._socket.wait_closed()
        await self._events.aclose()

    def print_report(self) -> None:
        """Print measured media and interruption facts, including missing facts."""
        event_times = [
            int(event["pocketstation_timestamp_ns"])
            for event in self._event_records
            if "pocketstation_timestamp_ns" in event
        ]
        audio_times = [
            timeline.voiced_frames[0][0]
            for timeline in self._timelines.values()
            if timeline.voiced_frames
        ]
        origin = min((*event_times, *audio_times), default=0)
        print("\nPocketStation voice timeline")
        for route_id, timeline in sorted(self._timelines.items()):
            first = timeline.voiced_frames[0][0] if timeline.voiced_frames else None
            last = (
                timeline.voiced_frames[-1][0] + timeline.voiced_frames[-1][1]
                if timeline.voiced_frames
                else None
            )
            print(
                f"  {timeline.label:18} route={route_id} "
                f"first_voice={_relative(first, origin)} "
                f"last_voice={_relative(last, origin)} "
                f"sequence_gaps={timeline.sequence_gaps} "
                f"discontinuities={len(timeline.discontinuities)} "
                f"max_route_delay_ms={timeline.maximum_route_delay_ns / 1_000_000:.1f}"
            )
        interruption = _event_time(
            self._event_records, "input_audio_buffer.speech_started"
        )
        cancelled = _event_time(
            self._event_records,
            "pocketstation.output.cancelled",
            after=interruption,
        )
        if interruption is not None:
            print(f"  user speech detected       {_relative(interruption, origin)}")
        if interruption is not None and cancelled is not None:
            print(f"  output cancelled           {_relative(cancelled, origin)}")
            print(
                "  cancellation decision      "
                f"{max(cancelled - interruption, 0) / 1_000_000:.1f} ms"
            )
        print(f"  provider boundary         {self.observations}")
        print(
            "  browser playout cutoff    unavailable: the receiver has not returned "
            "a played-sample acknowledgement"
        )
        print(
            "  conversation truncation   unavailable until that playout position "
            "can be sent to the model provider"
        )

    async def _read_audio(self, running: pks.RunningSession) -> None:
        async for frame in running.audio:
            timeline = self._timelines.setdefault(
                int(frame.route_id),
                _RouteTimeline(
                    self._route_labels.get(
                        int(frame.route_id), f"route-{int(frame.route_id)}"
                    )
                ),
            )
            _observe_frame(timeline, frame)
            if (
                int(frame.route_id) != self._microphone_route_id
                or not self._input_enabled.is_set()
            ):
                continue
            try:
                encoded = _encode_microphone_frame(frame)
                self._input_queue.put_nowait(encoded)
            except asyncio.QueueFull:
                self._input_frames_dropped += 1
                self._event("pocketstation.provider_input.full")

    async def _send_audio(self) -> None:
        while True:
            encoded = await self._input_queue.get()
            try:
                if encoded is None:
                    return
                await self._send(
                    {"type": "input_audio_buffer.append", "audio": encoded}
                )
                self._input_frames_sent += 1
            finally:
                self._input_queue.task_done()

    async def _receive(self) -> None:
        assert self._socket is not None
        try:
            async for message in self._socket:
                if not isinstance(message, str):
                    raise ValueError("OpenAI Realtime returned a binary message")
                event = json.loads(message)
                if not isinstance(event, dict):
                    raise ValueError("OpenAI Realtime event must be an object")
                self._handle_event(event)
        except asyncio.CancelledError:
            raise
        except BaseException as error:
            self._failure = error
            self._provider_errors += 1
            self._event(
                "provider.connection.failed",
                detail=f"{type(error).__name__}: {error}"[:2_048],
            )
        finally:
            self._ready.set()

    def _handle_event(self, event: Mapping[str, Any]) -> None:
        event_type = event.get("type")
        if not isinstance(event_type, str) or len(event_type) > 128:
            raise ValueError("OpenAI Realtime event type is invalid")
        if event_type == "session.updated":
            self._event(event_type)
            self._ready.set()
            return
        if event_type == "error":
            detail = event.get("error")
            self._provider_errors += 1
            self._event(event_type, detail=str(detail)[:2_048])
            self._failure = RuntimeError(f"OpenAI Realtime error: {detail}")
            self._ready.set()
            return
        if event_type == "response.created":
            response_id = _nested_string(event, "response", "id")
            generation = self._output.begin_output()
            self._response = _ResponseOutput(response_id, generation)
            self._event(
                event_type,
                response_id=response_id,
                output_generation_id=generation.id,
            )
            return
        if event_type == "response.output_item.added":
            response_id = _required_string(event, "response_id")
            if self._response is not None and self._response.response_id == response_id:
                self._response.item_id = _nested_string(event, "item", "id")
            self._event(event_type, response_id=response_id)
            return
        if event_type == "response.output_audio.delta":
            self._queue_output_delta(event)
            return
        if event_type == "response.output_audio.done":
            response = self._matching_response(event)
            self._queue_output(
                _OutputChunk(response.response_id, response.generation, b"", done=True)
            )
            self._event(event_type, response_id=response.response_id)
            return
        if event_type == "input_audio_buffer.speech_started":
            self._event(
                event_type,
                item_id=_optional_string(event, "item_id"),
                audio_start_ms=event.get("audio_start_ms"),
            )
            self._cancel_output()
            return
        if event_type in {
            "input_audio_buffer.speech_stopped",
            "conversation.item.input_audio_transcription.delta",
            "conversation.item.input_audio_transcription.completed",
            "response.output_audio_transcript.delta",
            "response.output_audio_transcript.done",
            "response.done",
        }:
            self._record_text_event(event_type, event)
            return
        self._event(event_type)

    def _queue_output_delta(self, event: Mapping[str, Any]) -> None:
        response = self._matching_response(event)
        encoded = event.get("delta")
        if (
            not isinstance(encoded, str)
            or not encoded
            or len(encoded) > _MAX_EVENT_BYTES
        ):
            raise ValueError("OpenAI Realtime audio delta has an invalid size")
        try:
            pcm16le = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("OpenAI Realtime audio delta is not Base64") from error
        if len(pcm16le) > _MAX_EVENT_BYTES or len(pcm16le) % 2:
            raise ValueError("OpenAI Realtime audio delta has an invalid size")
        self._output_chunks_received += 1
        self._queue_output(
            _OutputChunk(response.response_id, response.generation, pcm16le)
        )

    def _queue_output(self, chunk: _OutputChunk) -> None:
        if not chunk.generation.active:
            self._output_chunks_dropped += 1
            return
        try:
            self._output_queue.put_nowait(chunk)
        except asyncio.QueueFull:
            self._output_chunks_dropped += 1
            if chunk.generation.active:
                chunk.generation.cancel()
                self._output_generations_cancelled += 1
            self._event(
                "pocketstation.provider_output.full",
                response_id=chunk.response_id,
                output_generation_id=chunk.generation.id,
            )

    async def _write_output(self) -> None:
        converters: dict[int, _Pcm24To48] = {}
        discontinuity = False
        while True:
            chunk = await self._output_queue.get()
            try:
                if chunk is None:
                    return
                if not chunk.generation.active:
                    self._output_chunks_dropped += 1
                    discontinuity = True
                    continue
                converter = converters.setdefault(chunk.generation.id, _Pcm24To48())
                frames = (
                    converter.finish()
                    if chunk.done
                    else converter.append(chunk.pcm16le)
                )
                for samples in frames:
                    try:
                        await self._output.write(
                            samples,
                            discontinuity=discontinuity,
                            generation=chunk.generation,
                            timeout_s=1.0,
                        )
                    except AudioInputFullError:
                        self._output_chunks_dropped += 1
                        discontinuity = True
                        self._event(
                            "pocketstation.output.full",
                            response_id=chunk.response_id,
                            output_generation_id=chunk.generation.id,
                        )
                    else:
                        discontinuity = False
                        self._output_frames_written += 1
                if chunk.done:
                    converters.pop(chunk.generation.id, None)
            finally:
                self._output_queue.task_done()

    async def _read_events(
        self,
        running: pks.RunningSession,
        subscription: BusSubscription[bytes],
    ) -> None:
        async for envelope in running.signals(subscription):
            record = _decode_event(envelope)
            record["pocketstation_timestamp_ns"] = envelope.timing.observed_timestamp_ns
            self._event_records.append(record)
            if record.get("type") in {
                "input_audio_buffer.speech_started",
                "pocketstation.output.cancelled",
                "provider.connection.failed",
                "error",
            }:
                print(
                    f"{envelope.timing.observed_timestamp_ns / 1_000_000_000:12.3f}  "
                    f"{record['type']}",
                    flush=True,
                )

    async def _send(self, event: Mapping[str, Any]) -> None:
        if self._socket is None:
            raise RuntimeError("OpenAI Realtime connection is not open")
        await self._socket.send(
            json.dumps(event, ensure_ascii=True, separators=(",", ":"))
        )

    def _matching_response(self, event: Mapping[str, Any]) -> _ResponseOutput:
        response_id = _required_string(event, "response_id")
        if self._response is None or self._response.response_id != response_id:
            raise ValueError("OpenAI Realtime output has no matching response")
        return self._response

    def _cancel_output(self) -> None:
        response = self._response
        if response is None or not response.generation.active:
            return
        response.generation.cancel()
        self._output_generations_cancelled += 1
        self._event(
            "pocketstation.output.cancelled",
            response_id=response.response_id,
            item_id=response.item_id,
            output_generation_id=response.generation.id,
            browser_playout_position="unavailable",
        )

    def _record_text_event(self, event_type: str, event: Mapping[str, Any]) -> None:
        text = event.get("delta")
        if not isinstance(text, str):
            text = event.get("transcript")
        values: dict[str, object] = {}
        if isinstance(text, str):
            values["text"] = text[:8_192]
        for name in ("item_id", "response_id"):
            value = event.get(name)
            if isinstance(value, str):
                values[name] = value[:128]
        self._event(event_type, **values)
        if event_type == "conversation.item.input_audio_transcription.delta" and text:
            print(text, end="", flush=True)
        elif (
            event_type == "conversation.item.input_audio_transcription.completed"
            and text
        ):
            print(flush=True)

    def _event(self, event_type: str, **values: object) -> None:
        event = {"type": event_type, **values}
        try:
            self._events.try_write(event, timestamp_ns=monotonic_ns())
        except EventInputFullError:
            self._event_input_drops += 1


def silent_frame() -> array[float]:
    """Return one exact 10 ms Session frame for Relay attachment."""
    return array("f", [0.0] * _SESSION_FRAME_SAMPLES)


def _encode_microphone_frame(frame: Any) -> str:
    if frame.sample_rate_hz != _SESSION_SAMPLE_RATE_HZ or frame.channel_count != 1:
        raise ValueError("the OpenAI example requires 48 kHz mono Session audio")
    samples = _f32le(frame.samples_f32le)
    if len(samples) != _SESSION_FRAME_SAMPLES:
        raise ValueError("the OpenAI example requires exact 10 ms Session frames")
    pcm = array(
        "h",
        (
            _pcm16((float(samples[index]) + float(samples[index + 1])) * 0.5)
            for index in range(0, len(samples), 2)
        ),
    )
    if sys.byteorder != "little":
        pcm.byteswap()
    return base64.b64encode(pcm.tobytes()).decode("ascii")


def _pcm16(value: float) -> int:
    return max(-32_768, min(32_767, round(value * 32_767.0)))


def _f32le(payload: bytes) -> array[float]:
    samples = array("f")
    samples.frombytes(payload)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def _pcm16le(payload: bytes) -> array[int]:
    samples = array("h")
    samples.frombytes(payload)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def _observe_frame(timeline: _RouteTimeline, frame: Any) -> None:
    if timeline.first_sequence is None:
        timeline.first_sequence = frame.sequence_number
    elif (
        timeline.last_sequence is not None
        and frame.sequence_number != timeline.last_sequence + 1
    ):
        timeline.sequence_gaps += 1
    timeline.last_sequence = frame.sequence_number
    timeline.discontinuities.add(frame.discontinuity_epoch)
    timeline.maximum_route_delay_ns = max(
        timeline.maximum_route_delay_ns,
        frame.route_received_at_ns - frame.route_enqueued_at_ns,
    )
    samples = _f32le(frame.samples_f32le)
    rms = sqrt(sum(float(value) ** 2 for value in samples) / len(samples))
    if rms >= 0.01:
        timeline.voiced_frames.append((frame.route_received_at_ns, frame.duration_ns))


def _decode_event(envelope: SignalEnvelope[bytes]) -> dict[str, Any]:
    decoded = json.loads(envelope.payload.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("event input emitted a non-object JSON value")
    return decoded


def _required_string(event: Mapping[str, Any], name: str) -> str:
    value = event.get(name)
    if not isinstance(value, str) or not value or len(value) > 8_192:
        raise ValueError(f"OpenAI Realtime event has invalid {name}")
    return value


def _optional_string(event: Mapping[str, Any], name: str) -> str | None:
    value = event.get(name)
    return value[:128] if isinstance(value, str) else None


def _nested_string(event: Mapping[str, Any], parent: str, name: str) -> str:
    nested = event.get(parent)
    if not isinstance(nested, dict):
        raise ValueError(f"OpenAI Realtime event has invalid {parent}")
    return _required_string(nested, name)


def _event_time(
    events: deque[dict[str, Any]],
    event_type: str,
    *,
    after: int | None = None,
) -> int | None:
    return next(
        (
            int(event["pocketstation_timestamp_ns"])
            for event in events
            if event.get("type") == event_type
            and (after is None or int(event["pocketstation_timestamp_ns"]) >= after)
        ),
        None,
    )


def _relative(value: int | None, origin: int) -> str:
    return (
        "not observed" if value is None else f"{(value - origin) / 1_000_000_000:.3f}s"
    )


__all__ = [
    "OpenAIRealtimeVoice",
    "RealtimeVoiceConfig",
    "RealtimeVoiceObservations",
    "silent_frame",
]
