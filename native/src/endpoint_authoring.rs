use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use pocketstation::graph::NodeConfig;
use pocketstation::{
    ConfigError, EndpointCancellationOutcome, EndpointDriverFactory, EndpointDriverFinalization,
    EndpointDriverObservations, EndpointFailure, EndpointFailureRetryability, EndpointFailureStage,
    EndpointInputOrigin, EndpointPortInput, EndpointPreparationGroup, EndpointReceiver,
    EndpointShutdownMode, EndpointStartGate, ExecutionPartition, NodeDefinition, NodeDescriptor,
    NodeTypeId, OperatorId, PreparedEndpointDriver, RunningEndpointDriver, SafetyContract, Session,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::errors::{coded_reason, session_endpoint_error};
use crate::graph::{
    PythonEdgeContract, PythonEndpoint, PythonMediaCaps, PythonPortSpec, PythonSignalSpec,
};
use crate::signals::{copy_envelope, python_envelope, PythonSignalEnvelope};
use crate::streams::{owned_endpoint_audio_frame_for_route, python_audio_frame, PythonAudioFrame};

const MAXIMUM_ENDPOINT_ERROR_MESSAGE_BYTES: usize = 4_096;

#[pyclass(name = "_EndpointManifest", frozen)]
#[derive(Clone)]
pub(crate) struct PythonEndpointManifest {
    operator_id: OperatorId,
    descriptor: NodeDescriptor,
}

#[pymethods]
impl PythonEndpointManifest {
    #[new]
    #[pyo3(signature = (operator_id, node_type_id, inputs))]
    fn new(
        py: Python<'_>,
        operator_id: String,
        node_type_id: String,
        inputs: Vec<Py<PythonPortSpec>>,
    ) -> PyResult<Self> {
        validate_contract_id("operator ID", &operator_id)?;
        validate_contract_id("node type ID", &node_type_id)?;
        if inputs.is_empty() {
            return Err(invalid_endpoint(
                "Endpoint manifest needs at least one input",
            ));
        }
        let inputs = inputs
            .into_iter()
            .map(|input| input.borrow(py).value.clone())
            .collect::<Vec<_>>();
        if inputs
            .iter()
            .any(|input| input.direction() != pocketstation::PortDirection::Input)
        {
            return Err(invalid_endpoint(
                "Endpoint manifest ports must all be inputs",
            ));
        }
        let descriptor = NodeDescriptor::new(
            NodeTypeId::from(node_type_id.as_str()),
            "Python Endpoint",
            inputs,
            Vec::new(),
            ExecutionPartition::External,
            SafetyContract::ExternalService,
            true,
        )
        .map_err(|error| invalid_endpoint(error.to_string()))?;
        Ok(Self {
            operator_id: OperatorId::new(operator_id),
            descriptor,
        })
    }

    #[getter]
    fn operator_id(&self) -> &str {
        self.operator_id.as_str()
    }

    #[getter]
    fn node_type_id(&self) -> &str {
        self.descriptor.type_id().as_str()
    }
}

struct PythonEndpointDefinition {
    manifest: PythonEndpointManifest,
    factory: Py<PyAny>,
}

impl NodeDefinition for PythonEndpointDefinition {
    fn descriptor(&self) -> NodeDescriptor {
        self.manifest.descriptor.clone()
    }

    fn validate_config(&self, configuration: &NodeConfig) -> Result<(), ConfigError> {
        Python::attach(|py| {
            let values =
                node_configuration(py, configuration).map_err(|error| ConfigError::Invalid {
                    key: "<configuration>".to_owned(),
                    reason: error.to_string(),
                })?;
            self.factory
                .bind(py)
                .call_method1("validate_configuration", (values,))
                .map(|_| ())
                .map_err(|error| ConfigError::Invalid {
                    key: "<configuration>".to_owned(),
                    reason: bounded_message(error.to_string()),
                })
        })
    }
}

struct PythonEndpointFactory {
    factory: Py<PyAny>,
}

impl EndpointDriverFactory for PythonEndpointFactory {
    fn preparation_group(
        &self,
        route_id: pocketstation::RouteId,
        configuration: &NodeConfig,
    ) -> Result<EndpointPreparationGroup, EndpointFailure> {
        Python::attach(|py| {
            let values = node_configuration(py, configuration)
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Prepare))?;
            let result = self
                .factory
                .bind(py)
                .call_method1("preparation_group", (route_id.get(), values))
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Prepare))?;
            if result.is_none() {
                Ok(EndpointPreparationGroup::Route(route_id))
            } else {
                let group = result
                    .extract::<String>()
                    .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Prepare))?;
                if group.trim().is_empty() {
                    return Err(EndpointFailure::new(
                        EndpointFailureStage::Prepare,
                        "Endpoint preparation group cannot be empty",
                    )
                    .with_external_details(
                        "endpoint.invalid_preparation_group",
                        EndpointFailureRetryability::ReconfigurationRequired,
                    ));
                }
                Ok(EndpointPreparationGroup::Shared(
                    pocketstation::EndpointGroupId::new(group),
                ))
            }
        })
    }

    fn prepare(
        &self,
        inputs: Vec<EndpointPortInput>,
    ) -> Result<Box<dyn PreparedEndpointDriver>, EndpointFailure> {
        Python::attach(|py| {
            let inputs = inputs
                .into_iter()
                .map(|input| python_port_input(py, input))
                .collect::<PyResult<Vec<_>>>()
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Prepare))?;
            let prepared = self
                .factory
                .bind(py)
                .call_method1("prepare", (inputs,))
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Prepare))?
                .unbind();
            Ok(Box::new(PythonPreparedEndpoint {
                prepared,
                completed: false,
            }) as Box<dyn PreparedEndpointDriver>)
        })
    }
}

struct PythonPreparedEndpoint {
    prepared: Py<PyAny>,
    completed: bool,
}

impl Drop for PythonPreparedEndpoint {
    fn drop(&mut self) {
        if !self.completed {
            Python::attach(|py| {
                let _ = self.prepared.bind(py).call_method0("cancel_preparation");
            });
        }
    }
}

impl PreparedEndpointDriver for PythonPreparedEndpoint {
    fn start(
        mut self: Box<Self>,
        start_gate: Arc<EndpointStartGate>,
    ) -> Result<Box<dyn RunningEndpointDriver>, EndpointFailure> {
        Python::attach(|py| {
            let gate = Py::new(py, PythonEndpointStartGate { gate: start_gate })
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Start))?;
            let running = self
                .prepared
                .bind(py)
                .call_method1("start", (gate,))
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::Start))?
                .unbind();
            self.completed = true;
            Ok(Box::new(PythonRunningEndpoint {
                running,
                finalized: false,
            }) as Box<dyn RunningEndpointDriver>)
        })
    }

    fn cancel_preparation(mut self: Box<Self>) -> EndpointCancellationOutcome {
        let result = Python::attach(|py| {
            self.prepared
                .bind(py)
                .call_method0("cancel_preparation")
                .map(|_| ())
                .map_err(|error| {
                    endpoint_failure(py, error, EndpointFailureStage::CancelPreparation)
                })
        });
        self.completed = true;
        EndpointCancellationOutcome {
            observations: EndpointDriverObservations::default(),
            result,
        }
    }
}

struct PythonRunningEndpoint {
    running: Py<PyAny>,
    finalized: bool,
}

impl Drop for PythonRunningEndpoint {
    fn drop(&mut self) {
        if !self.finalized {
            Python::attach(|py| {
                let value = self.running.bind(py);
                let _ = value.call_method1("request_shutdown", ("abort",));
                let _ = value.call_method0("join_and_finalize");
            });
        }
    }
}

impl RunningEndpointDriver for PythonRunningEndpoint {
    fn observations(&self) -> EndpointDriverObservations {
        Python::attach(|py| python_observations(py, self.running.bind(py)).unwrap_or_default())
    }

    fn request_stop(&mut self) -> Result<(), EndpointFailure> {
        self.request_shutdown(EndpointShutdownMode::Drain)
    }

    fn request_shutdown(&mut self, mode: EndpointShutdownMode) -> Result<(), EndpointFailure> {
        Python::attach(|py| {
            self.running
                .bind(py)
                .call_method1("request_shutdown", (shutdown_mode_name(mode),))
                .map(|_| ())
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::RequestStop))
        })
    }

    fn join_and_finalize(mut self: Box<Self>) -> EndpointDriverFinalization {
        let result = Python::attach(|py| {
            let observations = self
                .running
                .bind(py)
                .call_method0("join_and_finalize")
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::JoinFinalize))?;
            python_observations(py, &observations)
                .map_err(|error| endpoint_failure(py, error, EndpointFailureStage::JoinFinalize))
        });
        self.finalized = true;
        match result {
            Ok(observations) => EndpointDriverFinalization {
                observations,
                result: Ok(()),
            },
            Err(error) => EndpointDriverFinalization {
                observations: EndpointDriverObservations::default(),
                result: Err(error),
            },
        }
    }
}

#[pyclass(name = "EndpointStartGate", frozen)]
struct PythonEndpointStartGate {
    gate: Arc<EndpointStartGate>,
}

#[pymethods]
impl PythonEndpointStartGate {
    #[getter]
    fn is_open(&self) -> bool {
        self.gate.is_open()
    }
}

#[pyclass(name = "EndpointPrepareContext", frozen)]
struct PythonEndpointPrepareContext {
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    endpoint_id: u64,
    #[pyo3(get)]
    connector_id: Option<u64>,
    #[pyo3(get)]
    route_id: u64,
    #[pyo3(get)]
    origin_kind: &'static str,
    #[pyo3(get)]
    source_id: Option<u64>,
    #[pyo3(get)]
    stream_id: Option<u64>,
    #[pyo3(get)]
    stem_id: Option<u64>,
    #[pyo3(get)]
    session_timeline_origin_ns: u64,
    configuration: HashMap<String, String>,
}

#[pymethods]
impl PythonEndpointPrepareContext {
    #[getter]
    fn configuration(&self) -> HashMap<String, String> {
        self.configuration.clone()
    }
}

#[pyclass(name = "EndpointReceiver")]
struct PythonEndpointReceiver {
    receiver: Mutex<EndpointReceiver>,
    endpoint_id: u64,
    connector_id: Option<u64>,
    route_id: u64,
}

#[pymethods]
impl PythonEndpointReceiver {
    fn try_recv(&self, py: Python<'_>) -> PyResult<Option<PythonEndpointItem>> {
        let mut receiver = self
            .receiver
            .lock()
            .map_err(|_| invalid_endpoint("Endpoint receiver is unavailable"))?;
        match &mut *receiver {
            EndpointReceiver::Audio { receiver, .. } => receiver
                .try_recv()
                .map(|frame| {
                    let frame = owned_endpoint_audio_frame_for_route(
                        frame,
                        self.endpoint_id,
                        self.connector_id,
                        self.route_id,
                    );
                    Py::new(py, python_audio_frame(py, frame)).map(|audio| PythonEndpointItem {
                        kind: "audio",
                        audio: Some(audio),
                        signal: None,
                    })
                })
                .transpose(),
            EndpointReceiver::Signal(receiver) => receiver
                .try_recv()
                .map(|signal| {
                    Py::new(py, python_envelope(py, copy_envelope(&signal))?).map(|signal| {
                        PythonEndpointItem {
                            kind: "signal",
                            audio: None,
                            signal: Some(signal),
                        }
                    })
                })
                .transpose(),
        }
    }

    fn is_abandoned(&self) -> bool {
        let Ok(receiver) = self.receiver.lock() else {
            return true;
        };
        match &*receiver {
            EndpointReceiver::Audio { receiver, .. } => receiver.is_abandoned(),
            EndpointReceiver::Signal(receiver) => receiver.is_abandoned(),
        }
    }

    fn mark_discontinuity(&self) {
        let Ok(receiver) = self.receiver.lock() else {
            return;
        };
        if let EndpointReceiver::Audio { receiver, .. } = &*receiver {
            receiver.mark_discontinuity();
        }
    }

    fn mark_worker_failure(&self) {
        let Ok(receiver) = self.receiver.lock() else {
            return;
        };
        if let EndpointReceiver::Audio { receiver, .. } = &*receiver {
            receiver.mark_worker_failure();
        }
    }
}

#[pyclass(name = "EndpointItem", frozen)]
struct PythonEndpointItem {
    #[pyo3(get)]
    kind: &'static str,
    audio: Option<Py<PythonAudioFrame>>,
    signal: Option<Py<PythonSignalEnvelope>>,
}

#[pymethods]
impl PythonEndpointItem {
    #[getter]
    fn audio(&self, py: Python<'_>) -> Option<Py<PythonAudioFrame>> {
        self.audio.as_ref().map(|value| value.clone_ref(py))
    }

    #[getter]
    fn signal(&self, py: Python<'_>) -> Option<Py<PythonSignalEnvelope>> {
        self.signal.as_ref().map(|value| value.clone_ref(py))
    }
}

#[pyclass(name = "EndpointPortInput", frozen)]
struct PythonEndpointPortInput {
    #[pyo3(get)]
    port_name: String,
    signal: Py<PythonSignalSpec>,
    media: Py<PythonMediaCaps>,
    edge: Py<PythonEdgeContract>,
    context: Py<PythonEndpointPrepareContext>,
    receiver: Py<PythonEndpointReceiver>,
}

#[pymethods]
impl PythonEndpointPortInput {
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

    #[getter]
    fn context(&self, py: Python<'_>) -> Py<PythonEndpointPrepareContext> {
        self.context.clone_ref(py)
    }

    #[getter]
    fn receiver(&self, py: Python<'_>) -> Py<PythonEndpointReceiver> {
        self.receiver.clone_ref(py)
    }
}

#[pyclass(name = "_RegisteredEndpoint", frozen)]
pub(crate) struct PythonRegisteredEndpoint {
    session_id: pocketstation::SessionId,
    operator_id: OperatorId,
    node_type_id: NodeTypeId,
}

#[pymethods]
impl PythonRegisteredEndpoint {
    #[getter]
    fn session_id(&self) -> u64 {
        self.session_id.get()
    }

    #[getter]
    fn operator_id(&self) -> &str {
        self.operator_id.as_str()
    }

    #[getter]
    fn node_type_id(&self) -> &str {
        self.node_type_id.as_str()
    }
}

pub(crate) fn register_endpoint(
    session: &Session,
    manifest: &PythonEndpointManifest,
    factory: Py<PyAny>,
) -> PyResult<PythonRegisteredEndpoint> {
    Python::attach(|py| {
        session.register_endpoint(
            manifest.operator_id.clone(),
            Arc::new(PythonEndpointDefinition {
                manifest: manifest.clone(),
                factory: factory.clone_ref(py),
            }),
            Arc::new(PythonEndpointFactory { factory }),
        )
    })
    .map_err(session_endpoint_error)?;
    Ok(PythonRegisteredEndpoint {
        session_id: session.id(),
        operator_id: manifest.operator_id.clone(),
        node_type_id: manifest.descriptor.type_id().clone(),
    })
}

pub(crate) fn declare_endpoint(
    session: &Session,
    registered: &PythonRegisteredEndpoint,
    configuration: HashMap<String, String>,
    edge: &PythonEdgeContract,
) -> PyResult<PythonEndpoint> {
    if registered.session_id != session.id() {
        return Err(PyValueError::new_err(coded_reason(
            "endpoint.wrong_session",
            "registered Endpoint belongs to a different Session",
        )));
    }
    let configuration = configuration.into_iter().fold(
        pocketstation::EndpointConfiguration::new(),
        |configuration, (key, value)| configuration.with(key, value),
    );
    session
        .endpoint(
            pocketstation::EndpointDescriptor::new(
                registered.node_type_id.clone(),
                registered.operator_id.clone(),
            )
            .with_configuration(configuration)
            .with_input_edge(edge.value),
        )
        .map(|handle| PythonEndpoint { handle })
        .map_err(crate::errors::session_error)
}

fn python_port_input(
    py: Python<'_>,
    input: EndpointPortInput,
) -> PyResult<Py<PythonEndpointPortInput>> {
    let port_name = input.port_name().to_owned();
    let signal = Py::new(
        py,
        PythonSignalSpec {
            value: input.signal_spec().clone(),
        },
    )?;
    let media = Py::new(
        py,
        PythonMediaCaps {
            value: *input.media(),
        },
    )?;
    let edge = Py::new(
        py,
        PythonEdgeContract {
            value: *input.edge_contract(),
        },
    )?;
    let prepare = input.context();
    let route = prepare.route_context();
    let (origin_kind, source_id, stream_id, stem_id) = match route.origin() {
        EndpointInputOrigin::Stem(stem_id) => ("stem", None, None, Some(stem_id.get())),
        EndpointInputOrigin::Signal => ("signal", None, None, None),
        EndpointInputOrigin::Source {
            source_id,
            stream_id,
            audio_stem_id,
        } => (
            "source",
            Some(source_id.get()),
            Some(stream_id.get()),
            audio_stem_id.map(pocketstation::StemId::get),
        ),
    };
    let endpoint_id = prepare.endpoint_id().get();
    let connector_id = prepare.connector_id().map(pocketstation::ConnectorId::get);
    let route_id = route.route_id().get();
    let context = Py::new(
        py,
        PythonEndpointPrepareContext {
            session_id: prepare.session_id().get(),
            endpoint_id,
            connector_id,
            route_id,
            origin_kind,
            source_id,
            stream_id,
            stem_id,
            session_timeline_origin_ns: prepare.session_timeline_origin().monotonic_timestamp_ns(),
            configuration: prepare
                .node_configuration()
                .iter()
                .map(|(key, value)| (key.to_owned(), value.to_owned()))
                .collect(),
        },
    )?;
    let (receiver, _) = input.into_parts();
    let receiver = Py::new(
        py,
        PythonEndpointReceiver {
            receiver: Mutex::new(receiver),
            endpoint_id,
            connector_id,
            route_id,
        },
    )?;
    Py::new(
        py,
        PythonEndpointPortInput {
            port_name,
            signal,
            media,
            edge,
            context,
            receiver,
        },
    )
}

fn node_configuration<'py>(
    py: Python<'py>,
    configuration: &NodeConfig,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    for (key, value) in configuration.iter() {
        values.set_item(key, value)?;
    }
    Ok(values)
}

fn python_observations(
    _py: Python<'_>,
    value: &Bound<'_, PyAny>,
) -> PyResult<EndpointDriverObservations> {
    let value = if value.hasattr("observations")? {
        let observations = value.getattr("observations")?;
        if observations.is_callable() {
            observations.call0()?
        } else {
            observations
        }
    } else {
        value.clone()
    };
    Ok(EndpointDriverObservations {
        frames_received_total: observation_value(&value, "frames_received_total")?,
        frames_delivered_total: observation_value(&value, "frames_delivered_total")?,
        frames_dropped_total: observation_value(&value, "frames_dropped_total")?,
        discontinuities_total: observation_value(&value, "discontinuities_total")?,
        failures_total: observation_value(&value, "failures_total")?,
    })
}

fn observation_value(value: &Bound<'_, PyAny>, name: &str) -> PyResult<u64> {
    value.getattr(name)?.extract()
}

fn endpoint_failure(
    py: Python<'_>,
    error: PyErr,
    default_stage: EndpointFailureStage,
) -> EndpointFailure {
    let value = error.value(py);
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
        .unwrap_or(EndpointFailureRetryability::Never);
    let code = value
        .getattr("code")
        .and_then(|value| value.extract::<String>())
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| "python.endpoint_exception".to_owned());
    let message = value
        .getattr("message")
        .and_then(|value| value.extract::<String>())
        .unwrap_or_else(|_| error.to_string());
    EndpointFailure::new(stage, bounded_message(message)).with_external_details(code, retryability)
}

fn parse_stage(value: &str) -> Option<EndpointFailureStage> {
    match value {
        "prepare" => Some(EndpointFailureStage::Prepare),
        "cancel-preparation" => Some(EndpointFailureStage::CancelPreparation),
        "start" => Some(EndpointFailureStage::Start),
        "request-stop" => Some(EndpointFailureStage::RequestStop),
        "join-finalize" => Some(EndpointFailureStage::JoinFinalize),
        _ => None,
    }
}

fn parse_retryability(value: &str) -> Option<EndpointFailureRetryability> {
    match value {
        "never" => Some(EndpointFailureRetryability::Never),
        "retryable" => Some(EndpointFailureRetryability::Retryable),
        "retry-after-reconfiguration" | "reconfiguration-required" => {
            Some(EndpointFailureRetryability::ReconfigurationRequired)
        }
        _ => None,
    }
}

fn shutdown_mode_name(mode: EndpointShutdownMode) -> &'static str {
    match mode {
        EndpointShutdownMode::Drain => "drain",
        EndpointShutdownMode::Abort => "abort",
    }
}

fn bounded_message(mut value: String) -> String {
    if value.len() > MAXIMUM_ENDPOINT_ERROR_MESSAGE_BYTES {
        let mut boundary = MAXIMUM_ENDPOINT_ERROR_MESSAGE_BYTES;
        while boundary > 0 && !value.is_char_boundary(boundary) {
            boundary -= 1;
        }
        value.truncate(boundary);
    }
    value
}

fn validate_contract_id(label: &str, value: &str) -> PyResult<()> {
    if value.trim().is_empty() || value.trim() != value {
        return Err(invalid_endpoint(format!("{label} is invalid")));
    }
    Ok(())
}

fn invalid_endpoint(reason: impl Into<String>) -> PyErr {
    PyValueError::new_err(coded_reason("endpoint.invalid_contract", reason.into()))
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonEndpointManifest>()?;
    module.add_class::<PythonRegisteredEndpoint>()?;
    module.add_class::<PythonEndpointStartGate>()?;
    module.add_class::<PythonEndpointPrepareContext>()?;
    module.add_class::<PythonEndpointReceiver>()?;
    module.add_class::<PythonEndpointItem>()?;
    module.add_class::<PythonEndpointPortInput>()?;
    Ok(())
}
