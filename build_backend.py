"""Delegate compilation to Maturin and describe the licenses in each wheel.

The source archive remains MIT. Wheels include their compiled dependencies,
so their expression is computed from their own SBOM and retained notices.
No metadata preparation hook is exposed: PEP 517 frontends inspect the built
wheel, after its exact native dependencies are known.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

NOTICE_FILE = "THIRD_PARTY_NOTICES.md"
INDEX_START = "<!-- pocketstation-notice-index\n"
INDEX_END = "\n-->"


def read_notices(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8")
    if text.count(INDEX_START) != 1:
        raise ValueError("missing or duplicate dependency notice index")
    index = json.loads(text.split(INDEX_START, 1)[1].split(INDEX_END, 1)[0])
    identities: set[tuple[str, str, str]] = set()
    for component in index["components"]:
        identity = (component["ecosystem"], component["name"], component["version"])
        if identity in identities or not component["notices"]:
            raise ValueError("duplicate component or missing dependency notice")
        identities.add(identity)
        expression = component["license_expression"]
        if not expression or not re.fullmatch(r"[A-Za-z0-9.()+ -]+", expression):
            raise ValueError("invalid recorded license expression")
        for digest in component["notices"]:
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("invalid dependency notice digest")
            start = f"<!-- notice:{digest} -->\n"
            end = f"\n<!-- /notice:{digest} -->"
            if text.count(start) != 1 or text.count(end) != 1:
                raise ValueError("dependency notice text is missing or duplicated")
            body = text.split(start, 1)[1].split(end, 1)[0].encode("utf-8")
            if hashlib.sha256(body).hexdigest() != digest:
                raise ValueError("dependency notice text changed")
    return index


def wheel_license_expression(files: Mapping[str, bytes]) -> str:
    notice_paths = [
        n for n in files if n.endswith(f".dist-info/licenses/{NOTICE_FILE}")
    ]
    if len(notice_paths) != 1:
        raise ValueError("wheel must contain exactly one dependency notice document")
    index = read_notices(files[notice_paths[0]])
    components = {
        (c["ecosystem"], c["name"], c["version"]): c for c in index["components"]
    }
    sboms = [n for n in files if ".dist-info/sboms/" in n and n.endswith(".json")]
    if not any(n.endswith("/pocketstation-python.cyclonedx.json") for n in sboms):
        raise ValueError("native dependency SBOM is missing")
    expressions = {"MIT"}
    for name in sboms:
        document = json.loads(files[name])
        ecosystem = "rpm" if name.endswith("/auditwheel.cdx.json") else "cargo"
        if document.get("bomFormat") != "CycloneDX":
            raise ValueError("unsupported dependency SBOM")
        for component in document.get("components", []):
            if ecosystem == "rpm" and component["name"] == "pocketstation":
                continue
            identity = (ecosystem, component["name"], component["version"])
            if identity not in components:
                raise ValueError(f"dependency lacks reviewed notices: {identity}")
            expressions.add(components[identity]["license_expression"])
    return " AND ".join(
        f"({expression})"
        if " AND " in expression or " OR " in expression
        else expression
        for expression in sorted(expressions)
    )


def finalize_wheel(wheel: Path) -> None:
    """Finalize metadata before qualification, preserving every other member."""
    with zipfile.ZipFile(wheel) as archive:
        infos = archive.infolist()
        if len({i.filename for i in infos}) != len(infos):
            raise ValueError("duplicate wheel member")
        files = {i.filename: archive.read(i) for i in infos}
    expression = wheel_license_expression(files).encode("ascii")
    metadata_names = [n for n in files if n.endswith(".dist-info/METADATA")]
    record_names = [n for n in files if n.endswith(".dist-info/RECORD")]
    if len(metadata_names) != 1 or len(record_names) != 1:
        raise ValueError("wheel metadata or RECORD is missing or duplicated")
    metadata_name, record_name = metadata_names[0], record_names[0]
    metadata = files[metadata_name]
    headers, separator, description = metadata.partition(b"\n\n")
    if not separator:
        raise ValueError("wheel metadata has no description separator")
    pattern = rb"(?m)^License-Expression:[^\n]*(?:\n[ \t][^\n]*)*"
    if len(re.findall(pattern, headers)) != 1:
        raise ValueError("wheel must declare one license expression")
    updated = re.sub(pattern, b"License-Expression: " + expression, headers)
    updated += separator + description
    if updated == metadata:
        return
    files[metadata_name] = updated
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for name, data in files.items():
        if name == record_name:
            continue
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
        writer.writerow((name, "sha256=" + digest.decode("ascii"), len(data)))
    writer.writerow((record_name, "", ""))
    files[record_name] = output.getvalue().encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=".license-", dir=wheel.parent)
    os.close(descriptor)
    try:
        with zipfile.ZipFile(temporary, "w") as archive:
            for info in infos:
                archive.writestr(info, files[info.filename])
        os.replace(temporary, wheel)
    finally:
        Path(temporary).unlink(missing_ok=True)


def build_wheel(
    wheel_directory: str,
    config_settings: Mapping[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    import maturin

    name = maturin.build_wheel(wheel_directory, config_settings, metadata_directory)
    finalize_wheel(Path(wheel_directory) / name)
    return name


def build_sdist(
    sdist_directory: str, config_settings: Mapping[str, Any] | None = None
) -> str:
    import maturin

    return str(maturin.build_sdist(sdist_directory, config_settings))


def build_editable(
    wheel_directory: str,
    config_settings: Mapping[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    import maturin

    return str(
        maturin.build_editable(wheel_directory, config_settings, metadata_directory)
    )


def get_requires_for_build_wheel(
    config_settings: Mapping[str, Any] | None = None,
) -> list[str]:
    import maturin

    return list(maturin.get_requires_for_build_wheel(config_settings))


get_requires_for_build_editable = get_requires_for_build_wheel


def get_requires_for_build_sdist(
    config_settings: Mapping[str, Any] | None = None,
) -> list[str]:
    import maturin

    return list(maturin.get_requires_for_build_sdist(config_settings))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheels", type=Path, nargs="+")
    for selected in parser.parse_args().wheels:
        finalize_wheel(selected)
        print(f"Finalized license metadata: {selected.name}")
