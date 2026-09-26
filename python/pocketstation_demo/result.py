"""Authoritative output for the installed PocketStation demo."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pocketstation.aio as pks
from pocketstation.aio.capture import Capture
from pocketstation.observations import (
    RecordingOutcome,
    RecordingStemOutcome,
    RouteMetrics,
    SessionMetrics,
    StopResult,
)
from pocketstation.relay import (
    PublisherActivation,
    ReceiverActivation,
    ReceiverInvitation,
    RelayRoute,
)

from .transcript import Transcript


class DemoOutput:
    """Render human output or the stable JSON Lines automation stream."""

    def __init__(self, output_format: str) -> None:
        self._jsonl = output_format == "jsonl"

    def invitation(self, bus_id: str, invitation: ReceiverInvitation) -> str:
        # expose_url() is intentionally called only at this explicit display or
        # automation boundary. Invitation repr/str remain redacted.
        share_url = invitation.expose_url()
        if self._jsonl:
            self._json(
                {
                    "event": "invitation",
                    "bus_id": bus_id,
                    "share_url": share_url,
                }
            )
        else:
            print(f"{bus_id.title()} invitation: {invitation.share_alias}", flush=True)
            print(f"{bus_id.title()} listen URL: {share_url}", flush=True)
        return share_url

    def receivers_connected(self) -> None:
        if not self._jsonl:
            print("Both browser receivers connected.", flush=True)

    def transcript(self, transcript: Transcript) -> None:
        if self._jsonl:
            self._json(
                {
                    "event": "transcript",
                    "source_id": str(transcript.source_id),
                    "text": transcript.text,
                }
            )
        else:
            print(
                f"source {transcript.source_id}: {transcript.text}",
                flush=True,
            )

    def completed(self, result: Mapping[str, object]) -> None:
        if self._jsonl:
            self._json(dict(result))
        else:
            status = str(result["status"])
            print(
                "Capture finished with "
                f"status {status}; inspect the recording manifest for final details.",
                flush=True,
            )

    @staticmethod
    def _json(value: dict[str, object]) -> None:
        print(json.dumps(value, separators=(",", ":"), sort_keys=False), flush=True)


def result_event(
    live: Capture,
    remote: pks.RelaySession,
    relay_routes: Mapping[str, RelayRoute],
    stop: StopResult,
    *,
    duration_seconds: float,
) -> dict[str, object]:
    """Build the final secret-free result from public SDK observations."""
    source_ids, manifest_gap = _recording_source_ids(stop.recording)
    api_gaps = [
        {
            "field": "live_source_id",
            "detail": (
                "Capture Stem exposes stem_id but not source_id; final source IDs "
                "are read from the public recording manifest after Session stop."
            ),
        },
        {
            "field": "receiver_playout",
            "detail": (
                "RelaySession reports active subscriptions but not browser decode "
                "or loudspeaker playout; the Lab receiver proves those separately."
            ),
        },
    ]
    if manifest_gap is not None:
        api_gaps.append(
            {"field": "recording_manifest_source_id", "detail": manifest_gap}
        )
    metrics = stop.metrics
    receiver_count = (
        0
        if remote.receiver_activation is None
        else remote.receiver_activation.snapshot.subscription_count
    )
    return {
        "event": "result",
        "status": "completed" if stop.success else "failed",
        "duration_seconds": duration_seconds,
        "receiver_count": receiver_count,
        "session_id": str(live.application_stem.session_id),
        "relay_session_id": str(remote.session_id),
        "source_ids": source_ids,
        "session": _stop_result(stop),
        "sources": _source_observations(live, metrics, source_ids),
        "recording": _recording_result(stop.recording, source_ids),
        "relay": _relay_result(remote, relay_routes, stop, metrics),
        "api_gaps": api_gaps,
    }


def _stop_result(stop: StopResult) -> dict[str, object]:
    return {
        "success": stop.success,
        "already_stopped": stop.already_stopped,
        "disposition": stop.disposition.value,
        "state": stop.session_state.value,
        "runtime_worker_panicked": stop.runtime_worker_panicked,
        "capture_finalization_failures_total": (
            stop.capture_finalization_failures_total
        ),
        "operator_finalization_failures_total": (
            stop.operator_finalization_failures_total
        ),
        "endpoint_finalization_failures_total": (
            stop.endpoint_finalization_failures_total
        ),
        "runtime_failures_total": stop.runtime_failures_total,
        "lineage_failures_total": stop.lineage_failures_total,
        "source_send_rejections_total": stop.source_send_rejections_total,
        "runtime_events_total": stop.runtime_events_total,
        "metrics_available": stop.metrics is not None,
        "metrics_unavailable_reason": stop.metrics_unavailable_reason,
    }


def _recording_source_ids(
    recording: RecordingOutcome | None,
) -> tuple[dict[str, str | None], str | None]:
    missing: dict[str, str | None] = {
        "application": None,
        "microphone": None,
    }
    if recording is None:
        return missing, "StopResult contains no RecordingOutcome."
    try:
        payload: Any = json.loads(recording.manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return missing, f"recording manifest could not be read: {type(error).__name__}"
    if not isinstance(payload, dict):
        return missing, "recording manifest root is not an object."
    stems = payload.get("stems")
    if not isinstance(stems, list):
        return missing, "recording manifest contains no stems array."
    result = dict(missing)
    for stem in stems:
        if not isinstance(stem, dict):
            continue
        label = stem.get("label")
        source_id = stem.get("source_id")
        if (
            label in result
            and isinstance(source_id, int)
            and not isinstance(source_id, bool)
            and source_id > 0
        ):
            result[label] = str(source_id)
    absent = [label for label, source_id in result.items() if source_id is None]
    if absent:
        return result, (
            "recording manifest omitted a positive source_id for: " + ", ".join(absent)
        )
    return result, None


def _recording_result(
    recording: RecordingOutcome | None,
    source_ids: Mapping[str, str | None],
) -> dict[str, object] | None:
    if recording is None:
        return None
    return {
        "session_id": str(recording.session_id),
        "group_id": recording.group_id,
        "state": recording.state.value,
        "complete": recording.complete,
        "completed_stems": recording.completed_stems,
        "failed_stems": recording.failed_stems,
        "session_directory": str(recording.session_directory),
        "manifest_path": str(recording.manifest_path),
        "manifest_schema_version": recording.manifest_schema_version,
        "error_code": recording.error_code,
        "stems": [
            _recording_stem_result(stem, source_ids.get(stem.stem_name))
            for stem in recording.stems
        ],
    }


def _recording_stem_result(
    stem: RecordingStemOutcome,
    source_id: str | None,
) -> dict[str, object]:
    return {
        "stem_name": stem.stem_name,
        "source_id": source_id,
        "frames_written_total": stem.frames_written_total,
        "stale_frames_total": stem.stale_frames_total,
        "error": stem.error,
        "queue_capacity_frames": stem.queue_capacity_frames,
        "queue_peak_frames": stem.queue_peak_frames,
        "frames_delivered_total": stem.frames_delivered_total,
        "frames_dropped_total": stem.frames_dropped_total,
        "queue_full_drops_total": stem.queue_full_drops_total,
        "discontinuities_total": stem.discontinuities_total,
        "discontinuities": [
            {
                "stem_id": str(item.stem_id),
                "label": item.label,
                "type": item.kind.value,
                "timestamp_start_ns": str(item.timestamp_start_ns),
                "timestamp_end_ns": str(item.timestamp_end_ns),
                "sequence_start": _decimal(item.sequence_start),
                "sequence_end": _decimal(item.sequence_end),
            }
            for item in stem.discontinuities
        ],
    }


def _source_observations(
    live: Capture,
    metrics: SessionMetrics | None,
    source_ids: Mapping[str, str | None],
) -> list[dict[str, object]]:
    microphone = live.microphone_stem
    if microphone is None:
        raise RuntimeError("the installed demo requires a microphone stem")
    stems = {
        int(live.application_stem.id): ("application", live.application_stem),
        int(microphone.id): ("microphone", microphone),
    }
    if metrics is None:
        return [
            {
                "label": label,
                "stem_id": str(stem.id),
                "source_id": source_ids.get(label),
                "metrics": None,
            }
            for label, stem in stems.values()
        ]

    observations: list[dict[str, object]] = []
    for index, source in enumerate(metrics.sources):
        identified = stems.get(int(source.stem_id))
        if identified is None:
            continue
        label, stem = identified
        activity = metrics.source_activities[index]
        signal = metrics.source_signals[index]
        native_format = metrics.source_native_formats[index].opened_native_format
        replacement = metrics.source_replacements[index]
        observations.append(
            {
                "label": label,
                "stem_id": str(stem.id),
                "source_id": source_ids.get(label),
                "capture": {
                    "callback_buffers_total": source.callback_buffers_total,
                    "frames_enqueued_total": source.capture_frames_enqueued_total,
                    "pool_exhausted_total": source.capture_pool_exhausted_total,
                    "dispatch_queue_full_total": (
                        source.capture_dispatch_queue_full_total
                    ),
                    "invalid_buffer_total": source.capture_invalid_buffer_total,
                    "oversized_buffer_total": source.capture_oversized_buffer_total,
                    "stream_errors_total": source.capture_stream_errors_total,
                    "frame_stream_dropped_total": (
                        source.frame_stream_dropped_newest_frames_total
                    ),
                    "ingress_rejected_full_total": (
                        source.ingress_frames_rejected_full_total
                    ),
                    "ingress_rejected_cancelled_total": (
                        source.ingress_frames_rejected_cancelled_total
                    ),
                    "ingress_discarded_total": source.ingress_frames_discarded_total,
                    "runtime_event_drops_total": (
                        source.runtime_event_queue.dropped_total
                    ),
                },
                "activity": {
                    "frames_received_total": activity.frames_received_total,
                    "first_frame_received_at_ns": _decimal(
                        activity.first_frame_received_at_ns
                    ),
                    "latest_frame_received_at_ns": _decimal(
                        activity.latest_frame_received_at_ns
                    ),
                },
                "signal": {
                    "samples_observed_total": signal.samples_observed_total,
                    "nonzero_samples_observed_total": (
                        signal.nonzero_samples_observed_total
                    ),
                    "nonfinite_samples_observed_total": (
                        signal.nonfinite_samples_observed_total
                    ),
                    "window_source_generation": signal.window_source_generation,
                    "window_discontinuity_epoch": signal.window_discontinuity_epoch,
                    "window_peak_dbfs": signal.window_peak_dbfs,
                    "window_rms_dbfs": signal.window_rms_dbfs,
                    "consecutive_exact_zero_duration_ns": str(
                        signal.consecutive_exact_zero_duration_ns
                    ),
                },
                "native_format": (
                    None
                    if native_format is None
                    else {
                        "sample_rate_hz": native_format.sample_rate_hz,
                        "channel_count": native_format.channel_count,
                        "sample_representation": (
                            native_format.sample_representation.value
                        ),
                    }
                ),
                "replacement": {
                    "attempts_total": replacement.attempts_total,
                    "completed_total": replacement.completed_total,
                    "failed_before_attach_total": (
                        replacement.failed_before_attach_total
                    ),
                    "response_timeouts_total": replacement.response_timeouts_total,
                    "source_generation": replacement.source_generation,
                    "discontinuity_epoch": replacement.discontinuity_epoch,
                },
            }
        )
    return observations


def _relay_result(
    remote: pks.RelaySession,
    declared_routes: Mapping[str, RelayRoute],
    stop: StopResult,
    metrics: SessionMetrics | None,
) -> dict[str, object]:
    routes_by_id = (
        {}
        if metrics is None
        else {int(route.route_id): route for route in metrics.routes}
    )
    return {
        "publisher": _activation(remote.publisher_activation),
        "receiver": _activation(remote.receiver_activation),
        "declared_buses": [
            {"bus_id": bus_id, "route_id": str(route.route_id)}
            for bus_id, route in declared_routes.items()
        ],
        "outcomes": [
            {
                "bus_id": outcome.bus_id,
                "endpoint_id": str(outcome.endpoint_id),
                "route_id": str(outcome.route_id),
                "frames_received_total": outcome.frames_received_total,
                "rtp_packets_sent_total": outcome.rtp_packets_sent_total,
                "rtp_payload_bytes_sent_total": outcome.rtp_payload_bytes_sent_total,
                "ingress_queue_drops_total": outcome.ingress_queue_drops_total,
                "publisher_stale_drops_total": outcome.publisher_stale_drops_total,
                "cancelled_output_frames_total": (
                    outcome.cancelled_output_frames_total
                ),
                "cancelled_output_samples_total": (
                    outcome.cancelled_output_samples_total
                ),
                "failures_total": outcome.failures_total,
                "error": outcome.error,
                "route_observations": _route_observations(
                    routes_by_id.get(int(outcome.route_id))
                ),
            }
            for outcome in stop.relay_outcomes
        ],
    }


def _activation(
    activation: PublisherActivation | ReceiverActivation | None,
) -> dict[str, object] | None:
    if activation is None:
        return None
    snapshot = activation.snapshot
    return {
        "ready": snapshot.ready,
        "subscription_count": snapshot.subscription_count,
        "buses": [
            {
                "bus_id": bus.bus_id,
                "source_active": bus.source_active,
                "source_generation": bus.source_generation,
            }
            for bus in snapshot.buses
        ],
        "subscription_buses": [item.bus_id for item in snapshot.subscriptions],
    }


def _route_observations(route: RouteMetrics | None) -> dict[str, object] | None:
    if route is None:
        return None
    delivery = route.delivery
    return {
        "frames_enqueued_total": delivery.frames_enqueued_total,
        "frames_delivered_total": delivery.frames_delivered_total,
        "frames_dropped_total": delivery.frames_dropped_total,
        "overruns_total": delivery.overruns_total,
        "receiver_unavailable_drops_total": delivery.receiver_unavailable_drops_total,
        "queue_full_drops_total": delivery.queue_full_drops_total,
        "shared_reference_exhausted_drops_total": (
            delivery.shared_reference_exhausted_drops_total
        ),
        "branch_pool_exhausted_drops_total": (
            delivery.branch_pool_exhausted_drops_total
        ),
        "invalid_copy_policy_drops_total": delivery.invalid_copy_policy_drops_total,
        "freeze_failed_drops_total": delivery.freeze_failed_drops_total,
        "discontinuities_total": delivery.discontinuities_total,
        "source_identity_discontinuities_total": (
            delivery.source_identity_discontinuities_total
        ),
        "sequence_discontinuities_total": delivery.sequence_discontinuities_total,
        "timestamp_discontinuities_total": delivery.timestamp_discontinuities_total,
        "lineage_epoch_discontinuities_total": (
            delivery.lineage_epoch_discontinuities_total
        ),
        "manually_reported_discontinuities_total": (
            delivery.manually_reported_discontinuities_total
        ),
        "worker_failures_total": delivery.worker_failures_total,
        "shutdown_discarded_total": delivery.shutdown_discarded_total,
        "endpoint_frames_dropped_total": route.endpoint.frames_dropped_total,
        "endpoint_discontinuities_total": route.endpoint.discontinuities_total,
        "endpoint_failures_total": route.endpoint.failures_total,
        "endpoint_finalization_failures_total": (
            route.endpoint.finalization_failures_total
        ),
    }


def _decimal(value: int | None) -> str | None:
    return None if value is None else str(value)
