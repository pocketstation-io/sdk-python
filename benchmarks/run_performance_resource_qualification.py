"""Qualify one exact installed PocketStation wheel with repeated processes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse
from urllib.request import url2pathname

CANDIDATE_ID = "pks-20260926-w21-python-performance-resource-qualification-105"
SOURCE_CANDIDATE_ID = "pks-20260926-w21-python-real-path-e2e-103"
EXPECTED_WHEEL_SHA256 = (
    "fae9d40dec5664cffeb8f3989fa31430c7557f7db6b83730bfbab64390019b44"
)
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = (
    "1ee3a8317a8abd57ca0128e7ae9253dbe740b62c0507199f0cc2e1a43378b32e"
)
EXPECTED_SDK_COMMIT = "13908d3a689f65b33540d2ba443e29d0fa01e17f"
WHEEL_INSTALL_NAME = "pocketstation-0.1.4-cp311-abi3-macosx_11_0_arm64.whl"
RUNTIME_DEPENDENCIES = (
    "anyio==4.15.1",
    "certifi==2026.7.22",
    "h11==0.16.0",
    "httpcore==1.0.9",
    "httpx==0.28.1",
    "idna==3.20",
    "typing-extensions==4.16.0",
)
BUDGETS = {
    "sync_latency_p99_ns_max": 10_000_000,
    "asyncio_latency_p99_ns_max": 15_000_000,
    "sync_throughput_frames_per_second_min": 500.0,
    "asyncio_throughput_frames_per_second_min": 500.0,
    "product_load_aggregate_frames_per_second_min": 180.0,
    "cancellation_latency_ns_max": 250_000_000,
    "current_rss_delta_bytes_max": 8 * 1_024 * 1_024,
    "python_thread_delta_max": 0,
    "os_thread_delta_max": 0,
    "file_descriptor_delta_max": 0,
    "async_task_delta_max": 0,
}
SOURCE_COUNT = 2
SAMPLE_RATE_HZ = 48_000
FRAME_DURATION_MS = 10
FRAMES_PER_SECOND_PER_SOURCE = 100
PRODUCT_LOAD_SECONDS = 4
DEFAULT_ROUND_TRIP_FRAMES = 300
DEFAULT_CAPACITY_FRAMES_PER_SOURCE = 1_000
DEFAULT_REPETITIONS = 7
DEFAULT_WARMUPS = 2
DEFAULT_LIFECYCLE_CYCLES = 20
DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE = (
    PRODUCT_LOAD_SECONDS * FRAMES_PER_SECOND_PER_SOURCE
)
SUBPROCESS_TIMEOUT_SECONDS = 180
C104_REPORT_SHA256 = "6de4feef056549ab4e39d2a1ec747b9bee8c8ec3c1ea7d2d37ac6fddf678eb8d"
C104_FAILURE_SHA256 = "3eac9f06ff4819674bf1a205c65c200eeb508f2e0695b8c4b5f8dcc372c8e290"
C104_REFERENCE_REVIEW_SHA256 = (
    "5e84502aaed3f023fda35b8d88cd190e6bc4393b964bef8f08c9a80589ce7831"
)
C104_SHA256SUMS_SHA256 = (
    "ad3eeb5db6434c263a0baad9f8dfd21f99519ffcf849ace0f6cd7487cd9ae3d0"
)
WHEEL_PACKAGE_PATH = "pocketstation/__init__.py"
WHEEL_NATIVE_PATH = "pocketstation/_native.abi3.so"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def distribution(values: list[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    p95_index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    mean = statistics.fmean(values)
    standard_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    absolute_deviations = [abs(value - statistics.median(values)) for value in values]
    return {
        "samples_total": len(values),
        "min": ordered[0],
        "median": statistics.median(values),
        "p95": ordered[p95_index],
        "max": ordered[-1],
        "mean": mean,
        "standard_deviation": standard_deviation,
        "median_absolute_deviation": statistics.median(absolute_deviations),
        "coefficient_of_variation": standard_deviation / mean if mean else 0.0,
    }


def run_checked(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout_s: int = SUBPROCESS_TIMEOUT_SECONDS,
) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as error:
        rendered = " ".join(command)
        raise RuntimeError(
            f"command exceeded {timeout_s} seconds: {rendered}"
        ) from error
    if completed.returncode != 0:
        rendered = " ".join(command)
        raise RuntimeError(
            f"command failed ({completed.returncode}): {rendered}\n{completed.stderr}"
        )
    return completed.stdout


def python_in(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def validate_output_path(requested: Path, workspace_root: Path) -> Path:
    output = requested.resolve()
    expected = (
        workspace_root
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-105/report.json"
    ).resolve()
    if output != expected:
        raise RuntimeError(f"output must be the exact Candidate 105 path: {expected}")
    if output.exists():
        raise RuntimeError(
            "Candidate 105 report already exists; refusing to overwrite it"
        )
    if output.parent.exists() and any(output.parent.iterdir()):
        raise RuntimeError(
            "Candidate 105 evidence directory is not empty; refusing to overwrite it"
        )
    return output


def validate_source_acceptance(wheel: Path) -> dict[str, Any]:
    acceptance_path = wheel.parent.parent / "acceptance.json"
    if sha256(acceptance_path) != EXPECTED_SOURCE_ACCEPTANCE_SHA256:
        raise RuntimeError(
            "Candidate 103 acceptance bytes do not match the pinned manifest"
        )
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    if acceptance.get("candidate_id") != SOURCE_CANDIDATE_ID:
        raise RuntimeError("wheel is not owned by accepted Candidate 103")
    source_commits = {
        entry["repo_id"]: entry["commit_sha"]
        for entry in acceptance.get("source_commits", [])
    }
    if source_commits.get("sdk-python") != EXPECTED_SDK_COMMIT:
        raise RuntimeError("Candidate 103 SDK commit does not match the pinned commit")
    artifacts = {
        Path(entry["path"]).name: entry["sha256"]
        for entry in acceptance.get("artifacts", [])
    }
    if artifacts.get("candidate-wheel.whl") != EXPECTED_WHEEL_SHA256:
        raise RuntimeError("Candidate 103 acceptance does not bind the expected wheel")
    return cast(dict[str, Any], acceptance)


def validate_candidate_104_retention(workspace_root: Path) -> None:
    candidate = (
        workspace_root
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-104"
    )
    expected = {
        "report.json": C104_REPORT_SHA256,
        "failure.json": C104_FAILURE_SHA256,
        "reference-review.json": C104_REFERENCE_REVIEW_SHA256,
        "SHA256SUMS": C104_SHA256SUMS_SHA256,
    }
    for name, expected_sha256 in expected.items():
        path = candidate / name
        if not path.is_file() or sha256(path) != expected_sha256:
            raise RuntimeError(f"Candidate 104 retained {name} changed")
    sums = (candidate / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    recorded = {
        name: digest for line in sums for digest, name in [line.split(maxsplit=1)]
    }
    if recorded != {
        "report.json": C104_REPORT_SHA256,
        "failure.json": C104_FAILURE_SHA256,
    }:
        raise RuntimeError("Candidate 104 SHA256SUMS changed")


def wheel_payload_hashes(wheel: Path) -> dict[str, str]:
    expected_paths = (WHEEL_PACKAGE_PATH, WHEEL_NATIVE_PATH)
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        missing = sorted(set(expected_paths) - names)
        if missing:
            raise RuntimeError(
                f"Candidate wheel is missing required payload files: {missing}"
            )
        return {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in expected_paths
        }


def validate_dependency_freeze(installed: list[str], install_wheel: Path) -> list[str]:
    expected_dependencies = set(RUNTIME_DEPENDENCIES)
    dependency_lines = {
        line for line in installed if not line.startswith("pocketstation")
    }
    pocketstation_lines = [
        line for line in installed if line.startswith("pocketstation")
    ]
    if dependency_lines != expected_dependencies:
        missing = sorted(expected_dependencies - dependency_lines)
        extra = sorted(dependency_lines - expected_dependencies)
        raise RuntimeError(
            f"installed dependency freeze changed: missing={missing}, extra={extra}"
        )
    if len(pocketstation_lines) != 1 or " @ " not in pocketstation_lines[0]:
        raise RuntimeError(
            "installed PocketStation distribution is not bound to the exact wheel: "
            f"actual={pocketstation_lines!r}"
        )
    _, wheel_uri = pocketstation_lines[0].split(" @ ", maxsplit=1)
    parsed = urlparse(wheel_uri)
    if (
        parsed.scheme != "file"
        or parsed.netloc not in ("", "localhost")
        or bool(parsed.query or parsed.fragment)
        or Path(url2pathname(parsed.path)).resolve() != install_wheel.resolve()
    ):
        raise RuntimeError(
            "installed PocketStation distribution is not bound to the exact wheel: "
            f"actual={pocketstation_lines!r}"
        )
    if len(installed) != len(RUNTIME_DEPENDENCIES) + 1:
        raise RuntimeError("installed dependency freeze contains duplicate entries")
    return sorted(installed)


def validate_measurement_environment(
    measurement: dict[str, Any],
    *,
    python: Path,
    venv: Path,
    payload_hashes: dict[str, str],
) -> None:
    expected_python = python.resolve()
    expected_venv = venv.resolve()
    if Path(measurement["python_executable"]).resolve() != expected_python:
        raise RuntimeError(
            "measurement interpreter is not the private venv interpreter"
        )
    if Path(measurement["environment_root"]).resolve() != expected_venv:
        raise RuntimeError("measurement environment root is not the private venv")
    package_path = Path(measurement["package_path"]).resolve()
    native_path = Path(measurement["native_module_path"]).resolve()
    if (
        expected_venv not in package_path.parents
        or expected_venv not in native_path.parents
    ):
        raise RuntimeError(
            "measurement imported PocketStation outside its private venv"
        )
    if (
        package_path.name != "__init__.py"
        or package_path.parent.name != "pocketstation"
    ):
        raise RuntimeError("measurement package path is not PocketStation __init__.py")
    if native_path.name != Path(WHEEL_NATIVE_PATH).name:
        raise RuntimeError("measurement native module path changed")
    if measurement.get("distribution_name") != "pocketstation":
        raise RuntimeError("measurement distribution name changed")
    if measurement.get("distribution_version") != "0.1.4":
        raise RuntimeError("measurement distribution version changed")
    if measurement.get("package_sha256") != payload_hashes[WHEEL_PACKAGE_PATH]:
        raise RuntimeError("installed package bytes do not match the exact wheel")
    if measurement.get("native_module_sha256") != payload_hashes[WHEEL_NATIVE_PATH]:
        raise RuntimeError("installed native module bytes do not match the exact wheel")


def validate_raw_latency_samples(
    measurement: dict[str, Any], *, round_trip_frames: int
) -> None:
    for mode_name in ("sync", "asyncio"):
        latency = measurement[mode_name]["round_trip"]["latency"]
        samples = latency.get("samples_ns")
        if not isinstance(samples, list) or len(samples) != round_trip_frames:
            raise RuntimeError(
                f"{mode_name} raw latency samples were not retained exactly"
            )
        if not all(isinstance(value, int) and value >= 0 for value in samples):
            raise RuntimeError(f"{mode_name} raw latency samples are invalid")
        expected = latency_summary_from_samples(samples)
        for name, value in expected.items():
            if latency.get(name) != value:
                raise RuntimeError(
                    f"{mode_name} latency summary does not match raw samples"
                )


def latency_summary_from_samples(samples: list[int]) -> dict[str, int]:
    ordered = sorted(samples)

    def percentile(percentile_value: int) -> int:
        index = max(0, (len(ordered) * percentile_value + 99) // 100 - 1)
        return ordered[index]

    return {
        "p50_ns": percentile(50),
        "p95_ns": percentile(95),
        "p99_ns": percentile(99),
        "max_ns": max(samples),
    }


def aggregate(repetitions: list[dict[str, Any]]) -> dict[str, Any]:
    fields = {
        "sync_latency_p99_ns": [
            item["sync"]["round_trip"]["latency"]["p99_ns"] for item in repetitions
        ],
        "asyncio_latency_p99_ns": [
            item["asyncio"]["round_trip"]["latency"]["p99_ns"] for item in repetitions
        ],
        "sync_throughput_frames_per_second": [
            item["sync"]["capacity"]["aggregate_frames_per_second"]
            for item in repetitions
        ],
        "asyncio_throughput_frames_per_second": [
            item["asyncio"]["capacity"]["aggregate_frames_per_second"]
            for item in repetitions
        ],
        "sync_round_trip_cpu_utilization_ratio": [
            item["sync"]["round_trip"]["cpu_utilization_ratio"] for item in repetitions
        ],
        "sync_capacity_cpu_utilization_ratio": [
            item["sync"]["capacity"]["cpu_utilization_ratio"] for item in repetitions
        ],
        "sync_product_load_cpu_utilization_ratio": [
            item["sync"]["product_load"]["cpu_utilization_ratio"]
            for item in repetitions
        ],
        "asyncio_round_trip_cpu_utilization_ratio": [
            item["asyncio"]["round_trip"]["cpu_utilization_ratio"]
            for item in repetitions
        ],
        "asyncio_capacity_cpu_utilization_ratio": [
            item["asyncio"]["capacity"]["cpu_utilization_ratio"] for item in repetitions
        ],
        "asyncio_product_load_cpu_utilization_ratio": [
            item["asyncio"]["product_load"]["cpu_utilization_ratio"]
            for item in repetitions
        ],
        "sync_product_load_aggregate_frames_per_second": [
            item["sync"]["product_load"]["aggregate_frames_per_second"]
            for item in repetitions
        ],
        "asyncio_product_load_aggregate_frames_per_second": [
            item["asyncio"]["product_load"]["aggregate_frames_per_second"]
            for item in repetitions
        ],
        "current_rss_delta_bytes": [
            item["resources"]["current_rss_delta_bytes"] for item in repetitions
        ],
        "peak_rss_growth_bytes": [
            item["resources"]["peak_rss_growth_bytes"] for item in repetitions
        ],
        "python_thread_delta": [
            item["resources"]["python_thread_delta"] for item in repetitions
        ],
        "os_thread_delta": [
            item["resources"]["os_thread_delta"] for item in repetitions
        ],
        "file_descriptor_delta": [
            item["resources"]["file_descriptor_delta"] for item in repetitions
        ],
        "async_task_delta": [
            item["resources"]["async_task_delta"] for item in repetitions
        ],
        "cancellation_latency_ns": [
            item["cancellation"]["latency_ns"] for item in repetitions
        ],
        "saturation_route_drops_total": [
            item["saturation"]["route_drops_total"] for item in repetitions
        ],
    }
    return {name: distribution(values) for name, values in fields.items()}


def two_source_delivery_is_exact(
    workload: dict[str, Any],
    *,
    frames_per_source: int,
    period_ns: int | None,
) -> bool:
    sources = workload["sources"]
    routes = workload["routes"]
    aggregate_expected = SOURCE_COUNT * frames_per_source
    return (
        workload["source_count"] == SOURCE_COUNT
        and workload["frames_per_source"] == frames_per_source
        and workload["sample_rate_hz"] == SAMPLE_RATE_HZ
        and workload["samples_per_frame"] == 480
        and workload["aggregate_frames_sent_total"] == aggregate_expected
        and workload["aggregate_frames_received_total"] == aggregate_expected
        and workload["configured_period_ns"] == period_ns
        and workload["workload_timeout_ns"] == 30_000_000_000
        and workload["scheduler_tolerance_ns"]
        == (50_000_000 if period_ns is not None else None)
        and workload["deadline_misses_total"] == 0
        and workload["route_drops_total"] == 0
        and workload["stop_success"]
        and workload["all_buffers_returned"]
        and len(sources) == SOURCE_COUNT
        and {source["name"] for source in sources} == {"application", "microphone"}
        and len({source["source_id"] for source in sources}) == SOURCE_COUNT
        and len({source["stream_id"] for source in sources}) == SOURCE_COUNT
        and all(
            source["frames_sent_total"] == frames_per_source
            and source["frames_received_total"] == frames_per_source
            and source["last_sequence_number"] == frames_per_source - 1
            and source["deadline_misses_total"] == 0
            and source["available_buffers_after_stop"] == source["buffer_slots"]
            for source in sources
        )
        and len(routes) == SOURCE_COUNT
        and len({route["route_id"] for route in routes}) == SOURCE_COUNT
        and all(route["frames_dropped_total"] == 0 for route in routes)
    )


def evaluate(repetitions: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        "sync_latency_within_budget": all(
            item["sync"]["round_trip"]["latency"]["p99_ns"]
            <= BUDGETS["sync_latency_p99_ns_max"]
            for item in repetitions
        ),
        "asyncio_latency_within_budget": all(
            item["asyncio"]["round_trip"]["latency"]["p99_ns"]
            <= BUDGETS["asyncio_latency_p99_ns_max"]
            for item in repetitions
        ),
        "sync_throughput_within_budget": all(
            item["sync"]["capacity"]["aggregate_frames_per_second"]
            >= BUDGETS["sync_throughput_frames_per_second_min"]
            for item in repetitions
        ),
        "asyncio_throughput_within_budget": all(
            item["asyncio"]["capacity"]["aggregate_frames_per_second"]
            >= BUDGETS["asyncio_throughput_frames_per_second_min"]
            for item in repetitions
        ),
        "cancellation_within_budget": all(
            item["cancellation"]["cancelled"]
            and item["cancellation"]["stop_success"]
            and item["cancellation"]["used_default_timeout"]
            and item["cancellation"]["requested_timeout_ns"] == 100_000_000
            and item["cancellation"]["latency_ns"]
            <= BUDGETS["cancellation_latency_ns_max"]
            for item in repetitions
        ),
        "resources_returned_within_budget": all(
            item["resources"]["current_rss_delta_bytes"]
            <= BUDGETS["current_rss_delta_bytes_max"]
            and item["resources"]["python_thread_delta"]
            <= BUDGETS["python_thread_delta_max"]
            and item["resources"]["os_thread_delta"] <= BUDGETS["os_thread_delta_max"]
            and item["resources"]["file_descriptor_delta"]
            <= BUDGETS["file_descriptor_delta_max"]
            and item["resources"]["async_task_delta"] <= BUDGETS["async_task_delta_max"]
            for item in repetitions
        ),
        "saturation_is_bounded_and_observed": all(
            item["saturation"]["route_peak_frames"]
            <= item["saturation"]["route_capacity_frames"]
            and item["saturation"]["route_drops_total"] > 0
            and item["saturation"]["stop_success"]
            and item["saturation"]["all_buffers_returned"]
            for item in repetitions
        ),
        "capacity_delivery_is_exact": all(
            two_source_delivery_is_exact(
                mode["capacity"],
                frames_per_source=DEFAULT_CAPACITY_FRAMES_PER_SOURCE,
                period_ns=None,
            )
            for item in repetitions
            for mode in (item["sync"], item["asyncio"])
        ),
        "product_load_is_lossless_and_bounded": all(
            two_source_delivery_is_exact(
                mode["product_load"],
                frames_per_source=DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE,
                period_ns=10_000_000,
            )
            and mode["product_load"]["wall_time_ns"]
            >= PRODUCT_LOAD_SECONDS * 1_000_000_000
            and mode["product_load"]["aggregate_frames_per_second"]
            >= BUDGETS["product_load_aggregate_frames_per_second_min"]
            for item in repetitions
            for mode in (item["sync"], item["asyncio"])
        ),
        "round_trip_delivery_is_lossless": all(
            mode["round_trip"]["frames_total"] == DEFAULT_ROUND_TRIP_FRAMES
            and mode["round_trip"]["samples_per_frame"] == 480
            and len(mode["round_trip"]["latency"]["samples_ns"])
            == DEFAULT_ROUND_TRIP_FRAMES
            and mode["round_trip"]["route_drops_total"] == 0
            and mode["round_trip"]["available_buffers_after_stop"]
            == mode["round_trip"]["buffer_slots"]
            for item in repetitions
            for mode in (item["sync"], item["asyncio"])
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUPS)
    parser.add_argument(
        "--round-trip-frames", type=int, default=DEFAULT_ROUND_TRIP_FRAMES
    )
    parser.add_argument(
        "--capacity-frames-per-source",
        type=int,
        default=DEFAULT_CAPACITY_FRAMES_PER_SOURCE,
    )
    parser.add_argument(
        "--product-load-frames-per-source",
        type=int,
        default=DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE,
    )
    parser.add_argument("--samples-per-frame", type=int, default=480)
    parser.add_argument(
        "--lifecycle-cycles", type=int, default=DEFAULT_LIFECYCLE_CYCLES
    )
    arguments = parser.parse_args()
    if arguments.repetitions != DEFAULT_REPETITIONS:
        parser.error("--repetitions must be exactly 7 for Candidate 105")
    if arguments.warmups != DEFAULT_WARMUPS:
        parser.error("--warmups must be exactly 2 for Candidate 105")
    if arguments.round_trip_frames != DEFAULT_ROUND_TRIP_FRAMES:
        parser.error("--round-trip-frames must be exactly 300")
    if arguments.capacity_frames_per_source != DEFAULT_CAPACITY_FRAMES_PER_SOURCE:
        parser.error("--capacity-frames-per-source must be exactly 1000")
    if (
        arguments.product_load_frames_per_source
        != DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE
    ):
        parser.error("--product-load-frames-per-source must be exactly 400")
    if arguments.samples_per_frame != 480:
        parser.error("--samples-per-frame must be exactly 480")
    if arguments.lifecycle_cycles != DEFAULT_LIFECYCLE_CYCLES:
        parser.error("--lifecycle-cycles must be exactly 20")

    wheel = arguments.wheel.resolve(strict=True)
    workspace_root = Path(__file__).resolve().parents[3]
    report_output = validate_output_path(arguments.output, workspace_root)
    validate_candidate_104_retention(workspace_root)
    if sha256(wheel) != EXPECTED_WHEEL_SHA256:
        raise RuntimeError("wheel SHA-256 does not match Candidate 103")
    acceptance = validate_source_acceptance(wheel)
    payload_hashes = wheel_payload_hashes(wheel)
    probe_source = Path(__file__).with_name("performance_resource_probe.py")
    runner_path = Path(__file__).resolve()
    initial_probe_sha256 = sha256(probe_source)
    initial_runner_sha256 = sha256(runner_path)
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required for the offline isolated installation")

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["UV_OFFLINE"] = "1"
    repetitions: list[dict[str, Any]] = []
    warmup_durations_ns: list[int] = []
    observed_process_ids: set[int] = set()
    with tempfile.TemporaryDirectory(prefix="pks-python-performance-c105-") as raw:
        temporary = Path(raw)
        venv = temporary / "venv"
        run_checked(
            [uv, "venv", "--python", sys.executable, str(venv)],
            cwd=temporary,
            environment=environment,
        )
        venv = venv.resolve()
        python = python_in(venv)
        install_wheel = temporary / WHEEL_INSTALL_NAME
        shutil.copy2(wheel, install_wheel)
        install_command = [
            uv,
            "pip",
            "install",
            "--offline",
            "--python",
            str(python),
            *RUNTIME_DEPENDENCIES,
            str(install_wheel),
        ]
        run_checked(install_command, cwd=temporary, environment=environment)
        installed = validate_dependency_freeze(
            run_checked(
                [uv, "pip", "freeze", "--python", str(python)],
                cwd=temporary,
                environment=environment,
            ).splitlines(),
            install_wheel,
        )
        probe = temporary / "performance_resource_probe.py"
        shutil.copy2(probe_source, probe)
        if sha256(probe) != initial_probe_sha256:
            raise RuntimeError("isolated probe copy does not match the invoked probe")
        command = [
            str(python),
            "-I",
            str(probe),
            "--round-trip-frames",
            str(arguments.round_trip_frames),
            "--capacity-frames-per-source",
            str(arguments.capacity_frames_per_source),
            "--product-load-frames-per-source",
            str(arguments.product_load_frames_per_source),
            "--samples-per-frame",
            str(arguments.samples_per_frame),
            "--lifecycle-cycles",
            str(arguments.lifecycle_cycles),
        ]
        for index in range(arguments.warmups + arguments.repetitions):
            started_ns = datetime.now(UTC)
            command_output = run_checked(
                command, cwd=temporary, environment=environment
            )
            finished_ns = datetime.now(UTC)
            measurement = json.loads(command_output)
            process_id = measurement.get("process_id")
            if not isinstance(process_id, int) or process_id in observed_process_ids:
                raise RuntimeError("measurement process IDs must be unique integers")
            observed_process_ids.add(process_id)
            validate_measurement_environment(
                measurement,
                python=python,
                venv=venv,
                payload_hashes=payload_hashes,
            )
            validate_raw_latency_samples(
                measurement, round_trip_frames=arguments.round_trip_frames
            )
            elapsed_ns = int((finished_ns - started_ns).total_seconds() * 1_000_000_000)
            if index < arguments.warmups:
                warmup_durations_ns.append(elapsed_ns)
            else:
                measurement["repetition_index"] = index - arguments.warmups
                repetitions.append(measurement)

    if sha256(probe_source) != initial_probe_sha256:
        raise RuntimeError("probe changed while Candidate 105 was running")
    if sha256(runner_path) != initial_runner_sha256:
        raise RuntimeError("runner changed while Candidate 105 was running")
    checks = evaluate(repetitions)
    harness_dir = report_output.parent / "harness"
    harness_dir.mkdir(parents=True, exist_ok=False)
    retained_probe = harness_dir / probe_source.name
    retained_runner = harness_dir / runner_path.name
    shutil.copy2(probe_source, retained_probe)
    shutil.copy2(runner_path, retained_runner)
    if sha256(retained_probe) != initial_probe_sha256:
        raise RuntimeError("retained probe does not match the invoked probe")
    if sha256(retained_runner) != initial_runner_sha256:
        raise RuntimeError("retained runner does not match the invoked runner")
    report = {
        "schema": "io.pocketstation.python.performance-resource-qualification.v2",
        "task_id": "W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION",
        "candidate_id": CANDIDATE_ID,
        "source_candidate_id": SOURCE_CANDIDATE_ID,
        "sdk_commit": EXPECTED_SDK_COMMIT,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "classification": "SAFE-TO-TEST",
        "scope": "installed-wheel-local-component",
        "units": {
            "latency": "nanoseconds",
            "wall_time": "nanoseconds",
            "cpu_time": "nanoseconds",
            "throughput": "frames_per_second",
            "memory": "bytes",
            "queue_depth": "frames",
            "counts": "count",
        },
        "environment": {
            "os": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
            "runner_python": sys.version,
            "uv_version": run_checked(
                [uv, "--version"], cwd=Path.cwd(), environment=environment
            ).strip(),
        },
        "artifact": {
            "wheel_path": str(wheel),
            "wheel_sha256": sha256(wheel),
            "candidate_103_acceptance_sha256": sha256(
                wheel.parent.parent / "acceptance.json"
            ),
            "probe_path": str(retained_probe),
            "probe_sha256": sha256(retained_probe),
            "runner_path": str(retained_runner),
            "runner_sha256": sha256(retained_runner),
            "installed_distributions": installed,
            "wheel_payload_sha256": payload_hashes,
            "installation": {
                "network_allowed": False,
                "uv_offline": True,
                "python_isolated_flag": True,
                "python_user_site_disabled": True,
                "runtime_dependencies": list(RUNTIME_DEPENDENCIES),
                "dependency_freeze_verified": True,
                "exact_wheel_payload_verified": True,
            },
        },
        "method": {
            "warmups_total": arguments.warmups,
            "repetitions_total": arguments.repetitions,
            "fresh_process_per_repetition": True,
            "round_trip_frames": arguments.round_trip_frames,
            "capacity_frames_per_source": arguments.capacity_frames_per_source,
            "product_load_frames_per_source": (
                arguments.product_load_frames_per_source
            ),
            "source_count": SOURCE_COUNT,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "samples_per_frame": arguments.samples_per_frame,
            "lifecycle_cycles_per_mode_per_repetition": arguments.lifecycle_cycles,
            "round_trip_measurement": (
                "one accepted write followed by its matching frame read; wall and CPU "
                "cover only this serialized latency workload"
            ),
            "raw_latency_samples_retained": True,
            "capacity_measurement": (
                "two independent bounded producers and one concurrent batch consumer; "
                "the aggregate numerator is exactly two times frames per source"
            ),
            "product_load_measurement": (
                "two independent sources paced at 100 frames per second each for four "
                "seconds; exact identity, sequences, counts and zero drops are required"
            ),
            "throughput_requirement": {
                "sources_total": 2,
                "frame_duration_ms": 10,
                "frames_per_second_per_source": 100,
                "aggregate_product_frames_per_second": 200,
                "headroom_multiplier": 2.5,
                "qualified_minimum_frames_per_second": 500.0,
            },
            "product_load_requirement": {
                "duration_seconds": PRODUCT_LOAD_SECONDS,
                "configured_period_ns": 10_000_000,
                "frames_per_source": DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE,
                "aggregate_frames_total": (
                    SOURCE_COUNT * DEFAULT_PRODUCT_LOAD_FRAMES_PER_SOURCE
                ),
                "minimum_aggregate_frames_per_second": BUDGETS[
                    "product_load_aggregate_frames_per_second_min"
                ],
                "scheduler_tolerance_ns": 50_000_000,
                "workload_timeout_ns": 30_000_000_000,
            },
            "cancellation_read_timeout_ns": 100_000_000,
            "cancellation_total_budget_ns": 250_000_000,
            "subprocess_timeout_seconds": SUBPROCESS_TIMEOUT_SECONDS,
            "warmup_process_durations_ns": warmup_durations_ns,
            "measurement_engine": "pocketstation-installed-wheel-repeated-process-v1",
            "pyperf_used": False,
            "pyperf_decision": (
                "The workload measures Session lifecycle, cancellation, queues and "
                "process resources together; pyperf is not pinned in this candidate "
                "and its calibrated microbenchmark loop would not establish those "
                "invariants."
            ),
        },
        "budgets": BUDGETS,
        "repetitions": repetitions,
        "dispersion": aggregate(repetitions),
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "non_claims": [
            "No physical-device, browser, WAN, TURN or cross-platform claim follows.",
            "No competitor comparison or superiority claim follows.",
            "Peak RSS is a high-water mark; current RSS is measured separately.",
            "Candidate 103 remains the authority for the real app/mic product path.",
        ],
        "source_acceptance_classification": acceptance["classification"],
    }
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        f"{json.dumps(report, indent=2, sort_keys=True)}\n", encoding="utf-8"
    )
    if report["result"] != "PASS":
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"qualification failed: {', '.join(failed)}")
    print(f"performance/resource qualification: PASS ({len(repetitions)} repetitions)")


if __name__ == "__main__":
    main()
