#!/usr/bin/env python3
"""Build and test streams and provider authoring from an isolated wheel."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TEST_CASES = (
    "tests/test_streams.py::test_read_and_batch_modes_use_canonical_native_session",
    "tests/test_streams.py::test_audio_batch_result_distinguishes_empty_timeout_and_closed",
    "tests/test_aio_streams.py::test_async_read_and_batch_modes_use_canonical_native_session",
    "tests/test_aio_streams.py::test_async_audio_batch_result_distinguishes_states",
    "tests/test_sources.py::test_application_owned_pcm_uses_the_canonical_source_and_recording_path",
    "tests/test_aio_session.py::test_application_owned_pcm_has_an_async_writer",
    "tests/test_source_authoring.py::test_iterable_source_runs_in_core_and_receives_session_lineage",
    "tests/test_source_authoring.py::test_async_iterable_source_runs_on_the_owning_event_loop",
    "tests/test_operator_authoring.py::test_python_operator_processes_source_signal_with_derivation",
    "tests/test_operator_authoring.py::test_async_operator_runs_on_owning_loop",
    "tests/test_connector.py::test_connector_worker_receives_finite_native_owned_batches",
    "tests/test_aio_session.py::test_async_connector_worker_receives_finite_native_batches",
    "tests/test_audio_bridge.py::test_given_pcm_iterable_when_bridge_runs_then_core_drains_one_connector",
    "tests/test_aio_audio_bridge.py::test_given_async_pcm_when_bridge_runs_then_core_drains_connector",
    "tests/test_source_aware_transcription_example.py::test_two_source_lanes_keep_identity_through_one_model_operator",
)


def _run(
    arguments: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> None:
    subprocess.run(arguments, cwd=cwd, check=True, env=environment)


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        raise SystemExit("uv is required for installed-wheel conformance")
    maturin = shutil.which("maturin")
    if maturin is None:
        raise SystemExit("maturin is required for installed-wheel conformance")

    with tempfile.TemporaryDirectory(prefix="pks-w21-stream-") as temporary:
        root = Path(temporary)
        wheelhouse = root / "wheelhouse"
        environment = root / "environment"
        process_environment = os.environ.copy()
        process_environment["UV_CACHE_DIR"] = os.fspath(root / "uv-cache")
        wheelhouse.mkdir()
        shutil.copytree(REPOSITORY / "examples", root / "examples")

        _run(
            [
                maturin,
                "build",
                "--release",
                "--features",
                "conformance-fixtures",
                "--out",
                os.fspath(wheelhouse),
            ],
            cwd=REPOSITORY,
        )
        wheels = tuple(wheelhouse.glob("pocketstation-*.whl"))
        if len(wheels) != 1:
            raise SystemExit(f"expected one wheel, found {len(wheels)}")

        _run(
            [uv, "venv", os.fspath(environment), "--python", sys.executable],
            cwd=root,
            environment=process_environment,
        )
        interpreter = (
            environment / "Scripts" / "python.exe"
            if os.name == "nt"
            else environment / "bin" / "python"
        )
        _run(
            [
                uv,
                "pip",
                "install",
                "--python",
                os.fspath(interpreter),
                os.fspath(wheels[0]),
                "pytest",
                "pytest-asyncio",
            ],
            cwd=root,
            environment=process_environment,
        )
        _run(
            [
                os.fspath(interpreter),
                "-m",
                "pytest",
                "-q",
                "--import-mode=importlib",
                *(os.fspath(REPOSITORY / test_case) for test_case in TEST_CASES),
                "-rs",
            ],
            cwd=root,
        )
        runtime_report = root / "runtime-qualification.json"
        _run(
            [
                os.fspath(interpreter),
                os.fspath(
                    REPOSITORY / "tests" / "qualification" / "runtime_resources.py"
                ),
                "--frames",
                "100",
                "--output",
                os.fspath(runtime_report),
            ],
            cwd=root,
        )
        if not runtime_report.is_file():
            raise SystemExit("installed runtime qualification produced no report")
        package_path = subprocess.run(
            [
                os.fspath(interpreter),
                "-c",
                "import pocketstation; print(pocketstation.__file__)",
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not Path(package_path).is_relative_to(environment):
            raise SystemExit(
                f"PocketStation was not imported from the wheel: {package_path}"
            )
        print(f"installed_package={package_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
