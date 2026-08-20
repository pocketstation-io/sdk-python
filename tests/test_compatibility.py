"""Installed SDK compatibility metadata must match its build inputs."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pocketstation

REPOSITORY = Path(__file__).resolve().parents[1]


def test_runtime_compatibility_matches_python_and_native_manifests() -> None:
    project = tomllib.loads((REPOSITORY / "pyproject.toml").read_text())
    native = tomllib.loads((REPOSITORY / "native" / "Cargo.toml").read_text())
    compatibility = pocketstation.RUNTIME_COMPATIBILITY

    assert compatibility.sdk_version == project["project"]["version"]
    assert compatibility.core_version == native["dependencies"]["pocketstation"].lstrip(
        "="
    )
    assert compatibility.relay_connector_version == native["dependencies"][
        "pocketstation-relay"
    ].lstrip("=")
    assert compatibility.python_requires == project["project"]["requires-python"]
    assert compatibility.python_abi == "abi3-py311"
    assert not compatibility.free_threaded_cpython
    assert pocketstation.__version__ == compatibility.sdk_version
