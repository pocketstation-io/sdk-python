from __future__ import annotations

from pathlib import Path

import pocketstation
from pocketstation import signal

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "python" / "pocketstation"


def test_implemented_capabilities_have_explicit_python_owners() -> None:
    expected = {
        "capture.py",
        "control.py",
        "errors.py",
        "extensions.py",
        "graph.py",
        "observations.py",
        "relay.py",
        "session.py",
        "sidecar.py",
        "sources.py",
        "streams.py",
    }
    assert expected <= {path.name for path in PACKAGE.glob("*.py")}

    asynchronous_expected = {
        "capture.py",
        "control.py",
        "extensions.py",
        "observations.py",
        "relay.py",
        "session.py",
        "sidecar.py",
        "sources.py",
        "streams.py",
    }
    assert asynchronous_expected <= {
        path.name for path in (PACKAGE / "aio").glob("*.py")
    }


def test_relay_modules_are_real_owners_not_empty_parity_scaffolds() -> None:
    synchronous = (PACKAGE / "relay.py").read_text()
    asynchronous = (PACKAGE / "aio" / "relay.py").read_text()
    assert "class RelaySession" in synchronous
    assert "class RelaySession" in asynchronous
    assert "def create_receiver_invitation" in synchronous
    assert "async def create_receiver_invitation" in asynchronous


def test_public_declarations_report_their_canonical_owner() -> None:
    assert pocketstation.Source.__module__ == "pocketstation.sources"
    assert pocketstation.Endpoint.__module__ == "pocketstation.graph"
    assert pocketstation.Stem.__module__ == "pocketstation.graph"
    assert pocketstation.SignalSpec.__module__ == "pocketstation.graph"
    assert pocketstation.RelaySession.__module__ == "pocketstation.relay"
    assert signal.SignalSpec is pocketstation.SignalSpec


def test_session_modules_do_not_redeclare_source_or_graph_types() -> None:
    synchronous = (PACKAGE / "session.py").read_text()
    asynchronous = (PACKAGE / "aio" / "session.py").read_text()
    for declaration in ("class Source", "class Endpoint", "class Stem"):
        assert declaration not in synchronous
        assert declaration not in asynchronous


def test_native_error_policy_has_one_python_owner() -> None:
    errors = (PACKAGE / "errors.py").read_text()
    assert "def _native_call" in errors
    assert "def _normalize_native_error" in errors
    assert "def _native_call" not in (PACKAGE / "session.py").read_text()
    assert "def _native_sync" not in (PACKAGE / "aio" / "session.py").read_text()
