"""Complete immutable metrics projection tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pocketstation._native as _native
import pytest
from pocketstation._api import (
    EndpointObservationStage,
    PocketStationError,
    RouteDeliveryMetrics,
    RouteLatencyMeasurement,
    Session,
    Source,
)


def test_metrics_preserve_bounded_source_route_and_polled_audio_truth(tmp_path) -> None:
    if not hasattr(_native.Session, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")

    session = Session._from_native(_native.Session.conformance(tmp_path))
    application = session.capture(Source.application("PocketStation Python Fixture"))
    microphone = session.capture(Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)

    with session.start() as running:
        observed = set()
        while len(observed) < 2:
            frame = running.audio.read(timeout_s=1.0)
            assert frame is not None
            observed.add(frame.stem_id)
        metrics = running.metrics()

    assert metrics.source_count == 2
    assert metrics.route_count == 2
    assert len(metrics.sources) == 2
    assert len(metrics.routes) == 2
    assert metrics.polled_audio.registered_endpoints == 2
    assert metrics.polled_audio.queue_capacity_frames > 0
    assert metrics.event_queue.capacity_count > 0
    assert all(route.delivery.queue_capacity_frames > 0 for route in metrics.routes)
    assert all(
        isinstance(route.delivery, RouteDeliveryMetrics) for route in metrics.routes
    )
    assert all(
        route.endpoint.observation_stage is EndpointObservationStage.LIVE
        for route in metrics.routes
    )
    assert all(route.source_latency_unit == "nanoseconds" for route in metrics.routes)
    assert all(
        route.source_latency_measurement
        is RouteLatencyMeasurement.SOURCE_TIMESTAMP_TO_ROUTE_RECEIVE
        for route in metrics.routes
    )
    with pytest.raises(FrozenInstanceError):
        metrics.polled_audio.queue_capacity_frames = 0


def test_metrics_count_mismatch_is_rejected_instead_of_hidden() -> None:
    class InvalidMetrics:
        source_count = 1
        external_source_count = 0
        route_count = 0
        operator_count = 0
        derived_route_count = 0
        audio_reentry_count = 0
        sources = ()
        external_sources = ()
        routes = ()
        operators = ()
        derived_routes = ()
        audio_reentries = ()
        event_capacity_count = 1
        event_maximum_event_owned_bytes = 1
        event_maximum_buffered_owned_bytes = 1
        event_depth_count = 0
        event_depth_owned_bytes = 0
        event_peak_depth_count = 0
        event_peak_depth_owned_bytes = 0
        events_enqueued_total = 0
        events_dropped_total = 0
        events_dropped_oversized_total = 0
        event_receiver_closed_total = 0
        audio_registered_endpoints = 0
        audio_queue_capacity_frames = 0
        audio_queue_depth_frames = 0
        audio_queue_peak_frames = 0
        audio_queue_depth_invariant_failures_total = 0
        audio_frames_received_total = 0
        audio_frames_delivered_total = 0
        audio_queue_full_drops_total = 0
        audio_invalid_ownership_drops_total = 0
        audio_discarded_output_frames_total = 0
        audio_lease_capacity_count = 0
        audio_outstanding_leases = 0
        audio_lease_exhausted_total = 0
        audio_batches_polled_total = 0
        audio_frames_polled_total = 0

    from pocketstation.observations import SessionMetrics

    with pytest.raises(PocketStationError, match="counts are inconsistent"):
        SessionMetrics._from_native(InvalidMetrics())
