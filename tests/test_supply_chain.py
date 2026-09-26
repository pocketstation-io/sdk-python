from __future__ import annotations

import json
import tomllib
from pathlib import Path

from packaging.licenses import canonicalize_license_expression

from build_backend import read_notices

ROOT = Path(__file__).resolve().parents[1]


def test_retained_notice_index_matches_shipped_text_and_valid_spdx() -> None:
    index = read_notices((ROOT / "THIRD_PARTY_NOTICES.md").read_bytes())
    assert index == json.loads((ROOT / "tools/dependency-notices.json").read_text())
    for component in index["components"]:
        canonicalize_license_expression(component["license_expression"])
        assert component["source_url"].startswith("https://")
        if component["ecosystem"] == "rpm":
            assert len(component["source_sha256"]) == 64


def test_notices_cover_complete_locked_source_build_dependencies() -> None:
    index = read_notices((ROOT / "THIRD_PARTY_NOTICES.md").read_bytes())
    covered = {
        (c["name"], c["version"])
        for c in index["components"]
        if c["ecosystem"] == "cargo"
    }
    lock = tomllib.loads((ROOT / "native/Cargo.lock").read_text())
    required = {
        (p["name"], p["version"])
        for p in lock["package"]
        if p["name"] != "pocketstation-python"
    }
    assert required <= covered, (
        f"Missing locked dependency notices: {required - covered}"
    )
