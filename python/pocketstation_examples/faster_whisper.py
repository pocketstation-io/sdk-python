"""Transcribe source-aware example audio with faster-whisper."""

from __future__ import annotations

import asyncio
import importlib
import json
from collections.abc import AsyncIterator, Callable, Iterable, Mapping
from dataclasses import dataclass
from time import monotonic_ns
from typing import Any, Protocol, cast

from pocketstation.aio.capture import Capture
from pocketstation.aio.operator_authoring import (
    OperatorDeadlines as AsyncOperatorDeadlines,
)
from pocketstation.aio.operator_authoring import OperatorNode as AsyncOperatorNode
from pocketstation.aio.operator_authoring import (
    OperatorProvider as AsyncOperatorProvider,
)
from pocketstation.aio.session import Session as AsyncSession
from pocketstation.graph import (
    DerivedStream,
    Multiplicity,
    PortSpec,
    SignalSpec,
    SourceOutput,
    Stem,
)
from pocketstation.operator_authoring import (
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorProvider,
)
from pocketstation.signal import BusSubscription, SignalEnvelope

from .audio_windows import (
    AudioWindow,
    AudioWindowBuffer,
    mono_16khz,
)
from .transcript import TRANSCRIPT_SIGNAL, Transcript


class WhisperSegment(Protocol):
    start: float
    end: float
    text: str


class WhisperInfo(Protocol):
    language: str
    language_probability: float


class WhisperModel(Protocol):
    def transcribe(
        self,
        audio: object,
        *,
        beam_size: int,
        language: str | None,
        vad_filter: bool,
    ) -> tuple[Iterable[WhisperSegment], WhisperInfo]: ...


@dataclass(frozen=True, slots=True)
class FasterWhisperConfiguration:
    """Finite model and buffering policy for one local transcription Operator."""

    model: str = "base"
    model_revision: str | None = None
    device: str = "auto"
    compute_type: str = "default"
    cpu_threads: int = 4
    num_workers: int = 1
    allow_model_download: bool = True
    language: str | None = None
    beam_size: int = 5
    vad_filter: bool = True
    window_seconds: float = 5.0
    queue_capacity_signals: int = 512
    maximum_sources: int = 8
    maximum_output_bytes: int = 1_048_576
    create_timeout_s: float = 120.0
    inference_timeout_s: float = 120.0

    def __post_init__(self) -> None:
        for name, value in (
            ("model", self.model),
            ("device", self.device),
            ("compute_type", self.compute_type),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.language is not None and (
            not self.language or not self.language.isascii()
        ):
            raise ValueError("language must be None or non-empty ASCII")
        if self.model_revision is not None and (
            not self.model_revision.strip() or not self.model_revision.isascii()
        ):
            raise ValueError("model_revision must be None or non-empty ASCII")
        if not 1 <= self.cpu_threads <= 64:
            raise ValueError("cpu_threads must be between 1 and 64")
        if not 1 <= self.num_workers <= 16:
            raise ValueError("num_workers must be between 1 and 16")
        if not 1 <= self.beam_size <= 32:
            raise ValueError("beam_size must be between 1 and 32")
        if not 0.1 <= self.window_seconds <= 30:
            raise ValueError("window_seconds must be between 0.1 and 30")
        if not 8 <= self.queue_capacity_signals <= 4_096:
            raise ValueError("queue_capacity_signals must be between 8 and 4096")
        if not 1 <= self.maximum_sources <= 64:
            raise ValueError("maximum_sources must be between 1 and 64")
        if not 1_024 <= self.maximum_output_bytes <= 16_777_216:
            raise ValueError("maximum_output_bytes must be between 1024 and 16777216")
        if not 1 <= self.create_timeout_s <= 600:
            raise ValueError("create_timeout_s must be between 1 and 600")
        if not 1 <= self.inference_timeout_s <= 600:
            raise ValueError("inference_timeout_s must be between 1 and 600")


ModelFactory = Callable[[FasterWhisperConfiguration], WhisperModel]
AudioConverter = Callable[[AudioWindow], object]


class _FasterWhisperNode(AsyncOperatorNode):
    def __init__(
        self,
        configuration: FasterWhisperConfiguration,
        model: WhisperModel,
        audio_converter: AudioConverter,
    ) -> None:
        self._configuration = configuration
        self._model = model
        self._audio_converter = audio_converter
        self._windows = AudioWindowBuffer(
            window_seconds=configuration.window_seconds,
            maximum_sources=configuration.maximum_sources,
        )
        self._cancelled = False

    async def process(
        self,
        input_port: str,
        envelope: SignalEnvelope[object],
    ) -> tuple[OperatorEmission, ...]:
        if input_port != "audio":
            raise ValueError(f"unexpected input port: {input_port}")
        if self._cancelled:
            raise asyncio.CancelledError
        emissions = []
        for window in self._windows.push(envelope):
            emissions.append(await self._transcribe(window))
        return tuple(emissions)

    async def flush(self) -> tuple[OperatorEmission, ...]:
        if self._cancelled:
            self._windows.clear()
            return ()
        emissions = []
        for window in self._windows.flush():
            emissions.append(await self._transcribe(window))
        return tuple(emissions)

    async def cancel(self) -> None:
        self._cancelled = True
        self._windows.clear()

    async def close(self) -> None:
        await self.cancel()

    async def _transcribe(
        self,
        window: AudioWindow,
    ) -> OperatorEmission:
        return await asyncio.wait_for(
            asyncio.to_thread(
                _transcribe_window,
                self._configuration,
                self._model,
                self._audio_converter,
                window,
            ),
            timeout=self._configuration.inference_timeout_s,
        )


class _SyncFasterWhisperNode(OperatorNode):
    """Blocking model call hosted by Core's off-realtime Operator worker."""

    def __init__(
        self,
        configuration: FasterWhisperConfiguration,
        model: WhisperModel,
        audio_converter: AudioConverter,
    ) -> None:
        self._configuration = configuration
        self._model = model
        self._audio_converter = audio_converter
        self._windows = AudioWindowBuffer(
            window_seconds=configuration.window_seconds,
            maximum_sources=configuration.maximum_sources,
        )
        self._cancelled = False

    def process(
        self,
        input_port: str,
        envelope: SignalEnvelope[object],
    ) -> tuple[OperatorEmission, ...]:
        if input_port != "audio":
            raise ValueError(f"unexpected input port: {input_port}")
        if self._cancelled:
            raise RuntimeError("transcription Operator is cancelled")
        return tuple(
            _transcribe_window(
                self._configuration,
                self._model,
                self._audio_converter,
                window,
            )
            for window in self._windows.push(envelope)
        )

    def flush(self) -> tuple[OperatorEmission, ...]:
        if self._cancelled:
            self._windows.clear()
            return ()
        return tuple(
            _transcribe_window(
                self._configuration,
                self._model,
                self._audio_converter,
                window,
            )
            for window in self._windows.flush()
        )

    def cancel(self) -> None:
        self._cancelled = True
        self._windows.clear()

    def close(self) -> None:
        self.cancel()


def _transcribe_window(
    configuration: FasterWhisperConfiguration,
    model: WhisperModel,
    audio_converter: AudioConverter,
    window: AudioWindow,
) -> OperatorEmission:
    inference_started_ns = monotonic_ns()
    samples = audio_converter(window)
    segments, info = model.transcribe(
        samples,
        beam_size=configuration.beam_size,
        language=configuration.language,
        vad_filter=configuration.vad_filter,
    )
    completed = tuple(segments)
    result = {
        "channel_count": window.channel_count,
        "clock_id": window.clock_id,
        "discontinuity_epoch": window.discontinuity_epoch,
        "discontinuity_reasons": list(window.discontinuity_reasons),
        "duration_ms": window.duration_ms,
        "inference_duration_ns": monotonic_ns() - inference_started_ns,
        "language": info.language,
        "language_probability": info.language_probability,
        "policy_epoch": window.policy_epoch,
        "sample_rate_hz": window.sample_rate_hz,
        "session_id": window.session_id,
        "session_timestamp_end_ns": window.session_timestamp_end_ns,
        "session_timestamp_start_ns": window.session_timestamp_start_ns,
        "segments": [
            {
                "end_s": segment.end,
                "start_s": segment.start,
                "text": segment.text.strip(),
            }
            for segment in completed
        ],
        "sequence_end": window.sequence_end,
        "sequence_start": window.sequence_start,
        "source_id": window.source_id,
        "source_generation": window.source_generation,
        "source_timestamp_end_ns": window.source_timestamp_end_ns,
        "source_timestamp_start_ns": window.source_timestamp_start_ns,
        "stream_id": window.stream_id,
        "text": " ".join(segment.text.strip() for segment in completed).strip(),
        "timestamp_end_ns": window.timestamp_end_ns,
        "timestamp_start_ns": window.timestamp_start_ns,
    }
    encoded = json.dumps(result, separators=(",", ":"), sort_keys=True)
    if len(encoded.encode()) > configuration.maximum_output_bytes:
        raise RuntimeError("transcript envelope exceeds maximum_output_bytes")
    return OperatorEmission.text(encoded, signal=TRANSCRIPT_SIGNAL)


class _SyncFasterWhisperFactory:
    def __init__(
        self,
        configuration: FasterWhisperConfiguration,
        model_factory: ModelFactory,
        audio_converter: AudioConverter,
    ) -> None:
        self._configuration = configuration
        self._model_factory = model_factory
        self._audio_converter = audio_converter

    def create(self, _configuration: Mapping[str, str]) -> _SyncFasterWhisperNode:
        return _SyncFasterWhisperNode(
            self._configuration,
            self._model_factory(self._configuration),
            self._audio_converter,
        )


class FasterWhisper:
    """Optional faster-whisper integration over Core's Operator runtime."""

    def __init__(
        self,
        configuration: FasterWhisperConfiguration | None = None,
        *,
        model_factory: ModelFactory | None = None,
        _audio_converter: AudioConverter | None = None,
    ) -> None:
        self.configuration = configuration or FasterWhisperConfiguration()
        self._model_factory = model_factory or _load_model
        self._audio_converter = _audio_converter or _numpy_audio
        self.manifest = OperatorManifest(
            "community.faster-whisper.stt.v1",
            inputs=(
                PortSpec.input(
                    "audio",
                    SignalSpec.audio(),
                    multiplicity=Multiplicity.MANY,
                ),
            ),
            outputs=(PortSpec.output("transcript", TRANSCRIPT_SIGNAL),),
            queue_capacity_signals=self.configuration.queue_capacity_signals,
            process_timeout_ms=round(
                (self.configuration.inference_timeout_s + 1) * 1_000
            ),
            network_allowed=self.configuration.allow_model_download,
            filesystem_allowed=True,
            terminal_roles=("transcript.final",),
        )

    def sync_provider(self) -> OperatorProvider:
        """Use Core's off-realtime worker directly from sync or asyncio Sessions."""
        return OperatorProvider.with_node(
            self.manifest,
            _SyncFasterWhisperFactory(
                self.configuration,
                self._model_factory,
                self._audio_converter,
            ),
        )

    def provider(self) -> AsyncOperatorProvider:
        """Use an asyncio node while keeping native inference off the event loop."""

        async def create(_configuration: Mapping[str, str]) -> _FasterWhisperNode:
            model = await asyncio.to_thread(self._model_factory, self.configuration)
            return _FasterWhisperNode(
                self.configuration,
                model,
                self._audio_converter,
            )

        return AsyncOperatorProvider.with_node(
            self.manifest,
            create,
            deadlines=AsyncOperatorDeadlines(
                create_s=self.configuration.create_timeout_s,
                prepare_s=5,
                process_s=self.configuration.inference_timeout_s + 0.5,
                close_s=5,
            ),
        )

    def attach(
        self,
        session: AsyncSession,
        stream: Stem | SourceOutput | DerivedStream,
    ) -> BusSubscription[str]:
        """Attach transcription to any Session-owned PCM stream in two lines."""
        operator = session.register_operator(self.sync_provider()).declare()
        stream.connect(operator.input("audio"))
        return session.subscribe(
            operator.output("transcript"),
            signal=TRANSCRIPT_SIGNAL,
        )

    def attach_many(
        self,
        session: AsyncSession,
        streams: Iterable[Stem | SourceOutput | DerivedStream],
    ) -> BusSubscription[str]:
        """Share one model across finite source-aware Session inputs."""
        operator = session.register_operator(self.sync_provider()).declare()
        input_port = operator.input("audio")
        attached = 0
        for stream in streams:
            stream.connect(input_port)
            attached += 1
        if attached == 0:
            raise ValueError("transcription requires at least one input stream")
        return session.subscribe(
            operator.output("transcript"),
            signal=TRANSCRIPT_SIGNAL,
        )

    def transcribe(self, capture: Capture) -> AsyncIterator[Transcript]:
        """Attach to every selected stem and return typed transcript results."""
        subscription = self.attach_many(capture.session, capture.stems)

        async def results() -> AsyncIterator[Transcript]:
            async for event in capture.signals(subscription):
                yield Transcript.from_json(event.payload)

        return results()


def _load_model(configuration: FasterWhisperConfiguration) -> WhisperModel:
    try:
        module = importlib.import_module("faster_whisper")
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "install PocketStation with the transcription extra: "
            "pip install 'pocketstation[transcription]'"
        ) from error
    model: Any = module.WhisperModel(
        configuration.model,
        device=configuration.device,
        compute_type=configuration.compute_type,
        cpu_threads=configuration.cpu_threads,
        num_workers=configuration.num_workers,
        local_files_only=not configuration.allow_model_download,
        revision=configuration.model_revision,
    )
    return cast(WhisperModel, model)


def _numpy_audio(window: AudioWindow) -> object:
    numpy = importlib.import_module("numpy")
    return numpy.asarray(mono_16khz(window), dtype="float32")


__all__ = ["TRANSCRIPT_SIGNAL", "FasterWhisper", "FasterWhisperConfiguration"]
