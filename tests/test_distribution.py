from __future__ import annotations

import base64
import csv
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

from tests.test_build_backend import notice_document

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.5"


def _load_validator() -> ModuleType:
    path = ROOT / "tools" / "validate_distribution.py"
    spec = importlib.util.spec_from_file_location("validate_distribution", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load distribution validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator()


def _load_freezer() -> ModuleType:
    tools = ROOT / "tools"
    sys.path.insert(0, str(tools))
    try:
        path = tools / "freeze_release_manifest.py"
        spec = importlib.util.spec_from_file_location("freeze_release_manifest", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load release freezer")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(tools))


FREEZER = _load_freezer()


def _metadata() -> bytes:
    return (
        "Metadata-Version: 2.4\n"
        "Name: pocketstation\n"
        f"Version: {VERSION}\n"
        "Summary: PocketStation test artifact\n"
        "Requires-Python: >=3.11\n"
        "License-Expression: MIT\n"
        "License-File: LICENSE\n"
        "License-File: NOTICE\n"
        "License-File: THIRD_PARTY_NOTICES.md\n"
        "\n"
    ).encode()


def _sbom() -> bytes:
    return json.dumps(
        {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "components": [
                {"name": "pocketstation", "version": "1.1.13"},
                {"name": "pocketstation-relay", "version": "0.1.5"},
            ],
        }
    ).encode()


def _package_init() -> bytes:
    return f'__version__ = "{VERSION}"\n'.encode()


def _compatibility() -> bytes:
    return (
        "RUNTIME_COMPATIBILITY = RuntimeCompatibility(\n"
        f'    sdk_version="{VERSION}",\n'
        '    core_version="1.1.13",\n'
        '    relay_connector_version="0.1.5",\n'
        '    python_requires=">=3.11",\n'
        '    python_abi="abi3-py311",\n'
        "    free_threaded_cpython=False,\n"
        ")\n"
    ).encode()


def _record(files: dict[str, bytes], record_name: str) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for name, data in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
        writer.writerow((name, f"sha256={digest.decode()}", str(len(data))))
    writer.writerow((record_name, "", ""))
    return output.getvalue().encode()


def _wheel(
    directory: Path,
    *,
    extra_files: dict[str, bytes] | None = None,
    omit: frozenset[str] = frozenset(),
) -> Path:
    dist_info = f"pocketstation-{VERSION}.dist-info"
    files = {
        "pocketstation/__init__.py": _package_init(),
        "pocketstation/_api.py": _package_init(),
        "pocketstation/compatibility.py": _compatibility(),
        "pocketstation/_native.abi3.so": b"native",
        "pocketstation/_native.pyi": b"def runtime_compatibility() -> str: ...\n",
        "pocketstation/py.typed": b"",
        f"{dist_info}/METADATA": _metadata(),
        f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\nGenerator: maturin (1.9.6)\n",
        f"{dist_info}/entry_points.txt": (
            b"[console_scripts]\npocketstation-demo=pocketstation_demo:main\n"
        ),
        f"{dist_info}/licenses/LICENSE": b"MIT License\npermission granted\n",
        f"{dist_info}/licenses/NOTICE": b"PocketStation contributors\n",
        f"{dist_info}/licenses/THIRD_PARTY_NOTICES.md": notice_document(),
        f"{dist_info}/sboms/pocketstation-python.cyclonedx.json": _sbom(),
    }
    files.update(extra_files or {})
    for name in omit:
        files.pop(name, None)
    record_name = f"{dist_info}/RECORD"
    files[record_name] = _record(files, record_name)
    wheel = directory / f"pocketstation-{VERSION}-cp311-abi3-macosx_11_0_arm64.whl"
    with zipfile.ZipFile(wheel, mode="w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return wheel


def _pyproject(*, version: str = VERSION) -> bytes:
    return (
        "[build-system]\n"
        'requires = ["maturin==1.13.0"]\n'
        'build-backend = "build_backend"\nbackend-path = ["."]\n\n'
        "[project]\n"
        'name = "pocketstation"\n'
        f'version = "{version}"\n'
        'requires-python = ">=3.11"\n'
        'license = "MIT"\n'
        'license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"]\n'
        '\n[project.scripts]\npocketstation-demo = "pocketstation_demo:main"\n'
        '\n[tool.maturin]\nmanifest-path = "native/Cargo.toml"\n'
    ).encode()


def _cargo_manifest(
    *, version: str = VERSION, core_dependency: str = 'version = "=1.1.13"'
) -> bytes:
    return (
        "[package]\n"
        'name = "pocketstation-python"\n'
        f'version = "{version}"\n'
        'license = "MIT"\n\n'
        "[dependencies]\n"
        f"pocketstation = {{ {core_dependency} }}\n"
        'pocketstation-relay = { version = "=0.1.5" }\n'
    ).encode()


def _cargo_lock(*, version: str = VERSION) -> bytes:
    return (
        "version = 4\n\n"
        "[[package]]\n"
        'name = "pocketstation"\n'
        'version = "1.1.13"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
        f'checksum = "{"a" * 64}"\n\n'
        "[[package]]\n"
        'name = "pocketstation-relay"\n'
        'version = "0.1.5"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
        f'checksum = "{"b" * 64}"\n\n'
        "[[package]]\n"
        'name = "pocketstation-python"\n'
        f'version = "{version}"\n'
    ).encode()


def _uv_lock(*, local_dependency: bool = False) -> bytes:
    dependency_source = (
        'source = { path = "../httpx" }'
        if local_dependency
        else 'source = { registry = "https://pypi.org/simple" }'
    )
    return (
        'version = 1\nrevision = 3\nrequires-python = ">=3.11"\n\n'
        "[[package]]\n"
        'name = "httpx"\n'
        'version = "0.28.1"\n'
        f"{dependency_source}\n\n"
        "[[package]]\n"
        'name = "pocketstation"\n'
        f'version = "{VERSION}"\n'
        'source = { editable = "." }\n'
    ).encode()


def _sdist(
    directory: Path,
    *,
    extra_files: dict[str, bytes] | None = None,
    omit: frozenset[str] = frozenset(),
    cargo_manifest: bytes | None = None,
    pyproject: bytes | None = None,
) -> Path:
    root = f"pocketstation-{VERSION}"
    files = {
        "PKG-INFO": _metadata(),
        "LICENSE": b"MIT License\npermission granted\n",
        "NOTICE": b"PocketStation contributors\n",
        "THIRD_PARTY_NOTICES.md": notice_document(),
        "build_backend.py": (ROOT / "build_backend.py").read_bytes(),
        "pyproject.toml": pyproject or _pyproject(),
        "native/Cargo.toml": cargo_manifest or _cargo_manifest(),
        "native/Cargo.lock": _cargo_lock(),
        "uv.lock": _uv_lock(),
        "native/src/lib.rs": b"",
        "python/pocketstation/__init__.py": _package_init(),
        "python/pocketstation/_api.py": _package_init(),
        "python/pocketstation/compatibility.py": _compatibility(),
        "python/pocketstation/_native.pyi": b"",
        "python/pocketstation/py.typed": b"",
    }
    files.update(extra_files or {})
    for name in omit:
        files.pop(name, None)
    sdist = directory / f"{root}.tar.gz"
    with tarfile.open(sdist, mode="w:gz") as archive:
        for name, data in files.items():
            info = tarfile.TarInfo(f"{root}/{name}")
            info.size = len(data)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))
    return sdist


def test_given_complete_archives_when_validated_then_all_distribution_checks_pass(
    tmp_path: Path,
) -> None:
    wheel = _wheel(tmp_path)
    sdist = _sdist(tmp_path)

    wheel_report = VALIDATOR.validate_wheel(wheel, expected_version=VERSION)
    sdist_report = VALIDATOR.validate_sdist(sdist, expected_version=VERSION)

    assert wheel_report.filename == wheel.name
    assert wheel_report.members_total == 14
    assert sdist_report.filename == sdist.name
    assert sdist_report.members_total == 15


@pytest.mark.parametrize(
    "missing",
    (
        "pocketstation/py.typed",
        "pocketstation/_native.pyi",
        f"pocketstation-{VERSION}.dist-info/licenses/NOTICE",
    ),
)
def test_given_required_wheel_member_missing_when_validated_then_candidate_is_rejected(
    tmp_path: Path, missing: str
) -> None:
    wheel = _wheel(tmp_path, omit=frozenset({missing}))

    with pytest.raises(VALIDATOR.DistributionValidationError):
        VALIDATOR.validate_wheel(wheel, expected_version=VERSION)


def test_given_second_native_extension_when_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    wheel = _wheel(
        tmp_path,
        extra_files={"pocketstation/_native.second.so": b"duplicate"},
    )

    with pytest.raises(
        VALIDATOR.DistributionValidationError, match="exactly one native extension"
    ):
        VALIDATOR.validate_wheel(wheel, expected_version=VERSION)


def test_given_tampered_wheel_member_when_record_checked_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    wheel = _wheel(tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    files["pocketstation/py.typed"] = b"tampered"
    with zipfile.ZipFile(wheel, mode="w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)

    with pytest.raises(VALIDATOR.DistributionValidationError, match="RECORD"):
        VALIDATOR.validate_wheel(wheel, expected_version=VERSION)


def test_given_duplicate_record_row_when_wheel_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    wheel = _wheel(tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    record = f"pocketstation-{VERSION}.dist-info/RECORD"
    files[record] += files[record].splitlines(keepends=True)[0]
    with zipfile.ZipFile(wheel, mode="w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)

    with pytest.raises(VALIDATOR.DistributionValidationError, match="duplicate rows"):
        VALIDATOR.validate_wheel(wheel, expected_version=VERSION)


def test_given_cargo_path_dependency_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(
        tmp_path,
        cargo_manifest=_cargo_manifest(core_dependency='path = "../../pocketstation"'),
    )

    with pytest.raises(VALIDATOR.DistributionValidationError, match="local or Git"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_cargo_git_dependency_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(
        tmp_path,
        cargo_manifest=_cargo_manifest(
            core_dependency='git = "https://example.invalid/pocketstation"'
        ),
    )

    with pytest.raises(VALIDATOR.DistributionValidationError, match="local or Git"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_python_checkout_override_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    pyproject = _pyproject() + (
        b'\n[tool.uv.sources]\npocketstation = { path = "../pocketstation" }\n'
    )
    sdist = _sdist(tmp_path, pyproject=pyproject)

    with pytest.raises(VALIDATOR.DistributionValidationError, match="checkout"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_build_requirement_url_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    pyproject = _pyproject().replace(
        b'requires = ["maturin==1.13.0"]',
        b'requires = ["maturin @ file:///tmp/maturin"]',
    )
    sdist = _sdist(tmp_path, pyproject=pyproject)

    with pytest.raises(VALIDATOR.DistributionValidationError, match="path, or URL"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_absolute_native_manifest_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    pyproject = _pyproject().replace(
        b'manifest-path = "native/Cargo.toml"',
        b'manifest-path = "/tmp/pocketstation/Cargo.toml"',
    )
    sdist = _sdist(tmp_path, pyproject=pyproject)

    with pytest.raises(VALIDATOR.DistributionValidationError, match="manifest-path"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_uv_path_dependency_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(
        tmp_path,
        extra_files={"uv.lock": _uv_lock(local_dependency=True)},
    )

    with pytest.raises(VALIDATOR.DistributionValidationError, match="checkout, path"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_missing_cargo_lock_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(tmp_path, omit=frozenset({"native/Cargo.lock"}))

    with pytest.raises(VALIDATOR.DistributionValidationError, match="required files"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_missing_uv_lock_when_sdist_validated_then_candidate_is_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(tmp_path, omit=frozenset({"uv.lock"}))

    with pytest.raises(VALIDATOR.DistributionValidationError, match="required files"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


@pytest.mark.parametrize(
    "build_output",
    (
        "native/target/release/lib_native.dylib",
        "python/pocketstation/__pycache__/__init__.pyc",
        "dist/stale.whl",
    ),
)
def test_given_build_output_in_sdist_when_validated_then_candidate_is_rejected(
    tmp_path: Path, build_output: str
) -> None:
    sdist = _sdist(tmp_path, extra_files={build_output: b"stale"})

    with pytest.raises(VALIDATOR.DistributionValidationError, match="build output"):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_manifest_versions_disagree_when_sdist_validated_then_rejected(
    tmp_path: Path,
) -> None:
    sdist = _sdist(tmp_path, pyproject=_pyproject(version="0.1.6"))

    with pytest.raises(
        VALIDATOR.DistributionValidationError, match="same package version"
    ):
        VALIDATOR.validate_sdist(sdist, expected_version=VERSION)


def test_given_consumer_noise_before_json_when_parsed_then_final_result_is_bound() -> (
    None
):
    result = FREEZER._parse_consumer_json(
        "pip output\n"
        '{"artifact_format":"wheel","install":{"record_verified":true},'
        '"consumer":{},"qualification":{},"uninstall_verified":true,'
        '"checks":{"pip_check":true,"record_integrity_check":true,'
        '"runtime_check":true,"typing_check":true,"uninstall_check":true},'
        '"tools":{"mypy_requirement":"mypy==2.3.1",'
        '"mypy_version":"2.3.1"},'
        '"installed_dependencies":["mypy==2.3.1"]}\n',
        "wheel",
    )

    assert result["artifact_format"] == "wheel"


def test_given_undeclared_release_output_when_checked_then_freeze_fails_closed(
    tmp_path: Path,
) -> None:
    (tmp_path / "candidate.whl").touch()
    (tmp_path / "unexpected.tmp").touch()

    with pytest.raises(RuntimeError, match="membership mismatch"):
        FREEZER._require_exact_outputs(tmp_path, {"candidate.whl"})


def test_given_insufficient_disk_when_preflight_runs_then_freeze_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    usage = shutil.disk_usage(tmp_path)
    monkeypatch.setattr(
        FREEZER.shutil,
        "disk_usage",
        lambda _path: usage._replace(free=FREEZER.MINIMUM_FREE_BYTES - 1),
    )

    with pytest.raises(RuntimeError, match="requires at least"):
        FREEZER._require_disk_headroom(tmp_path)


def test_given_frozen_wheel_when_consumed_then_log_and_result_are_retained(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact = tmp_path / f"pocketstation-{VERSION}-cp311-abi3-test.whl"
    artifact.touch()
    result = {
        "artifact": artifact.name,
        "artifact_format": "wheel",
        "checks": {
            "pip_check": True,
            "record_integrity_check": True,
            "runtime_check": True,
            "typing_check": True,
            "uninstall_check": True,
        },
        "consumer": {"runtime": "passed"},
        "install": {
            "record_verified": True,
            "version": VERSION,
        },
        "installed_dependencies": ["mypy==2.3.1"],
        "qualification": {"bounded": True},
        "tools": {
            "mypy_requirement": "mypy==2.3.1",
            "mypy_version": "2.3.1",
        },
        "uninstall_verified": True,
    }

    def run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="pip output\n" + json.dumps(result) + "\n",
            stderr="",
        )

    monkeypatch.setattr(FREEZER.subprocess, "run", run)

    retained = FREEZER._run_consumer(
        tmp_path,
        distribution_format="wheel",
        artifact=artifact,
        expected_version=VERSION,
    )

    assert retained["result"] == result
    assert (tmp_path / "consumer-wheel.log").is_file()
    assert (tmp_path / "consumer-wheel.json").is_file()


def test_given_failed_freeze_when_unwinding_then_diagnostics_survive(
    tmp_path: Path,
) -> None:
    with pytest.raises(RuntimeError, match="consumer failed"):
        with FREEZER._build_directory(tmp_path / "release") as directory:
            (directory / "consumer.log").write_text("runtime failure")
            raise RuntimeError("consumer failed")

    assert (directory / "consumer.log").read_text() == "runtime failure"
    assert not (tmp_path / "release").exists()


def test_given_successful_freeze_when_finished_then_temporary_build_is_removed(
    tmp_path: Path,
) -> None:
    with FREEZER._build_directory(tmp_path / "release") as directory:
        (directory / "build.log").write_text("success")

    assert not directory.exists()
