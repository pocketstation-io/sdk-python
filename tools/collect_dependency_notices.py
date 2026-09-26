"""Render reviewed, retained source notices into a self-contained package file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from packaging.licenses import canonicalize_license_expression

LINUX_PACKAGES = {
    "alsa-lib": ("alsa-lib", "LGPL-2.1-or-later"),
    "openssl": ("openssl-libs", "Apache-2.0"),
    "pipewire": ("pipewire-libs", "MIT"),
}


def render(rust: dict[str, Any], linux: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if rust["missing_notices"]:
        raise ValueError("Rust dependencies lack retained notices")
    components: list[dict[str, Any]] = []
    texts: dict[str, str] = {}
    for ecosystem, inventory in (("cargo", rust), ("rpm", linux)):
        for package in inventory["packages"]:
            name = package["name"]
            if ecosystem == "rpm":
                name, expression = LINUX_PACKAGES[name]
                source = package["source_url"]
            else:
                expression = package["license_expression"].replace("/", " OR ")
                source = package["crate_url"]
            selected = package["notices"]
            if ecosystem == "rpm" and name == "alsa-lib":
                # The wheel includes libasound, not the GPL aserver executable.
                selected = [n for n in selected if "/aserver/" not in n["origin"]]
            if not selected:
                raise ValueError(f"no retained notice for {name}")
            refs = []
            origins = []
            for notice in selected:
                data = notice["text"].encode("utf-8")
                digest = hashlib.sha256(data).hexdigest()
                if digest != notice["sha256"]:
                    raise ValueError(f"retained notice changed: {name}")
                texts[digest] = notice["text"]
                refs.append(digest)
                origins.append({"origin": notice["origin"], "sha256": digest})
            component = {
                "ecosystem": ecosystem,
                "name": name,
                "version": package["version"],
                "license_expression": canonicalize_license_expression(expression),
                "source_url": source,
                "notices": sorted(set(refs)),
                "notice_origins": origins,
            }
            if ecosystem == "rpm":
                component["source_sha256"] = package["source_sha256"]
            components.append(component)
    components.sort(key=lambda c: (c["ecosystem"], c["name"], c["version"]))
    index = {"schema_version": 1, "components": components}
    parts = [
        "# Third-party licenses and notices\n\n",
        "PocketStation SDK source is MIT licensed. Native wheels include the\n",
        "components identified by their own CycloneDX SBOMs. This document\n",
        "retains notices for the locked source build and six native targets;\n",
        "each wheel's license expression describes only its listed components.\n\n",
        "Linux repaired wheels additionally include libasound (LGPL-2.1-or-later),\n",
        "libssl/libcrypto (Apache-2.0), and libpipewire (MIT). Exact corresponding\n",
        "source RPM URLs and hashes are recorded below, including distribution\n",
        "patches. The libraries remain separate shared objects and can be\n",
        "replaced or rebuilt; the SDK does not restrict modification or reverse\n",
        "engineering for debugging such modifications. ALSA's aserver and\n",
        "PipeWire's libjackserver/libspa-alsa plugins are not bundled.\n\n",
        "<!-- pocketstation-notice-index\n",
        json.dumps(index, sort_keys=True, separators=(",", ":")),
        "\n-->\n\n",
    ]
    for component in components:
        parts.extend(
            [
                f"## {component['name']} {component['version']}\n\n",
                f"License: `{component['license_expression']}`.\n\n",
                f"Source: {component['source_url']}\n\n",
                *[f"Notice SHA-256: `{d}`\n\n" for d in component["notices"]],
            ]
        )
    for digest, body in sorted(texts.items()):
        parts.extend(
            [
                f"## Notice {digest}\n\n",
                f"<!-- notice:{digest} -->\n",
                body,
                f"\n<!-- /notice:{digest} -->\n\n",
            ]
        )
    return "".join(parts), index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust-inventory", required=True, type=Path)
    parser.add_argument("--linux-inventory", required=True, type=Path)
    parser.add_argument(
        "--output-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    document, index = render(
        json.loads(args.rust_inventory.read_text()),
        json.loads(args.linux_inventory.read_text()),
    )
    (args.output_root / "THIRD_PARTY_NOTICES.md").write_text(document, encoding="utf-8")
    (args.output_root / "tools/dependency-notices.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Retained notices for {len(index['components'])} package versions")


if __name__ == "__main__":
    main()
