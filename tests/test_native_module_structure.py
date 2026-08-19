from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "native" / "src"


def test_native_binding_is_split_by_real_implemented_owner() -> None:
    expected = {
        "errors.rs",
        "extensions.rs",
        "graph.rs",
        "lib.rs",
        "observations.rs",
        "relay.rs",
        "session.rs",
        "sidecar.rs",
        "signals.rs",
        "sources.rs",
        "streams.rs",
    }
    assert expected <= {path.name for path in NATIVE.glob("*.rs")}


def test_process_sidecar_has_a_real_native_owner() -> None:
    source = (NATIVE / "sidecar.rs").read_text()
    assert "SidecarProcessSpec" in source
    assert "wait_sidecar" in source
    assert "sidecar_error_message" in source
    assert len(source.splitlines()) >= 200


def test_lib_rs_only_declares_and_registers_modules() -> None:
    source = (NATIVE / "lib.rs").read_text()
    assert len(source.splitlines()) <= 32
    assert "#[pymodule]" in source
    assert "#[pyclass" not in source
    assert "#[pymethods]" not in source
    assert "#[pyfunction]" not in source
    assert "include!(" not in source
    for owner in (
        "extensions",
        "sources",
        "graph",
        "relay",
        "streams",
        "observations",
        "session",
        "sidecar",
        "signals",
    ):
        assert f"{owner}::register(module)?" in source


def test_each_registered_owner_contains_real_binding_behavior() -> None:
    for owner in (
        "extensions.rs",
        "graph.rs",
        "observations.rs",
        "relay.rs",
        "session.rs",
        "sidecar.rs",
        "signals.rs",
        "sources.rs",
        "streams.rs",
    ):
        source = (NATIVE / owner).read_text()
        assert "fn register(" in source
        assert "include!(" not in source
        assert len(source.splitlines()) >= 40
