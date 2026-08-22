#!/usr/bin/env python3
"""Prove bounded Session cancellation while real transcription is in flight."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import sys
from array import array
from collections.abc import Iterator
from pathlib import Path
from threading import Event, Lock
from time import monotonic_ns
from typing import Any, cast

import pocketstation._api as pocketstation
import pocketstation.aio as pks_aio

# Resolve PocketStation from the isolated wheel before qualification support.
SDK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK_ROOT))

from pocketstation_examples import (  # noqa: E402
    FasterWhisper,
    FasterWhisperConfiguration,
)
from pocketstation_examples.faster_whisper import (  # noqa: E402
    WhisperInfo,
    WhisperSegment,
)

from tests.transcription.wav_input import read_pcm16_wav  # noqa: E402


class _ObservedRealModel:
    """Expose an exact cancellation boundary around one real model iterator."""

    def __init__(self, model: Any, entered: Event, release: Event) -> None:
        self._model = model
        self._entered = entered
        self._release = release
        self._lock = Lock()
        self._transcript = ""
        self.completed = Event()

    @property
    def transcript(self) -> str:
        with self._lock:
            return self._transcript

    def transcribe(
        self,
        audio: object,
        *,
        beam_size: int,
        language: str | None,
        vad_filter: bool,
    ) -> tuple[Iterator[WhisperSegment], WhisperInfo]:
        segments, info = self._model.transcribe(
            audio,
            beam_size=beam_size,
            language=language,
            vad_filter=vad_filter,
        )

        def observed_segments() -> Iterator[WhisperSegment]:
            self._entered.set()
            if not self._release.wait(timeout=10):
                raise TimeoutError("cancellation test did not release real inference")
            completed = tuple(segments)
            with self._lock:
                self._transcript = " ".join(
                    str(segment.text).strip() for segment in completed
                ).strip()
            self.completed.set()
            yield from completed

        return observed_segments(), cast(WhisperInfo, info)


def _model_factory(
    configuration: FasterWhisperConfiguration,
    entered: Event,
    release: Event,
) -> _ObservedRealModel:
    faster_whisper = importlib.import_module("faster_whisper")
    model: Any = faster_whisper.WhisperModel(
        configuration.model,
        device=configuration.device,
        compute_type=configuration.compute_type,
        cpu_threads=configuration.cpu_threads,
        num_workers=configuration.num_workers,
        local_files_only=not configuration.allow_model_download,
        revision=configuration.model_revision,
    )
    return _ObservedRealModel(model, entered, release)


async def _run(arguments: argparse.Namespace) -> dict[str, object]:
    package_path = Path(pocketstation.__file__).resolve()
    if "site-packages" not in package_path.parts:
        raise RuntimeError(
            f"PocketStation is not loaded from an installed wheel: {package_path}"
        )

    source = read_pcm16_wav(arguments.wav)
    if source.sample_rate_hz != 48_000 or source.channels != 1:
        raise ValueError("cancellation fixture must be 48 kHz mono PCM")

    entered = Event()
    release = Event()
    observed_model: _ObservedRealModel | None = None
    configuration = FasterWhisperConfiguration(
        model=str(arguments.model),
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        num_workers=1,
        allow_model_download=False,
        language="en",
        beam_size=1,
        window_seconds=2,
        queue_capacity_signals=512,
        maximum_sources=1,
        inference_timeout_s=60,
    )

    def create_model(config: FasterWhisperConfiguration) -> _ObservedRealModel:
        nonlocal observed_model
        observed_model = _model_factory(config, entered, release)
        return observed_model

    session = pks_aio.Session(recording_root=arguments.recording)
    audio = session.audio_input(
        "application",
        sample_rate_hz=source.sample_rate_hz,
        channels=source.channels,
        capacity_frames=63,
        frame_samples_per_channel=source.frame_samples_per_channel,
    )
    transcriber = FasterWhisper(configuration, model_factory=create_model)
    transcriber.attach(session, audio.output)
    audio.output.record("application")

    running = await session.start()
    cancel_task: asyncio.Task[pocketstation.StopResult] | None = None
    try:
        frame_values = source.frame_samples_per_channel * source.channels
        required_values = round(configuration.window_seconds * source.sample_rate_hz)
        samples = source.samples[:required_values]
        for offset in range(0, len(samples), frame_values):
            frame = array("f", samples[offset : offset + frame_values])
            if len(frame) < frame_values:
                frame.extend([0.0] * (frame_values - len(frame)))
            await audio.write(frame, timeout_s=2)
            await asyncio.sleep(0.001)

        inference_entered = await asyncio.to_thread(entered.wait, 15)
        if not inference_entered:
            raise TimeoutError("real faster-whisper inference did not begin")

        cancel_started_ns = monotonic_ns()
        cancel_task = asyncio.create_task(running.cancel())
        await asyncio.sleep(0.05)
        cancellation_waited_for_inflight_inference = not cancel_task.done()
        release.set()
        outcome = await asyncio.wait_for(cancel_task, timeout=65)
        cancel_completed_ns = monotonic_ns()
    finally:
        release.set()
        if cancel_task is not None and not cancel_task.done():
            await cancel_task
        if not running.is_stopped:
            await running.cancel()

    if observed_model is None or not observed_model.completed.is_set():
        raise RuntimeError("the exact real model call did not reach a bounded boundary")
    if not observed_model.transcript:
        raise RuntimeError("the real model did not produce transcript text")
    if outcome.disposition is not pocketstation.TerminationDisposition.CANCELLED:
        raise RuntimeError(
            f"unexpected cancellation disposition: {outcome.disposition}"
        )
    if not cancellation_waited_for_inflight_inference:
        raise RuntimeError("cancellation did not overlap the in-flight model call")
    if outcome.recording is None:
        raise RuntimeError("Session cancellation did not finalize recording")
    observations = await audio.observations()
    if not observations.cancelled:
        raise RuntimeError(
            "Core did not mark the application-owned PCM source cancelled"
        )

    return {
        "schema_version": 1,
        "classification": "LOOPBACK-ONLY",
        "installed_package": str(package_path),
        "real_inference": True,
        "real_transcript": observed_model.transcript,
        "inference_in_flight_when_cancel_requested": True,
        "native_inference_preempted": False,
        "cancellation_duration_ns": cancel_completed_ns - cancel_started_ns,
        "termination_disposition": outcome.disposition.value,
        "session_success": outcome.success,
        "operator_finalization_failures_total": (
            outcome.operator_finalization_failures_total
        ),
        "runtime_failures_total": outcome.runtime_failures_total,
        "source_cancelled": observations.cancelled,
        "recording_state": outcome.recording.state.value,
        "recording_complete": outcome.recording.complete,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--wav", type=Path, required=True)
    parser.add_argument("--recording", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = asyncio.run(_run(arguments))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
