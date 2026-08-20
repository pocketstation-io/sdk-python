"""Run the real Python → Rust connector → relay path for aggregate E2E."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import sleep
from typing import Any

import pocketstation as pks


def emit(message_type: str, **fields: Any) -> None:
    print(json.dumps({"type": message_type, **fields}, sort_keys=True), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-plane-url", required=True)
    parser.add_argument("--relay-url", required=True)
    parser.add_argument("--recording-root", type=Path, required=True)
    parser.add_argument("--active-seconds", type=float, default=2.0)
    application_selector = parser.add_mutually_exclusive_group()
    application_selector.add_argument("--application-name")
    application_selector.add_argument("--application-process-id", type=int)
    arguments = parser.parse_args()
    if arguments.active_seconds <= 0:
        parser.error("--active-seconds must be positive")
    if (
        arguments.application_name is None
        and arguments.application_process_id is None
        and not hasattr(pks._native.Session, "conformance")
    ):
        emit("failure", code="relay.conformance_fixture_unavailable")
        return 2

    remote: pks.RelaySession | None = None
    running: pks.RunningSession | None = None
    try:
        remote = pks.RelaySession.create(
            control_plane_url=arguments.control_plane_url,
            relay_url=arguments.relay_url,
        )
        if (
            arguments.application_name is None
            and arguments.application_process_id is None
        ):
            session = pks.Session._from_native(
                pks._native.Session.conformance(arguments.recording_root)
            )
            application_source = pks.Source.application("PocketStation Python Fixture")
            source_mode = "conformance-fixture"
        elif arguments.application_process_id is not None:
            session = pks.Session(recording_root=arguments.recording_root)
            application_source = pks.Source.application_process_id(
                arguments.application_process_id
            )
            source_mode = "physical"
        else:
            assert arguments.application_name is not None
            matches = tuple(
                source
                for source in pks.discover_sources()
                if source.name == arguments.application_name
                and source.stable_id.kind is pks.SourceKind.APPLICATION
            )
            if len(matches) != 1:
                raise RuntimeError(
                    "expected one application named "
                    f"{arguments.application_name!r}, found {len(matches)}"
                )
            session = pks.Session(recording_root=arguments.recording_root)
            application_source = pks.Source.from_discovered(matches[0])
            source_mode = "physical"
        application = session.capture(application_source)
        microphone = session.capture(pks.Source.microphone_default())
        publisher = session.relay(remote)
        routes = (
            application.publish(publisher, "application"),
            microphone.publish(publisher, "microphone"),
        )
        application.record("application")
        microphone.record("microphone")

        running = session.start()
        invitation = remote.wait_for_publisher_and_invitation(
            timeout_seconds=15.0,
            poll_interval_seconds=0.05,
        )
        emit(
            "invitation",
            session_id=str(remote.session_id),
            join_code=invitation.join_code,
            join_url=invitation.join_url,
            buses=[route.bus_id for route in routes],
            route_ids=[route.route_id for route in routes],
            source_mode=source_mode,
        )

        receiver = remote.wait_for_receiver(
            timeout_seconds=20.0,
            poll_interval_seconds=0.05,
        )
        emit(
            "receiver-active",
            session_id=str(remote.session_id),
            source_active=receiver.snapshot.source_active,
            subscription_count=receiver.snapshot.subscription_count,
        )
        sleep(arguments.active_seconds)

        stop = running.stop()
        running = None
        recording = stop.recording
        relay_outcomes = [
            {
                "bus_id": outcome.bus_id,
                "frames_received_total": outcome.frames_received_total,
                "rtp_packets_sent_total": outcome.rtp_packets_sent_total,
                "rtp_payload_bytes_sent_total": outcome.rtp_payload_bytes_sent_total,
                "ingress_queue_drops_total": outcome.ingress_queue_drops_total,
                "publisher_stale_drops_total": outcome.publisher_stale_drops_total,
                "failures_total": outcome.failures_total,
                "error": outcome.error,
            }
            for outcome in stop.relay_outcomes
        ]
        recording_stems = (
            []
            if recording is None
            else [
                {
                    "stem_name": stem.stem_name,
                    "frames_written_total": stem.frames_written_total,
                    "frames_dropped_total": stem.frames_dropped_total,
                    "discontinuities_total": stem.discontinuities_total,
                    "error": stem.error,
                }
                for stem in recording.stems
            ]
        )
        expected_buses = {"application", "microphone"}
        success = (
            stop.success
            and recording is not None
            and recording.complete
            and {stem["stem_name"] for stem in recording_stems} == expected_buses
            and all(stem["frames_written_total"] > 0 for stem in recording_stems)
            and {outcome["bus_id"] for outcome in relay_outcomes} == expected_buses
            and all(
                outcome["frames_received_total"] > 0
                and outcome["rtp_packets_sent_total"] > 0
                and outcome["failures_total"] == 0
                and outcome["error"] is None
                for outcome in relay_outcomes
            )
        )
        remote.close()
        remote = None
        emit(
            "final",
            success=success,
            recording_complete=recording is not None and recording.complete,
            recording_stems=recording_stems,
            relay_outcomes=relay_outcomes,
        )
        return 0 if success else 3
    except BaseException as error:
        emit(
            "failure",
            error_type=type(error).__name__,
            code=getattr(error, "code", "relay.e2e_failure"),
        )
        return 1
    finally:
        if running is not None:
            try:
                running.cancel()
            except BaseException:
                pass
        if remote is not None:
            try:
                remote.close()
            except BaseException:
                pass


if __name__ == "__main__":
    sys.exit(main())
