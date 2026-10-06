from __future__ import annotations

import base64
import copy
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest

import build_backend as backend


def notice_document(extra: bool = False) -> bytes:
    """Small synthetic archive fixture; never used as distribution evidence."""
    body = "MIT License\nTest fixture copyright\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    components = [
        {
            "ecosystem": "cargo",
            "name": name,
            "version": version,
            "license_expression": "MIT",
            "notices": [digest],
        }
        for name, version in [
            ("pocketstation", "1.1.13"),
            ("pocketstation-relay", "0.1.5"),
        ]
    ]
    if extra:
        components.append(
            {
                "ecosystem": "rpm",
                "name": "alsa-lib",
                "version": "1.2.15.3-1.el9",
                "license_expression": "LGPL-2.1-or-later",
                "notices": [digest],
            }
        )
    index = {"schema_version": 1, "components": components}
    return (
        backend.INDEX_START
        + json.dumps(index)
        + backend.INDEX_END
        + f"\n<!-- notice:{digest} -->\n{body}\n<!-- /notice:{digest} -->\n"
    ).encode()


def wheel_files() -> dict[str, bytes]:
    root = "pocketstation-0.1.5.dist-info/"
    return {
        "pocketstation/_native.abi3.so": b"synthetic test native bytes",
        root + "METADATA": (
            b"Name: pocketstation\nLicense-Expression: MIT\n\nOriginal README.\n"
        ),
        root + "RECORD": b"",
        root + "licenses/THIRD_PARTY_NOTICES.md": notice_document(extra=True),
        root + "sboms/pocketstation-python.cyclonedx.json": json.dumps(
            {
                "bomFormat": "CycloneDX",
                "components": [{"name": "pocketstation", "version": "1.1.13"}],
            }
        ).encode(),
        root + "sboms/auditwheel.cdx.json": json.dumps(
            {
                "bomFormat": "CycloneDX",
                "components": [{"name": "alsa-lib", "version": "1.2.15.3-1.el9"}],
            }
        ).encode(),
    }


def test_wheel_license_includes_repaired_library_and_requires_its_notices() -> None:
    files = wheel_files()
    assert backend.wheel_license_expression(files) == "LGPL-2.1-or-later AND MIT"
    broken = copy.deepcopy(files)
    name = next(n for n in broken if n.endswith("auditwheel.cdx.json"))
    broken[name] = broken[name].replace(b"1.2.15.3-1.el9", b"unknown-version")
    with pytest.raises(ValueError, match="lacks reviewed notices"):
        backend.wheel_license_expression(broken)


def test_notice_text_changes_and_duplicate_indexes_are_rejected() -> None:
    original = notice_document()
    backend.read_notices(original)
    with pytest.raises(ValueError, match="notice text changed"):
        backend.read_notices(
            original.replace(b"Test fixture copyright", b"Changed copyright")
        )
    with pytest.raises(ValueError, match="duplicate dependency notice index"):
        backend.read_notices(original + original)


def test_finalization_preserves_code_and_readme_rehashes_record_and_is_idempotent(
    tmp_path: Path,
) -> None:
    files = wheel_files()
    wheel = tmp_path / "example.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    backend.finalize_wheel(wheel)
    first = wheel.read_bytes()
    with zipfile.ZipFile(wheel) as archive:
        for name, data in files.items():
            if not name.endswith(("/RECORD", "/METADATA")):
                assert archive.read(name) == data
        metadata = archive.read("pocketstation-0.1.5.dist-info/METADATA")
        assert b"License-Expression: LGPL-2.1-or-later AND MIT\n" in metadata
        assert metadata.split(b"\n\n", 1)[1] == b"Original README.\n"
        rows = csv.reader(
            io.StringIO(archive.read("pocketstation-0.1.5.dist-info/RECORD").decode())
        )
        for name, digest, size in rows:
            if name.endswith("/RECORD"):
                assert digest == size == ""
            else:
                data = archive.read(name)
                expected = base64.urlsafe_b64encode(
                    hashlib.sha256(data).digest()
                ).rstrip(b"=")
                assert digest == "sha256=" + expected.decode()
                assert int(size) == len(data)
    backend.finalize_wheel(wheel)
    assert wheel.read_bytes() == first


def test_source_backend_defers_metadata_until_native_dependencies_are_known() -> None:
    assert not hasattr(backend, "prepare_metadata_for_build_wheel")
