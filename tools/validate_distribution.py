#!/usr/bin/env python3
"""Validate one PocketStation wheel and source distribution."""

from __future__ import annotations

import argparse
import ast
import base64
import configparser
import csv
import hashlib
import importlib.util
import io
import json
import tarfile
import tomllib
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from email.message import Message
from email.parser import BytesParser
from email.policy import compat32
from pathlib import Path, PurePosixPath
from typing import Any

_backend_spec = importlib.util.spec_from_file_location(
    "pocketstation_build_backend",
    Path(__file__).resolve().parents[1] / "build_backend.py",
)
assert _backend_spec is not None and _backend_spec.loader is not None
BUILD_BACKEND = importlib.util.module_from_spec(_backend_spec)
_backend_spec.loader.exec_module(BUILD_BACKEND)

PROJECT_NAME = "pocketstation"
NATIVE_PACKAGE_NAME = "pocketstation-python"
CORE_NAME = "pocketstation"
CORE_VERSION = "1.1.13"
RELAY_NAME = "pocketstation-relay"
RELAY_VERSION = "0.1.5"
CONSOLE_COMMAND = "pocketstation-demo"
CONSOLE_TARGET = "pocketstation_demo:main"
NATIVE_SUFFIXES = (".so", ".pyd", ".dll", ".dylib")
FORBIDDEN_COMPONENTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "target",
    "venv",
}


class DistributionValidationError(ValueError):
    """The candidate archive is not a self-contained release artifact."""


@dataclass(frozen=True)
class ArtifactReport:
    filename: str
    sha256: str
    size_bytes: int
    members_total: int


@dataclass(frozen=True)
class DistributionReport:
    project_name: str
    project_version: str
    core_version: str
    relay_connector_version: str
    wheel: ArtifactReport
    sdist: ArtifactReport
    checks: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fail(message: str) -> None:
    raise DistributionValidationError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_report(path: Path, members_total: int) -> ArtifactReport:
    return ArtifactReport(
        filename=path.name,
        sha256=_sha256(path),
        size_bytes=path.stat().st_size,
        members_total=members_total,
    )


def _validated_member_names(names: Iterable[str], *, archive: str) -> tuple[str, ...]:
    normalized: list[str] = []
    for raw_name in names:
        path = PurePosixPath(raw_name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            _fail(f"{archive} contains unsafe member {raw_name!r}")
        name = path.as_posix().removeprefix("./")
        if not name or name in normalized:
            _fail(f"{archive} contains a duplicate or empty member {raw_name!r}")
        normalized.append(name)
    return tuple(normalized)


def _relative_sdist_name(name: str, root: str) -> str:
    prefix = f"{root}/"
    if name == root:
        return ""
    if not name.startswith(prefix):
        _fail(f"source distribution member escapes root {root!r}: {name!r}")
    return name[len(prefix) :]


def _reject_build_outputs(names: Iterable[str], *, archive: str) -> None:
    for name in names:
        path = PurePosixPath(name)
        if FORBIDDEN_COMPONENTS.intersection(path.parts):
            _fail(f"{archive} contains checkout or build output {name!r}")
        if path.suffix in {".pyc", ".pyo"}:
            _fail(f"{archive} contains compiled Python output {name!r}")


def _one_member(names: Iterable[str], suffix: str, *, archive: str) -> str:
    matches = tuple(name for name in names if name.endswith(suffix))
    if len(matches) != 1:
        _fail(f"{archive} must contain exactly one {suffix}, found {len(matches)}")
    return matches[0]


def _metadata(data: bytes, *, archive: str) -> Message:
    return BytesParser(policy=compat32).parsebytes(data)


def _required_metadata(
    metadata: Message, *, version: str, archive: str, license_expression: str = "MIT"
) -> None:
    expected = {
        "Name": PROJECT_NAME,
        "Version": version,
        "Requires-Python": ">=3.11",
        "License-Expression": license_expression,
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            _fail(
                f"{archive} metadata {field!r} must be {value!r}, "
                f"found {metadata.get(field)!r}"
            )


def _parse_toml(data: bytes, *, member: str) -> dict[str, Any]:
    try:
        return tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise DistributionValidationError(
            f"invalid TOML in {member}: {error}"
        ) from error


def _dependency_version(
    manifest: Mapping[str, Any], dependency: str, *, member: str
) -> str:
    raw = manifest.get("dependencies", {}).get(dependency)
    if isinstance(raw, str):
        return raw
    if not isinstance(raw, Mapping):
        _fail(f"{member} omits dependency {dependency!r}")
    if "path" in raw or "git" in raw:
        _fail(f"{member} uses a local or Git dependency for {dependency!r}")
    version = raw.get("version")
    if not isinstance(version, str):
        _fail(f"{member} does not pin {dependency!r} by version")
    return version


def _reject_non_registry_dependencies(
    document: Mapping[str, Any], *, member: str
) -> None:
    def visit(value: object, location: str) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                child_location = f"{location}.{key}" if location else str(key)
                if key in {"dependencies", "dev-dependencies", "build-dependencies"}:
                    if isinstance(child, Mapping):
                        for dependency, requirement in child.items():
                            if isinstance(requirement, Mapping) and (
                                "path" in requirement or "git" in requirement
                            ):
                                _fail(
                                    f"{member} uses a local or Git dependency for "
                                    f"{dependency!r} at {child_location}"
                                )
                visit(child, child_location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]")

    visit(document, "")


def _reject_python_path_dependencies(pyproject: Mapping[str, Any]) -> None:
    sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
    if sources:
        _fail("pyproject.toml contains tool.uv.sources checkout overrides")
    dependency_groups = [
        pyproject.get("build-system", {}).get("requires", ()),
        pyproject.get("project", {}).get("dependencies", ()),
    ]
    dependency_groups.extend(
        pyproject.get("project", {}).get("optional-dependencies", {}).values()
    )
    for dependency in (
        item for group in dependency_groups for item in group if isinstance(item, str)
    ):
        normalized = dependency.lower().replace(" ", "")
        if (
            "@" in normalized
            or "://" in normalized
            or "/" in normalized
            or "\\" in normalized
            or normalized.startswith(".")
        ):
            _fail(
                "pyproject.toml contains a checkout, path, or URL dependency "
                f"{dependency!r}"
            )


def _locked_package(
    lock: Mapping[str, Any], name: str, version: str, *, member: str
) -> None:
    matches = tuple(
        package
        for package in lock.get("package", ())
        if package.get("name") == name and package.get("version") == version
    )
    if len(matches) != 1:
        _fail(f"{member} must lock exactly one {name} {version}")
    package = matches[0]
    source = package.get("source")
    checksum = package.get("checksum")
    if not isinstance(source, str) or not source.startswith("registry+"):
        _fail(f"{member} resolves {name} {version} outside a registry")
    if not isinstance(checksum, str) or len(checksum) != 64:
        _fail(f"{member} has no registry checksum for {name} {version}")


def _validate_uv_lock(lock: Mapping[str, Any], *, version: str) -> None:
    packages = lock.get("package")
    if not isinstance(packages, list):
        _fail("uv.lock contains no package inventory")
    own = tuple(
        package
        for package in packages
        if package.get("name") == PROJECT_NAME and package.get("version") == version
    )
    if len(own) != 1 or own[0].get("source") != {"editable": "."}:
        _fail("uv.lock must contain exactly one local root PocketStation package")
    for package in packages:
        source = package.get("source")
        if package is own[0]:
            continue
        if not isinstance(source, Mapping) or set(source) != {"registry"}:
            _fail(
                "uv.lock contains a checkout, path, Git, or otherwise unlocked "
                f"dependency for {package.get('name')!r}"
            )
        registry = source.get("registry")
        if not isinstance(registry, str) or not registry.startswith("https://"):
            _fail(f"uv.lock contains an invalid registry for {package.get('name')!r}")


def _source_versions(
    pyproject: Mapping[str, Any],
    cargo_manifest: Mapping[str, Any],
    cargo_lock: Mapping[str, Any],
    uv_lock: Mapping[str, Any],
) -> str:
    project = pyproject.get("project", {})
    package = cargo_manifest.get("package", {})
    _reject_python_path_dependencies(pyproject)
    _reject_non_registry_dependencies(cargo_manifest, member="native/Cargo.toml")
    maturin = pyproject.get("tool", {}).get("maturin", {})
    if not isinstance(maturin, Mapping):
        _fail("pyproject.toml omits tool.maturin configuration")
    if maturin.get("manifest-path") != "native/Cargo.toml":
        _fail("tool.maturin.manifest-path must be exactly native/Cargo.toml")
    project_version = project.get("version")
    native_version = package.get("version")
    if not isinstance(project_version, str) or project_version != native_version:
        _fail(
            "pyproject.toml and native/Cargo.toml must declare the same package version"
        )
    if project.get("name") != PROJECT_NAME:
        _fail(f"pyproject.toml project name must be {PROJECT_NAME!r}")
    scripts = project.get("scripts")
    if (
        not isinstance(scripts, Mapping)
        or scripts.get(CONSOLE_COMMAND) != CONSOLE_TARGET
    ):
        _fail(f"pyproject.toml must install {CONSOLE_COMMAND}={CONSOLE_TARGET}")
    if project.get("license") != "MIT":
        _fail("pyproject.toml must declare the MIT license expression")
    license_files = project.get("license-files")
    if not isinstance(license_files, list) or set(license_files) != {
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
    }:
        _fail("pyproject.toml license-files must contain SDK and dependency notices")
    build_system = pyproject.get("build-system", {})
    if (
        build_system.get("build-backend") != "build_backend"
        or build_system.get("backend-path") != ["."]
        or build_system.get("requires") != ["maturin==1.13.0"]
    ):
        _fail("source build must use the self-contained license-aware Maturin wrapper")
    if package.get("name") != NATIVE_PACKAGE_NAME:
        _fail(f"native Cargo package name must be {NATIVE_PACKAGE_NAME!r}")
    if package.get("license") != "MIT":
        _fail("native Cargo package must declare MIT")
    core = _dependency_version(cargo_manifest, CORE_NAME, member="native/Cargo.toml")
    relay = _dependency_version(cargo_manifest, RELAY_NAME, member="native/Cargo.toml")
    if core != f"={CORE_VERSION}":
        _fail(f"native/Cargo.toml must pin {CORE_NAME} to ={CORE_VERSION}")
    if relay != f"={RELAY_VERSION}":
        _fail(f"native/Cargo.toml must pin {RELAY_NAME} to ={RELAY_VERSION}")
    _locked_package(cargo_lock, CORE_NAME, CORE_VERSION, member="native/Cargo.lock")
    _locked_package(cargo_lock, RELAY_NAME, RELAY_VERSION, member="native/Cargo.lock")
    own = tuple(
        item
        for item in cargo_lock.get("package", ())
        if item.get("name") == NATIVE_PACKAGE_NAME
    )
    if len(own) != 1 or own[0].get("version") != project_version:
        _fail("native/Cargo.lock package version does not match pyproject.toml")
    _validate_uv_lock(uv_lock, version=project_version)
    return project_version


def _assigned_string(data: bytes, name: str, *, member: str) -> str:
    try:
        tree = ast.parse(data.decode("utf-8"), filename=member)
    except (SyntaxError, UnicodeDecodeError) as error:
        raise DistributionValidationError(
            f"invalid Python in {member}: {error}"
        ) from error
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(
            isinstance(target, ast.Name) and target.id == name for target in targets
        ):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    _fail(f"{member} does not assign a literal string to {name}")


def _compatibility_versions(data: bytes, *, member: str) -> dict[str, str]:
    try:
        tree = ast.parse(data.decode("utf-8"), filename=member)
    except (SyntaxError, UnicodeDecodeError) as error:
        raise DistributionValidationError(
            f"invalid Python in {member}: {error}"
        ) from error
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "RUNTIME_COMPATIBILITY"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.Call):
            break
        values: dict[str, str] = {}
        for keyword in node.value.keywords:
            if (
                keyword.arg is not None
                and isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
            ):
                values[keyword.arg] = keyword.value.value
        return values
    _fail(f"{member} does not assign RUNTIME_COMPATIBILITY")


def _validate_python_versions(
    *,
    package_init: bytes,
    private_api: bytes,
    compatibility: bytes,
    version: str,
) -> None:
    if (
        _assigned_string(
            package_init, "__version__", member="pocketstation/__init__.py"
        )
        != version
    ):
        _fail("pocketstation.__version__ does not match package metadata")
    if (
        _assigned_string(private_api, "__version__", member="pocketstation/_api.py")
        != version
    ):
        _fail("pocketstation._api.__version__ does not match package metadata")
    values = _compatibility_versions(
        compatibility, member="pocketstation/compatibility.py"
    )
    expected = {
        "sdk_version": version,
        "core_version": CORE_VERSION,
        "relay_connector_version": RELAY_VERSION,
        "python_requires": ">=3.11",
        "python_abi": "abi3-py311",
    }
    if values != expected:
        _fail(f"RUNTIME_COMPATIBILITY does not match package inputs: {values!r}")


def validate_source_versions(repository: Path) -> str:
    repository = repository.resolve()
    required = (
        repository / "pyproject.toml",
        repository / "native" / "Cargo.toml",
        repository / "native" / "Cargo.lock",
        repository / "uv.lock",
        repository / "LICENSE",
        repository / "NOTICE",
        repository / "python" / "pocketstation" / "__init__.py",
        repository / "python" / "pocketstation" / "_api.py",
        repository / "python" / "pocketstation" / "compatibility.py",
    )
    missing = tuple(
        path.relative_to(repository).as_posix()
        for path in required
        if not path.is_file()
    )
    if missing:
        _fail(f"source checkout omits required files: {', '.join(missing)}")
    version = _source_versions(
        _parse_toml(required[0].read_bytes(), member="pyproject.toml"),
        _parse_toml(required[1].read_bytes(), member="native/Cargo.toml"),
        _parse_toml(required[2].read_bytes(), member="native/Cargo.lock"),
        _parse_toml(required[3].read_bytes(), member="uv.lock"),
    )
    _validate_python_versions(
        package_init=required[6].read_bytes(),
        private_api=required[7].read_bytes(),
        compatibility=required[8].read_bytes(),
        version=version,
    )
    return version


def _verify_record(
    archive: zipfile.ZipFile, names: tuple[str, ...], record: str
) -> None:
    rows = tuple(csv.reader(io.StringIO(archive.read(record).decode("utf-8"))))
    malformed = tuple(row for row in rows if len(row) != 3)
    if malformed:
        _fail("wheel RECORD contains malformed rows")
    record_names = tuple(row[0] for row in rows)
    if len(record_names) != len(set(record_names)):
        _fail("wheel RECORD contains duplicate rows")
    entries = {row[0]: row for row in rows if len(row) == 3}
    if set(entries) != set(names):
        missing = sorted(set(names) - set(entries))
        extra = sorted(set(entries) - set(names))
        _fail(f"wheel RECORD membership mismatch: missing={missing}, extra={extra}")
    for name in names:
        digest, size = entries[name][1:]
        if name == record:
            if digest or size:
                _fail("wheel RECORD row must not hash itself")
            continue
        if not digest.startswith("sha256=") or not size.isdecimal():
            _fail(f"wheel RECORD omits hash or size for {name!r}")
        expected = (
            base64.urlsafe_b64encode(hashlib.sha256(archive.read(name)).digest())
            .rstrip(b"=")
            .decode("ascii")
        )
        if digest != f"sha256={expected}" or int(size) != len(archive.read(name)):
            _fail(f"wheel RECORD does not match {name!r}")


def _sbom_versions(data: bytes) -> set[tuple[str, str]]:
    try:
        document = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DistributionValidationError(
            f"wheel contains invalid CycloneDX JSON: {error}"
        ) from error
    found: set[tuple[str, str]] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            name = value.get("name")
            version = value.get("version")
            if isinstance(name, str) and isinstance(version, str):
                found.add((name, version))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    return found


def validate_wheel(path: Path, *, expected_version: str) -> ArtifactReport:
    path = path.resolve()
    if not path.name.startswith(f"{PROJECT_NAME}-{expected_version}-"):
        _fail(f"wheel filename does not match {PROJECT_NAME} {expected_version}")
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as error:
        raise DistributionValidationError(
            f"cannot read wheel {path}: {error}"
        ) from error
    with archive:
        names = _validated_member_names(archive.namelist(), archive="wheel")
        _reject_build_outputs(names, archive="wheel")
        native = tuple(
            name
            for name in names
            if name.startswith("pocketstation/_native")
            and name.endswith(NATIVE_SUFFIXES)
        )
        if len(native) != 1:
            _fail(
                f"wheel must contain exactly one native extension, found {len(native)}"
            )
        required = {
            "pocketstation/__init__.py",
            "pocketstation/_api.py",
            "pocketstation/compatibility.py",
            "pocketstation/py.typed",
            "pocketstation/_native.pyi",
        }
        missing = sorted(required - set(names))
        if missing:
            _fail(f"wheel omits required typing files: {missing}")
        metadata_name = _one_member(names, ".dist-info/METADATA", archive="wheel")
        entry_points_name = _one_member(
            names, ".dist-info/entry_points.txt", archive="wheel"
        )
        record_name = _one_member(names, ".dist-info/RECORD", archive="wheel")
        license_name = _one_member(
            names, ".dist-info/licenses/LICENSE", archive="wheel"
        )
        notice_name = _one_member(names, ".dist-info/licenses/NOTICE", archive="wheel")
        sbom_name = _one_member(
            names,
            ".dist-info/sboms/pocketstation-python.cyclonedx.json",
            archive="wheel",
        )
        metadata = _metadata(archive.read(metadata_name), archive="wheel")
        license_inputs = {
            name: archive.read(name)
            for name in names
            if ".dist-info/sboms/" in name or name.endswith("/THIRD_PARTY_NOTICES.md")
        }
        try:
            expression = BUILD_BACKEND.wheel_license_expression(license_inputs)
        except (ValueError, KeyError, TypeError) as error:
            _fail(f"wheel dependency notices are invalid: {error}")
        _required_metadata(
            metadata,
            version=expected_version,
            archive="wheel",
            license_expression=expression,
        )
        _validate_python_versions(
            package_init=archive.read("pocketstation/__init__.py"),
            private_api=archive.read("pocketstation/_api.py"),
            compatibility=archive.read("pocketstation/compatibility.py"),
            version=expected_version,
        )
        license_files = set(metadata.get_all("License-File", []))
        if license_files != {"LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"}:
            _fail("wheel metadata must include SDK and dependency license files")
        if b"MIT License" not in archive.read(license_name):
            _fail("wheel LICENSE is not the MIT license text")
        if not archive.read(notice_name).strip():
            _fail("wheel NOTICE is empty")
        parser = configparser.ConfigParser()
        parser.read_string(archive.read(entry_points_name).decode("utf-8"))
        if (
            parser.get("console_scripts", CONSOLE_COMMAND, fallback=None)
            != CONSOLE_TARGET
        ):
            _fail(f"wheel must install {CONSOLE_COMMAND}={CONSOLE_TARGET}")
        sbom = _sbom_versions(archive.read(sbom_name))
        for expected in ((CORE_NAME, CORE_VERSION), (RELAY_NAME, RELAY_VERSION)):
            if expected not in sbom:
                _fail(f"wheel SBOM omits {expected[0]} {expected[1]}")
        _verify_record(archive, names, record_name)
    return _artifact_report(path, len(names))


def validate_sdist(path: Path, *, expected_version: str) -> ArtifactReport:
    path = path.resolve()
    expected_root = f"{PROJECT_NAME}-{expected_version}"
    if path.name != f"{expected_root}.tar.gz":
        _fail(f"sdist filename must be {expected_root}.tar.gz")
    try:
        archive = tarfile.open(path, mode="r:gz")
    except (OSError, tarfile.TarError) as error:
        raise DistributionValidationError(
            f"cannot read sdist {path}: {error}"
        ) from error
    with archive:
        members = archive.getmembers()
        names = _validated_member_names(
            (member.name for member in members), archive="source distribution"
        )
        if any(
            member.issym() or member.islnk() or member.isdev() or member.isfifo()
            for member in members
        ):
            _fail("source distribution contains a link or special file")
        relative = tuple(
            _relative_sdist_name(name, expected_root)
            for name in names
            if name != expected_root
        )
        _reject_build_outputs(relative, archive="source distribution")
        compiled = tuple(name for name in relative if name.endswith(NATIVE_SUFFIXES))
        if compiled:
            _fail(f"source distribution contains compiled native output: {compiled}")
        required = {
            "PKG-INFO",
            "LICENSE",
            "NOTICE",
            "THIRD_PARTY_NOTICES.md",
            "build_backend.py",
            "pyproject.toml",
            "native/Cargo.toml",
            "native/Cargo.lock",
            "uv.lock",
            "python/pocketstation/py.typed",
            "python/pocketstation/_native.pyi",
            "python/pocketstation/__init__.py",
            "python/pocketstation/_api.py",
            "python/pocketstation/compatibility.py",
        }
        missing = sorted(required - set(relative))
        if missing:
            _fail(f"source distribution omits required files: {missing}")

        def read(member: str) -> bytes:
            extracted = archive.extractfile(f"{expected_root}/{member}")
            if extracted is None:
                _fail(f"source distribution member is not a file: {member}")
            return extracted.read()

        metadata = _metadata(read("PKG-INFO"), archive="source distribution")
        _required_metadata(
            metadata, version=expected_version, archive="source distribution"
        )
        if b"MIT License" not in read("LICENSE"):
            _fail("source distribution LICENSE is not the MIT license text")
        if not read("NOTICE").strip():
            _fail("source distribution NOTICE is empty")
        try:
            BUILD_BACKEND.read_notices(read("THIRD_PARTY_NOTICES.md"))
        except (ValueError, KeyError, TypeError) as error:
            _fail(f"source dependency notices are invalid: {error}")
        version = _source_versions(
            _parse_toml(read("pyproject.toml"), member="pyproject.toml"),
            _parse_toml(read("native/Cargo.toml"), member="native/Cargo.toml"),
            _parse_toml(read("native/Cargo.lock"), member="native/Cargo.lock"),
            _parse_toml(read("uv.lock"), member="uv.lock"),
        )
        if version != expected_version:
            _fail("source distribution manifests do not match its filename version")
        _validate_python_versions(
            package_init=read("python/pocketstation/__init__.py"),
            private_api=read("python/pocketstation/_api.py"),
            compatibility=read("python/pocketstation/compatibility.py"),
            version=expected_version,
        )
    return _artifact_report(path, len(names))


def validate_distributions(
    wheel: Path,
    sdist: Path,
    *,
    repository: Path,
) -> DistributionReport:
    version = validate_source_versions(repository)
    wheel_report = validate_wheel(wheel, expected_version=version)
    sdist_report = validate_sdist(sdist, expected_version=version)
    return DistributionReport(
        project_name=PROJECT_NAME,
        project_version=version,
        core_version=CORE_VERSION,
        relay_connector_version=RELAY_VERSION,
        wheel=wheel_report,
        sdist=sdist_report,
        checks={
            "archives_are_self_contained": True,
            "console_command_present": True,
            "license_and_notice_present": True,
            "native_extension_exactly_once": True,
            "record_is_complete": True,
            "registry_dependencies_locked": True,
            "sbom_versions_match": True,
            "typing_files_present": True,
            "versions_match": True,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument(
        "--repository", type=Path, default=Path(__file__).resolve().parents[1]
    )
    arguments = parser.parse_args()
    report = validate_distributions(
        arguments.wheel,
        arguments.sdist,
        repository=arguments.repository,
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
