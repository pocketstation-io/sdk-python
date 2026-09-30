#!/usr/bin/env python3
"""Run native installed consumers and verify the complete retained wheel matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_distribution import validate_sdist, validate_wheel

ROOT = Path(__file__).resolve().parents[1]
MATRIX = Path(__file__).with_name("wheel-matrix.json")


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def matrix() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(MATRIX.read_text())
    targets = result["targets"]
    if len(targets) != 6 or len({item["id"] for item in targets}) != 6:
        raise ValueError("expected six distinct native targets")
    return result


def target_named(identifier: str) -> dict[str, Any]:
    matches = [item for item in matrix()["targets"] if item["id"] == identifier]
    if len(matches) != 1:
        raise ValueError(f"unknown native target: {identifier}")
    return matches[0]


def matrix_digest() -> str:
    # Git may check out text with CRLF on Windows. Bind the parsed declaration;
    # the source commit separately pins its original Git bytes.
    payload = json.dumps(matrix(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
    ).strip()


def one(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"expected one {pattern} in {directory}; found {len(matches)}")
    return matches[0]


def validate_aec(result: dict[str, Any]) -> None:
    observation = result.get("aec")
    if not isinstance(observation, dict):
        raise ValueError("installed AEC evidence is missing")
    echo = observation.get("echo_power_ratio")
    voice = observation.get("voice_power_ratio")
    if not (
        type(observation.get("processed_frames_total")) is int
        and observation["processed_frames_total"] == 400
        and type(observation.get("output_frames_total")) is int
        and observation["output_frames_total"] == 404
        and type(observation.get("tail_frames_total")) is int
        and observation["tail_frames_total"] == 4
        and type(observation.get("tail_padding_samples_total")) is int
        and observation["tail_padding_samples_total"] == 1920
        and observation.get("input_provenance_preserved") is True
        and observation.get("polled_tail_preserved") is True
        and type(echo) in (int, float)
        and math.isfinite(echo)
        and 0 <= echo < 0.5
        and type(voice) in (int, float)
        and math.isfinite(voice)
        and 0.5 < voice < 2.0
        and observation.get("raw_stem_unchanged") is True
        and observation.get("terminal_state") == "stopped"
    ):
        raise ValueError("installed AEC processing evidence failed")


def validate_result(result: dict[str, Any], distribution_format: str) -> None:
    expected_checks = {
        "pip_check",
        "record_integrity_check",
        "runtime_check",
        "typing_check",
        "uninstall_check",
    }
    if result.get("checks") != dict.fromkeys(expected_checks, True):
        raise ValueError("installed checks are incomplete")
    if result.get("artifact_format") != distribution_format:
        raise ValueError("consumer distribution format differs")
    install = result["install"]
    if install["version"] != matrix()["package_version"]:
        raise ValueError("installed package version differs")
    if install["record_verified"] is not True or not result["uninstall_verified"]:
        raise ValueError("RECORD or uninstall was not verified")
    consumer = result["consumer"]
    if consumer["success"] is not True or consumer["transformed"] != "INSTALLED":
        raise ValueError("canonical Session/Operator did not execute")
    if "site-packages" not in consumer["package_path"].replace("\\", "/").split("/"):
        raise ValueError("consumer imported outside site-packages")
    if consumer["source_id"] <= 0 or consumer["stream_id"] <= 0:
        raise ValueError("source identity is absent")
    validate_aec(consumer)
    if result["tools"] != {"mypy_requirement": "mypy==2.3.1", "mypy_version": "2.3.1"}:
        raise ValueError("installed typing tool differs")
    for mode in ("sync", "asyncio"):
        cell = result["qualification"][mode]
        if (
            cell["frames_total"],
            cell["samples_per_frame"],
            cell["route_drops_total"],
        ) != (500, 480, 0):
            raise ValueError(f"{mode} delivery differs from the complete vector")
    slow = result["qualification"]["slow_consumer"]
    if not (
        slow["route_drops_total"] > 0
        and slow["route_peak_frames"] <= slow["route_capacity_frames"]
        and slow["stop_success"] is True
    ):
        raise ValueError("bounded saturation or teardown is unproved")


def validate_identity(report: dict[str, Any], expected_source: str) -> None:
    target = target_named(report["target_id"])
    if (
        report["source_commit"] != expected_source
        or report["matrix_sha256"] != matrix_digest()
    ):
        raise ValueError("source or declared matrix changed")
    if (
        report["system"] != target["system"]
        or report["machine"].lower() != target["machine"].lower()
    ):
        raise ValueError("actual native host does not match declared target")
    if report["python_version"] not in target["python_versions"]:
        raise ValueError("Python runtime is outside the declared matrix")
    if report["implementation"] != "CPython" or report["exit_code"] != 0:
        raise ValueError("consumer did not pass on CPython")


def run_consumer(args: argparse.Namespace) -> None:
    target = target_named(args.target)
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    report = {
        "schema_version": 1,
        "target_id": target["id"],
        "source_commit": source_commit(),
        "matrix_sha256": matrix_digest(),
        "system": platform.system(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": version,
        "python_full_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "exit_code": 0,
        "classification": "SAFE-TO-TEST",
    }
    validate_identity(report, source_commit())
    artifact = one(args.artifact_dir, "*.whl" if args.format == "wheel" else "*.tar.gz")
    if args.format == "wheel":
        validate_wheel(artifact, expected_version=matrix()["package_version"])
    else:
        validate_sdist(artifact, expected_version=matrix()["package_version"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "tests/run_artifact_consumer.py"),
        "--artifact-format",
        args.format,
        "--artifact-dir",
        str(args.artifact_dir.resolve()),
    ]
    process = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=2400
    )
    log = args.output.with_suffix(".log")
    log.write_text(process.stdout + "\nSTDERR:\n" + process.stderr, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(f"installed consumer failed: {log}")
    result = json.loads(process.stdout.strip().splitlines()[-1])
    validate_result(result, args.format)
    report.update(
        artifact=artifact.name,
        artifact_sha256=digest(artifact),
        artifact_format=args.format,
        result=result,
        log_file=log.name,
        log_sha256=digest(log),
    )
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"PASS {target['id']} Python {version} {args.format}")


def aggregate(directory: Path, expected_source: str) -> dict[str, Any]:
    declarations = matrix()
    expected = {
        (t["id"], v) for t in declarations["targets"] for v in t["python_versions"]
    }
    reports = sorted(directory.rglob("consumer-*.json"))
    seen: set[tuple[str, str]] = set()
    wheel_hashes: dict[str, str] = {}
    artifacts: dict[str, dict[str, str]] = {}
    sdist_seen = False
    for path in reports:
        report = json.loads(path.read_text())
        validate_identity(report, expected_source)
        form = report["artifact_format"]
        validate_result(report["result"], form)
        if Path(report["artifact"]).name != report["artifact"]:
            raise ValueError("artifact name must not contain a directory")
        if report["result"]["artifact"] != report["artifact"]:
            raise ValueError("consumer tested another artifact")
        matches = list(directory.rglob(report["artifact"]))
        if len(matches) != 1 or digest(matches[0]) != report["artifact_sha256"]:
            raise ValueError("tested artifact is missing, duplicated or changed")
        artifact = matches[0]
        log = path.with_name(report["log_file"])
        if log.parent != path.parent or digest(log) != report["log_sha256"]:
            raise ValueError("consumer log changed")
        if form == "wheel":
            target = target_named(report["target_id"])
            validate_wheel(artifact, expected_version=declarations["package_version"])
            tags = artifact.name.removesuffix(".whl").split("-")
            if "-".join(tags[-3:-1]) != declarations["abi"] or target[
                "platform_tag"
            ] not in tags[-1].split("."):
                raise ValueError("wheel ABI or native platform tag differs")
            cell = (report["target_id"], report["python_version"])
            if cell in seen:
                raise ValueError("duplicate runtime consumer")
            seen.add(cell)
            previous = wheel_hashes.setdefault(target["id"], digest(artifact))
            if previous != digest(artifact):
                raise ValueError("runtimes tested different wheel bytes")
        elif form == "sdist":
            if sdist_seen or report["target_id"] != "linux-x64":
                raise ValueError("duplicate or undeclared sdist rebuild")
            validate_sdist(artifact, expected_version=declarations["package_version"])
            sdist_seen = True
        else:
            raise ValueError("unexpected distribution format")
        artifacts[artifact.name] = {
            "filename": artifact.name,
            "sha256": digest(artifact),
        }
    if seen != expected or not sdist_seen or len(artifacts) != 7:
        raise ValueError(
            f"incomplete native matrix: missing={sorted(expected - seen)}, "
            f"sdist={sdist_seen}"
        )
    return {
        "schema_version": 1,
        "package": "pocketstation",
        "version": declarations["package_version"],
        "source_commit": expected_source,
        "matrix_sha256": matrix_digest(),
        "classification": "SAFE-TO-TEST",
        "runtime_cells": len(seen),
        "targets": sorted(wheel_hashes),
        "distributions": sorted(artifacts.values(), key=lambda item: item["filename"]),
        "consumer_reports": [
            {"path": str(p.relative_to(directory)), "sha256": digest(p)}
            for p in reports
        ],
        "limits": declarations["limits"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command")
    selection = commands.add_parser("matrix")
    selection.add_argument("--kind", choices=("build", "test"), required=True)
    consumer = commands.add_parser("consume")
    consumer.add_argument("--target", required=True)
    consumer.add_argument("--format", choices=("wheel", "sdist"), default="wheel")
    consumer.add_argument("--artifact-dir", type=Path, required=True)
    consumer.add_argument("--output", type=Path, required=True)
    validation = commands.add_parser("verify")
    validation.add_argument("--directory", type=Path, required=True)
    validation.add_argument("--source-commit", required=True)
    validation.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "matrix":
        targets = matrix()["targets"]
        entries = (
            targets
            if args.kind == "build"
            else [
                {**target, "python": version}
                for target in targets
                for version in target["python_versions"]
            ]
        )
        print(json.dumps({"include": entries}, separators=(",", ":")))
    elif args.command == "consume":
        run_consumer(args)
    elif args.command == "verify":
        result = aggregate(args.directory, args.source_commit)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"PASS: {result['runtime_cells']} runtime cells, six wheels and sdist")
    else:
        declarations = matrix()
        print(f"PASS: {len(declarations['targets'])} declared native targets")


if __name__ == "__main__":
    main()
