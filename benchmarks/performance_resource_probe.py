"""One isolated installed-wheel performance and resource measurement.

The parent runner copies this file outside the checkout before execution.  The
only PocketStation code imported by this process must therefore come from the
wheel installed in its private environment.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import resource
import subprocess
import sys
import threading
import tracemalloc
from array import array
from pathlib import Path
from statistics import median
from time import perf_counter_ns, process_time_ns, sleep
from typing import Any, cast

import pocketstation
import pocketstation._native as native
import pocketstation.aio as aio
from pocketstation.errors import AudioInputFullError
from pocketstation.signal import EndOfStream

WORKLOAD_TIMEOUT_NS = 30_000_000_000
PRODUCT_LOAD_SCHEDULER_TOLERANCE_NS = 50_000_000


def percentile(values: list[int], percentile_value: int) -> int:
    ordered = sorted(values)
    index = max(0, (len(ordered) * percentile_value + 99) // 100 - 1)
    return ordered[index]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def descriptor_count() -> int | None:
    root = Path("/dev/fd")
    return len(tuple(root.iterdir())) if root.is_dir() else None


def os_thread_count() -> int | None:
    task_root = Path("/proc/self/task")
    if task_root.is_dir():
        return len(tuple(task_root.iterdir()))
    if sys.platform == "darwin":
        completed = subprocess.run(
            ["/bin/ps", "-M", "-p", str(os.getpid())],
            check=True,
            capture_output=True,
            text=True,
        )
        return max(0, len(completed.stdout.splitlines()) - 1)
    return None


def current_rss_bytes() -> int | None:
    statm = Path("/proc/self/statm")
    if statm.is_file():
        resident_pages = int(statm.read_text(encoding="utf-8").split()[1])
        return resident_pages * os.sysconf("SC_PAGE_SIZE")
    if sys.platform == "darwin":
        completed = subprocess.run(
            ["/bin/ps", "-o", "rss=", "-p", str(os.getpid())],
            check=True,
            capture_output=True,
            text=True,
        )
        return int(completed.stdout.strip()) * 1_024
    return None


def peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1_024


def delta(before: int | None, after: int | None) -> int | None:
    return None if before is None or after is None else after - before


def write_sync(audio: pocketstation.AudioInput, samples: array[float]) -> int:
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


def latency_summary(latencies_ns: list[int]) -> dict[str, Any]:
    return {
        "samples_ns": latencies_ns,
        "p50_ns": percentile(latencies_ns, 50),
        "p95_ns": percentile(latencies_ns, 95),
        "p99_ns": percentile(latencies_ns, 99),
        "max_ns": max(latencies_ns),
    }


def measure_sync_round_trip(
    frames_total: int, samples_per_frame: int
) -> dict[str, Any]:
    session = pocketstation.Session()
    audio = session.audio_input(
        "qualification-sync",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.125] * samples_per_frame)
    running = session.start()
    latencies_ns: list[int] = []
    retries_total = 0
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    cpu_started_ns = process_time_ns()
    try:
        for expected_sequence in range(frames_total):
            started_ns = perf_counter_ns()
            retries_total += write_sync(audio, samples)
            frame = running.audio.read(timeout_s=1.0)
            if frame is None or isinstance(frame, EndOfStream):
                raise RuntimeError("sync delivery ended before the expected frame")
            if (
                frame.source_id != audio.source_id
                or frame.stream_id != audio.stream_id
                or frame.sequence_number != expected_sequence
            ):
                raise RuntimeError("sync delivery changed frame identity")
            latencies_ns.append(perf_counter_ns() - started_ns)
        metrics = running.metrics()
    finally:
        stop = running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    observations = audio.observations()
    route_drops_total = sum(route.frames_dropped_total for route in metrics.routes)
    if (
        not stop.success
        or route_drops_total
        or observations.available_buffers != observations.buffer_slots
    ):
        raise RuntimeError("sync delivery failed its loss or resource invariant")
    return {
        "frames_total": frames_total,
        "samples_per_frame": samples_per_frame,
        "wall_time_ns": wall_time_ns,
        "process_cpu_time_ns": cpu_time_ns,
        "cpu_utilization_ratio": cpu_time_ns / wall_time_ns,
        "latency": latency_summary(latencies_ns),
        "input_full_retries_total": retries_total,
        "route_drops_total": route_drops_total,
        "python_traced_peak_bytes": traced_peak_bytes,
        "buffer_slots": observations.buffer_slots,
        "available_buffers_after_stop": observations.available_buffers,
    }


def measure_sync_two_source(
    frames_per_source: int,
    samples_per_frame: int,
    *,
    label: str,
    period_ns: int | None,
) -> dict[str, Any]:
    session = pocketstation.Session()
    endpoint = session.polled_audio()
    audio_inputs = (
        session.audio_input(
            f"qualification-sync-{label}-application",
            sample_rate_hz=48_000,
            capacity_frames=8,
            frame_samples_per_channel=samples_per_frame,
        ),
        session.audio_input(
            f"qualification-sync-{label}-microphone",
            sample_rate_hz=48_000,
            capacity_frames=8,
            frame_samples_per_channel=samples_per_frame,
        ),
    )
    for audio in audio_inputs:
        audio.output.send(endpoint)
    source_names = ("application", "microphone")
    samples = (
        array("f", [0.125] * samples_per_frame),
        array("f", [0.25] * samples_per_frame),
    )
    running = session.start()
    abort_writers = threading.Event()
    writer_done = (threading.Event(), threading.Event())
    writer_results: list[dict[str, Any]] = [
        {
            "sent_total": 0,
            "retries_total": 0,
            "deadline_misses_total": 0,
            "max_lateness_ns": 0,
            "error": None,
        },
        {
            "sent_total": 0,
            "retries_total": 0,
            "deadline_misses_total": 0,
            "max_lateness_ns": 0,
            "error": None,
        },
    ]
    sent_by_source = [0, 0]
    scheduled_start_ns = perf_counter_ns() + (100_000_000 if period_ns else 0)

    def write_all(source_index: int) -> None:
        try:
            retries_total = 0
            sent_total = 0
            deadline_misses_total = 0
            max_lateness_ns = 0
            for sequence_number in range(frames_per_source):
                deadline_ns = 0
                if period_ns is None:
                    while sum(sent_by_source) - sum(received_by_source.values()) >= 4:
                        if abort_writers.is_set():
                            return
                        sleep(0)
                if period_ns is not None:
                    deadline_ns = scheduled_start_ns + (
                        (sequence_number + 1) * period_ns
                    )
                    remaining_ns = deadline_ns - perf_counter_ns()
                    if remaining_ns > 0:
                        sleep(remaining_ns / 1_000_000_000)
                retries_total += write_sync(
                    audio_inputs[source_index], samples[source_index]
                )
                sent_by_source[source_index] = sent_total + 1
                if period_ns is not None:
                    lateness_ns = max(0, perf_counter_ns() - deadline_ns)
                    max_lateness_ns = max(max_lateness_ns, lateness_ns)
                    if lateness_ns > PRODUCT_LOAD_SCHEDULER_TOLERANCE_NS:
                        deadline_misses_total += 1
                sent_total += 1
            writer_results[source_index]["sent_total"] = sent_total
            writer_results[source_index]["retries_total"] = retries_total
            writer_results[source_index]["deadline_misses_total"] = (
                deadline_misses_total
            )
            writer_results[source_index]["max_lateness_ns"] = max_lateness_ns
        except BaseException as error:
            writer_results[source_index]["error"] = error
        finally:
            writer_done[source_index].set()

    writers = (
        threading.Thread(
            target=write_all,
            args=(0,),
            name=f"pks-sync-{label}-application",
        ),
        threading.Thread(
            target=write_all,
            args=(1,),
            name=f"pks-sync-{label}-microphone",
        ),
    )
    received_by_source = {audio.source_id: 0 for audio in audio_inputs}
    stream_by_source = {audio.source_id: audio.stream_id for audio in audio_inputs}
    aggregate_expected = len(audio_inputs) * frames_per_source
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    workload_deadline_ns = wall_started_ns + WORKLOAD_TIMEOUT_NS
    cpu_started_ns = process_time_ns()
    for writer in writers:
        writer.start()
    try:
        while sum(received_by_source.values()) < aggregate_expected:
            if perf_counter_ns() >= workload_deadline_ns:
                raise RuntimeError(f"sync {label} exceeded its workload deadline")
            batch = running.audio.read_batch(timeout_s=0.1)
            if batch is None:
                if all(done.is_set() for done in writer_done):
                    raise RuntimeError(f"sync {label} delivery ended early")
                continue
            for frame in batch:
                if frame.source_id not in received_by_source:
                    raise RuntimeError(f"sync {label} emitted an unknown source")
                expected_sequence = received_by_source[frame.source_id]
                if (
                    frame.stream_id != stream_by_source[frame.source_id]
                    or frame.sequence_number != expected_sequence
                ):
                    raise RuntimeError(
                        f"sync {label} changed frame identity: "
                        f"source={frame.source_id} "
                        f"stream={frame.stream_id}/"
                        f"{stream_by_source[frame.source_id]} "
                        f"sequence={frame.sequence_number}/{expected_sequence}"
                    )
                received_by_source[frame.source_id] += 1
        for writer in writers:
            writer.join(timeout=1.0)
            if writer.is_alive():
                raise RuntimeError(f"sync {label} producer did not finish")
        for result in writer_results:
            if result["error"] is not None:
                raise result["error"]
        metrics = running.metrics()
    finally:
        abort_writers.set()
        stop = running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        for writer in writers:
            writer.join(timeout=1.0)
    observations = [audio.observations() for audio in audio_inputs]
    route_drops = [
        {
            "route_id": int(route.route_id),
            "frames_dropped_total": route.frames_dropped_total,
        }
        for route in metrics.routes
    ]
    route_drops_total = sum(item["frames_dropped_total"] for item in route_drops)
    sources = [
        {
            "name": source_names[index],
            "source_id": int(audio.source_id),
            "stream_id": int(audio.stream_id),
            "frames_sent_total": writer_results[index]["sent_total"],
            "frames_received_total": received_by_source[audio.source_id],
            "last_sequence_number": received_by_source[audio.source_id] - 1,
            "input_full_retries_total": writer_results[index]["retries_total"],
            "deadline_misses_total": writer_results[index]["deadline_misses_total"],
            "max_lateness_ns": writer_results[index]["max_lateness_ns"],
            "buffer_slots": observations[index].buffer_slots,
            "available_buffers_after_stop": observations[index].available_buffers,
        }
        for index, audio in enumerate(audio_inputs)
    ]
    all_buffers_returned = all(
        source["available_buffers_after_stop"] == source["buffer_slots"]
        for source in sources
    )
    if (
        not stop.success
        or route_drops_total
        or not all_buffers_returned
        or any(source["frames_sent_total"] != frames_per_source for source in sources)
        or any(
            source["frames_received_total"] != frames_per_source for source in sources
        )
    ):
        raise RuntimeError(f"sync {label} failed its delivery or resource invariant")
    return {
        "source_count": len(audio_inputs),
        "frames_per_source": frames_per_source,
        "aggregate_frames_sent_total": sum(
            source["frames_sent_total"] for source in sources
        ),
        "aggregate_frames_received_total": sum(received_by_source.values()),
        "sample_rate_hz": 48_000,
        "samples_per_frame": samples_per_frame,
        "wall_time_ns": wall_time_ns,
        "process_cpu_time_ns": cpu_time_ns,
        "cpu_utilization_ratio": cpu_time_ns / wall_time_ns,
        "aggregate_frames_per_second": (
            aggregate_expected * 1_000_000_000 / wall_time_ns
        ),
        "configured_period_ns": period_ns,
        "scheduler_tolerance_ns": (
            PRODUCT_LOAD_SCHEDULER_TOLERANCE_NS if period_ns is not None else None
        ),
        "deadline_misses_total": sum(
            source["deadline_misses_total"] for source in sources
        ),
        "max_lateness_ns": max(
            cast(int, source["max_lateness_ns"]) for source in sources
        ),
        "workload_timeout_ns": WORKLOAD_TIMEOUT_NS,
        "sources": sources,
        "routes": route_drops,
        "route_drops_total": route_drops_total,
        "python_traced_peak_bytes": traced_peak_bytes,
        "stop_success": stop.success,
        "all_buffers_returned": all_buffers_returned,
    }


def measure_sync(
    round_trip_frames: int,
    capacity_frames_per_source: int,
    product_load_frames_per_source: int,
    samples_per_frame: int,
) -> dict[str, Any]:
    return {
        "round_trip": measure_sync_round_trip(round_trip_frames, samples_per_frame),
        "capacity": measure_sync_two_source(
            capacity_frames_per_source,
            samples_per_frame,
            label="capacity",
            period_ns=None,
        ),
        "product_load": measure_sync_two_source(
            product_load_frames_per_source,
            samples_per_frame,
            label="product-load",
            period_ns=10_000_000,
        ),
    }


async def measure_async_round_trip(
    frames_total: int, samples_per_frame: int
) -> dict[str, Any]:
    session = aio.Session()
    audio = session.audio_input(
        "qualification-async",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.125] * samples_per_frame)
    running = await session.start()
    latencies_ns: list[int] = []
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    cpu_started_ns = process_time_ns()
    try:
        for expected_sequence in range(frames_total):
            started_ns = perf_counter_ns()
            await audio.write(samples, timeout_s=1.0)
            frame = await running.audio.read(timeout_s=1.0)
            if frame is None or isinstance(frame, EndOfStream):
                raise RuntimeError("async delivery ended before the expected frame")
            if (
                frame.source_id != audio.source_id
                or frame.stream_id != audio.stream_id
                or frame.sequence_number != expected_sequence
            ):
                raise RuntimeError("async delivery changed frame identity")
            latencies_ns.append(perf_counter_ns() - started_ns)
        metrics = await running.metrics()
    finally:
        stop = await running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    observations = await audio.observations()
    route_drops_total = sum(route.frames_dropped_total for route in metrics.routes)
    if (
        not stop.success
        or route_drops_total
        or observations.available_buffers != observations.buffer_slots
    ):
        raise RuntimeError("async delivery failed its loss or resource invariant")
    return {
        "frames_total": frames_total,
        "samples_per_frame": samples_per_frame,
        "wall_time_ns": wall_time_ns,
        "process_cpu_time_ns": cpu_time_ns,
        "cpu_utilization_ratio": cpu_time_ns / wall_time_ns,
        "latency": latency_summary(latencies_ns),
        "route_drops_total": route_drops_total,
        "python_traced_peak_bytes": traced_peak_bytes,
        "buffer_slots": observations.buffer_slots,
        "available_buffers_after_stop": observations.available_buffers,
    }


async def measure_async_two_source(
    frames_per_source: int,
    samples_per_frame: int,
    *,
    label: str,
    period_ns: int | None,
) -> dict[str, Any]:
    session = aio.Session()
    endpoint = session.polled_audio()
    audio_inputs = (
        session.audio_input(
            f"qualification-asyncio-{label}-application",
            sample_rate_hz=48_000,
            capacity_frames=8,
            frame_samples_per_channel=samples_per_frame,
        ),
        session.audio_input(
            f"qualification-asyncio-{label}-microphone",
            sample_rate_hz=48_000,
            capacity_frames=8,
            frame_samples_per_channel=samples_per_frame,
        ),
    )
    for audio in audio_inputs:
        audio.output.send(endpoint)
    source_names = ("application", "microphone")
    samples = (
        array("f", [0.125] * samples_per_frame),
        array("f", [0.25] * samples_per_frame),
    )
    running = await session.start()
    scheduled_start_ns = perf_counter_ns() + (100_000_000 if period_ns else 0)
    writer_results: list[dict[str, int]] = [
        {"sent_total": 0, "deadline_misses_total": 0, "max_lateness_ns": 0},
        {"sent_total": 0, "deadline_misses_total": 0, "max_lateness_ns": 0},
    ]
    sent_by_source = [0, 0]

    async def write_all(source_index: int) -> None:
        sent_total = 0
        deadline_misses_total = 0
        max_lateness_ns = 0
        for sequence_number in range(frames_per_source):
            deadline_ns = 0
            if period_ns is None:
                while sum(sent_by_source) - sum(received_by_source.values()) >= 4:
                    await asyncio.sleep(0)
            if period_ns is not None:
                deadline_ns = scheduled_start_ns + ((sequence_number + 1) * period_ns)
                remaining_ns = deadline_ns - perf_counter_ns()
                if remaining_ns > 0:
                    await asyncio.sleep(remaining_ns / 1_000_000_000)
            await audio_inputs[source_index].write(samples[source_index], timeout_s=1.0)
            sent_by_source[source_index] = sent_total + 1
            if period_ns is not None:
                lateness_ns = max(0, perf_counter_ns() - deadline_ns)
                max_lateness_ns = max(max_lateness_ns, lateness_ns)
                if lateness_ns > PRODUCT_LOAD_SCHEDULER_TOLERANCE_NS:
                    deadline_misses_total += 1
            sent_total += 1
        writer_results[source_index]["sent_total"] = sent_total
        writer_results[source_index]["deadline_misses_total"] = deadline_misses_total
        writer_results[source_index]["max_lateness_ns"] = max_lateness_ns

    writers = (
        asyncio.create_task(write_all(0)),
        asyncio.create_task(write_all(1)),
    )
    received_by_source = {audio.source_id: 0 for audio in audio_inputs}
    stream_by_source = {audio.source_id: audio.stream_id for audio in audio_inputs}
    aggregate_expected = len(audio_inputs) * frames_per_source
    tracemalloc.start()
    wall_started_ns = perf_counter_ns()
    workload_deadline_ns = wall_started_ns + WORKLOAD_TIMEOUT_NS
    cpu_started_ns = process_time_ns()
    try:
        while sum(received_by_source.values()) < aggregate_expected:
            if perf_counter_ns() >= workload_deadline_ns:
                raise RuntimeError(f"asyncio {label} exceeded its workload deadline")
            batch = await running.audio.read_batch(timeout_s=0.1)
            if batch is None:
                if all(writer.done() for writer in writers):
                    await asyncio.gather(*writers)
                    raise RuntimeError(f"asyncio {label} delivery ended early")
                continue
            for frame in batch:
                if frame.source_id not in received_by_source:
                    raise RuntimeError(f"asyncio {label} emitted an unknown source")
                expected_sequence = received_by_source[frame.source_id]
                if (
                    frame.stream_id != stream_by_source[frame.source_id]
                    or frame.sequence_number != expected_sequence
                ):
                    raise RuntimeError(
                        f"asyncio {label} changed frame identity: "
                        f"source={frame.source_id} "
                        f"stream={frame.stream_id}/"
                        f"{stream_by_source[frame.source_id]} "
                        f"sequence={frame.sequence_number}/{expected_sequence}"
                    )
                received_by_source[frame.source_id] += 1
        await asyncio.gather(*writers)
        metrics = await running.metrics()
    finally:
        for writer in writers:
            if not writer.done():
                writer.cancel()
        await asyncio.gather(*writers, return_exceptions=True)
        stop = await running.stop()
        wall_time_ns = perf_counter_ns() - wall_started_ns
        cpu_time_ns = process_time_ns() - cpu_started_ns
        _, traced_peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    observations = [await audio.observations() for audio in audio_inputs]
    route_drops = [
        {
            "route_id": int(route.route_id),
            "frames_dropped_total": route.frames_dropped_total,
        }
        for route in metrics.routes
    ]
    route_drops_total = sum(item["frames_dropped_total"] for item in route_drops)
    sources = [
        {
            "name": source_names[index],
            "source_id": int(audio.source_id),
            "stream_id": int(audio.stream_id),
            "frames_sent_total": writer_results[index]["sent_total"],
            "frames_received_total": received_by_source[audio.source_id],
            "last_sequence_number": received_by_source[audio.source_id] - 1,
            "deadline_misses_total": writer_results[index]["deadline_misses_total"],
            "max_lateness_ns": writer_results[index]["max_lateness_ns"],
            "buffer_slots": observations[index].buffer_slots,
            "available_buffers_after_stop": observations[index].available_buffers,
        }
        for index, audio in enumerate(audio_inputs)
    ]
    all_buffers_returned = all(
        source["available_buffers_after_stop"] == source["buffer_slots"]
        for source in sources
    )
    if (
        not stop.success
        or route_drops_total
        or not all_buffers_returned
        or any(source["frames_sent_total"] != frames_per_source for source in sources)
        or any(
            source["frames_received_total"] != frames_per_source for source in sources
        )
    ):
        raise RuntimeError(f"asyncio {label} failed its delivery or resource invariant")
    return {
        "source_count": len(audio_inputs),
        "frames_per_source": frames_per_source,
        "aggregate_frames_sent_total": sum(
            source["frames_sent_total"] for source in sources
        ),
        "aggregate_frames_received_total": sum(received_by_source.values()),
        "sample_rate_hz": 48_000,
        "samples_per_frame": samples_per_frame,
        "wall_time_ns": wall_time_ns,
        "process_cpu_time_ns": cpu_time_ns,
        "cpu_utilization_ratio": cpu_time_ns / wall_time_ns,
        "aggregate_frames_per_second": (
            aggregate_expected * 1_000_000_000 / wall_time_ns
        ),
        "configured_period_ns": period_ns,
        "scheduler_tolerance_ns": (
            PRODUCT_LOAD_SCHEDULER_TOLERANCE_NS if period_ns is not None else None
        ),
        "deadline_misses_total": sum(
            source["deadline_misses_total"] for source in sources
        ),
        "max_lateness_ns": max(
            cast(int, source["max_lateness_ns"]) for source in sources
        ),
        "workload_timeout_ns": WORKLOAD_TIMEOUT_NS,
        "sources": sources,
        "routes": route_drops,
        "route_drops_total": route_drops_total,
        "python_traced_peak_bytes": traced_peak_bytes,
        "stop_success": stop.success,
        "all_buffers_returned": all_buffers_returned,
    }


async def measure_async(
    round_trip_frames: int,
    capacity_frames_per_source: int,
    product_load_frames_per_source: int,
    samples_per_frame: int,
) -> dict[str, Any]:
    return {
        "round_trip": await measure_async_round_trip(
            round_trip_frames, samples_per_frame
        ),
        "capacity": await measure_async_two_source(
            capacity_frames_per_source,
            samples_per_frame,
            label="capacity",
            period_ns=None,
        ),
        "product_load": await measure_async_two_source(
            product_load_frames_per_source,
            samples_per_frame,
            label="product-load",
            period_ns=10_000_000,
        ),
    }


def sync_lifecycle(cycles_total: int, samples_per_frame: int) -> None:
    samples = array("f", [0.25] * samples_per_frame)
    for cycle in range(cycles_total):
        session = pocketstation.Session()
        audio = session.audio_input(
            f"sync-cycle-{cycle}", frame_samples_per_channel=samples_per_frame
        )
        audio.output.send(session.polled_audio())
        running = session.start()
        audio.write(samples)
        frame = running.audio.read(timeout_s=1.0)
        if frame is None or isinstance(frame, EndOfStream):
            raise RuntimeError("sync lifecycle did not deliver its frame")
        if not running.stop().success:
            raise RuntimeError("sync lifecycle did not stop successfully")
        observations = audio.observations()
        if observations.available_buffers != observations.buffer_slots:
            raise RuntimeError("sync lifecycle leaked a native buffer")


async def async_lifecycle_and_cancellation(
    cycles_total: int,
    samples_per_frame: int,
) -> dict[str, int | bool]:
    current = asyncio.current_task()
    tasks_before = len(asyncio.all_tasks() - ({current} if current else set()))
    samples = array("f", [0.25] * samples_per_frame)
    for cycle in range(cycles_total):
        session = aio.Session()
        audio = session.audio_input(
            f"async-cycle-{cycle}", frame_samples_per_channel=samples_per_frame
        )
        audio.output.send(session.polled_audio())
        running = await session.start()
        await audio.write(samples, timeout_s=1.0)
        frame = await running.audio.read(timeout_s=1.0)
        if frame is None or isinstance(frame, EndOfStream):
            raise RuntimeError("async lifecycle did not deliver its frame")
        if not (await running.stop()).success:
            raise RuntimeError("async lifecycle did not stop successfully")
        observations = await audio.observations()
        if observations.available_buffers != observations.buffer_slots:
            raise RuntimeError("async lifecycle leaked a native buffer")

    session = aio.Session()
    audio = session.audio_input(
        "cancellation", frame_samples_per_channel=samples_per_frame
    )
    audio.output.send(session.polled_audio())
    running = await session.start()
    default_timeout_ns = 100_000_000
    pending = asyncio.create_task(running.audio.read())
    await asyncio.sleep(0)
    started_ns = perf_counter_ns()
    pending.cancel()
    cancelled = False
    try:
        await pending
    except asyncio.CancelledError:
        cancelled = True
    cancellation_latency_ns = perf_counter_ns() - started_ns
    stop = await running.stop()
    await asyncio.sleep(0)
    tasks_after = len(asyncio.all_tasks() - ({current} if current else set()))
    return {
        "cancelled": cancelled,
        "used_default_timeout": True,
        "requested_timeout_ns": default_timeout_ns,
        "latency_ns": cancellation_latency_ns,
        "stop_success": stop.success,
        "async_tasks_before": tasks_before,
        "async_tasks_after": tasks_after,
        "async_task_delta": tasks_after - tasks_before,
    }


def measure_saturation(frames_total: int, samples_per_frame: int) -> dict[str, Any]:
    session = pocketstation.Session()
    audio = session.audio_input(
        "saturation",
        capacity_frames=8,
        frame_samples_per_channel=samples_per_frame,
    )
    audio.output.send(session.polled_audio())
    samples = array("f", [0.5] * samples_per_frame)
    running = session.start()
    retries_total = 0
    for _ in range(frames_total):
        retries_total += write_sync(audio, samples)
    sleep(0.05)
    metrics = running.metrics()
    stop = running.stop()
    [route] = metrics.routes
    observations = audio.observations()
    if observations.available_buffers != observations.buffer_slots:
        raise RuntimeError("saturation workload leaked a native buffer")
    return {
        "frames_attempted_total": frames_total,
        "frames_accepted_total": observations.accepted_total,
        "input_full_retries_total": retries_total,
        "route_capacity_frames": route.queue_capacity_frames,
        "route_peak_frames": route.delivery.queue_peak_frames,
        "route_drops_total": route.frames_dropped_total,
        "stop_success": stop.success,
        "all_buffers_returned": observations.available_buffers
        == observations.buffer_slots,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round-trip-frames", type=int, required=True)
    parser.add_argument("--capacity-frames-per-source", type=int, required=True)
    parser.add_argument("--product-load-frames-per-source", type=int, required=True)
    parser.add_argument("--samples-per-frame", type=int, required=True)
    parser.add_argument("--lifecycle-cycles", type=int, required=True)
    arguments = parser.parse_args()

    package_path = Path(pocketstation.__file__).resolve()
    current_rss_before = current_rss_bytes()
    peak_rss_before = peak_rss_bytes()
    python_threads_before = threading.active_count()
    os_threads_before = os_thread_count()
    file_descriptors_before = descriptor_count()
    resources_before = {
        "current_rss_bytes": current_rss_before,
        "peak_rss_bytes": peak_rss_before,
        "python_threads": python_threads_before,
        "os_threads": os_threads_before,
        "file_descriptors": file_descriptors_before,
    }
    sync_result = measure_sync(
        arguments.round_trip_frames,
        arguments.capacity_frames_per_source,
        arguments.product_load_frames_per_source,
        arguments.samples_per_frame,
    )
    async_result = asyncio.run(
        measure_async(
            arguments.round_trip_frames,
            arguments.capacity_frames_per_source,
            arguments.product_load_frames_per_source,
            arguments.samples_per_frame,
        )
    )
    sync_lifecycle(arguments.lifecycle_cycles, arguments.samples_per_frame)
    async_lifecycle = asyncio.run(
        async_lifecycle_and_cancellation(
            arguments.lifecycle_cycles, arguments.samples_per_frame
        )
    )
    saturation = measure_saturation(
        max(200, arguments.round_trip_frames), arguments.samples_per_frame
    )
    sleep(0.1)
    current_rss_after = current_rss_bytes()
    peak_rss_after = peak_rss_bytes()
    python_threads_after = threading.active_count()
    os_threads_after = os_thread_count()
    file_descriptors_after = descriptor_count()
    resources_after = {
        "current_rss_bytes": current_rss_after,
        "peak_rss_bytes": peak_rss_after,
        "python_threads": python_threads_after,
        "os_threads": os_threads_after,
        "file_descriptors": file_descriptors_after,
    }
    resources = {
        "before": resources_before,
        "after": resources_after,
        "current_rss_delta_bytes": delta(
            current_rss_before,
            current_rss_after,
        ),
        "peak_rss_growth_bytes": peak_rss_after - peak_rss_before,
        "python_thread_delta": python_threads_after - python_threads_before,
        "os_thread_delta": delta(os_threads_before, os_threads_after),
        "file_descriptor_delta": delta(file_descriptors_before, file_descriptors_after),
        "lifecycle_cycles_sync": arguments.lifecycle_cycles,
        "lifecycle_cycles_async": arguments.lifecycle_cycles,
        "async_task_delta": async_lifecycle["async_task_delta"],
    }
    report = {
        "schema": "io.pocketstation.python.performance-resource-process.v2",
        "process_id": os.getpid(),
        "python_executable": sys.executable,
        "environment_root": str(Path(sys.prefix).resolve()),
        "distribution_name": "pocketstation",
        "distribution_version": importlib.metadata.version("pocketstation"),
        "python_version": sys.version,
        "package_path": str(package_path),
        "package_sha256": sha256(package_path),
        "native_module_path": str(Path(native.__file__).resolve()),
        "native_module_sha256": sha256(Path(native.__file__).resolve()),
        "sync": sync_result,
        "asyncio": async_result,
        "cancellation": async_lifecycle,
        "resources": resources,
        "saturation": saturation,
        "median_boundary_latency_ns": int(
            median(
                [
                    sync_result["round_trip"]["latency"]["p50_ns"],
                    async_result["round_trip"]["latency"]["p50_ns"],
                ]
            )
        ),
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
