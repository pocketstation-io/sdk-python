from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
try:
    spec = importlib.util.spec_from_file_location(
        "release_preparation", TOOLS / "prepare_release.py"
    )
    assert spec is not None and spec.loader is not None
    release = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release)
finally:
    sys.path.remove(str(TOOLS))

SOURCE = "a" * 40
TAG = "pocketstation-v0.1.5"


def run_info() -> dict[str, object]:
    return {
        "id": 123,
        "status": "completed",
        "conclusion": "success",
        "head_sha": SOURCE,
        "path": release.WORKFLOW,
        "event": "push",
        "head_repository": {"full_name": release.REPOSITORY},
        "repository": {"full_name": release.REPOSITORY},
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", True),
        ("id", 0),
        ("status", "in_progress"),
        ("conclusion", "failure"),
        ("head_sha", "b" * 40),
        ("path", ".github/workflows/another.yml"),
        ("event", "pull_request"),
        ("head_repository", {"full_name": "fork/sdk-python"}),
        ("repository", {"full_name": "fork/sdk-python"}),
    ],
)
def test_wrong_qualification_origin_or_result_cannot_publish(
    field: str, value: object
) -> None:
    valid = run_info()
    release.validate_run(valid, SOURCE, TAG)
    valid[field] = value
    with pytest.raises(ValueError, match="successful same-source"):
        release.validate_run(valid, SOURCE, TAG)


def test_release_tag_must_match_the_qualified_package_version() -> None:
    with pytest.raises(ValueError, match="tag or source"):
        release.validate_run(run_info(), SOURCE, "pocketstation-v0.1.4")


@pytest.mark.parametrize("corruption", [None, "extra-file", "changed-file", "manifest"])
def test_preparation_copies_only_verified_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str | None
) -> None:
    qualified = tmp_path / "qualified"
    qualified.mkdir()
    files = [qualified / f"synthetic-{i}.whl" for i in range(6)]
    files.append(qualified / "synthetic.tar.gz")
    for path in files:
        path.write_bytes(b"synthetic copier unit-test input")
    manifest = {
        "version": "0.1.5",
        "runtime_cells": 22,
        "distributions": [
            {"filename": p.name, "sha256": release.digest(p)} for p in files
        ],
    }
    (qualified / "release-manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(release, "aggregate", lambda *_: copy.deepcopy(manifest))
    if corruption == "extra-file":
        (qualified / "unexpected.whl").write_bytes(b"unexpected")
    elif corruption == "changed-file":
        files[0].write_bytes(b"changed")
    elif corruption == "manifest":
        (qualified / "release-manifest.json").write_text("{}")
    output = tmp_path / "dist"
    if corruption:
        with pytest.raises(ValueError):
            release.prepare(qualified, run_info(), SOURCE, TAG, output)
        assert not output.exists()
    else:
        receipt = release.prepare(qualified, run_info(), SOURCE, TAG, output)
        assert receipt["rebuilt_during_publication"] is False
        assert sorted(p.name for p in output.iterdir()) == sorted(p.name for p in files)
        for path in files:
            assert (output / path.name).read_bytes() == path.read_bytes()
