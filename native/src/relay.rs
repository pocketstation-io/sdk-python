use std::sync::{Arc, Mutex};

use pocketstation::connector::RegisteredConnector;
use pocketstation_relay::{RelayConnector, RelayPublishReceiptKey};
use pyo3::prelude::*;

#[pyclass(name = "RelayPublisher", frozen)]
pub(crate) struct PythonRelayPublisher {
    pub(crate) session: Arc<Mutex<Option<pocketstation::Session>>>,
    pub(crate) registered: RegisteredConnector,
    pub(crate) relay_url: String,
    pub(crate) relay_session_id: String,
    pub(crate) source_token: String,
    pub(crate) routes: Arc<Mutex<Vec<RelayRouteRegistration>>>,
}

pub(crate) struct RelayRouteRegistration {
    pub(crate) bus_id: String,
    pub(crate) key: RelayPublishReceiptKey,
}

pub(crate) struct RelayRuntime {
    pub(crate) connector: Arc<RelayConnector>,
    pub(crate) routes: Vec<(String, RelayPublishReceiptKey)>,
}

#[pyclass(name = "RelayPublishOutcome", frozen)]
pub(crate) struct PythonRelayPublishOutcome {
    #[pyo3(get)]
    bus_id: String,
    #[pyo3(get)]
    endpoint_id: u64,
    #[pyo3(get)]
    route_id: u64,
    #[pyo3(get)]
    frames_received_total: u64,
    #[pyo3(get)]
    rtp_packets_sent_total: u64,
    #[pyo3(get)]
    rtp_payload_bytes_sent_total: u64,
    #[pyo3(get)]
    ingress_queue_drops_total: u64,
    #[pyo3(get)]
    publisher_stale_drops_total: u64,
    #[pyo3(get)]
    cancelled_output_frames_total: u64,
    #[pyo3(get)]
    cancelled_output_samples_total: u64,
    #[pyo3(get)]
    failures_total: u64,
    #[pyo3(get)]
    error: Option<String>,
}

pub(crate) struct OwnedRelayPublishOutcome {
    pub(crate) bus_id: String,
    pub(crate) endpoint_id: u64,
    pub(crate) route_id: u64,
    pub(crate) frames_received_total: u64,
    pub(crate) rtp_packets_sent_total: u64,
    pub(crate) rtp_payload_bytes_sent_total: u64,
    pub(crate) ingress_queue_drops_total: u64,
    pub(crate) publisher_stale_drops_total: u64,
    pub(crate) cancelled_output_frames_total: u64,
    pub(crate) cancelled_output_samples_total: u64,
    pub(crate) failures_total: u64,
    pub(crate) error: Option<String>,
}

pub(crate) fn owned_relay_outcomes(relay: Option<&RelayRuntime>) -> Vec<OwnedRelayPublishOutcome> {
    let Some(relay) = relay else {
        return Vec::new();
    };
    relay
        .routes
        .iter()
        .map(|(bus_id, key)| {
            relay.connector.take_result(*key).map_or_else(
                || OwnedRelayPublishOutcome {
                    bus_id: bus_id.clone(),
                    endpoint_id: key.endpoint_id.get(),
                    route_id: key.route_id.get(),
                    frames_received_total: 0,
                    rtp_packets_sent_total: 0,
                    rtp_payload_bytes_sent_total: 0,
                    ingress_queue_drops_total: 0,
                    publisher_stale_drops_total: 0,
                    cancelled_output_frames_total: 0,
                    cancelled_output_samples_total: 0,
                    failures_total: 1,
                    error: Some("relay publication result is unavailable".to_owned()),
                },
                |result| OwnedRelayPublishOutcome {
                    bus_id: bus_id.clone(),
                    endpoint_id: key.endpoint_id.get(),
                    route_id: key.route_id.get(),
                    frames_received_total: result.edge_observations.frames_delivered_total,
                    rtp_packets_sent_total: result.statistics.rtp_packets_sent_total,
                    rtp_payload_bytes_sent_total: result.statistics.rtp_payload_bytes_sent_total,
                    ingress_queue_drops_total: result.statistics.ingress_queue_drops_total,
                    publisher_stale_drops_total: result.statistics.publisher_stale_drops_total,
                    cancelled_output_frames_total: result
                        .statistics
                        .cancelled_output_frames_total,
                    cancelled_output_samples_total: result
                        .statistics
                        .cancelled_output_samples_total,
                    failures_total: u64::from(result.error.is_some()),
                    error: result.error.map(|error| error.to_string()),
                },
            )
        })
        .collect()
}

pub(crate) fn python_relay_outcome(
    py: Python<'_>,
    outcome: OwnedRelayPublishOutcome,
) -> PyResult<Py<PythonRelayPublishOutcome>> {
    Py::new(
        py,
        PythonRelayPublishOutcome {
            bus_id: outcome.bus_id,
            endpoint_id: outcome.endpoint_id,
            route_id: outcome.route_id,
            frames_received_total: outcome.frames_received_total,
            rtp_packets_sent_total: outcome.rtp_packets_sent_total,
            rtp_payload_bytes_sent_total: outcome.rtp_payload_bytes_sent_total,
            ingress_queue_drops_total: outcome.ingress_queue_drops_total,
            publisher_stale_drops_total: outcome.publisher_stale_drops_total,
            cancelled_output_frames_total: outcome.cancelled_output_frames_total,
            cancelled_output_samples_total: outcome.cancelled_output_samples_total,
            failures_total: outcome.failures_total,
            error: outcome.error,
        },
    )
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonRelayPublisher>()?;
    module.add_class::<PythonRelayPublishOutcome>()?;
    Ok(())
}
