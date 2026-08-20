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
TESTS = (
    REPOSITORY / "tests" / "test_streams.py",
    REPOSITORY / "tests" / "test_aio_streams.py",
    REPOSITORY / "tests" / "test_connector.py",
    REPOSITORY / "tests" / "test_source_authoring.py",
    REPOSITORY / "tests" / "test_operator_authoring.py",
    REPOSITORY / "tests" / "test_aio_session.py",
    REPOSITORY / "tests" / "test_transcription_example.py",
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
                *(os.fspath(test) for test in TESTS),
                "-k",
                (
                    "canonical_native_session or "
                    "connector_worker_receives_finite_native_owned_batches or "
                    "async_connector_worker_receives_finite_native_batches or "
                    "iterable_source_runs_in_core or "
                    "async_iterable_source_runs_on_the_owning_event_loop or "
                    "python_operator_processes_source_signal_with_derivation or "
                    "async_operator_runs_on_owning_loop or "
                    "whisper_example_declares_a_bounded_source_aware_operator or "
                    "real_whisper_process_preserves_source_identity"
                ),
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
