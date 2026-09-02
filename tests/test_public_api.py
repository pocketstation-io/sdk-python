from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pocketstation
import pocketstation._native as native

ROOT = Path(__file__).resolve().parents[1]


def test_root_exports_are_a_small_intentional_entry_point() -> None:
    assert set(pocketstation.__all__) == {
        "RUNTIME_COMPATIBILITY",
        "AudioFrame",
        "AudioInput",
        "AudioInputConfig",
        "Capture",
        "CaptureError",
        "Connector",
        "PcmSource",
        "PocketStationError",
        "RecordingOutcome",
        "RunningSession",
        "RuntimeCompatibility",
        "Session",
        "SessionError",
        "Source",
        "StopResult",
        "aio",
        "capture",
        "discover_sources",
    }


def test_advanced_types_are_not_duplicated_at_the_package_root() -> None:
    assert hasattr(pocketstation, "Connector")
    assert not hasattr(pocketstation, "ConnectorManifest")
    assert not hasattr(pocketstation, "OperatorProvider")


def test_async_namespace_is_concise() -> None:
    assert set(pocketstation.aio.__all__) == {
        "AudioInput",
        "Capture",
        "Connector",
        "ConnectorDeadlines",
        "PcmSource",
        "RelaySession",
        "RunningSession",
        "Session",
        "capture",
        "discover_sources",
    }
    assert hasattr(pocketstation.aio, "Connector")
    assert not hasattr(pocketstation.aio, "ConnectorManifest")


def test_private_native_runtime_and_stub_export_the_same_classes() -> None:
    stub = ast.parse((ROOT / "python" / "pocketstation" / "_native.pyi").read_text())
    stub_classes = {node.name for node in stub.body if isinstance(node, ast.ClassDef)}
    runtime_classes = {
        name for name in dir(native) if isinstance(getattr(native, name), type)
    }
    feature_only_test_classes = {"ExtensionConformanceReport"}
    assert runtime_classes - feature_only_test_classes == stub_classes
    assert not feature_only_test_classes & stub_classes


def test_private_native_runtime_and_stub_export_the_same_functions() -> None:
    stub = ast.parse((ROOT / "python" / "pocketstation" / "_native.pyi").read_text())
    stub_functions = {
        node.name for node in stub.body if isinstance(node, ast.FunctionDef)
    }
    runtime_functions = {
        name for name in dir(native) if inspect.isbuiltin(getattr(native, name))
    }
    feature_only_test_functions = {"run_extension_conformance"}
    assert runtime_functions - feature_only_test_functions == stub_functions
    assert not feature_only_test_functions & stub_functions


def test_relay_members_already_exported_by_native_are_typed() -> None:
    stub = (ROOT / "python" / "pocketstation" / "_native.pyi").read_text()
    for declaration in (
        "class RelayPublisher",
        "class RelayPublishOutcome",
        "def publish(self, publisher: RelayPublisher, bus_id: str) -> RouteId",
        "def relay_outcomes(self) -> list[RelayPublishOutcome]",
        "def relay(",
    ):
        assert declaration in stub
