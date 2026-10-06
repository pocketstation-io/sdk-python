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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("processed_frames_total", 0),
        ("processed_frames_total", True),
        ("output_frames_total", 400),
        ("output_frames_total", True),
        ("tail_frames_total", 0),
        ("tail_frames_total", True),
        ("tail_padding_samples_total", 0),
        ("tail_padding_samples_total", True),
        ("input_provenance_preserved", False),
        ("polled_tail_preserved", False),
        ("echo_power_ratio", 1.0),
        ("echo_power_ratio", float("nan")),
        ("echo_power_ratio", False),
        ("voice_power_ratio", 0.0),
        ("voice_power_ratio", float("inf")),
        ("raw_stem_unchanged", False),
        ("terminal_state", "processing"),
    ],
)
def test_given_bad_aec_evidence_when_checked_then_rejected(
    field: str, value: object
) -> None:
    aec = {
        "processed_frames_total": 400,
        "output_frames_total": 404,
        "tail_frames_total": 4,
        "tail_padding_samples_total": 1920,
        "input_provenance_preserved": True,
        "polled_tail_preserved": True,
        "echo_power_ratio": 0.1,
        "voice_power_ratio": 0.9,
        "raw_stem_unchanged": True,
        "terminal_state": "stopped",
    }
    validator.validate_aec({"aec": aec})
    aec[field] = value
    with pytest.raises(ValueError, match="AEC processing evidence failed"):
        validator.validate_aec({"aec": aec})


def test_given_missing_aec_evidence_when_checked_then_rejected() -> None:
    with pytest.raises(ValueError, match="AEC evidence is missing"):
        validator.validate_aec({})


def test_given_lean_artifact_when_checked_then_explicit_unavailability_required() -> (
    None
):
    evidence = {"available": False, "unavailable_error_verified": True}
    validator.validate_aec({"aec": evidence}, expected_available=False)
    for key, value in (
        ("available", True),
        ("available", 0),
        ("unavailable_error_verified", False),
        ("unavailable_error_verified", 1),
    ):
        altered = dict(evidence, **{key: value})
        with pytest.raises(ValueError, match="availability evidence failed"):
            validator.validate_aec({"aec": altered}, expected_available=False)
    with pytest.raises(ValueError, match="availability evidence failed"):
        validator.validate_aec(
            {"aec": {**evidence, "processed_frames_total": 400}},
            expected_available=False,
        )
    with pytest.raises(ValueError, match="processing evidence failed"):
        validator.validate_aec({"aec": evidence}, expected_available=True)
