"""Transcribe two independent PCM sources through one installed PocketStation SDK."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from time import monotonic
from typing import cast

import pocketstation._api as pocketstation
import pocketstation.aio as pks_aio
from pocketstation_demo import (
    FasterWhisper,
    FasterWhisperConfiguration,
)

from tests.transcription.wav_input import WavInput, feed_live, read_pcm16_wav


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--application-wav", type=Path, required=True)
    parser.add_argument("--microphone-wav", type=Path, required=True)
    parser.add_argument("--record-to", type=Path, required=True)
    parser.add_argument("--model", default="tiny.en")
    parser.add_argument("--model-revision")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--cpu-threads", type=int, default=4)
    parser.add_argument("--window-seconds", type=float, default=2.0)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--allow-model-download", action="store_true")
    return parser.parse_args()


async def main() -> None:
    arguments = _arguments()
    result = await transcribe_sources(
        application=read_pcm16_wav(arguments.application_wav),
        microphone=read_pcm16_wav(arguments.microphone_wav),
        record_to=arguments.record_to,
        model=arguments.model,
        model_revision=arguments.model_revision,
        device=arguments.device,
        compute_type=arguments.compute_type,
        cpu_threads=arguments.cpu_threads,
        window_seconds=arguments.window_seconds,
        timeout_s=arguments.timeout_seconds,
        allow_model_download=arguments.allow_model_download,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


async def transcribe_sources(
    *,
    application: WavInput,
    microphone: WavInput,
    record_to: Path,
    model: str,
    model_revision: str | None,
    device: str,
    compute_type: str,
    cpu_threads: int,
    window_seconds: float,
    timeout_s: float,
    allow_model_download: bool,
) -> dict[str, object]:
    """Run real inference while preserving two independent Session sources."""
    if not 1 <= timeout_s <= 300:
        raise ValueError("timeout_s must be between 1 and 300")
    application_contract = (
        application.sample_rate_hz,
        application.channels,
        application.frame_samples_per_channel,
    )
    microphone_contract = (
        microphone.sample_rate_hz,
        microphone.channels,
        microphone.frame_samples_per_channel,
    )
    if application_contract != microphone_contract:
        raise ValueError(
            "application and microphone WAV inputs must use the same "
            "sample rate, channel count, and frame size"
        )
    session = pks_aio.Session(
        recording_root=record_to,
        sample_rate_hz=application.sample_rate_hz,
        channels=application.channels,
    )
    application_audio = session.audio_input(
        "application",
        sample_rate_hz=application.sample_rate_hz,
        channels=application.channels,
        capacity_frames=32,
        frame_samples_per_channel=application.frame_samples_per_channel,
    )
    microphone_audio = session.audio_input(
        "microphone",
        sample_rate_hz=microphone.sample_rate_hz,
        channels=microphone.channels,
        capacity_frames=32,
        frame_samples_per_channel=microphone.frame_samples_per_channel,
    )
    transcriber = FasterWhisper(
        FasterWhisperConfiguration(
            model=model,
            model_revision=model_revision,
            device=device,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            allow_model_download=allow_model_download,
            language="en" if model.endswith(".en") else None,
            beam_size=1,
            window_seconds=window_seconds,
            queue_capacity_signals=1_024,
            maximum_sources=2,
            create_timeout_s=timeout_s,
            inference_timeout_s=timeout_s,
        )
    )
    transcripts = transcriber.attach_many(
        session,
        (application_audio.output, microphone_audio.output),
    )
    application_audio.output.record("application")
    microphone_audio.output.record("microphone")

    running = await session.start()
    transcript_stream = running.signals(transcripts)
    expected_sources = {
        int(application_audio.source_id): "application",
        int(microphone_audio.source_id): "microphone",
    }
    received: dict[str, dict[str, object]] = {}
    collector = asyncio.create_task(
        _collect_transcripts(
            transcript_stream,
            expected_sources=expected_sources,
            received=received,
            timeout_s=timeout_s,
        )
    )
    try:
        async with asyncio.TaskGroup() as feeds:
            feeds.create_task(
                feed_live(
                    application_audio,
                    application,
                    pacing_ratio=1,
                    close_when_complete=False,
                )
            )
            feeds.create_task(
                feed_live(
                    microphone_audio,
                    microphone,
                    pacing_ratio=1,
                    close_when_complete=False,
                )
            )
        await application_audio.close()
        await microphone_audio.close()
    finally:
        outcome = await running.stop()
    await collector
    if (
        not outcome.success
        or outcome.recording is None
        or not outcome.recording.complete
    ):
        raise RuntimeError(f"Session did not finalize cleanly: {outcome!r}")

    return {
        "application_source_id": int(application_audio.source_id),
        "microphone_source_id": int(microphone_audio.source_id),
        "recording_complete": True,
        "recording_stems": [stem.stem_name for stem in outcome.recording.stems],
        "transcripts": received,
    }


async def _collect_transcripts(
    stream: pks_aio.SignalStream[str],
    *,
    expected_sources: dict[int, str],
    received: dict[str, dict[str, object]],
    timeout_s: float,
) -> None:
    """Drain the bounded branch through Session finalization."""
    deadline = monotonic() + timeout_s
    while True:
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise TimeoutError("transcription did not finalize within its deadline")
        envelope = await stream.read(timeout_s=min(1.0, remaining))
        if envelope is None:
            continue
        if isinstance(envelope, pocketstation.EndOfStream):
            if set(received) != set(expected_sources.values()):
                raise RuntimeError("transcript stream ended before both sources")
            return
        value = json.loads(str(envelope.payload))
        if not isinstance(value, dict):
            raise RuntimeError("transcript payload must be a JSON object")
        source_id = value.get("source_id")
        if not isinstance(source_id, int) or source_id not in expected_sources:
            raise RuntimeError("transcript lost its input source identity")
        if value.get("text"):
            _accumulate_transcript(received, expected_sources[source_id], value)


def _accumulate_transcript(
    received: dict[str, dict[str, object]],
    source_name: str,
    window: dict[str, object],
) -> None:
    summary = received.get(source_name)
    if summary is None:
        summary = dict(window)
        summary["windows"] = [dict(window)]
        summary["windows_total"] = 1
        received[source_name] = summary
        return

    for identity in ("session_id", "source_id", "stream_id"):
        if summary.get(identity) != window.get(identity):
            raise RuntimeError(f"transcript changed {identity} within one source")
    summary["text"] = " ".join(
        part
        for part in (str(summary.get("text", "")), str(window.get("text", "")))
        if part
    )
    summary["segments"] = [
        *cast(list[object], summary.get("segments", [])),
        *cast(list[object], window.get("segments", [])),
    ]
    for terminal_field in (
        "sequence_end",
        "timestamp_end_ns",
        "source_timestamp_end_ns",
        "session_timestamp_end_ns",
    ):
        summary[terminal_field] = window.get(terminal_field)
    summary["inference_duration_ns"] = cast(
        int, summary.get("inference_duration_ns", 0)
    ) + cast(int, window.get("inference_duration_ns", 0))
    summary["discontinuity_reasons"] = sorted(
        {
            *cast(list[str], summary.get("discontinuity_reasons", [])),
            *cast(list[str], window.get("discontinuity_reasons", [])),
        }
    )
    windows = summary.get("windows")
    if not isinstance(windows, list):
        raise RuntimeError("transcript summary lost its bounded window history")
    windows.append(dict(window))
    summary["windows_total"] = len(windows)


if __name__ == "__main__":
    asyncio.run(main())
