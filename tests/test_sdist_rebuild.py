from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from tests.run_artifact_consumer import _extract_sdist


def _write_sdist(path: Path, members: dict[str, bytes]) -> None:
    with tarfile.open(path, mode="w:gz") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))


def test_given_self_contained_sdist_when_extracted_then_one_build_root_is_returned(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5.tar.gz"
    _write_sdist(
        artifact,
        {
            "pocketstation-0.1.5/pyproject.toml": b"[build-system]\n",
            "pocketstation-0.1.5/native/Cargo.toml": b"[package]\n",
        },
    )

    source_root = _extract_sdist(artifact, tmp_path / "source")

    assert source_root == (tmp_path / "source" / "pocketstation-0.1.5").resolve()
    assert (source_root / "native" / "Cargo.toml").is_file()


def test_given_parent_traversal_when_extracting_sdist_then_rebuild_is_rejected(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5.tar.gz"
    _write_sdist(
        artifact,
        {
            "pocketstation-0.1.5/pyproject.toml": b"[build-system]\n",
            "pocketstation-0.1.5/../../outside": b"not allowed",
        },
    )

    with pytest.raises(SystemExit, match="unsafe path"):
        _extract_sdist(artifact, tmp_path / "source")


def test_given_multiple_roots_when_extracting_sdist_then_rebuild_is_rejected(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5.tar.gz"
    _write_sdist(
        artifact,
        {
            "pocketstation-0.1.5/pyproject.toml": b"[build-system]\n",
            "sibling-repository/Cargo.toml": b"[package]\n",
        },
    )

    with pytest.raises(SystemExit, match="one top-level directory"):
        _extract_sdist(artifact, tmp_path / "source")


def test_given_symlink_when_extracting_sdist_then_rebuild_is_rejected(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "pocketstation-0.1.5.tar.gz"
    with tarfile.open(artifact, mode="w:gz") as archive:
        project = tarfile.TarInfo("pocketstation-0.1.5/pyproject.toml")
        project.size = len(b"[build-system]\n")
        archive.addfile(project, io.BytesIO(b"[build-system]\n"))
        link = tarfile.TarInfo("pocketstation-0.1.5/pocketstation")
        link.type = tarfile.SYMTYPE
        link.linkname = "../../pocketstation-io/pocketstation"
        archive.addfile(link)

    with pytest.raises(SystemExit, match="link or device"):
        _extract_sdist(artifact, tmp_path / "source")
