"""Source-aware local transcription through the faster-whisper Python API."""

from __future__ import annotations

import asyncio
import importlib
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast

import pocketstation
import pocketstation.aio as pks_aio

from examples.transcription.audio_windows import (
    AudioWindow,
    AudioWindowBuffer,
    mono_16khz,
)
from examples.transcription.transcript import TRANSCRIPT_SIGNAL


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
    device: str = "auto"
    compute_type: str = "default"
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


class _FasterWhisperNode(pks_aio.OperatorNode):
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
        envelope: pocketstation.SignalEnvelope,
    ) -> tuple[pocketstation.OperatorEmission, ...]:
        if input_port != "audio":
            raise ValueError(f"unexpected input port: {input_port}")
        if self._cancelled:
            raise asyncio.CancelledError
        emissions = []
        for window in self._windows.push(envelope):
            emissions.append(await self._transcribe(window))
        return tuple(emissions)

    async def flush(self) -> tuple[pocketstation.OperatorEmission, ...]:
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
    ) -> pocketstation.OperatorEmission:
        result = await asyncio.wait_for(
            asyncio.to_thread(self._transcribe_sync, window),
            timeout=self._configuration.inference_timeout_s,
        )
        encoded = json.dumps(result, separators=(",", ":"), sort_keys=True)
        if len(encoded.encode()) > self._configuration.maximum_output_bytes:
            raise RuntimeError("transcript envelope exceeds maximum_output_bytes")
        return pocketstation.OperatorEmission.text(encoded, signal=TRANSCRIPT_SIGNAL)

    def _transcribe_sync(self, window: AudioWindow) -> dict[str, object]:
        samples = self._audio_converter(window)
        segments, info = self._model.transcribe(
            samples,
            beam_size=self._configuration.beam_size,
            language=self._configuration.language,
            vad_filter=self._configuration.vad_filter,
        )
        completed = tuple(segments)
        return {
            "channel_count": window.channel_count,
            "discontinuity_epoch": window.discontinuity_epoch,
            "duration_ms": window.duration_ms,
            "language": info.language,
            "language_probability": info.language_probability,
            "sample_rate_hz": window.sample_rate_hz,
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
            "stream_id": window.stream_id,
            "text": " ".join(segment.text.strip() for segment in completed).strip(),
        }


class FasterWhisper:
    """Example-owned faster-whisper provider registered as one async Operator."""

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
        self.manifest = pocketstation.OperatorManifest(
            "community.faster-whisper.stt.v1",
            inputs=(
                pocketstation.PortSpec.input("audio", pocketstation.SignalSpec.audio()),
            ),
            outputs=(pocketstation.PortSpec.output("transcript", TRANSCRIPT_SIGNAL),),
            queue_capacity_signals=self.configuration.queue_capacity_signals,
            process_timeout_ms=round(
                (self.configuration.inference_timeout_s + 1) * 1_000
            ),
            network_allowed=self.configuration.allow_model_download,
            filesystem_allowed=True,
            terminal_roles=("transcript.final",),
        )

    def provider(self) -> pks_aio.OperatorProvider:
        async def create(_configuration: Mapping[str, str]) -> _FasterWhisperNode:
            model = await asyncio.to_thread(self._model_factory, self.configuration)
            return _FasterWhisperNode(
                self.configuration,
                model,
                self._audio_converter,
            )

        return pks_aio.OperatorProvider.with_node(
            self.manifest,
            create,
            deadlines=pks_aio.OperatorDeadlines(
                create_s=self.configuration.create_timeout_s,
                prepare_s=5,
                process_s=self.configuration.inference_timeout_s + 0.5,
                close_s=5,
            ),
        )

    def attach(
        self,
        session: pks_aio.Session,
        stream: pocketstation.Stem
        | pocketstation.SourceOutput
        | pocketstation.DerivedStream,
    ) -> pocketstation.BusSubscription:
        """Attach transcription to any Session-owned PCM stream in two lines."""
        operator = session.register_operator(self.provider()).declare()
        stream.connect(operator.input("audio"))
        return session.subscribe(
            operator.output("transcript"),
            signal=TRANSCRIPT_SIGNAL,
        )


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
        local_files_only=not configuration.allow_model_download,
    )
    return cast(WhisperModel, model)


def _numpy_audio(window: AudioWindow) -> object:
    numpy = importlib.import_module("numpy")
    return numpy.asarray(mono_16khz(window), dtype="float32")


__all__ = ["TRANSCRIPT_SIGNAL", "FasterWhisper", "FasterWhisperConfiguration"]
