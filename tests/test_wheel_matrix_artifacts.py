from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
try:
    spec = importlib.util.spec_from_file_location(
        "wheel_matrix_validator", TOOLS / "validate_wheel_matrix.py"
    )
    assert spec is not None and spec.loader is not None
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
finally:
    sys.path.remove(str(TOOLS))


def _identity() -> dict[str, object]:
    return {
        "target_id": "windows-arm64",
        "source_commit": "a" * 40,
        "matrix_sha256": validator.matrix_digest(),
        "system": "Windows",
        "machine": "ARM64",
        "python_version": "3.13",
        "implementation": "CPython",
        "exit_code": 0,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("machine", "AMD64"),
        ("system", "Linux"),
        ("python_version", "3.11"),
        ("source_commit", "b" * 40),
        ("matrix_sha256", "0" * 64),
        ("implementation", "PyPy"),
        ("exit_code", 1),
    ],
)
def test_given_mislabeled_native_consumer_when_checked_then_rejected(
    field: str, value: object
) -> None:
    report = _identity()
    validator.validate_identity(report, "a" * 40)
    report[field] = value
    with pytest.raises(ValueError):
        validator.validate_identity(report, "a" * 40)


def test_given_no_consumer_evidence_when_aggregated_then_matrix_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="incomplete native matrix"):
        validator.aggregate(tmp_path, "a" * 40)


def test_given_six_targets_when_declared_then_runtime_availability_is_explicit() -> (
    None
):
    declarations = validator.matrix()
    assert sum(len(t["python_versions"]) for t in declarations["targets"]) == 22
    assert validator.target_named("windows-arm64")["python_versions"] == [
        "3.13",
        "3.14",
    ]


@pytest.mark.parametrize("check", ["typing_check", "runtime_check", "uninstall_check"])
def test_given_missing_installed_gate_when_checked_then_rejected(check: str) -> None:
    result = {
        "checks": dict.fromkeys(
            [
                "pip_check",
                "record_integrity_check",
                "runtime_check",
                "typing_check",
                "uninstall_check",
            ],
            True,
        )
    }
    broken = copy.deepcopy(result)
    broken["checks"][check] = False
    with pytest.raises(ValueError, match="installed checks are incomplete"):
        validator.validate_result(broken, "wheel")
