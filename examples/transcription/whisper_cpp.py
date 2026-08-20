"""Bounded source-aware speech transcription using a local whisper.cpp process."""

from __future__ import annotations

import asyncio
import json
import sys
import wave
from array import array
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

import pocketstation
import pocketstation.aio as pks_aio

TRANSCRIPT_SIGNAL = pocketstation.SignalSpec.text(
    pocketstation.TextFormat.JSON,
    role="transcript.final",
    schema="io.pocketstation.transcript.batch.v1",
)


@dataclass(frozen=True, slots=True)
class WhisperCppConfiguration:
    """Finite process, buffering, and output limits for whisper.cpp."""

    executable: Path
    model: Path
    language: str = "en"
    window_seconds: float = 5.0
    process_timeout_s: float = 90.0
    shutdown_timeout_s: float = 2.0
    threads: int = 4
    queue_capacity_signals: int = 512
    maximum_sources: int = 8
    maximum_output_bytes: int = 1_048_576
    maximum_error_bytes: int = 65_536
    use_gpu: bool = False

    def __post_init__(self) -> None:
        if not self.executable.is_file():
            raise ValueError(f"whisper executable does not exist: {self.executable}")
        if not self.model.is_file():
            raise ValueError(f"whisper model does not exist: {self.model}")
        if not self.language or not self.language.isascii():
            raise ValueError("language must be non-empty ASCII")
        if not 0.1 <= self.window_seconds <= 30:
            raise ValueError("window_seconds must be between 0.1 and 30")
        if not 1 <= self.process_timeout_s <= 300:
            raise ValueError("process_timeout_s must be between 1 and 300")
        if not 0.1 <= self.shutdown_timeout_s <= 10:
            raise ValueError("shutdown_timeout_s must be between 0.1 and 10")
        if not 1 <= self.threads <= 64:
            raise ValueError("threads must be between 1 and 64")
        if not 8 <= self.queue_capacity_signals <= 4_096:
            raise ValueError("queue_capacity_signals must be between 8 and 4096")
        if not 1 <= self.maximum_sources <= 64:
            raise ValueError("maximum_sources must be between 1 and 64")
        if not 1_024 <= self.maximum_output_bytes <= 16_777_216:
            raise ValueError("maximum_output_bytes must be between 1024 and 16777216")
        if not 1_024 <= self.maximum_error_bytes <= 1_048_576:
            raise ValueError("maximum_error_bytes must be between 1024 and 1048576")


@dataclass(slots=True)
class _AudioWindow:
    sample_rate_hz: int
    channel_count: int
    source_id: int
    stream_id: int
    sequence_start: int
    sequence_end: int
    discontinuity_epoch: int
    samples: array[float] = field(default_factory=lambda: array("f"))


class _WhisperNode(pks_aio.OperatorNode):
    def __init__(self, configuration: WhisperCppConfiguration) -> None:
        self._configuration = configuration
        self._windows: dict[tuple[int, int], _AudioWindow] = {}
        self._children: set[asyncio.subprocess.Process] = set()
        self._cancelled = False

    async def process(
        self,
        input_port: str,
        envelope: pocketstation.SignalEnvelope,
    ) -> tuple[pocketstation.OperatorEmission, ...]:
        if input_port != "audio":
            raise ValueError(f"unexpected input port: {input_port}")
        payload = envelope.payload
        if not isinstance(payload, pocketstation.SignalAudioPayload):
            raise TypeError("WhisperCpp accepts only PCM audio signals")
        lineage = envelope.lineage
        if lineage is None:
            raise ValueError("WhisperCpp requires source-aware audio lineage")
        if self._cancelled:
            raise asyncio.CancelledError

        key = (payload.source_id, payload.stream_id)
        window = self._windows.get(key)
        incompatible = window is not None and (
            window.sample_rate_hz != payload.sample_rate_hz
            or window.channel_count != payload.channel_count
            or window.discontinuity_epoch != lineage.discontinuity_epoch
        )
        emissions: list[pocketstation.OperatorEmission] = []
        if incompatible and window is not None:
            if window.samples:
                emissions.append(await self._transcribe(window))
            del self._windows[key]
            window = None
        if window is None:
            if len(self._windows) >= self._configuration.maximum_sources:
                raise RuntimeError("maximum concurrent transcription sources exceeded")
            window = _AudioWindow(
                sample_rate_hz=payload.sample_rate_hz,
                channel_count=payload.channel_count,
                source_id=payload.source_id,
                stream_id=payload.stream_id,
                sequence_start=payload.sequence_number,
                sequence_end=payload.sequence_number,
                discontinuity_epoch=lineage.discontinuity_epoch,
            )
            self._windows[key] = window

        samples = array("f")
        samples.frombytes(payload.samples_f32le)
        if sys.byteorder != "little":
            samples.byteswap()
        if len(samples) != payload.sample_count:
            raise ValueError("audio payload size does not match sample_count")
        window.samples.extend(samples)
        window.sequence_end = payload.sequence_number

        target_samples = int(
            window.sample_rate_hz
            * window.channel_count
            * self._configuration.window_seconds
        )
        if len(window.samples) >= target_samples:
            batch = _AudioWindow(
                sample_rate_hz=window.sample_rate_hz,
                channel_count=window.channel_count,
                source_id=window.source_id,
                stream_id=window.stream_id,
                sequence_start=window.sequence_start,
                sequence_end=window.sequence_end,
                discontinuity_epoch=window.discontinuity_epoch,
                samples=array("f", window.samples[:target_samples]),
            )
            del window.samples[:target_samples]
            window.sequence_start = payload.sequence_number
            emissions.append(await self._transcribe(batch))
        return tuple(emissions)

    async def flush(self) -> tuple[pocketstation.OperatorEmission, ...]:
        emissions: list[pocketstation.OperatorEmission] = []
        for window in tuple(self._windows.values()):
            if window.samples and not self._cancelled:
                emissions.append(await self._transcribe(window))
        self._windows.clear()
        return tuple(emissions)

    async def cancel(self) -> None:
        self._cancelled = True
        await asyncio.gather(
            *(self._stop_child(child) for child in tuple(self._children)),
            return_exceptions=True,
        )
        self._windows.clear()

    async def close(self) -> None:
        await self.cancel()

    async def _transcribe(self, window: _AudioWindow) -> pocketstation.OperatorEmission:
        if self._cancelled:
            raise asyncio.CancelledError
        with TemporaryDirectory(prefix="pocketstation-whisper-") as directory:
            root = Path(directory)
            wav_path = root / "input.wav"
            output_prefix = root / "transcript"
            stdout_path = root / "stdout.log"
            stderr_path = root / "stderr.log"
            await asyncio.to_thread(_write_whisper_wav, wav_path, window)
            arguments = [
                str(self._configuration.executable),
                "-m",
                str(self._configuration.model),
                "-f",
                str(wav_path),
                "-oj",
                "-of",
                str(output_prefix),
                "-np",
                "-nt",
                "-l",
                self._configuration.language,
                "-t",
                str(self._configuration.threads),
            ]
            if not self._configuration.use_gpu:
                arguments.insert(1, "-ng")
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                child = await asyncio.create_subprocess_exec(
                    *arguments,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=stderr,
                )
                self._children.add(child)
                try:
                    await asyncio.wait_for(
                        child.wait(), timeout=self._configuration.process_timeout_s
                    )
                except (asyncio.CancelledError, TimeoutError):
                    await self._stop_child(child)
                    raise
                finally:
                    self._children.discard(child)

            if child.returncode != 0:
                provider_error = await asyncio.to_thread(
                    _read_bounded,
                    stderr_path,
                    self._configuration.maximum_error_bytes,
                )
                raise RuntimeError(
                    f"whisper-cli exited with status {child.returncode}: "
                    f"{provider_error.decode('utf-8', errors='replace').strip()}"
                )
            result_bytes = await asyncio.to_thread(
                _read_bounded,
                output_prefix.with_suffix(".json"),
                self._configuration.maximum_output_bytes,
            )

        provider_result = json.loads(result_bytes)
        segments = provider_result.get("transcription", ())
        text = " ".join(
            str(segment.get("text", "")).strip()
            for segment in segments
            if isinstance(segment, dict)
        ).strip()
        output = json.dumps(
            {
                "channel_count": window.channel_count,
                "discontinuity_epoch": window.discontinuity_epoch,
                "duration_ms": round(
                    len(window.samples)
                    * 1_000
                    / (window.sample_rate_hz * window.channel_count)
                ),
                "language": provider_result.get("result", {}).get(
                    "language", self._configuration.language
                ),
                "sample_rate_hz": window.sample_rate_hz,
                "sequence_end": window.sequence_end,
                "sequence_start": window.sequence_start,
                "source_id": window.source_id,
                "stream_id": window.stream_id,
                "text": text,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(output.encode()) > self._configuration.maximum_output_bytes:
            raise RuntimeError("transcript envelope exceeds maximum_output_bytes")
        return pocketstation.OperatorEmission.text(output, signal=TRANSCRIPT_SIGNAL)

    async def _stop_child(self, child: asyncio.subprocess.Process) -> None:
        if child.returncode is not None:
            return
        child.terminate()
        try:
            await asyncio.wait_for(
                child.wait(), timeout=self._configuration.shutdown_timeout_s
            )
        except TimeoutError:
            child.kill()
            await child.wait()


class WhisperCpp:
    """Example-owned provider that registers as one bounded async Operator."""

    def __init__(self, configuration: WhisperCppConfiguration) -> None:
        self.configuration = configuration
        timeout_ms = round((configuration.process_timeout_s + 1) * 1_000)
        self.manifest = pocketstation.OperatorManifest(
            "community.whisper.cpp.stt.v1",
            inputs=(
                pocketstation.PortSpec.input("audio", pocketstation.SignalSpec.audio()),
            ),
            outputs=(pocketstation.PortSpec.output("transcript", TRANSCRIPT_SIGNAL),),
            queue_capacity_signals=configuration.queue_capacity_signals,
            process_timeout_ms=timeout_ms,
            filesystem_allowed=True,
            terminal_roles=("transcript.final",),
        )

    def provider(self) -> pks_aio.OperatorProvider:
        async def create(_configuration: Mapping[str, str]) -> _WhisperNode:
            return _WhisperNode(self.configuration)

        return pks_aio.OperatorProvider.with_node(
            self.manifest,
            create,
            deadlines=pks_aio.OperatorDeadlines(
                create_s=5,
                prepare_s=5,
                process_s=self.configuration.process_timeout_s + 0.5,
                close_s=self.configuration.shutdown_timeout_s + 0.5,
            ),
        )


def _write_whisper_wav(path: Path, window: _AudioWindow) -> None:
    mono = _downmix(window.samples, window.channel_count)
    resampled = _resample(mono, window.sample_rate_hz, 16_000)
    pcm = array(
        "h", (round(max(-1.0, min(1.0, value)) * 32_767) for value in resampled)
    )
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16_000)
        output.writeframes(pcm.tobytes())


def _downmix(samples: array[float], channels: int) -> array[float]:
    if channels == 1:
        return array("f", samples)
    return array(
        "f",
        (
            sum(samples[index : index + channels]) / channels
            for index in range(0, len(samples), channels)
        ),
    )


def _resample(
    samples: array[float], source_rate_hz: int, target_rate_hz: int
) -> array[float]:
    if source_rate_hz == target_rate_hz:
        return samples
    output_count = round(len(samples) * target_rate_hz / source_rate_hz)
    if not samples or output_count == 0:
        return array("f")
    if len(samples) == 1:
        return array("f", [samples[0]] * output_count)
    scale = source_rate_hz / target_rate_hz
    output = array("f")
    for output_index in range(output_count):
        position = min(output_index * scale, len(samples) - 1)
        lower = int(position)
        upper = min(lower + 1, len(samples) - 1)
        fraction = position - lower
        output.append(samples[lower] + (samples[upper] - samples[lower]) * fraction)
    return output


def _read_bounded(path: Path, maximum_bytes: int) -> bytes:
    size = path.stat().st_size
    if size > maximum_bytes:
        raise RuntimeError(f"provider output exceeds {maximum_bytes} bytes")
    return path.read_bytes()
