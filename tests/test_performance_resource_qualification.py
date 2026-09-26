from __future__ import annotations

import copy
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

SDK_ROOT = Path(__file__).parents[1]
WORKSPACE_ROOT = SDK_ROOT.parents[1]


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
verifier = load_module(
    "performance_resource_verifier",
    WORKSPACE_ROOT / "tools/verify-python-performance-report.py",
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


def valid_report() -> dict[str, Any]:
    repetitions = [valid_repetition(index) for index in range(7)]
    return {
        "schema": "io.pocketstation.python.performance-resource-qualification.v2",
        "task_id": "W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION",
        "candidate_id": verifier.CANDIDATE_ID,
        "source_candidate_id": verifier.SOURCE_CANDIDATE_ID,
        "sdk_commit": verifier.SDK_COMMIT,
        "classification": "SAFE-TO-TEST",
        "scope": "installed-wheel-local-component",
        "units": dict(verifier.UNITS),
        "environment": {
            "os": "Darwin",
            "os_release": "test",
            "machine": "arm64",
            "runner_python": "3.13",
            "uv_version": "uv 0.10.9",
        },
        "artifact": {
            "wheel_path": str(
                WORKSPACE_ROOT
                / "docs/execution/evidence/W21-PYTHON-REAL-PATH-E2E"
                / "candidate-103/candidate-wheel.whl"
            ),
            "wheel_sha256": verifier.WHEEL_SHA256,
            "candidate_103_acceptance_sha256": verifier.SOURCE_ACCEPTANCE_SHA256,
            "probe_path": str(
                WORKSPACE_ROOT / "docs/execution/evidence/"
                "W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION/"
                "candidate-105/harness/performance_resource_probe.py"
            ),
            "probe_sha256": runner.sha256(
                SDK_ROOT / "benchmarks/performance_resource_probe.py"
            ),
            "runner_path": str(
                WORKSPACE_ROOT / "docs/execution/evidence/"
                "W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION/"
                "candidate-105/harness/run_performance_resource_qualification.py"
            ),
            "runner_sha256": runner.sha256(
                SDK_ROOT / "benchmarks/run_performance_resource_qualification.py"
            ),
            "installed_distributions": sorted(
                [
                    *runner.RUNTIME_DEPENDENCIES,
                    "pocketstation @ file:///private/tmp/c105/"
                    + runner.WHEEL_INSTALL_NAME,
                ]
            ),
            "wheel_payload_sha256": {
                runner.WHEEL_PACKAGE_PATH: (
                    "1b51e73722ed6e67187f24e4fb0e496023765119f0f033547f8447557cbb21b2"
                ),
                runner.WHEEL_NATIVE_PATH: (
                    "3e71b71202d7d3fffe10d8c821c6b9b0bcf49735eb5d8b5fe970770e2058be21"
                ),
            },
            "installation": {
                "network_allowed": False,
                "uv_offline": True,
                "python_isolated_flag": True,
                "python_user_site_disabled": True,
                "runtime_dependencies": list(runner.RUNTIME_DEPENDENCIES),
                "dependency_freeze_verified": True,
                "exact_wheel_payload_verified": True,
            },
        },
        "method": {
            "warmups_total": 2,
            "repetitions_total": 7,
            "fresh_process_per_repetition": True,
            "round_trip_frames": 300,
            "capacity_frames_per_source": 1_000,
            "product_load_frames_per_source": 400,
            "source_count": 2,
            "sample_rate_hz": 48_000,
            "samples_per_frame": 480,
            "lifecycle_cycles_per_mode_per_repetition": 20,
            "round_trip_measurement": "serialized latency workload",
            "raw_latency_samples_retained": True,
            "capacity_measurement": "two-source bounded capacity workload",
            "product_load_measurement": "two-source paced four-second workload",
            "throughput_requirement": {
                "sources_total": 2,
                "frame_duration_ms": 10,
                "frames_per_second_per_source": 100,
                "aggregate_product_frames_per_second": 200,
                "headroom_multiplier": 2.5,
                "qualified_minimum_frames_per_second": 500.0,
            },
            "product_load_requirement": {
                "duration_seconds": 4,
                "configured_period_ns": 10_000_000,
                "frames_per_source": 400,
                "aggregate_frames_total": 800,
                "minimum_aggregate_frames_per_second": 180.0,
                "scheduler_tolerance_ns": 50_000_000,
                "workload_timeout_ns": 30_000_000_000,
            },
            "cancellation_read_timeout_ns": 100_000_000,
            "cancellation_total_budget_ns": 250_000_000,
            "subprocess_timeout_seconds": 180,
            "warmup_process_durations_ns": [1_000_000_000, 1_000_000_000],
            "measurement_engine": ("pocketstation-installed-wheel-repeated-process-v1"),
            "pyperf_used": False,
            "pyperf_decision": "multi-resource workload; no pyperf claim",
        },
        "budgets": dict(verifier.BUDGETS),
        "repetitions": repetitions,
        "dispersion": runner.aggregate(repetitions),
        "checks": runner.evaluate(repetitions),
        "result": "PASS",
        "non_claims": [
            "No competitor superiority claim follows.",
            "No physical-device claim follows.",
            "No cross-platform claim follows.",
            "Candidate 103 owns real-path evidence.",
        ],
        "source_acceptance_classification": "REAL-DEVICE-PROVEN",
    }


def test_given_repeated_values_when_summarized_then_dispersion_is_unit_free() -> None:
    summary = runner.distribution([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

    assert summary["samples_total"] == 7
    assert summary["median"] == 4.0
    assert summary["p95"] == 7.0
    assert summary["standard_deviation"] > 0


def write_report(tmp_path: Path, report: dict[str, Any]) -> Path:
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_given_complete_report_when_verified_then_it_passes(tmp_path: Path) -> None:
    verifier.verify(write_report(tmp_path, valid_report()))


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


def test_candidate_104_retention_pins_every_retained_file(tmp_path: Path) -> None:
    source = (
        WORKSPACE_ROOT
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-104"
    )
    target = (
        tmp_path
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-104"
    )
    shutil.copytree(source, target)

    runner.validate_candidate_104_retention(tmp_path)


def test_candidate_104_retention_rejects_reference_review_tampering(
    tmp_path: Path,
) -> None:
    source = (
        WORKSPACE_ROOT
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-104"
    )
    target = (
        tmp_path
        / "docs/execution/evidence/W21-PYTHON-PERFORMANCE-RESOURCE-QUALIFICATION"
        / "candidate-104"
    )
    shutil.copytree(source, target)
    (target / "reference-review.json").write_text("tampered", encoding="utf-8")

    with pytest.raises(RuntimeError, match=r"reference-review\.json changed"):
        runner.validate_candidate_104_retention(tmp_path)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda report: report["units"].pop("memory"), "units"),
        (
            lambda report: report["artifact"].update(wheel_sha256="0" * 64),
            "wheel hash changed",
        ),
        (
            lambda report: report["artifact"].update(
                candidate_103_acceptance_sha256="0" * 64
            ),
            "source acceptance hash changed",
        ),
        (
            lambda report: report["method"].update(repetitions_total=6),
            "fewer than seven",
        ),
        (
            lambda report: report["budgets"].update(
                cancellation_latency_ns_max=10_000_000_000
            ),
            "budgets",
        ),
        (
            lambda report: report["repetitions"][0]["cancellation"].update(
                latency_ns=300_000_000
            ),
            "reported checks do not match repetitions",
        ),
        (
            lambda report: report["repetitions"][0]["cancellation"].update(
                requested_timeout_ns=1_000_000_000
            ),
            "cancellation timeout changed",
        ),
        (
            lambda report: report["checks"].update(
                resources_returned_within_budget=False
            ),
            "reported checks do not match repetitions",
        ),
        (
            lambda report: report["repetitions"][1].update(
                process_id=report["repetitions"][0]["process_id"]
            ),
            "process",
        ),
        (
            lambda report: report["repetitions"][0].update(
                native_module_path=(
                    "/private/tmp/c105-sibling/venv/lib/python3.13/"
                    "site-packages/pocketstation/_native.abi3.so"
                )
            ),
            "environment",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"].update(
                source_count=1
            ),
            "source count",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"]["sources"][
                1
            ].update(source_id=1),
            "source IDs",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"]["routes"][
                1
            ].update(route_id=1),
            "route IDs",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"]["sources"][
                0
            ].update(frames_received_total=999),
            "received",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"]["sources"][
                0
            ].update(last_sequence_number=998),
            "sequence",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"].update(
                route_drops_total=1
            ),
            "drop",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["product_load"].update(
                configured_period_ns=None
            ),
            "period",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["capacity"].update(
                aggregate_frames_per_second=99_999.0
            ),
            "derived",
        ),
        (
            lambda report: report["repetitions"][0]["sync"]["product_load"].update(
                wall_time_ns=5_000_000_000,
                aggregate_frames_per_second=160.0,
            ),
            "product load",
        ),
        (
            lambda report: report["repetitions"][0].update(
                package_path=str(
                    SDK_ROOT / "fake/site-packages/pocketstation/__init__.py"
                )
            ),
            "checkout",
        ),
    ],
)
def test_given_tampered_report_when_verified_then_it_is_rejected(
    mutation: Any,
    expected: str,
    tmp_path: Path,
) -> None:
    report = valid_report()
    mutation(report)

    with pytest.raises(verifier.Rejected, match=expected):
        verifier.verify(write_report(tmp_path, report))
