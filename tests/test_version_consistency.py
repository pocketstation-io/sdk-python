from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_validator() -> ModuleType:
    path = ROOT / "tools" / "validate_distribution.py"
    spec = importlib.util.spec_from_file_location(
        "distribution_version_validator", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load distribution validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator()


def test_given_release_checkout_when_versions_validated_then_all_inputs_agree() -> None:
    assert VALIDATOR.validate_source_versions(ROOT) == "0.1.6"


def test_given_checkout_without_uv_lock_when_versions_validated_then_check_fails(
    tmp_path: Path,
) -> None:
    for relative in (
        "pyproject.toml",
        "native/Cargo.toml",
        "native/Cargo.lock",
        "LICENSE",
        "NOTICE",
        "python/pocketstation/__init__.py",
        "python/pocketstation/_api.py",
        "python/pocketstation/compatibility.py",
    ):
        source = ROOT / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    with pytest.raises(VALIDATOR.DistributionValidationError, match=r"uv\.lock"):
        VALIDATOR.validate_source_versions(tmp_path)
