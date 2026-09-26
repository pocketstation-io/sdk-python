from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import pytest

SDK_ROOT = Path(__file__).parents[1]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_module(
    "performance_resource_runner",
    SDK_ROOT / "benchmarks/run_performance_resource_qualification.py",
)


def valid_repetition(index: int) -> dict[str, Any]:
    latency_samples = [10_000] * 150 + [20_000] * 135 + [30_000] * 12 + [40_000] * 3
    round_trip = {
        "frames_total": 300,
        "samples_per_frame": 480,
        "wall_time_ns": 10_000_000,
        "process_cpu_time_ns": 5_000_000,
        "cpu_utilization_ratio": 0.5,
        "latency": {
            "samples_ns": latency_samples,
            "p50_ns": 10_000,
            "p95_ns": 20_000,
            "p99_ns": 30_000,
            "max_ns": 40_000,
        },
        "route_drops_total": 0,
        "python_traced_peak_bytes": 1_024,
        "buffer_slots": 8,
        "available_buffers_after_stop": 8,
    }

    def two_source(
        frames_per_source: int,
        wall_time_ns: int,
        *,
        period_ns: int | None,
    ) -> dict[str, Any]:
        aggregate_total = 2 * frames_per_source
        sources = [
            {
                "name": "application",
                "source_id": 1,
                "stream_id": 1,
                "frames_sent_total": frames_per_source,
                "frames_received_total": frames_per_source,
                "last_sequence_number": frames_per_source - 1,
                "input_full_retries_total": 0,
                "deadline_misses_total": 0,
                "max_lateness_ns": 1_000,
                "buffer_slots": 8,
                "available_buffers_after_stop": 8,
            },
            {
                "name": "microphone",
                "source_id": 2,
                "stream_id": 2,
                "frames_sent_total": frames_per_source,
                "frames_received_total": frames_per_source,
                "last_sequence_number": frames_per_source - 1,
                "input_full_retries_total": 0,
                "deadline_misses_total": 0,
                "max_lateness_ns": 1_000,
                "buffer_slots": 8,
                "available_buffers_after_stop": 8,
            },
        ]
        return {
            "source_count": 2,
            "frames_per_source": frames_per_source,
            "aggregate_frames_sent_total": aggregate_total,
            "aggregate_frames_received_total": aggregate_total,
            "sample_rate_hz": 48_000,
            "samples_per_frame": 480,
            "wall_time_ns": wall_time_ns,
            "process_cpu_time_ns": wall_time_ns // 2,
            "cpu_utilization_ratio": 0.5,
            "aggregate_frames_per_second": (
                aggregate_total * 1_000_000_000 / wall_time_ns
            ),
            "configured_period_ns": period_ns,
            "scheduler_tolerance_ns": 50_000_000 if period_ns else None,
            "deadline_misses_total": 0,
            "max_lateness_ns": 1_000 if period_ns else 0,
            "workload_timeout_ns": 30_000_000_000,
            "sources": sources,
            "routes": [
                {"route_id": 1, "frames_dropped_total": 0},
                {"route_id": 2, "frames_dropped_total": 0},
            ],
            "route_drops_total": 0,
            "python_traced_peak_bytes": 1_024,
            "stop_success": True,
            "all_buffers_returned": True,
        }

    capacity = two_source(1_000, 1_000_000_000, period_ns=None)
    product_load = two_source(400, 4_100_000_000, period_ns=10_000_000)
    return {
        "schema": "io.pocketstation.python.performance-resource-process.v2",
        "process_id": 10_000 + index,
        "python_executable": "/private/tmp/c105/venv/bin/python",
        "environment_root": "/private/tmp/c105/venv",
        "python_version": "3.13",
        "distribution_name": "pocketstation",
        "distribution_version": "0.1.4",
        "repetition_index": index,
        "package_path": (
            "/private/tmp/c105/venv/lib/python3.13/"
            "site-packages/pocketstation/__init__.py"
        ),
        "native_module_path": (
            "/private/tmp/c105/venv/lib/python3.13/"
            "site-packages/pocketstation/_native.abi3.so"
        ),
        "package_sha256": (
            "1b51e73722ed6e67187f24e4fb0e496023765119f0f033547f8447557cbb21b2"
        ),
        "native_module_sha256": (
            "3e71b71202d7d3fffe10d8c821c6b9b0bcf49735eb5d8b5fe970770e2058be21"
        ),
        "sync": {
            "round_trip": {**round_trip, "input_full_retries_total": 0},
            "capacity": copy.deepcopy(capacity),
            "product_load": copy.deepcopy(product_load),
        },
        "asyncio": {
            "round_trip": copy.deepcopy(round_trip),
            "capacity": copy.deepcopy(capacity),
            "product_load": copy.deepcopy(product_load),
        },
        "cancellation": {
            "cancelled": True,
            "used_default_timeout": True,
            "requested_timeout_ns": 100_000_000,
            "latency_ns": 100_000,
            "stop_success": True,
            "async_tasks_before": 0,
            "async_tasks_after": 0,
            "async_task_delta": 0,
        },
        "resources": {
            "before": {
                "current_rss_bytes": 10_000_000,
                "peak_rss_bytes": 12_000_000,
                "python_threads": 1,
                "os_threads": 2,
                "file_descriptors": 3,
            },
            "after": {
                "current_rss_bytes": 10_000_000,
                "peak_rss_bytes": 12_001_024,
                "python_threads": 1,
                "os_threads": 2,
                "file_descriptors": 3,
            },
            "current_rss_delta_bytes": 0,
            "peak_rss_growth_bytes": 1_024,
            "python_thread_delta": 0,
            "os_thread_delta": 0,
            "file_descriptor_delta": 0,
            "lifecycle_cycles_sync": 20,
            "lifecycle_cycles_async": 20,
            "async_task_delta": 0,
        },
        "saturation": {
            "frames_attempted_total": 300,
            "frames_accepted_total": 300,
            "input_full_retries_total": 0,
            "route_capacity_frames": 32,
            "route_peak_frames": 32,
            "route_drops_total": 268,
            "stop_success": True,
            "all_buffers_returned": True,
        },
        "median_boundary_latency_ns": 10_000,
    }


def test_given_repeated_values_when_summarized_then_dispersion_is_unit_free() -> None:
    summary = runner.distribution([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

    assert summary["samples_total"] == 7
    assert summary["median"] == 4.0
    assert summary["p95"] == 7.0
    assert summary["standard_deviation"] > 0


def test_given_non_candidate_output_when_validated_then_it_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(RuntimeError, match="exact Candidate 105 path"):
        runner.validate_output_path(tmp_path / "wrong.json", tmp_path)


def test_given_existing_candidate_output_when_validated_then_it_is_rejected(
    tmp_path: Path,
) -> None:
    expected = (
        tmp_path
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-105/report.json"
    )
    expected.parent.mkdir(parents=True)
    expected.write_text("retained", encoding="utf-8")

    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        runner.validate_output_path(expected, tmp_path)


def test_given_existing_candidate_harness_when_validated_then_it_is_rejected(
    tmp_path: Path,
) -> None:
    expected = (
        tmp_path
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-105/report.json"
    )
    harness = expected.parent / "harness"
    harness.mkdir(parents=True)
    (harness / "performance_resource_probe.py").write_text("retained", encoding="utf-8")

    with pytest.raises(RuntimeError, match="evidence directory is not empty"):
        runner.validate_output_path(expected, tmp_path)


def test_given_exact_dependency_freeze_when_validated_then_it_is_retained(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / runner.WHEEL_INSTALL_NAME
    installed = [
        *runner.RUNTIME_DEPENDENCIES,
        f"pocketstation @ {wheel.as_uri()}",
    ]

    assert runner.validate_dependency_freeze(installed, wheel) == sorted(installed)


def test_given_extra_dependency_when_validated_then_it_is_rejected(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / runner.WHEEL_INSTALL_NAME
    installed = [
        *runner.RUNTIME_DEPENDENCIES,
        "unexpected==1.0",
        f"pocketstation @ {wheel.as_uri()}",
    ]

    with pytest.raises(RuntimeError, match="dependency freeze changed"):
        runner.validate_dependency_freeze(installed, wheel)


def test_given_exact_private_environment_when_validated_then_it_passes(
    tmp_path: Path,
) -> None:
    venv = tmp_path / "venv"
    python = venv / "bin/python"
    package = venv / "lib/python3.13/site-packages/pocketstation/__init__.py"
    native = venv / "lib/python3.13/site-packages/pocketstation/_native.abi3.so"
    payload_hashes = {
        runner.WHEEL_PACKAGE_PATH: "1" * 64,
        runner.WHEEL_NATIVE_PATH: "2" * 64,
    }
    runner.validate_measurement_environment(
        {
            "python_executable": str(python),
            "environment_root": str(venv),
            "package_path": str(package),
            "native_module_path": str(native),
            "distribution_name": "pocketstation",
            "distribution_version": "0.1.4",
            "package_sha256": "1" * 64,
            "native_module_sha256": "2" * 64,
        },
        python=python,
        venv=venv,
        payload_hashes=payload_hashes,
    )


def test_given_wrong_private_interpreter_when_validated_then_it_is_rejected(
    tmp_path: Path,
) -> None:
    venv = tmp_path / "venv"
    payload_hashes = {
        runner.WHEEL_PACKAGE_PATH: "1" * 64,
        runner.WHEEL_NATIVE_PATH: "2" * 64,
    }

    with pytest.raises(RuntimeError, match="private venv interpreter"):
        runner.validate_measurement_environment(
            {
                "python_executable": str(tmp_path / "other/bin/python"),
                "environment_root": str(venv),
                "package_path": str(
                    venv / "lib/python3.13/site-packages/pocketstation/__init__.py"
                ),
                "native_module_path": str(
                    venv / "lib/python3.13/site-packages/pocketstation/_native.abi3.so"
                ),
                "distribution_name": "pocketstation",
                "distribution_version": "0.1.4",
                "package_sha256": "1" * 64,
                "native_module_sha256": "2" * 64,
            },
            python=venv / "bin/python",
            venv=venv,
            payload_hashes=payload_hashes,
        )


def test_given_raw_latency_samples_when_validated_then_summary_is_recomputed() -> None:
    measurement = valid_repetition(0)

    runner.validate_raw_latency_samples(measurement, round_trip_frames=300)


def test_given_tampered_raw_latency_summary_when_validated_then_it_is_rejected() -> (
    None
):
    measurement = valid_repetition(0)
    measurement["asyncio"]["round_trip"]["latency"]["p99_ns"] += 1

    with pytest.raises(RuntimeError, match="summary does not match raw samples"):
        runner.validate_raw_latency_samples(measurement, round_trip_frames=300)


@pytest.mark.parametrize("kind", ["remote-host", "query", "fragment", "sibling"])
def test_dependency_freeze_rejects_nonlocal_or_changed_wheel_uri(
    tmp_path: Path, kind: str
) -> None:
    wheel = tmp_path / runner.WHEEL_INSTALL_NAME
    uri = wheel.as_uri()
    if kind == "remote-host":
        uri = uri.replace("file://", "file://untrusted.example")
    elif kind == "query":
        uri += "?other=wheel"
    elif kind == "fragment":
        uri += "#other"
    else:
        uri = wheel.with_name("another.whl").as_uri()
    installed = [*runner.RUNTIME_DEPENDENCIES, f"pocketstation @ {uri}"]
    with pytest.raises(RuntimeError, match="exact wheel"):
        runner.validate_dependency_freeze(installed, wheel)
