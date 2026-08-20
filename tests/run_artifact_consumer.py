#!/usr/bin/env python3
"""Install one wheel or sdist into a clean environment and execute it."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


def _artifact(directory: Path, kind: str) -> Path:
    pattern = "pocketstation-*.whl" if kind == "wheel" else "pocketstation-*.tar.gz"
    matches = tuple(sorted(directory.glob(pattern)))
    if len(matches) != 1:
        raise SystemExit(
            f"expected one PocketStation {kind} in {directory}, found {len(matches)}"
        )
    return matches[0].resolve()


def _interpreter(environment: Path) -> Path:
    return (
        environment / "Scripts" / "python.exe"
        if os.name == "nt"
        else environment / "bin" / "python"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-kind", choices=("wheel", "sdist"), required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    arguments = parser.parse_args()
    artifact = _artifact(arguments.artifact_dir, arguments.artifact_kind)

    with tempfile.TemporaryDirectory(prefix="pks-artifact-consumer-") as temporary:
        root = Path(temporary)
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        interpreter = _interpreter(environment)
        process_environment = os.environ.copy()
        process_environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        subprocess.run(
            [
                os.fspath(interpreter),
                "-m",
                "pip",
                "install",
                os.fspath(artifact),
            ],
            cwd=root,
            env=process_environment,
            check=True,
            timeout=900,
        )
        consumer = root / "installed_consumer.py"
        shutil.copyfile(REPOSITORY / "tests" / "installed_consumer.py", consumer)
        subprocess.run(
            [os.fspath(interpreter), os.fspath(consumer)],
            cwd=root,
            env=process_environment,
            check=True,
            timeout=60,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
