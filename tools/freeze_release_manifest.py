#!/usr/bin/env python3
"""Build, validate, and freeze one local wheel/source-distribution pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from validate_distribution import validate_distributions

REPOSITORY = Path(__file__).resolve().parents[1]
CONSUMER = REPOSITORY / "tests" / "run_artifact_consumer.py"
CONSUMER_FORMATS = ("wheel", "sdist")
MYPY_REQUIREMENT = "mypy==2.3.1"
REPOSITORY_ID = "pocketstation-io/sdk-python"
CANDIDATE_ID = "pks-20260926-w21-python-packaging-106"
TASK_ID = "W21-PYTHON-PACKAGING"
MINIMUM_FREE_BYTES = 8 * 1024**3


def _one_artifact(directory: Path, pattern: str, description: str) -> Path:
    matches = tuple(sorted(directory.glob(pattern)))
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one {description} in {directory}, found {len(matches)}"
        )
    return matches[0]


def _command_output(command: list[str]) -> str:
    return subprocess.run(
        command,
        cwd=REPOSITORY,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_output(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout.strip()


def _source_report() -> dict[str, object]:
    status = tuple(
        line
        for line in _git_output(
            "status", "--porcelain=v1", "--untracked-files=all"
        ).splitlines()
        if line
    )
    if status:
        raise RuntimeError(
            "release freeze requires a clean committed source tree; dirty paths: "
            + ", ".join(line[3:] for line in status)
        )
    return {
        "repository": REPOSITORY_ID,
        "git_commit": _git_output("rev-parse", "HEAD"),
        "git_tree": _git_output("rev-parse", "HEAD^{tree}"),
        "git_status_porcelain": [],
        "working_tree_clean": True,
        "lockfiles": {
            "native/Cargo.lock": _sha256(REPOSITORY / "native" / "Cargo.lock"),
            "uv.lock": _sha256(REPOSITORY / "uv.lock"),
        },
    }


def _parse_consumer_json(stdout: str, distribution_format: str) -> dict[str, object]:
    for line in reversed(stdout.splitlines()):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            break
    else:
        raise RuntimeError(
            f"{distribution_format} consumer emitted no JSON result object"
        )
    if value.get("artifact_format") != distribution_format:
        raise RuntimeError(
            f"{distribution_format} consumer reported the wrong artifact format"
        )
    install = value.get("install")
    if not isinstance(install, dict) or install.get("record_verified") is not True:
        raise RuntimeError(
            f"{distribution_format} consumer did not verify the installed RECORD"
        )
    if value.get("uninstall_verified") is not True:
        raise RuntimeError(
            f"{distribution_format} consumer did not verify uninstall cleanup"
        )
    if not isinstance(value.get("consumer"), dict):
        raise RuntimeError(
            f"{distribution_format} consumer omitted installed runtime results"
        )
    if not isinstance(value.get("qualification"), dict):
        raise RuntimeError(
            f"{distribution_format} consumer omitted runtime qualification results"
        )
    expected_checks = {
        "pip_check": True,
        "record_integrity_check": True,
        "runtime_check": True,
        "typing_check": True,
        "uninstall_check": True,
    }
    if value.get("checks") != expected_checks:
        raise RuntimeError(
            f"{distribution_format} consumer checks are incomplete or unexpected"
        )
    expected_tools = {
        "mypy_requirement": MYPY_REQUIREMENT,
        "mypy_version": "2.3.1",
    }
    if value.get("tools") != expected_tools:
        raise RuntimeError(
            f"{distribution_format} consumer used an unexpected typing tool"
        )
    dependencies = value.get("installed_dependencies")
    if (
        not isinstance(dependencies, list)
        or not dependencies
        or not all(isinstance(item, str) and item for item in dependencies)
        or dependencies != sorted(dependencies)
        or MYPY_REQUIREMENT not in dependencies
    ):
        raise RuntimeError(
            f"{distribution_format} consumer dependency freeze is invalid"
        )
    return value


def _run_consumer(
    output: Path,
    *,
    distribution_format: str,
    artifact: Path,
    expected_version: str,
) -> dict[str, object]:
    command = [
        sys.executable,
        os.fspath(CONSUMER),
        "--artifact-format",
        distribution_format,
        "--artifact-dir",
        os.fspath(output),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    for variable in ("MYPYPATH", "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP"):
        environment.pop(variable, None)
    process = subprocess.run(
        command,
        cwd=output.parent,
        env=environment,
        capture_output=True,
        text=True,
        timeout=2_400,
    )
    log_path = output / f"consumer-{distribution_format}.log"
    log_path.write_text(
        "command: "
        + " ".join(command)
        + f"\nexit_code: {process.returncode}\n\nstdout:\n"
        + process.stdout
        + "\nstderr:\n"
        + process.stderr
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"{distribution_format} installed consumer failed with exit code "
            f"{process.returncode}; see {log_path}"
        )
    result = _parse_consumer_json(process.stdout, distribution_format)
    if result.get("artifact") != artifact.name:
        raise RuntimeError(
            f"{distribution_format} consumer qualified {result.get('artifact')!r}, "
            f"not {artifact.name!r}"
        )
    install = result["install"]
    if not isinstance(install, dict) or install.get("version") != expected_version:
        raise RuntimeError(
            f"{distribution_format} consumer installed an unexpected package version"
        )
    result_path = output / f"consumer-{distribution_format}.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return {
        "result": result,
        "result_file": result_path.name,
        "result_sha256": _sha256(result_path),
        "log_file": log_path.name,
        "log_sha256": _sha256(log_path),
    }


def _require_exact_outputs(output: Path, expected: set[str]) -> None:
    actual = {path.name for path in output.iterdir()}
    if actual != expected:
        raise RuntimeError(
            "release output membership mismatch: "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )


def _require_disk_headroom(directory: Path) -> int:
    free_bytes = shutil.disk_usage(directory).free
    if free_bytes < MINIMUM_FREE_BYTES:
        raise RuntimeError(
            "release freeze requires at least "
            f"{MINIMUM_FREE_BYTES} free bytes, found {free_bytes}"
        )
    return free_bytes


def _build(directory: Path) -> tuple[Path, Path]:
    environment = os.environ.copy()
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    environment["UV_NO_PROGRESS"] = "1"
    subprocess.run(
        [
            "uv",
            "build",
            "--wheel",
            "--sdist",
            "--no-sources",
            "--no-create-gitignore",
            "--out-dir",
            os.fspath(directory),
            os.fspath(REPOSITORY),
        ],
        cwd=REPOSITORY,
        env=environment,
        check=True,
        timeout=1_800,
    )
    return (
        _one_artifact(directory, "pocketstation-*.whl", "wheel"),
        _one_artifact(directory, "pocketstation-*.tar.gz", "source distribution"),
    )


@contextmanager
def _build_directory(output: Path) -> Iterator[Path]:
    directory = Path(
        tempfile.mkdtemp(prefix=f".{output.name}-build-", dir=output.parent)
    )
    try:
        yield directory
    except BaseException:
        print(
            f"Incomplete packaging diagnostics retained at {directory}", file=sys.stderr
        )
        raise
    else:
        shutil.rmtree(directory)


def freeze(output: Path) -> dict[str, object]:
    output = output.resolve()
    source = _source_report()
    try:
        output.relative_to(REPOSITORY)
    except ValueError:
        pass
    else:
        raise RuntimeError("release output must be outside the source repository")
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing release output {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    free_bytes_before = _require_disk_headroom(output.parent)
    with _build_directory(output) as temporary:
        build_directory = temporary / "build"
        release_directory = temporary / "release"
        build_directory.mkdir()
        release_directory.mkdir()
        wheel, sdist = _build(build_directory)
        validate_distributions(
            wheel,
            sdist,
            repository=REPOSITORY,
        )
        frozen_wheel = release_directory / wheel.name
        frozen_sdist = release_directory / sdist.name
        shutil.copyfile(wheel, frozen_wheel)
        shutil.copyfile(sdist, frozen_sdist)
        frozen = validate_distributions(
            frozen_wheel,
            frozen_sdist,
            repository=REPOSITORY,
        )
        consumers = {
            distribution_format: _run_consumer(
                release_directory,
                distribution_format=distribution_format,
                artifact=(
                    frozen_wheel if distribution_format == "wheel" else frozen_sdist
                ),
                expected_version=frozen.project_version,
            )
            for distribution_format in CONSUMER_FORMATS
        }
        post_consumer = validate_distributions(
            frozen_wheel,
            frozen_sdist,
            repository=REPOSITORY,
        )
        if post_consumer != frozen:
            raise RuntimeError("frozen artifact bytes changed during consumer tests")
        retained_names = {
            frozen_wheel.name,
            frozen_sdist.name,
            *(entry["log_file"] for entry in consumers.values()),
            *(entry["result_file"] for entry in consumers.values()),
        }
        _require_exact_outputs(release_directory, retained_names)
        report: dict[str, object] = {
            "schema_version": 1,
            "candidate_id": CANDIDATE_ID,
            "task_id": TASK_ID,
            "candidate": {
                "package": frozen.project_name,
                "version": frozen.project_version,
            },
            "classification": "SAFE-TO-TEST",
            "publishable": False,
            "source": source,
            "distribution": frozen.to_dict(),
            "consumers": consumers,
            "build": {
                "command": [
                    "uv",
                    "build",
                    "--wheel",
                    "--sdist",
                    "--no-sources",
                    "--no-create-gitignore",
                ],
                "python": sys.version.split()[0],
                "rustc": _command_output(["rustc", "--version"]),
                "cargo": _command_output(["cargo", "--version"]),
                "uv": _command_output(["uv", "--version"]),
                "mypy_requirement": MYPY_REQUIREMENT,
                "mypy_version": "2.3.1",
                "free_bytes_before": free_bytes_before,
                "minimum_free_bytes": MINIMUM_FREE_BYTES,
                "network_policy": {
                    "network_allowed": True,
                    "allowed_uses": [
                        "build-system dependencies declared in pyproject.toml",
                        "Rust registry dependencies locked by native/Cargo.lock",
                        "runtime dependencies declared in artifact metadata",
                        MYPY_REQUIREMENT + " for the installed typing proof",
                    ],
                    "forbidden_uses": [
                        "checkout, path, or Git dependencies",
                        "package publication",
                        "hosted PocketStation services",
                    ],
                },
            },
            "checks": {
                **frozen.checks,
                "fresh_build_directory": True,
                "frozen_bytes_revalidated": True,
                "frozen_bytes_unchanged_after_consumers": True,
                "sdist_consumer_passed": True,
                "wheel_consumer_passed": True,
                "installed_runtime": True,
                "installed_typing": True,
                "no_registry_publication": True,
                "no_checkout_dependencies": True,
                "pip_check": True,
                "record_verified": True,
                "release_output_membership_exact": True,
                "sdist_rebuild": True,
                "uninstall_verified": True,
            },
            "retained_outputs": sorted({*retained_names, "report.json"}),
            "limits": [
                "The immutable 0.1.4 name already exists on PyPI; these bytes "
                "are not publishable under that version.",
                "Cross-platform wheel execution is qualified by a later task.",
                "This local package gate adds no device, browser, WAN, or "
                "hosted-service claim.",
            ],
        }
        report_path = release_directory / "report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        expected_outputs = {*retained_names, report_path.name}
        _require_exact_outputs(release_directory, expected_outputs)
        source_after = _source_report()
        if source_after != source:
            raise RuntimeError("source tree changed during release freeze")
        release_directory.replace(output)
    _require_exact_outputs(output, expected_outputs)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    report = freeze(arguments.output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
