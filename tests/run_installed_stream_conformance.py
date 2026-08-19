#!/usr/bin/env python3
"""Build and test the stream surface from an isolated conformance wheel."""

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
)


def _run(arguments: list[str], *, cwd: Path) -> None:
    subprocess.run(arguments, cwd=cwd, check=True)


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        raise SystemExit("uv is required for installed-wheel conformance")

    with tempfile.TemporaryDirectory(prefix="pks-w21-stream-") as temporary:
        root = Path(temporary)
        wheelhouse = root / "wheelhouse"
        environment = root / "environment"
        wheelhouse.mkdir()

        _run(
            [
                uv,
                "run",
                "maturin",
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
                "canonical_native_session",
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
