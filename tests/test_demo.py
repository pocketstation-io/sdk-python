"""Installed demo CLI, discovery, invitation, and finite-run behavior."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path
from time import monotonic
from types import SimpleNamespace
from typing import Any

import pytest
from pocketstation_demo import demo
from pocketstation_demo import relay as demo_relay
from pocketstation_demo.transcript import Transcript


def test_demo_options_cover_the_finite_installed_workflow() -> None:
    options = demo._parse_options(
        [
            "--application",
            "Browser",
            "--microphone-id",
            "mic-7",
            "--recording-root",
            "captures",
            "--duration-seconds",
            "12.5",
            "--model",
            "/models/whisper",
            "--allow-model-download",
            "--no-browser",
            "--output-format",
            "jsonl",
        ]
    )

    assert options == demo.DemoOptions(
        application="Browser",
        microphone_id="mic-7",
        recording_root=Path("captures"),
        duration_seconds=12.5,
        model="/models/whisper",
        allow_model_download=True,
        no_browser=True,
        output_format="jsonl",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("4312", 4312),
        (" 4312 ", 4312),
        ("Browser", "Browser"),
        ("com.example.browser", "com.example.browser"),
    ],
)
def test_application_selector_preserves_names_and_parses_process_ids(
    value: str,
    expected: str | int,
) -> None:
    assert demo._parse_options(["--application", value]).application == expected


@pytest.mark.parametrize("value", ["", " ", "0", "-1"])
def test_application_selector_rejects_empty_or_nonpositive_process_ids(
    value: str,
) -> None:
    with pytest.raises(SystemExit):
        demo._parse_options(["--application", value])


def test_demo_help_exposes_workflow_inputs_without_relay_plumbing() -> None:
    help_text = demo._parser().format_help()

    for option in (
        "--application",
        "--microphone-id",
        "--recording-root",
        "--duration-seconds",
        "--model",
        "--allow-model-download",
        "--no-browser",
        "--output-format",
    ):
        assert option in help_text
    assert "--relay" not in help_text


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "3601"])
def test_demo_rejects_nonfinite_or_unbounded_duration(value: str) -> None:
    with pytest.raises(SystemExit):
        demo._parse_options(["--duration-seconds", value])


@pytest.mark.asyncio
async def test_demo_service_discovers_relay_from_control_plane(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[dict[str, object]] = []

    async def create(**values: object) -> object:
        calls.append(values)
        return object()

    monkeypatch.setenv("POCKETSTATION_CONTROL_URL", "https://control.example")
    monkeypatch.setenv("POCKETSTATION_RELAY_URL", "https://must-not-be-used.example")
    monkeypatch.setattr(demo_relay.pks.RelaySession, "create", create)

    await demo_relay.demo_relay_session(required_buses=("application", "microphone"))

    assert calls == [
        {
            "control_plane_url": "https://control.example",
            "required_buses": ("application", "microphone"),
        }
    ]
    assert capsys.readouterr().out == ""


@pytest.mark.asyncio
async def test_demo_emits_two_exact_bus_invitations_and_stops_when_idle(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    remote = _Remote()
    live = _Capture()
    transcription = _Transcription()
    capture_calls: list[dict[str, object]] = []
    result_calls: list[tuple[object, object, object, object, float]] = []

    async def create_remote() -> _Remote:
        return remote

    def capture(**values: object) -> _Capture:
        capture_calls.append(values)
        return live

    def fail_browser_open(_url: str) -> bool:
        raise AssertionError("--no-browser must not open a browser")

    def result_event(
        capture: object,
        relay_session: object,
        routes: object,
        stop: object,
        *,
        duration_seconds: float,
    ) -> dict[str, object]:
        result_calls.append((capture, relay_session, routes, stop, duration_seconds))
        return {"event": "result", "status": "completed"}

    monkeypatch.setattr(demo, "demo_relay_session", create_remote)
    monkeypatch.setattr(demo.pks, "capture", capture)
    monkeypatch.setattr(demo, "FasterWhisper", lambda _configuration: transcription)
    monkeypatch.setattr(demo.webbrowser, "open", fail_browser_open)
    monkeypatch.setattr(demo, "result_event", result_event)
    options = demo.DemoOptions(
        application=4312,
        microphone_id="mic-7",
        recording_root=Path("captures"),
        duration_seconds=0.02,
        model="/models/whisper",
        allow_model_download=False,
        no_browser=True,
        output_format="jsonl",
    )

    started = monotonic()
    await demo.run_demo(options)
    elapsed = monotonic() - started

    assert elapsed < 0.5
    assert capture_calls == [
        {
            "application": 4312,
            "microphone": "mic-7",
            "record_to": Path("captures"),
            "stream_audio": False,
        }
    ]
    assert live.application_stem.publications == [
        (remote.publisher_value, "application")
    ]
    assert live.microphone_stem.publications == [(remote.publisher_value, "microphone")]
    assert remote.invitation_buses == ["application", "microphone"]
    assert remote.minimum_receivers == 2
    assert transcription.capture is live
    assert result_calls == [
        (live, remote, relay_routes_for(live, remote), live.stop_result, 0.02)
    ]
    assert "application" not in repr(_Invitation("application"))
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert lines[:2] == [
        {
            "event": "invitation",
            "bus_id": "application",
            "share_url": "https://receiver.example/calm-forest#secret=application",
        },
        {
            "event": "invitation",
            "bus_id": "microphone",
            "share_url": "https://receiver.example/calm-forest#secret=microphone",
        },
    ]
    result = lines[2]
    assert result == {"event": "result", "status": "completed"}
    assert "#secret=" not in json.dumps(result)


class _Invitation:
    def __init__(self, bus_id: str) -> None:
        self.share_alias = "calm-forest"
        self._url = f"https://receiver.example/calm-forest#secret={bus_id}"

    def expose_url(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return "_Invitation([redacted])"


class _Stem:
    def __init__(self, stem_id: int) -> None:
        self.id = stem_id
        self.session_id = 17
        self.publications: list[tuple[object, str]] = []

    def publish(self, publisher: object, bus_id: str) -> Any:
        self.publications.append((publisher, bus_id))
        return SimpleNamespace(bus_id=bus_id, route_id=stem_id_for_bus(bus_id) + 10)


class _Capture:
    def __init__(self) -> None:
        self.session = object()
        self.application_stem = _Stem(1)
        self.microphone_stem = _Stem(2)
        self.stop_result: Any = None

    async def __aenter__(self) -> _Capture:
        return self

    async def __aexit__(self, *_details: object) -> None:
        self.stop_result = object()


class _Remote:
    def __init__(self) -> None:
        self.publisher_value = object()
        self.invitation_buses: list[str] = []
        self.minimum_receivers: int | None = None
        self.publisher_activation: Any = None
        self.receiver_activation: Any = None

    def publisher(self, _session: object) -> object:
        return self.publisher_value

    async def wait_for_publisher(self, **_values: object) -> None:
        self.publisher_activation = _activation(subscription_count=0)

    async def create_receiver_invitation(self, *, bus_id: str) -> Any:
        self.invitation_buses.append(bus_id)
        return _Invitation(bus_id)

    async def wait_for_receiver(
        self,
        *,
        minimum_receivers: int,
        timeout_seconds: float,
    ) -> None:
        assert timeout_seconds == 30
        self.minimum_receivers = minimum_receivers
        self.receiver_activation = _activation(subscription_count=2)

    async def __aenter__(self) -> _Remote:
        return self

    async def __aexit__(self, *_details: object) -> None:
        return None


class _Transcription:
    def __init__(self) -> None:
        self.capture: _Capture | None = None

    def transcribe(self, capture: _Capture) -> AsyncIterator[Transcript]:
        self.capture = capture

        async def idle() -> AsyncIterator[Transcript]:
            await asyncio.Event().wait()
            yield Transcript(1, "", "en", 0, 0, ())

        return idle()


_BUS_IDS = ("application", "microphone")


def stem_id_for_bus(bus_id: str) -> int:
    return _BUS_IDS.index(bus_id) + 1


def relay_routes_for(live: _Capture, remote: _Remote) -> dict[str, object]:
    return {
        "application": SimpleNamespace(bus_id="application", route_id=11),
        "microphone": SimpleNamespace(bus_id="microphone", route_id=12),
    }


def _activation(*, subscription_count: int) -> Any:
    return SimpleNamespace(
        snapshot=SimpleNamespace(
            ready=True,
            subscription_count=subscription_count,
            buses=tuple(
                SimpleNamespace(
                    bus_id=bus_id,
                    source_active=True,
                    source_generation=1,
                )
                for bus_id in _BUS_IDS
            ),
            subscriptions=tuple(
                SimpleNamespace(bus_id=bus_id)
                for bus_id in _BUS_IDS[:subscription_count]
            ),
        )
    )
