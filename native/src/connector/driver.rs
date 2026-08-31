use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use pocketstation::connector::{
    Connector, ConnectorContext, ConnectorDeliveryOutcome, ConnectorDriver, ConnectorDriverFactory,
    ConnectorError, ConnectorErrorCode, ConnectorErrorStage, ConnectorInputDescriptor,
    ConnectorItem, ConnectorRetryability, RegisteredConnector,
};
use pocketstation::{
    EndpointGroupId, EndpointPreparationGroup, EndpointShutdownMode, RouteId, Session,
};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::observations::{python_connector_observations, python_runtime_observations};
use super::values::{
    configuration_values, PythonConnectorConfiguration, PythonConnectorConfigurationValue,
    PythonConnectorManifest,
};
use crate::errors::coded_reason;
use crate::graph::{PythonEdgeContract, PythonEndpoint, PythonMediaCaps, PythonSignalSpec};
use crate::signals::{copy_envelope, python_envelope, PythonSignalEnvelope};
use crate::streams::{owned_endpoint_audio_frame, python_audio_frame, PythonAudioFrame};

#[pyclass(name = "ConnectorInputDescriptor", frozen)]
pub(crate) struct PythonConnectorInputDescriptor {
    #[pyo3(get)]
    pub(super) endpoint_id: u64,
    #[pyo3(get)]
    pub(super) connector_id: Option<u64>,
    #[pyo3(get)]
    pub(super) route_id: u64,
    #[pyo3(get)]
    pub(super) port_name: String,
    #[pyo3(get)]
    pub(super) signal_wire_id: String,
    pub(super) signal: Py<PythonSignalSpec>,
    pub(super) media: Py<PythonMediaCaps>,
    pub(super) edge: Py<PythonEdgeContract>,
    pub(super) configuration: Vec<(String, Py<PythonConnectorConfigurationValue>)>,
}

#[pymethods]
impl PythonConnectorInputDescriptor {
    #[getter]
    fn configuration(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let values = PyDict::new(py);
        for (name, value) in &self.configuration {
            values.set_item(name, value.clone_ref(py))?;
        }
        Ok(values.unbind())
    }

    #[getter]
    fn signal(&self, py: Python<'_>) -> Py<PythonSignalSpec> {
        self.signal.clone_ref(py)
    }

    #[getter]
    fn media(&self, py: Python<'_>) -> Py<PythonMediaCaps> {
        self.media.clone_ref(py)
    }

    #[getter]
    fn edge(&self, py: Python<'_>) -> Py<PythonEdgeContract> {
        self.edge.clone_ref(py)
    }
}

#[pyclass(name = "ConnectorItem", frozen)]
pub(crate) struct PythonConnectorItem {
    #[pyo3(get)]
    pub(super) kind: &'static str,
    pub(super) input: Py<PythonConnectorInputDescriptor>,
    pub(super) audio: Option<Py<PythonAudioFrame>>,
    pub(super) signal: Option<Py<PythonSignalEnvelope>>,
}

#[pymethods]
impl PythonConnectorItem {
    #[getter]
    fn input(&self, py: Python<'_>) -> Py<PythonConnectorInputDescriptor> {
        self.input.clone_ref(py)
    }

    #[getter]
    fn audio(&self, py: Python<'_>) -> Option<Py<PythonAudioFrame>> {
        self.audio.as_ref().map(|value| value.clone_ref(py))
    }

    #[getter]
    fn signal(&self, py: Python<'_>) -> Option<Py<PythonSignalEnvelope>> {
        self.signal.as_ref().map(|value| value.clone_ref(py))
    }
}

#[pyclass(name = "ConnectorContext", frozen)]
pub(crate) struct PythonConnectorContext {
    context: ConnectorContext,
    active: Arc<AtomicBool>,
}

#[pymethods]
impl PythonConnectorContext {
    #[getter]
    fn stop_requested(&self) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.is_stop_requested())
    }

    #[getter]
    fn shutdown_mode(&self) -> PyResult<Option<&'static str>> {
        self.ensure_active()?;
        Ok(match self.context.shutdown_mode() {
            Some(EndpointShutdownMode::Drain) => Some("drain"),
            Some(EndpointShutdownMode::Abort) => Some("abort"),
            None => None,
        })
    }

    fn set_ready(&self) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.set_ready())
    }

    fn set_not_ready(&self, reason_code: Option<String>) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self
            .context
            .set_not_ready(reason_code.map(make_error_code).transpose()?))
    }

    fn set_degraded(&self, reason_code: String) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.set_degraded(make_error_code(reason_code)?))
    }

    fn set_healthy(&self) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.set_healthy())
    }

    fn set_reconnecting(&self, reason_code: String) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.set_reconnecting(make_error_code(reason_code)?))
    }

    fn set_connected(&self) -> PyResult<bool> {
        self.ensure_active()?;
        Ok(self.context.set_connected())
    }

    fn record_retry(&self) -> PyResult<()> {
        self.ensure_active()?;
        self.context.record_retry();
        Ok(())
    }
}

impl PythonConnectorContext {
    fn ensure_active(&self) -> PyResult<()> {
        if self.active.load(Ordering::Acquire) {
            Ok(())
        } else {
            Err(PyRuntimeError::new_err(coded_reason(
                "connector.context_closed",
                "Connector context is no longer active",
            )))
        }
    }
}

struct PythonDriverFactory {
    factory: Py<PyAny>,
}

impl ConnectorDriverFactory for PythonDriverFactory {
    fn preparation_group(
        &self,
        route_id: RouteId,
        configuration: &pocketstation::connector::ResolvedConnectorConfiguration,
    ) -> Result<EndpointPreparationGroup, ConnectorError> {
        Python::attach(|py| {
            let result = (|| -> PyResult<EndpointPreparationGroup> {
                let values = configuration_values(configuration)
                    .into_iter()
                    .map(|(name, value)| Py::new(py, value).map(|value| (name, value)))
                    .collect::<PyResult<Vec<_>>>()?;
                let configuration = PyDict::new(py);
                for (name, value) in values {
                    configuration.set_item(name, value)?;
                }
                let group = self
                    .factory
                    .bind(py)
                    .call_method1("preparation_group", (route_id.get(), configuration))?;
                if group.is_none() {
                    Ok(EndpointPreparationGroup::Route(route_id))
                } else {
                    let group = group.extract::<String>()?;
                    if group.trim().is_empty() {
                        return Err(PyValueError::new_err(coded_reason(
                            "connector.invalid_preparation_group",
                            "Connector preparation group cannot be empty",
                        )));
                    }
                    Ok(EndpointPreparationGroup::Shared(EndpointGroupId::new(
                        group,
                    )))
                }
            })();
            result.map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))
        })
    }

    fn prepare(
        &self,
        inputs: &[ConnectorInputDescriptor],
    ) -> Result<Box<dyn ConnectorDriver>, ConnectorError> {
        Python::attach(|py| {
            let descriptors = inputs
                .iter()
                .map(|input| python_input_descriptor(py, input))
                .collect::<PyResult<Vec<_>>>()
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))?;
            let driver = self
                .factory
                .bind(py)
                .call_method1("prepare", (descriptors,))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))?
                .unbind();
            let idle_enabled = driver
                .bind(py)
                .getattr("_pocketstation_idle_enabled")
                .and_then(|value| value.extract::<bool>())
                .unwrap_or(false);
            Ok(Box::new(PythonDriver {
                driver,
                active: Arc::new(AtomicBool::new(true)),
                idle_enabled,
            }) as Box<dyn ConnectorDriver>)
        })
    }
}

struct PythonDriver {
    driver: Py<PyAny>,
    active: Arc<AtomicBool>,
    idle_enabled: bool,
}

impl Drop for PythonDriver {
    fn drop(&mut self) {
        self.active.store(false, Ordering::Release);
    }
}

impl ConnectorDriver for PythonDriver {
    fn start(&mut self, context: &ConnectorContext) -> Result<(), ConnectorError> {
        self.call_context_method("start", context, ConnectorErrorStage::Startup)
    }

    fn deliver(
        &mut self,
        item: ConnectorItem<'_>,
        context: &ConnectorContext,
    ) -> Result<ConnectorDeliveryOutcome, ConnectorError> {
        Python::attach(|py| {
            let item = python_item(py, item)
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            let outcome = self
                .driver
                .bind(py)
                .call_method1("deliver", (item, context))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            if outcome.is_none() {
                return Ok(ConnectorDeliveryOutcome::Delivered);
            }
            match outcome
                .extract::<String>()
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?
                .as_str()
            {
                "delivered" => Ok(ConnectorDeliveryOutcome::Delivered),
                "dropped" => Ok(ConnectorDeliveryOutcome::Dropped),
                _ => Err(internal_error(
                    "python.invalid_delivery_outcome",
                    ConnectorErrorStage::Delivery,
                    "Python Connector deliver() must return 'delivered', 'dropped', or None",
                )),
            }
        })
    }

    fn idle(&mut self, context: &ConnectorContext) -> Result<(), ConnectorError> {
        if self.idle_enabled {
            self.call_context_method("idle", context, ConnectorErrorStage::Delivery)
        } else {
            Ok(())
        }
    }

    fn shutdown(
        &mut self,
        mode: EndpointShutdownMode,
        context: &ConnectorContext,
    ) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Shutdown))?;
            let mode = match mode {
                EndpointShutdownMode::Drain => "drain",
                EndpointShutdownMode::Abort => "abort",
            };
            self.driver
                .bind(py)
                .call_method1("shutdown", (mode, context))
                .map(|_| ())
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Shutdown))
        })
    }

    fn cancel_preparation(self: Box<Self>) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let result = self
                .driver
                .bind(py)
                .call_method0("cancel_preparation")
                .map(|_| ())
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare));
            self.active.store(false, Ordering::Release);
            result
        })
    }
}

impl PythonDriver {
    fn call_context_method(
        &self,
        method: &str,
        context: &ConnectorContext,
        stage: ConnectorErrorStage,
    ) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, stage))?;
            self.driver
                .bind(py)
                .call_method1(method, (context,))
                .map(|_| ())
                .map_err(|error| python_error(py, error, stage))
        })
    }
}

#[pyclass(name = "_RegisteredConnector", frozen)]
pub(crate) struct PythonRegisteredConnector {
    pub(super) registered: RegisteredConnector,
}

#[pymethods]
impl PythonRegisteredConnector {
    #[getter]
    fn session_id(&self) -> u64 {
        self.registered.session_id().get()
    }

    fn observations(
        &self,
        py: Python<'_>,
    ) -> PyResult<Vec<Py<super::observations::PythonConnectorRuntimeObservations>>> {
        self.registered
            .observations()
            .map_err(|error| {
                PyRuntimeError::new_err(coded_reason(
                    "connector.observations_unavailable",
                    error.to_string(),
                ))
            })?
            .into_iter()
            .map(|value| python_runtime_observations(py, value))
            .collect()
    }

    fn observation(
        &self,
        py: Python<'_>,
        endpoint: &PythonEndpoint,
    ) -> PyResult<Option<Py<super::observations::PythonConnectorObservations>>> {
        self.registered
            .observation(endpoint.handle)
            .map_err(|error| {
                PyValueError::new_err(coded_reason(
                    "connector.observation_lookup_failed",
                    error.to_string(),
                ))
            })?
            .map(|handle| {
                handle
                    .snapshot()
                    .map_err(|error| {
                        PyRuntimeError::new_err(coded_reason(
                            "connector.observation_unavailable",
                            error.to_string(),
                        ))
                    })
                    .and_then(|value| python_connector_observations(py, value))
            })
            .transpose()
    }
}

pub(crate) fn register_connector(
    session: &Session,
    manifest: &PythonConnectorManifest,
    factory: Py<PyAny>,
) -> PyResult<PythonRegisteredConnector> {
    let connector = Connector::with_driver(
        manifest.value.clone(),
        Arc::new(PythonDriverFactory { factory }),
    )
    .map_err(|error| {
        PyValueError::new_err(coded_reason(
            "connector.invalid_contract",
            error.to_string(),
        ))
    })?;
    session
        .register_connector(connector)
        .map(|registered| PythonRegisteredConnector { registered })
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "connector.registration_failed",
                error.to_string(),
            ))
        })
}

pub(crate) fn declare_connector(
    registered: &PythonRegisteredConnector,
    session: &Session,
    configuration: &PythonConnectorConfiguration,
    edge: &PythonEdgeContract,
) -> PyResult<PythonEndpoint> {
    registered
        .registered
        .declare(session, configuration.value.clone(), edge.value)
        .map(|handle| PythonEndpoint { handle })
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "connector.declaration_failed",
                error.to_string(),
            ))
        })
}

fn python_input_descriptor(
    py: Python<'_>,
    input: &ConnectorInputDescriptor,
) -> PyResult<Py<PythonConnectorInputDescriptor>> {
    let configuration = configuration_values(input.configuration())
        .into_iter()
        .map(|(name, value)| Py::new(py, value).map(|value| (name, value)))
        .collect::<PyResult<Vec<_>>>()?;
    let signal = Py::new(
        py,
        PythonSignalSpec {
            value: input.signal_spec().clone(),
        },
    )?;
    let media = Py::new(
        py,
        PythonMediaCaps {
            value: input.media(),
        },
    )?;
    let edge = Py::new(
        py,
        PythonEdgeContract {
            value: input.edge_contract(),
        },
    )?;
    Py::new(
        py,
        PythonConnectorInputDescriptor {
            endpoint_id: input.endpoint_id().get(),
            connector_id: input.connector_id().map(pocketstation::ConnectorId::get),
            route_id: input.route_id().get(),
            port_name: input.port_name().to_owned(),
            signal_wire_id: input.signal_spec().wire_id().to_owned(),
            signal,
            media,
            edge,
            configuration,
        },
    )
}

fn python_item(py: Python<'_>, item: ConnectorItem<'_>) -> PyResult<Py<PythonConnectorItem>> {
    match item {
        ConnectorItem::Audio { input, frame } => {
            let descriptor = python_input_descriptor(py, input)?;
            let frame = owned_endpoint_audio_frame(frame, input);
            let audio = Py::new(py, python_audio_frame(py, frame))?;
            Py::new(
                py,
                PythonConnectorItem {
                    kind: "audio",
                    input: descriptor,
                    audio: Some(audio),
                    signal: None,
                },
            )
        }
        ConnectorItem::Signal { input, signal } => {
            let descriptor = python_input_descriptor(py, input)?;
            let signal = Py::new(py, python_envelope(py, copy_envelope(&signal))?)?;
            Py::new(
                py,
                PythonConnectorItem {
                    kind: "signal",
                    input: descriptor,
                    audio: None,
                    signal: Some(signal),
                },
            )
        }
    }
}

pub(super) fn python_context(
    py: Python<'_>,
    context: &ConnectorContext,
    active: Arc<AtomicBool>,
) -> PyResult<Py<PythonConnectorContext>> {
    Py::new(
        py,
        PythonConnectorContext {
            context: context.clone(),
            active,
        },
    )
}

fn make_error_code(value: String) -> PyResult<ConnectorErrorCode> {
    ConnectorErrorCode::new(value).map_err(|error| PyValueError::new_err(error.to_string()))
}

pub(super) fn python_error(
    py: Python<'_>,
    error: PyErr,
    default_stage: ConnectorErrorStage,
) -> ConnectorError {
    let value = error.value(py);
    let code = value
        .getattr("code")
        .and_then(|value| value.extract::<String>())
        .ok()
        .and_then(|value| ConnectorErrorCode::new(value).ok())
        .unwrap_or_else(|| ConnectorErrorCode::new("python.exception").expect("valid constant"));
    let stage = value
        .getattr("stage")
        .and_then(|value| value.extract::<String>())
        .ok()
        .and_then(|value| parse_stage(&value))
        .unwrap_or(default_stage);
    let retryability = value
        .getattr("retryability")
        .and_then(|value| value.extract::<String>())
        .ok()
        .and_then(|value| parse_retryability(&value))
        .unwrap_or(ConnectorRetryability::Never);
    let mut message = value
        .getattr("message")
        .and_then(|value| value.extract::<String>())
        .unwrap_or_else(|_| error.to_string());
    const MAXIMUM_MESSAGE_BYTES: usize =
        pocketstation::connector::MAX_CONNECTOR_ERROR_MESSAGE_BYTES;
    if message.len() > MAXIMUM_MESSAGE_BYTES {
        let mut boundary = MAXIMUM_MESSAGE_BYTES;
        while boundary > 0 && !message.is_char_boundary(boundary) {
            boundary -= 1;
        }
        message.truncate(boundary);
    }
    ConnectorError::new(code, stage, retryability, message)
        .unwrap_or_else(|_| internal_error("python.exception", stage, "Python Connector failed"))
}

fn parse_stage(value: &str) -> Option<ConnectorErrorStage> {
    match value {
        "configuration" => Some(ConnectorErrorStage::Configuration),
        "prepare" => Some(ConnectorErrorStage::Prepare),
        "startup" => Some(ConnectorErrorStage::Startup),
        "readiness" => Some(ConnectorErrorStage::Readiness),
        "delivery" => Some(ConnectorErrorStage::Delivery),
        "retry" => Some(ConnectorErrorStage::Retry),
        "shutdown" => Some(ConnectorErrorStage::Shutdown),
        "join" => Some(ConnectorErrorStage::Join),
        _ => None,
    }
}

fn parse_retryability(value: &str) -> Option<ConnectorRetryability> {
    match value {
        "never" => Some(ConnectorRetryability::Never),
        "retryable" => Some(ConnectorRetryability::Retryable),
        "retry-after-reconfiguration" => Some(ConnectorRetryability::RetryAfterReconfiguration),
        _ => None,
    }
}

pub(super) fn internal_error(
    code: &str,
    stage: ConnectorErrorStage,
    message: &str,
) -> ConnectorError {
    ConnectorError::new(
        ConnectorErrorCode::new(code).expect("internal Connector code is valid"),
        stage,
        ConnectorRetryability::Never,
        message,
    )
    .expect("internal Connector error is valid")
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonConnectorInputDescriptor>()?;
    module.add_class::<PythonConnectorItem>()?;
    module.add_class::<PythonConnectorContext>()?;
    module.add_class::<PythonRegisteredConnector>()?;
    Ok(())
}
