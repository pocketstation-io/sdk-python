from __future__ import annotations

import sys
import threading
from pathlib import Path
from time import monotonic

import pocketstation as pks
import pytest
from pocketstation._native import Session as NativeSession

ROOT = Path(__file__).parents[1]
CORE = ROOT.parent / "pocketstation"
CHILD = Path(__file__).with_name("_pkss_child.py")


def session_with_hung_sidecar(tmp_path: Path) -> pks.RunningSession:
    if not hasattr(NativeSession, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    session = pks.Session._from_native(NativeSession.conformance(tmp_path))
    audio = session.polled_audio()
    session.capture(pks.Source.application("PocketStation Python Fixture")).send(audio)
    session.capture(pks.Source.microphone_default()).send(audio)
    session.register_sidecar(
        pks.SidecarProcessSpec(
            91,
            sys.executable,
            (str(CHILD), "hang"),
            deadlines=pks.SidecarDeadlines(
                ready_s=1.0,
                processing_s=1.0,
                shutdown_s=0.1,
            ),
        )
    )
    return session.start()


def test_sidecar_binding_contains_no_python_callback_contract() -> None:
    sidecar_source = (ROOT / "native/src/sidecar.rs").read_text()
    core_extension = (CORE / "src/abi/executable_extension.rs").read_text()

    assert "PyAny" not in sidecar_source
    assert "PyObject" not in sidecar_source
    assert "callable" not in sidecar_source.lower()
    assert (
        "PCM audio remains on the native fixed-capacity realtime lane" in core_extension
    )
    assert "blocking/async Session" in core_extension


def test_blocking_sidecar_reap_detaches_from_python(tmp_path: Path) -> None:
    running = session_with_hung_sidecar(tmp_path)
    stopping = threading.Event()
    stopped = threading.Event()
    observed: list[float] = []

    def heartbeat() -> None:
        stopping.wait()
        while not stopped.is_set():
            observed.append(monotonic())

    thread = threading.Thread(target=heartbeat, name="python-heartbeat")
    thread.start()
    started = monotonic()
    stopping.set()
    result = running.stop()
    ended = monotonic()
    stopped.set()
    thread.join(timeout=1.0)

    assert not result.success
    assert ended - started >= 0.05
    assert any(started <= timestamp <= ended for timestamp in observed)
    [final] = result.sidecar_outcomes
    assert final.forced_kills_total == 1
    assert final.reaps_total == 1
