"""Measure Python boundary cost and prove bounded slow-consumer behavior.

The copy counters describe the audited native implementation: Core samples are
copied into an owned Rust byte vector, then into Python-owned bytes. The
returned memoryview adds no third PCM copy.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import threading
import tracemalloc
from array import array
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from time import perf_counter_ns, process_time_ns, sleep

import pocketstation
import pocketstation.aio as aio
from pocketstation.errors import AudioInputFullError

try:
    import resource
except ImportError:  # pragma: no cover - Windows has no resource module.
    resource = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class BoundaryResult:
    mode: str
    frames_total: int
    samples_per_frame: int
    audited_native_to_owned_copies_per_frame: int
    audited_owned_to_python_copies_per_frame: int
    audited_total_pcm_copies_per_frame: int
    wall_time_ns: int
    process_cpu_time_ns: int
    frame_latency_p50_ns: int
    frame_latency_p95_ns: int
    frame_latency_p99_ns: int
    frame_latency_max_ns: int
    input_full_retries_total: int
    route_drops_total: int
    python_traced_peak_bytes: int
    resident_set_peak_delta_bytes: int | None
    thread_count_delta: int
    descriptor_count_delta: int | None


@dataclass(frozen=True, slots=True)
class SaturationResult:
    frames_attempted_total: int
    frames_accepted_total: int
    input_full_retries_total: int
    route_capacity_frames: int
    route_peak_frames: int
    route_drops_total: int
    stop_success: bool


def _percentile(values: list[int], percentile: int) -> int:
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = sorted(values)
    index = max(0, (len(ordered) * percentile + 99) // 100 - 1)
    return ordered[index]


def _descriptor_count() -> int | None:
    descriptor_root = Path("/dev/fd")
    if not descriptor_root.is_dir():
        return None
    return len(tuple(descriptor_root.iterdir()))


def _optional_delta(before: int | None, after: int | None) -> int | None:
    if before is None or after is None:
        return None
    return after - before


def _resident_set_peak_bytes() -> int | None:
    if resource is None:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname == "Darwin":
        return peak
    return peak * 1_024


def _write_sync(
    audio: pocketstation.AudioInput,
    samples: array[float],
) -> int:
    retries = 0
    deadline_ns = perf_counter_ns() + 1_000_000_000
    while True:
        try:
            audio.write(samples)
            return retries
        except AudioInputFullError:
            retries += 1
            if perf_counter_ns() >= deadline_ns:
                raise
            sleep(0)


def qualify_sync(frames_total: int, samples_per_frame: int) -> BoundaryResult:
    session = pocketstation.Session()
    audio = session.audio_input(
        "qualification",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.125] * samples_per_frame)
    threads_before = threading.active_count()
    descriptors_before = _descriptor_count()
    resident_set_before_bytes = _resident_set_peak_bytes()
    latencies_ns: list[int] = []
    retries_total = 0
    running = session.start()
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    cpu_started_ns = process_time_ns()
    try:
        for expected_sequence in range(frames_total):
            frame_started_ns = perf_counter_ns()
            retries_total += _write_sync(audio, samples)
            frame = running.audio.read(timeout_s=1.0)
            if frame is None:
                raise RuntimeError("sync qualification timed out waiting for audio")
            if frame.source_id != audio.source_id:
                raise RuntimeError("sync qualification changed source identity")
            if frame.stream_id != audio.stream_id:
                raise RuntimeError("sync qualification changed stream identity")
            if frame.sequence_number != expected_sequence:
                raise RuntimeError("sync qualification changed sequence identity")
            latencies_ns.append(perf_counter_ns() - frame_started_ns)
        metrics = running.metrics()
    finally:
        stop = running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        process_cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    if not stop.success:
        raise RuntimeError("sync qualification Session did not stop successfully")
    route_drops_total = sum(route.frames_dropped_total for route in metrics.routes)
    if route_drops_total != 0:
        raise RuntimeError("sync qualification unexpectedly dropped audio")
    observations = audio.observations()
    if observations.available_buffers != observations.buffer_slots:
        raise RuntimeError("sync qualification did not recover every native buffer")
    return BoundaryResult(
        mode="sync",
        frames_total=frames_total,
        samples_per_frame=samples_per_frame,
        audited_native_to_owned_copies_per_frame=1,
        audited_owned_to_python_copies_per_frame=1,
        audited_total_pcm_copies_per_frame=2,
        wall_time_ns=wall_time_ns,
        process_cpu_time_ns=process_cpu_time_ns,
        frame_latency_p50_ns=_percentile(latencies_ns, 50),
        frame_latency_p95_ns=_percentile(latencies_ns, 95),
        frame_latency_p99_ns=_percentile(latencies_ns, 99),
        frame_latency_max_ns=max(latencies_ns),
        input_full_retries_total=retries_total,
        route_drops_total=route_drops_total,
        python_traced_peak_bytes=traced_peak_bytes,
        resident_set_peak_delta_bytes=_optional_delta(
            resident_set_before_bytes,
            _resident_set_peak_bytes(),
        ),
        thread_count_delta=threading.active_count() - threads_before,
        descriptor_count_delta=_optional_delta(
            descriptors_before,
            _descriptor_count(),
        ),
    )


async def qualify_async(
    frames_total: int,
    samples_per_frame: int,
) -> BoundaryResult:
    session = aio.Session()
    audio = session.audio_input(
        "qualification",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.125] * samples_per_frame)
    latencies_ns: list[int] = []
    running = await session.start()
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    cpu_started_ns = process_time_ns()
    try:
        for expected_sequence in range(frames_total):
            frame_started_ns = perf_counter_ns()
            await audio.write(samples, timeout_s=1.0)
            frame = await running.audio.read(timeout_s=1.0)
            if frame is None:
                raise RuntimeError("async qualification timed out waiting for audio")
            if frame.source_id != audio.source_id:
                raise RuntimeError("async qualification changed source identity")
            if frame.stream_id != audio.stream_id:
                raise RuntimeError("async qualification changed stream identity")
            if frame.sequence_number != expected_sequence:
                raise RuntimeError("async qualification changed sequence identity")
            latencies_ns.append(perf_counter_ns() - frame_started_ns)
        metrics = await running.metrics()
    finally:
        stop = await running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        process_cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    if not stop.success:
        raise RuntimeError("async qualification Session did not stop successfully")
    route_drops_total = sum(route.frames_dropped_total for route in metrics.routes)
    if route_drops_total != 0:
        raise RuntimeError("async qualification unexpectedly dropped audio")
    observations = await audio.observations()
    if observations.available_buffers != observations.buffer_slots:
        raise RuntimeError("async qualification did not recover every native buffer")
    return BoundaryResult(
        mode="asyncio",
        frames_total=frames_total,
        samples_per_frame=samples_per_frame,
        audited_native_to_owned_copies_per_frame=1,
        audited_owned_to_python_copies_per_frame=1,
        audited_total_pcm_copies_per_frame=2,
        wall_time_ns=wall_time_ns,
        process_cpu_time_ns=process_cpu_time_ns,
        frame_latency_p50_ns=_percentile(latencies_ns, 50),
        frame_latency_p95_ns=_percentile(latencies_ns, 95),
        frame_latency_p99_ns=_percentile(latencies_ns, 99),
        frame_latency_max_ns=max(latencies_ns),
        input_full_retries_total=0,
        route_drops_total=route_drops_total,
        python_traced_peak_bytes=traced_peak_bytes,
        resident_set_peak_delta_bytes=None,
        thread_count_delta=0,
        descriptor_count_delta=None,
    )


def qualify_async_owned(
    frames_total: int,
    samples_per_frame: int,
) -> BoundaryResult:
    threads_before = threading.active_count()
    descriptors_before = _descriptor_count()
    resident_set_before_bytes = _resident_set_peak_bytes()
    result = asyncio.run(qualify_async(frames_total, samples_per_frame))
    return replace(
        result,
        resident_set_peak_delta_bytes=_optional_delta(
            resident_set_before_bytes,
            _resident_set_peak_bytes(),
        ),
        thread_count_delta=threading.active_count() - threads_before,
        descriptor_count_delta=_optional_delta(
            descriptors_before,
            _descriptor_count(),
        ),
    )


def qualify_slow_consumer(
    frames_total: int,
    samples_per_frame: int,
) -> SaturationResult:
    session = pocketstation.Session()
    audio = session.audio_input(
        "slow-consumer",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.25] * samples_per_frame)
    running = session.start()
    retries_total = 0
    for _ in range(frames_total):
        retries_total += _write_sync(audio, samples)
    sleep(0.05)
    metrics = running.metrics()
    stop = running.stop()
    if len(metrics.routes) != 1:
        raise RuntimeError("slow-consumer qualification expected one route")
    route = metrics.routes[0]
    if route.edge.queue_peak_frames > route.queue_capacity_frames:
        raise RuntimeError("slow-consumer queue exceeded its declared capacity")
    if route.frames_dropped_total == 0:
        raise RuntimeError("slow-consumer saturation was not observed")
    observations = audio.observations()
    if observations.available_buffers != observations.buffer_slots:
        raise RuntimeError("slow-consumer qualification leaked native buffers")
    return SaturationResult(
        frames_attempted_total=frames_total,
        frames_accepted_total=observations.accepted_total,
        input_full_retries_total=retries_total,
        route_capacity_frames=route.queue_capacity_frames,
        route_peak_frames=route.edge.queue_peak_frames,
        route_drops_total=route.frames_dropped_total,
        stop_success=stop.success,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=500)
    parser.add_argument("--samples-per-frame", type=int, default=480)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if not 10 <= arguments.frames <= 100_000:
        parser.error("--frames must be between 10 and 100000")
    if not 1 <= arguments.samples_per_frame <= 28_800:
        parser.error("--samples-per-frame must be between 1 and 28800")
    report = {
        "schema": "io.pocketstation.python.runtime-qualification.v1",
        "process_id": os.getpid(),
        "sync": asdict(qualify_sync(arguments.frames, arguments.samples_per_frame)),
        "asyncio": asdict(
            qualify_async_owned(arguments.frames, arguments.samples_per_frame)
        ),
        "slow_consumer": asdict(
            qualify_slow_consumer(arguments.frames, arguments.samples_per_frame)
        ),
    }
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if arguments.output is None:
        print(encoded)
    else:
        arguments.output.write_text(f"{encoded}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
