use pocketstation::connector::{
    ConnectorError, ConnectorErrorStage, ConnectorObservations, ConnectorRetryability,
    ConnectorRuntimeObservations, ConnectorServiceStatus,
};
use pyo3::prelude::*;

#[pyclass(name = "_ConnectorErrorSnapshot", frozen)]
pub(crate) struct PythonConnectorErrorSnapshot {
    #[pyo3(get)]
    code: String,
    #[pyo3(get)]
    stage: &'static str,
    #[pyo3(get)]
    retryability: &'static str,
    #[pyo3(get)]
    message: String,
}

#[pyclass(name = "_ConnectorServiceStatus", frozen)]
pub(crate) struct PythonConnectorServiceStatus {
    #[pyo3(get)]
    delivery_readiness: &'static str,
    #[pyo3(get)]
    health: &'static str,
    #[pyo3(get)]
    recovery: &'static str,
    #[pyo3(get)]
    readiness_reason_code: Option<String>,
    #[pyo3(get)]
    health_reason_code: Option<String>,
    #[pyo3(get)]
    recovery_reason_code: Option<String>,
    #[pyo3(get)]
    revision: u64,
    #[pyo3(get)]
    last_transition_elapsed_ns: u64,
    #[pyo3(get)]
    accepts_delivery: bool,
}

#[pyclass(name = "_ConnectorObservations", frozen)]
pub(crate) struct PythonConnectorObservations {
    #[pyo3(get)]
    service_status: Py<PythonConnectorServiceStatus>,
    #[pyo3(get)]
    status_transitions_total: u64,
    #[pyo3(get)]
    retry_attempts_total: u64,
    #[pyo3(get)]
    reconnects_total: u64,
    #[pyo3(get)]
    failures_total: u64,
    #[pyo3(get)]
    last_error: Option<Py<PythonConnectorErrorSnapshot>>,
}

#[pyclass(name = "_ConnectorRuntimeObservations", frozen)]
pub(crate) struct PythonConnectorRuntimeObservations {
    #[pyo3(get)]
    endpoint_ids: Vec<u64>,
    #[pyo3(get)]
    connector: Py<PythonConnectorObservations>,
    #[pyo3(get)]
    frames_received_total: u64,
    #[pyo3(get)]
    frames_delivered_total: u64,
    #[pyo3(get)]
    frames_dropped_total: u64,
    #[pyo3(get)]
    discontinuities_total: u64,
    #[pyo3(get)]
    endpoint_failures_total: u64,
}

pub(crate) fn python_connector_observations(
    py: Python<'_>,
    value: ConnectorObservations,
) -> PyResult<Py<PythonConnectorObservations>> {
    let service_status = Py::new(py, python_service_status(value.service_status))?;
    let last_error = value
        .last_error
        .map(|error| Py::new(py, python_error_snapshot(error)))
        .transpose()?;
    Py::new(
        py,
        PythonConnectorObservations {
            service_status,
            status_transitions_total: value.status_transitions_total,
            retry_attempts_total: value.retry_attempts_total,
            reconnects_total: value.reconnects_total,
            failures_total: value.failures_total,
            last_error,
        },
    )
}

pub(crate) fn python_runtime_observations(
    py: Python<'_>,
    value: ConnectorRuntimeObservations,
) -> PyResult<Py<PythonConnectorRuntimeObservations>> {
    let connector = python_connector_observations(py, value.connector)?;
    Py::new(
        py,
        PythonConnectorRuntimeObservations {
            endpoint_ids: value.endpoint_ids.iter().map(|id| id.get()).collect(),
            connector,
            frames_received_total: value.endpoint.frames_received_total,
            frames_delivered_total: value.endpoint.frames_delivered_total,
            frames_dropped_total: value.endpoint.frames_dropped_total,
            discontinuities_total: value.endpoint.discontinuities_total,
            endpoint_failures_total: value.endpoint.failures_total,
        },
    )
}

fn python_service_status(value: ConnectorServiceStatus) -> PythonConnectorServiceStatus {
    PythonConnectorServiceStatus {
        delivery_readiness: match value.delivery_readiness() {
            pocketstation::connector::ConnectorDeliveryReadiness::NotReady => "not-ready",
            pocketstation::connector::ConnectorDeliveryReadiness::Ready => "ready",
        },
        health: match value.health() {
            pocketstation::connector::ConnectorHealth::Healthy => "healthy",
            pocketstation::connector::ConnectorHealth::Degraded => "degraded",
        },
        recovery: match value.recovery() {
            pocketstation::connector::ConnectorRecovery::Idle => "idle",
            pocketstation::connector::ConnectorRecovery::Reconnecting => "reconnecting",
        },
        readiness_reason_code: value
            .readiness_reason_code()
            .map(|code| code.as_str().to_owned()),
        health_reason_code: value
            .health_reason_code()
            .map(|code| code.as_str().to_owned()),
        recovery_reason_code: value
            .recovery_reason_code()
            .map(|code| code.as_str().to_owned()),
        revision: value.revision(),
        last_transition_elapsed_ns: value.last_transition_elapsed_ns(),
        accepts_delivery: value.accepts_delivery(),
    }
}

fn python_error_snapshot(value: ConnectorError) -> PythonConnectorErrorSnapshot {
    PythonConnectorErrorSnapshot {
        code: value.code().as_str().to_owned(),
        stage: stage_name(value.stage()),
        retryability: retryability_name(value.retryability()),
        message: value.message().to_owned(),
    }
}

fn stage_name(value: ConnectorErrorStage) -> &'static str {
    match value {
        ConnectorErrorStage::Configuration => "configuration",
        ConnectorErrorStage::Prepare => "prepare",
        ConnectorErrorStage::Startup => "startup",
        ConnectorErrorStage::Readiness => "readiness",
        ConnectorErrorStage::Delivery => "delivery",
        ConnectorErrorStage::Retry => "retry",
        ConnectorErrorStage::Shutdown => "shutdown",
        ConnectorErrorStage::Join => "join",
    }
}

fn retryability_name(value: ConnectorRetryability) -> &'static str {
    match value {
        ConnectorRetryability::Never => "never",
        ConnectorRetryability::Retryable => "retryable",
        ConnectorRetryability::RetryAfterReconfiguration => "retry-after-reconfiguration",
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonConnectorErrorSnapshot>()?;
    module.add_class::<PythonConnectorServiceStatus>()?;
    module.add_class::<PythonConnectorObservations>()?;
    module.add_class::<PythonConnectorRuntimeObservations>()?;
    Ok(())
}
