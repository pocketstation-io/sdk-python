#!/usr/bin/env python3
"""Qualify one wheel or source distribution from an isolated installation."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn
from urllib.parse import unquote, urlsplit

REPOSITORY = Path(__file__).resolve().parents[1]
_MYPY_REQUIREMENT = "mypy==2.3.1"
_MYPY_VERSION = "2.3.1"
_NATIVE_SUFFIXES = (".so", ".pyd")


def _fail(message: str) -> NoReturn:
    raise SystemExit(message)


def _artifact(directory: Path, distribution_format: str) -> Path:
    pattern = (
        "pocketstation-*.whl"
        if distribution_format == "wheel"
        else "pocketstation-*.tar.gz"
    )
    matches = tuple(sorted(directory.glob(pattern)))
    if len(matches) != 1:
        _fail(
            f"expected one PocketStation {distribution_format} in {directory}, "
            f"found {len(matches)}"
        )
    return matches[0].resolve()


def _extract_sdist(artifact: Path, destination: Path) -> Path:
    roots: set[str] = set()
    with tarfile.open(artifact, mode="r:gz") as archive:
        members = archive.getmembers()
        if not members:
            _fail("source distribution is empty")
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not path.parts:
                _fail(f"source distribution contains an unsafe path: {member.name}")
            if member.issym() or member.islnk() or member.isdev():
                _fail(
                    "source distribution contains a link or device entry: "
                    f"{member.name}"
                )
            roots.add(path.parts[0])
        if len(roots) != 1:
            _fail(
                "source distribution must contain one top-level directory, found "
                f"{sorted(roots)}"
            )
        archive.extractall(destination, members=members, filter="data")
    source_root = (destination / next(iter(roots))).resolve()
    if not (source_root / "pyproject.toml").is_file():
        _fail("source distribution contains no root pyproject.toml")
    return source_root


def _interpreter(environment: Path) -> Path:
    return (
        environment / "Scripts" / "python.exe"
        if os.name == "nt"
        else environment / "bin" / "python"
    )


def _command(environment: Path) -> Path:
    return (
        environment / "Scripts" / "pocketstation-demo.exe"
        if os.name == "nt"
        else environment / "bin" / "pocketstation-demo"
    )


def _isolated_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for variable in (
        "MYPYPATH",
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "VIRTUAL_ENV",
    ):
        environment.pop(variable, None)
    environment.update(
        {
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    return environment


def _run(
    command: Sequence[str | os.PathLike[str]],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout_seconds: int,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [os.fspath(part) for part in command],
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.CalledProcessError as error:
        if capture_output:
            print(error.stdout or "", file=sys.stderr)
            print(error.stderr or "", file=sys.stderr)
        raise


def _installed_record(
    interpreter: Path,
    *,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    program = r"""
import csv
import importlib.metadata
import json
import sys
from pathlib import Path

distribution = importlib.metadata.distribution("pocketstation")
files = tuple(distribution.files or ())
record_path = next(
    Path(distribution.locate_file(file)).resolve()
    for file in files
    if str(file).replace("\\", "/").endswith(".dist-info/RECORD")
)
with record_path.open(encoding="utf-8", newline="") as stream:
    record_rows = list(csv.reader(stream))
records = [row[0].replace("\\", "/") for row in record_rows if row]
absolute_paths = [
    str(Path(distribution.locate_file(record)).resolve()) for record in records
]
package = Path(distribution.locate_file("pocketstation")).resolve()
print(json.dumps({
    "absolute_paths": absolute_paths,
    "dist_info": str(record_path.parent),
    "environment": str(Path(sys.prefix).resolve()),
    "package": str(package),
    "record_rows": record_rows,
    "records": records,
    "version": distribution.version,
}, sort_keys=True))
"""
    process = _run(
        (interpreter, "-I", "-c", program),
        cwd=cwd,
        environment=environment,
        timeout_seconds=30,
        capture_output=True,
    )
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        _fail(f"installed distribution produced invalid RECORD JSON: {error}")
    if not isinstance(report, dict):
        _fail("installed distribution RECORD report is not an object")
    return report


def _record_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    encoded = base64.urlsafe_b64encode(digest.digest()).rstrip(b"=").decode("ascii")
    return f"sha256={encoded}"


def _validate_installed_record(report: dict[str, Any]) -> tuple[Path, ...]:
    raw_records = report.get("records")
    raw_paths = report.get("absolute_paths")
    raw_rows = report.get("record_rows")
    if not isinstance(raw_records, list) or not all(
        isinstance(item, str) for item in raw_records
    ):
        _fail("installed distribution has no readable RECORD entries")
    if not isinstance(raw_paths, list) or not all(
        isinstance(item, str) for item in raw_paths
    ):
        _fail("installed distribution has no resolved RECORD paths")
    if not isinstance(raw_rows, list) or not all(
        isinstance(row, list)
        and len(row) == 3
        and all(isinstance(item, str) for item in row)
        for row in raw_rows
    ):
        _fail("installed distribution contains malformed RECORD rows")
    if len(raw_records) != len(raw_paths) or len(raw_records) != len(raw_rows):
        _fail("installed distribution RECORD rows and paths disagree")
    if [row[0].replace("\\", "/") for row in raw_rows] != raw_records:
        _fail("installed distribution RECORD row order disagrees with resolved paths")
    if len(set(raw_records)) != len(raw_records):
        _fail("installed distribution RECORD contains duplicate paths")
    raw_environment = report.get("environment")
    if not isinstance(raw_environment, str):
        _fail("installed distribution omitted its environment root")
    environment_root = Path(raw_environment).resolve()
    resolved_paths = tuple(Path(path).resolve() for path in raw_paths)
    outside_environment = tuple(
        path for path in resolved_paths if not path.is_relative_to(environment_root)
    )
    if outside_environment:
        _fail(
            "installed RECORD points outside its isolated environment: "
            f"{outside_environment}"
        )
    records = tuple(raw_records)
    required_suffixes = (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        ".dist-info/METADATA",
        ".dist-info/RECORD",
        ".dist-info/licenses/LICENSE",
        ".dist-info/licenses/NOTICE",
        ".dist-info/sboms/pocketstation-python.cyclonedx.json",
    )
    for suffix in required_suffixes:
        if sum(record.endswith(suffix) for record in records) != 1:
            _fail(f"installed RECORD must contain exactly one {suffix}")
    native_modules = tuple(
        record
        for record in records
        if Path(record).name.startswith("_native.")
        and record.lower().endswith(_NATIVE_SUFFIXES)
    )
    if len(native_modules) != 1:
        _fail("installed RECORD must contain exactly one pocketstation._native module")
    # PEP 770 permits repair tools to add their own SBOMs. The package SBOM
    # above is mandatory; every additional file receives the same RECORD
    # hash/size verification below and ownership/uninstall checks.
    missing = tuple(path for path in resolved_paths if not os.path.lexists(path))
    if missing:
        _fail(f"installed RECORD contains missing files: {missing}")
    record_entries = tuple(
        (record, path, digest, size)
        for record, path, (_, digest, size) in zip(
            records,
            resolved_paths,
            raw_rows,
            strict=True,
        )
    )
    record_self = tuple(
        entry for entry in record_entries if entry[0].endswith(".dist-info/RECORD")
    )
    if len(record_self) != 1:
        _fail("installed distribution must own exactly one RECORD file")
    for record, path, digest, size in record_entries:
        if record.endswith(".dist-info/RECORD"):
            if digest or size:
                _fail("installed RECORD row must not hash itself")
            continue
        if not path.is_file():
            _fail(f"installed RECORD member is not a regular file: {record}")
        if not size.isdecimal() or int(size) != path.stat().st_size:
            _fail(f"installed RECORD size does not match {record}")
        if digest != _record_digest(path):
            _fail(f"installed RECORD digest does not match {record}")
    return resolved_paths


def _validate_demo_help(
    demo: Path,
    *,
    cwd: Path,
    environment: dict[str, str],
) -> None:
    if not demo.is_file():
        _fail("installed artifact contains no pocketstation-demo command")
    help_text = _run(
        (demo, "--help"),
        cwd=cwd,
        environment=environment,
        timeout_seconds=30,
        capture_output=True,
    ).stdout
    for option in (
        "--application",
        "--microphone-id",
        "--recording-root",
        "--duration-seconds",
        "--model",
        "--allow-model-download",
        "--no-browser",
        "--output-format",
    ):
        if option not in help_text:
            _fail(f"installed demo help omitted {option}")
    if "--relay" in help_text:
        _fail("installed demo exposes Relay implementation plumbing")


def _run_installed_typing(
    interpreter: Path,
    consumer: Path,
    *,
    cwd: Path,
    environment: dict[str, str],
) -> str:
    _run(
        (interpreter, "-m", "pip", "install", _MYPY_REQUIREMENT),
        cwd=cwd,
        environment=environment,
        timeout_seconds=300,
    )
    _run(
        (
            interpreter,
            "-m",
            "mypy",
            "--strict",
            "--no-incremental",
            consumer,
        ),
        cwd=cwd,
        environment=environment,
        timeout_seconds=120,
    )
    process = _run(
        (
            interpreter,
            "-I",
            "-c",
            "import importlib.metadata; print(importlib.metadata.version('mypy'))",
        ),
        cwd=cwd,
        environment=environment,
        timeout_seconds=30,
        capture_output=True,
    )
    version = process.stdout.strip()
    if version != _MYPY_VERSION:
        _fail(f"installed MyPy version must be {_MYPY_VERSION}, found {version!r}")
    return version


def _installed_dependencies(
    interpreter: Path,
    *,
    cwd: Path,
    environment: dict[str, str],
    install_target: Path,
    expected_version: str,
) -> list[str]:
    process = _run(
        (interpreter, "-m", "pip", "freeze", "--all"),
        cwd=cwd,
        environment=environment,
        timeout_seconds=60,
        capture_output=True,
    )
    dependencies = sorted(line.strip() for line in process.stdout.splitlines() if line)
    if not dependencies:
        _fail("installed dependency inventory is empty")
    # pip records the local artifact URL for this distribution. Bind that URL
    # to the actual tested input, then retain its version beside the separately
    # hashed artifact instead of persisting a temporary build-directory name.
    for index, dependency in enumerate(dependencies):
        if dependency.startswith("pocketstation @ "):
            source = urlsplit(dependency.removeprefix("pocketstation @ "))
            source_path = unquote(source.path)
            if os.name == "nt" and source_path.startswith("/"):
                source_path = source_path[1:]
            if (
                source.scheme != "file"
                or source.netloc not in ("", "localhost")
                or Path(source_path).resolve() != install_target.resolve()
            ):
                _fail("installed PocketStation origin differs from the tested artifact")
            dependencies[index] = f"pocketstation=={expected_version}"
    dependencies.sort()
    return dependencies


def _verify_uninstalled(
    interpreter: Path,
    *,
    demo: Path,
    install_report: dict[str, Any],
    cwd: Path,
    environment: dict[str, str],
) -> None:
    package = Path(str(install_report["package"]))
    dist_info = Path(str(install_report["dist_info"]))
    owned_paths = tuple(Path(path) for path in install_report["absolute_paths"])
    leftovers = tuple(
        path
        for path in (package, dist_info, demo, *owned_paths)
        if os.path.lexists(path)
    )
    if leftovers:
        _fail(f"pip uninstall left PocketStation-owned paths: {leftovers}")
    program = r"""
import importlib.metadata
import importlib.util

if importlib.util.find_spec("pocketstation") is not None:
    raise SystemExit("pocketstation remains importable after uninstall")
try:
    importlib.metadata.distribution("pocketstation")
except importlib.metadata.PackageNotFoundError:
    pass
else:
    raise SystemExit("PocketStation metadata remains after uninstall")
"""
    _run(
        (interpreter, "-I", "-c", program),
        cwd=cwd,
        environment=environment,
        timeout_seconds=30,
    )


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-format",
        "--artifact-kind",
        choices=("wheel", "sdist"),
        dest="distribution_format",
        required=True,
    )
    parser.add_argument("--artifact-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    arguments = _parse_arguments()
    artifact = _artifact(arguments.artifact_dir, arguments.distribution_format)

    with tempfile.TemporaryDirectory(prefix="pks-artifact-consumer-") as temporary:
        root = Path(temporary).resolve()
        environment_path = root / "environment"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment_path)
        interpreter = _interpreter(environment_path)
        process_environment = _isolated_environment()
        install_target = (
            _extract_sdist(artifact, root / "source")
            if arguments.distribution_format == "sdist"
            else artifact
        )
        _run(
            (interpreter, "-m", "pip", "install", "--no-compile", install_target),
            cwd=root,
            environment=process_environment,
            timeout_seconds=900,
        )
        _run(
            (interpreter, "-m", "pip", "check"),
            cwd=root,
            environment=process_environment,
            timeout_seconds=60,
        )

        consumer = root / "installed_consumer.py"
        typing_consumer = root / "installed_typing_consumer.py"
        shutil.copyfile(REPOSITORY / "tests" / "installed_consumer.py", consumer)
        shutil.copyfile(
            REPOSITORY / "tests" / "installed_typing_consumer.py", typing_consumer
        )
        consumer_result = _run(
            (interpreter, "-I", consumer),
            cwd=root,
            environment=process_environment,
            timeout_seconds=90,
            capture_output=True,
        )
        mypy_version = _run_installed_typing(
            interpreter,
            typing_consumer,
            cwd=root,
            environment=process_environment,
        )
        demo = _command(environment_path)
        _validate_demo_help(
            demo,
            cwd=root,
            environment=process_environment,
        )
        install_report = _installed_record(
            interpreter,
            cwd=root,
            environment=process_environment,
        )
        _validate_installed_record(install_report)

        qualification = root / "runtime_resources.py"
        qualification_report = root / "runtime-qualification.json"
        shutil.copyfile(
            REPOSITORY / "tests" / "qualification" / "runtime_resources.py",
            qualification,
        )
        _run(
            (
                interpreter,
                "-I",
                qualification,
                "--frames",
                "500",
                "--output",
                qualification_report,
            ),
            cwd=root,
            environment=process_environment,
            timeout_seconds=180,
        )
        installed_dependencies = _installed_dependencies(
            interpreter,
            cwd=root,
            environment=process_environment,
            install_target=install_target,
            expected_version=install_report["version"],
        )

        _run(
            (interpreter, "-m", "pip", "uninstall", "--yes", "pocketstation"),
            cwd=root,
            environment=process_environment,
            timeout_seconds=120,
        )
        _verify_uninstalled(
            interpreter,
            demo=demo,
            install_report=install_report,
            cwd=root,
            environment=process_environment,
        )
        native_record = next(
            record
            for record in install_report["records"]
            if Path(record).name.startswith("_native.")
            and record.lower().endswith(_NATIVE_SUFFIXES)
        )
        output = {
            "artifact": artifact.name,
            "artifact_format": arguments.distribution_format,
            "checks": {
                "pip_check": True,
                "record_integrity_check": True,
                "runtime_check": True,
                "typing_check": True,
                "uninstall_check": True,
            },
            "consumer": json.loads(consumer_result.stdout),
            "install": {
                "native_module": native_record,
                "record_entries_total": len(install_report["records"]),
                "record_verified": True,
                "version": install_report["version"],
            },
            "installed_dependencies": installed_dependencies,
            "qualification": json.loads(qualification_report.read_text()),
            "tools": {
                "mypy_requirement": _MYPY_REQUIREMENT,
                "mypy_version": mypy_version,
            },
            "uninstall_verified": True,
        }
        print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
