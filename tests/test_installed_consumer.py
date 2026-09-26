from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.run_artifact_consumer import (
    _artifact,
    _installed_dependencies,
    _isolated_environment,
    _run,
    _validate_installed_record,
    _verify_uninstalled,
)


@pytest.mark.parametrize("wrong_origin", [False, True])
def test_given_local_install_origin_when_inventory_recorded_then_input_must_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, wrong_origin: bool
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5.whl"
    origin = tmp_path / "sibling.whl" if wrong_origin else artifact
    output = f"mypy==2.3.1\npocketstation @ {origin.as_uri()}#sha256=abc\n"
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, stdout=output),
    )
    arguments = {
        "cwd": tmp_path,
        "environment": {},
        "install_target": artifact,
        "expected_version": "0.1.5",
    }
    if wrong_origin:
        with pytest.raises(SystemExit, match="origin differs"):
            _installed_dependencies(Path(sys.executable), **arguments)
    else:
        assert _installed_dependencies(Path(sys.executable), **arguments) == [
            "mypy==2.3.1",
            "pocketstation==0.1.5",
        ]


def _digest(payload: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=")
    return f"sha256={encoded.decode('ascii')}"


def _record_report(tmp_path: Path, records: tuple[str, ...]) -> dict[str, object]:
    absolute_paths: list[str] = []
    rows: list[list[str]] = []
    for record in records:
        path = tmp_path / record
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = b"" if record.endswith(".dist-info/RECORD") else record.encode()
        path.write_bytes(payload)
        absolute_paths.append(os.fspath(path))
        rows.append(
            [
                record,
                "" if record.endswith(".dist-info/RECORD") else _digest(payload),
                "" if record.endswith(".dist-info/RECORD") else str(len(payload)),
            ]
        )
    return {
        "records": list(records),
        "record_rows": rows,
        "absolute_paths": absolute_paths,
        "environment": os.fspath(tmp_path),
    }


def test_given_one_wheel_when_selected_then_exact_artifact_is_returned(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5-py3-none-any.whl"
    artifact.touch()

    assert _artifact(tmp_path, "wheel") == artifact.resolve()


def test_given_ambiguous_wheels_when_selected_then_consumer_fails_closed(
    tmp_path: Path,
) -> None:
    (tmp_path / "pocketstation-0.1.5-py3-none-any.whl").touch()
    (tmp_path / "pocketstation-0.1.6-py3-none-any.whl").touch()

    with pytest.raises(SystemExit, match="expected one PocketStation wheel"):
        _artifact(tmp_path, "wheel")


def test_given_checkout_environment_when_sanitized_then_python_overrides_are_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for variable in (
        "MYPYPATH",
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "VIRTUAL_ENV",
    ):
        monkeypatch.setenv(variable, f"checkout-{variable.lower()}")

    environment = _isolated_environment()

    for variable in (
        "MYPYPATH",
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "VIRTUAL_ENV",
    ):
        assert variable not in environment
    assert environment["PYTHONNOUSERSITE"] == "1"
    assert environment["PYTHONDONTWRITEBYTECODE"] == "1"


def test_given_isolated_python_when_run_then_checkout_is_not_on_sys_path(
    tmp_path: Path,
) -> None:
    script = tmp_path / "show_path.py"
    script.write_text("import json, sys\nprint(json.dumps(sys.path))\n")

    result = _run(
        (sys.executable, "-I", script),
        cwd=tmp_path,
        environment=_isolated_environment(),
        timeout_seconds=30,
        capture_output=True,
    )

    paths = tuple(Path(path).resolve() for path in json.loads(result.stdout) if path)
    repository = Path(__file__).resolve().parents[1]
    assert repository not in paths


def test_given_complete_record_when_validated_then_native_and_typing_files_are_owned(
    tmp_path: Path,
) -> None:
    records = (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        "pocketstation/_native.abi3.so",
        "pocketstation-0.1.5.dist-info/METADATA",
        "pocketstation-0.1.5.dist-info/RECORD",
        "pocketstation-0.1.5.dist-info/licenses/LICENSE",
        "pocketstation-0.1.5.dist-info/licenses/NOTICE",
        "pocketstation-0.1.5.dist-info/sboms/pocketstation-python.cyclonedx.json",
    )
    assert len(_validate_installed_record(_record_report(tmp_path, records))) == len(
        records
    )


def test_given_duplicate_native_modules_when_validated_then_record_is_rejected(
    tmp_path: Path,
) -> None:
    records = (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        "pocketstation/_native.abi3.so",
        "pocketstation/_native.other.so",
        "pocketstation-0.1.5.dist-info/METADATA",
        "pocketstation-0.1.5.dist-info/RECORD",
        "pocketstation-0.1.5.dist-info/licenses/LICENSE",
        "pocketstation-0.1.5.dist-info/licenses/NOTICE",
        "pocketstation-0.1.5.dist-info/sboms/pocketstation-python.cyclonedx.json",
    )
    with pytest.raises(SystemExit, match=r"exactly one pocketstation\._native"):
        _validate_installed_record(_record_report(tmp_path, records))


@pytest.mark.parametrize("field", ("digest", "size"))
def test_given_tampered_installed_file_when_record_validated_then_rejected(
    tmp_path: Path, field: str
) -> None:
    records = (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        "pocketstation/_native.abi3.so",
        "pocketstation-0.1.5.dist-info/METADATA",
        "pocketstation-0.1.5.dist-info/RECORD",
        "pocketstation-0.1.5.dist-info/licenses/LICENSE",
        "pocketstation-0.1.5.dist-info/licenses/NOTICE",
        "pocketstation-0.1.5.dist-info/sboms/pocketstation-python.cyclonedx.json",
    )
    report = _record_report(tmp_path, records)
    rows = report["record_rows"]
    assert isinstance(rows, list)
    row = rows[0]
    assert isinstance(row, list)
    row[1 if field == "digest" else 2] = "sha256=wrong" if field == "digest" else "9"

    with pytest.raises(SystemExit, match=f"RECORD {field} does not match"):
        _validate_installed_record(report)


def test_given_duplicate_installed_record_row_when_validated_then_rejected(
    tmp_path: Path,
) -> None:
    records = (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        "pocketstation/_native.abi3.so",
        "pocketstation-0.1.5.dist-info/METADATA",
        "pocketstation-0.1.5.dist-info/RECORD",
        "pocketstation-0.1.5.dist-info/licenses/LICENSE",
        "pocketstation-0.1.5.dist-info/licenses/NOTICE",
        "pocketstation-0.1.5.dist-info/sboms/pocketstation-python.cyclonedx.json",
    )
    report = _record_report(tmp_path, records)
    report["records"] = [*report["records"], records[0]]
    report["absolute_paths"] = [
        *report["absolute_paths"],
        report["absolute_paths"][0],
    ]
    report["record_rows"] = [*report["record_rows"], report["record_rows"][0]]

    with pytest.raises(SystemExit, match="duplicate paths"):
        _validate_installed_record(report)


def test_given_owned_package_left_after_uninstall_when_verified_then_cleanup_fails(
    tmp_path: Path,
) -> None:
    package = tmp_path / "site-packages" / "pocketstation"
    package.mkdir(parents=True)
    report = {
        "package": os.fspath(package),
        "dist_info": os.fspath(tmp_path / "site-packages" / "metadata.dist-info"),
        "records": [],
        "absolute_paths": [],
    }

    with pytest.raises(SystemExit, match="left PocketStation-owned paths"):
        _verify_uninstalled(
            Path(sys.executable),
            demo=tmp_path / "bin" / "pocketstation-demo",
            install_report=report,
            cwd=tmp_path,
            environment=_isolated_environment(),
        )


def test_given_record_owned_script_left_after_uninstall_when_verified_then_fails(
    tmp_path: Path,
) -> None:
    script = tmp_path / "bin" / "pocketstation-extra"
    script.parent.mkdir(parents=True)
    script.write_text("left behind")
    report = {
        "package": os.fspath(tmp_path / "site-packages" / "pocketstation"),
        "dist_info": os.fspath(tmp_path / "site-packages" / "metadata.dist-info"),
        "records": ["../../../bin/pocketstation-extra"],
        "absolute_paths": [os.fspath(script)],
    }

    with pytest.raises(SystemExit, match="left PocketStation-owned paths"):
        _verify_uninstalled(
            Path(sys.executable),
            demo=tmp_path / "bin" / "pocketstation-demo",
            install_report=report,
            cwd=tmp_path,
            environment=_isolated_environment(),
        )
