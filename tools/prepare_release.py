#!/usr/bin/env python3
"""Select only exact distributions from a successful native qualification."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

from validate_wheel_matrix import aggregate, digest, matrix

REPOSITORY = "pocketstation-io/sdk-python"
WORKFLOW = ".github/workflows/qualify-distribution.yml"


def validate_run(run: dict[str, Any], source: str, release_tag: str) -> None:
    if release_tag != "pocketstation-v" + matrix()[
        "package_version"
    ] or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ValueError("release tag or source commit differs")
    if (
        run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or run.get("head_sha") != source
        or run.get("path") != WORKFLOW
        or run.get("event") not in ("push", "workflow_dispatch")
        or run.get("head_repository", {}).get("full_name") != REPOSITORY
        or run.get("repository", {}).get("full_name") != REPOSITORY
        or type(run.get("id")) is not int
        or run["id"] <= 0
    ):
        raise ValueError("qualification is not a successful same-source repository run")


def prepare(
    qualified: Path, run: dict[str, Any], source: str, tag: str, output: Path
) -> dict[str, Any]:
    validate_run(run, source, tag)
    retained = json.loads((qualified / "release-manifest.json").read_text())
    verified = aggregate(qualified, source)
    if retained != verified:
        raise ValueError("retained manifest differs from independent verification")
    distributions = list(qualified.rglob("*.whl")) + list(qualified.rglob("*.tar.gz"))
    expected = {item["filename"]: item["sha256"] for item in verified["distributions"]}
    if len(distributions) != 7 or {p.name for p in distributions} != set(expected):
        raise ValueError("qualification contains unexpected distribution files")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("release output must be a new or empty directory")
    for path in distributions:
        if path.is_symlink() or digest(path) != expected[path.name]:
            raise ValueError("qualified distribution changed or is a symlink")
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(distributions):
        destination = output / path.name
        shutil.copyfile(path, destination)
        if digest(destination) != expected[path.name]:
            raise ValueError("copied release distribution differs")
    return {
        "schema_version": 1,
        "repository": REPOSITORY,
        "version": verified["version"],
        "tag": tag,
        "source_commit": source,
        "qualification_run_id": run["id"],
        "qualification_workflow": WORKFLOW,
        "qualification_manifest_sha256": digest(qualified / "release-manifest.json"),
        "runtime_cells": verified["runtime_cells"],
        "distributions": verified["distributions"],
        "rebuilt_during_publication": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualified", required=True, type=Path)
    parser.add_argument("--run-info", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    result = prepare(
        args.qualified,
        json.loads(args.run_info.read_text()),
        args.source_commit,
        args.tag,
        args.output,
    )
    args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS: seven qualified distributions copied without rebuilding")


if __name__ == "__main__":
    main()
