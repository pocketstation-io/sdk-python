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
)


def _run(arguments: list[str], *, cwd: Path) -> None:
    subprocess.run(arguments, cwd=cwd, check=True)


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
        wheelhouse.mkdir()

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
                    "async_operator_runs_on_owning_loop"
                ),
                "-rs",
            ],
            cwd=root,
        )
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
