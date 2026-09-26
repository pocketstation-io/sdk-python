"""Authoritative installed-demo result and output behavior."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pocketstation_demo.result import DemoOutput, result_event


def test_jsonl_output_is_stable_and_exposes_secret_only_for_invitation(
    capsys: Any,
) -> None:
    invitation = _Invitation("application")
    output = DemoOutput("jsonl")

    exposed = output.invitation("application", invitation)
    output.completed({"event": "result", "status": "completed"})

    assert exposed == "https://receiver.example/calm-forest#secret=application"
    assert "#secret=" not in repr(invitation)
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert lines == [
        {
            "event": "invitation",
            "bus_id": "application",
            "share_url": "https://receiver.example/calm-forest#secret=application",
        },
        {"event": "result", "status": "completed"},
    ]
    assert "#secret=" not in json.dumps(lines[-1])


def test_result_event_reports_only_public_authoritative_observations(
    tmp_path: Path,
) -> None:
    live = _Capture()
    remote = _Remote(subscription_count=2)
    stop = _stop_result(tmp_path)
    routes = {
        bus_id: SimpleNamespace(route_id=stem_id_for_bus(bus_id) + 10)
        for bus_id in _BUS_IDS
    }

    result = result_event(
        live,
        remote,
        routes,
        stop,
        duration_seconds=12.5,
    )

    assert result["event"] == "result"
    assert result["status"] == "completed"
    assert result["duration_seconds"] == 12.5
    assert result["receiver_count"] == 2
    assert result["session_id"] == "17"
    assert result["relay_session_id"] == "018f4e4e-2f3b-7e24-a214-9913db127c02"
    assert result["session_id"] != result["relay_session_id"]
    assert result["source_ids"] == {
        "application": "9007199254740993",
        "microphone": "9007199254740995",
    }
    assert result["session"] == {
        "success": True,
        "already_stopped": False,
        "disposition": "stopped",
        "state": "stopped",
        "runtime_worker_panicked": False,
        "capture_finalization_failures_total": 0,
        "operator_finalization_failures_total": 0,
        "endpoint_finalization_failures_total": 0,
        "runtime_failures_total": 0,
        "lineage_failures_total": 0,
        "source_send_rejections_total": 0,
        "runtime_events_total": 1,
        "metrics_available": False,
        "metrics_unavailable_reason": "fixture",
    }
    assert result["sources"] == [
        {
            "label": "application",
            "stem_id": "1",
            "source_id": "9007199254740993",
            "metrics": None,
        },
        {
            "label": "microphone",
            "stem_id": "2",
            "source_id": "9007199254740995",
            "metrics": None,
        },
    ]
    recording = result["recording"]
    assert isinstance(recording, dict)
    assert recording["complete"] is True
    assert recording["manifest_path"] == str(tmp_path / "manifest.json")
    assert {item["stem_name"] for item in recording["stems"]} == set(_BUS_IDS)
    relay = result["relay"]
    assert isinstance(relay, dict)
    assert {item["bus_id"] for item in relay["declared_buses"]} == set(_BUS_IDS)
    assert {item["bus_id"] for item in relay["outcomes"]} == set(_BUS_IDS)
    assert [gap["field"] for gap in result["api_gaps"]] == [
        "live_source_id",
        "receiver_playout",
    ]
    assert "#secret=" not in json.dumps(result)


def test_result_event_names_missing_manifest_source_identity(tmp_path: Path) -> None:
    live = _Capture()
    remote = _Remote(subscription_count=0)
    stop = _stop_result(tmp_path, manifest={"schema_version": 2, "stems": []})

    result = result_event(live, remote, {}, stop, duration_seconds=1.0)

    assert result["source_ids"] == {"application": None, "microphone": None}
    assert result["receiver_count"] == 0
    assert result["api_gaps"][-1] == {
        "field": "recording_manifest_source_id",
        "detail": (
            "recording manifest omitted a positive source_id for: "
            "application, microphone"
        ),
    }


def test_result_event_sources_local_and_relay_session_ids_independently(
    tmp_path: Path,
) -> None:
    live = _Capture(session_id=29)
    relay_session_id = "018f4e66-28cf-7cbd-8759-965f76fb943e"
    remote = _Remote(subscription_count=2, session_id=relay_session_id)

    result = result_event(
        live,
        remote,
        {},
        _stop_result(tmp_path),
        duration_seconds=1.0,
    )

    assert result["session_id"] == str(live.application_stem.session_id) == "29"
    assert result["relay_session_id"] == str(remote.session_id) == relay_session_id
    assert result["session_id"] != result["relay_session_id"]


class _Invitation:
    def __init__(self, bus_id: str) -> None:
        self.share_alias = "calm-forest"
        self._url = f"https://receiver.example/calm-forest#secret={bus_id}"

    def expose_url(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return "_Invitation([redacted])"


class _Stem:
    def __init__(self, stem_id: int, *, session_id: int = 17) -> None:
        self.id = stem_id
        self.session_id = session_id


class _Capture:
    def __init__(self, *, session_id: int = 17) -> None:
        self.application_stem = _Stem(1, session_id=session_id)
        self.microphone_stem = _Stem(2, session_id=session_id)


class _Remote:
    def __init__(
        self,
        *,
        subscription_count: int,
        session_id: str = "018f4e4e-2f3b-7e24-a214-9913db127c02",
    ) -> None:
        self.session_id = session_id
        self.publisher_activation = _activation(subscription_count=0)
        self.receiver_activation = _activation(subscription_count=subscription_count)


_BUS_IDS = ("application", "microphone")


def stem_id_for_bus(bus_id: str) -> int:
    return _BUS_IDS.index(bus_id) + 1


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


def _stop_result(
    root: Path,
    *,
    manifest: dict[str, object] | None = None,
) -> Any:
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            manifest
            or {
                "schema_version": 2,
                "stems": [
                    {"label": "application", "source_id": 9_007_199_254_740_993},
                    {"label": "microphone", "source_id": 9_007_199_254_740_995},
                ],
            }
        )
    )
    recording = SimpleNamespace(
        session_id=17,
        group_id="session.multistem.default.v1",
        state=SimpleNamespace(value="complete"),
        complete=True,
        completed_stems=2,
        failed_stems=0,
        session_directory=root,
        manifest_path=manifest_path,
        manifest_schema_version=2,
        error_code=None,
        stems=tuple(_recording_stem(label) for label in _BUS_IDS),
    )
    return SimpleNamespace(
        success=True,
        already_stopped=False,
        disposition=SimpleNamespace(value="stopped"),
        session_state=SimpleNamespace(value="stopped"),
        runtime_worker_panicked=False,
        capture_finalization_failures_total=0,
        operator_finalization_failures_total=0,
        endpoint_finalization_failures_total=0,
        runtime_failures_total=0,
        lineage_failures_total=0,
        source_send_rejections_total=0,
        runtime_events_total=1,
        recording=recording,
        metrics=None,
        metrics_unavailable_reason="fixture",
        relay_outcomes=tuple(_relay_outcome(bus_id) for bus_id in _BUS_IDS),
    )


def _recording_stem(label: str) -> Any:
    return SimpleNamespace(
        stem_name=label,
        frames_written_total=10,
        stale_frames_total=0,
        error=None,
        queue_capacity_frames=8,
        queue_peak_frames=2,
        frames_delivered_total=10,
        frames_dropped_total=0,
        queue_full_drops_total=0,
        discontinuities_total=0,
        discontinuities=(),
    )


def _relay_outcome(bus_id: str) -> Any:
    return SimpleNamespace(
        bus_id=bus_id,
        endpoint_id=stem_id_for_bus(bus_id) + 20,
        route_id=stem_id_for_bus(bus_id) + 10,
        frames_received_total=10,
        rtp_packets_sent_total=5,
        rtp_payload_bytes_sent_total=500,
        ingress_queue_drops_total=0,
        publisher_stale_drops_total=0,
        cancelled_output_frames_total=0,
        cancelled_output_samples_total=0,
        failures_total=0,
        error=None,
    )
