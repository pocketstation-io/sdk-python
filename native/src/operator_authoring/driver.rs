use std::sync::Arc;

use pocketstation::graph::NodeConfig;
use pocketstation::{
    AsyncNode, AsyncNodeFuture, AsyncOperatorFactory, AsyncOperatorPrepareContext, ConfigError,
    NodeError, OperatorId, PortDirection, PortPrepareContext, SignalDerivation, SignalEnvelope,
    SignalLineage, SignalTiming,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::values::{PythonOperatorEmission, PythonOperatorManifest};
use crate::errors::coded_reason;
use crate::graph::{PythonEdgeContract, PythonMediaCaps, PythonSignalSpec};
use crate::signals::{copy_envelope, python_envelope};

pub(crate) fn register_operator(
    session: &pocketstation::Session,
    manifest: &PythonOperatorManifest,
    factory: Py<PyAny>,
) -> PyResult<()> {
    session
        .register_operator(Arc::new(PythonOperatorFactory {
            manifest: manifest.value.clone(),
            factory,
        }))
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "operator.registration_failed",
                error.to_string(),
            ))
        })
}

#[pyclass(name = "_OperatorPortContext", frozen)]
pub(crate) struct PythonOperatorPortContext {
    #[pyo3(get)]
    edge_id: Option<u64>,
    #[pyo3(get)]
    port_name: String,
    #[pyo3(get)]
    direction: &'static str,
    #[pyo3(get)]
    capacity_signals: usize,
    signal: Py<PythonSignalSpec>,
    media: Py<PythonMediaCaps>,
    edge: Py<PythonEdgeContract>,
}

#[pymethods]
impl PythonOperatorPortContext {
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

#[pyclass(name = "_OperatorPrepareContext", frozen)]
pub(crate) struct PythonOperatorPrepareContext {
    #[pyo3(get)]
    execution_partition: &'static str,
    inputs: Vec<Py<PythonOperatorPortContext>>,
    outputs: Vec<Py<PythonOperatorPortContext>>,
}

#[pymethods]
impl PythonOperatorPrepareContext {
    #[getter]
    fn inputs(&self, py: Python<'_>) -> Vec<Py<PythonOperatorPortContext>> {
        self.inputs
            .iter()
            .map(|value| value.clone_ref(py))
            .collect()
    }

    #[getter]
    fn outputs(&self, py: Python<'_>) -> Vec<Py<PythonOperatorPortContext>> {
        self.outputs
            .iter()
            .map(|value| value.clone_ref(py))
            .collect()
    }
}

struct PythonOperatorFactory {
    manifest: pocketstation::AsyncOperatorManifest,
    factory: Py<PyAny>,
}

impl AsyncOperatorFactory for PythonOperatorFactory {
    fn manifest(&self) -> &pocketstation::AsyncOperatorManifest {
        &self.manifest
    }

    fn validate_config(&self, configuration: &NodeConfig) -> Result<(), ConfigError> {
        Python::attach(|py| {
            let values = configuration_dict(py, configuration)
                .map_err(|error| config_error("configuration", error))?;
            self.factory
                .bind(py)
                .call_method1("validate_config", (values,))
                .map(|_| ())
                .map_err(|error| config_error("configuration", error))
        })
    }

    fn create(&self, configuration: &NodeConfig) -> Result<Box<dyn AsyncNode>, NodeError> {
        Python::attach(|py| {
            let values = configuration_dict(py, configuration).map_err(node_process_error)?;
            let node = self
                .factory
                .bind(py)
                .call_method1("create", (values,))
                .map_err(node_process_error)?
                .unbind();
            Ok(Box::new(PythonOperatorNode {
                node,
                operator_id: self.manifest.operator_id().clone(),
                revision: self.manifest.revision(),
                generation: self.manifest.generation(),
                last_input: None,
            }) as Box<dyn AsyncNode>)
        })
    }
}

struct PythonOperatorNode {
    node: Py<PyAny>,
    operator_id: OperatorId,
    revision: u32,
    generation: u32,
    last_input: Option<(SignalLineage, SignalTiming)>,
}

impl AsyncNode for PythonOperatorNode {
    fn prepare<'a>(
        &'a mut self,
        context: &'a AsyncOperatorPrepareContext,
    ) -> AsyncNodeFuture<'a, Result<(), NodeError>> {
        Box::pin(async move {
            Python::attach(|py| {
                let context = python_prepare_context(py, context).map_err(node_prepare_error)?;
                self.node
                    .bind(py)
                    .call_method1("prepare", (context,))
                    .map(|_| ())
                    .map_err(node_prepare_error)
            })
        })
    }

    fn process<'a>(
        &'a mut self,
        input: SignalEnvelope,
    ) -> AsyncNodeFuture<'a, Result<Vec<SignalEnvelope>, NodeError>> {
        self.process_port("input", input)
    }

    fn process_port<'a>(
        &'a mut self,
        input_port: &'a str,
        input: SignalEnvelope,
    ) -> AsyncNodeFuture<'a, Result<Vec<SignalEnvelope>, NodeError>> {
        Box::pin(async move {
            let lineage = input
                .lineage()
                .ok_or_else(|| NodeError::Process("operator input has no lineage".to_owned()))?;
            let timing = input.timing();
            self.last_input = Some((lineage, timing));
            let emissions = Python::attach(|py| {
                let input = Py::new(py, python_envelope(py, copy_envelope(&input))?)?;
                let output = self
                    .node
                    .bind(py)
                    .call_method1("process", (input_port, input))?;
                extract_emissions(&output)
            })
            .map_err(node_process_error)?;
            self.build_outputs(emissions, lineage, timing)
        })
    }

    fn flush<'a>(&'a mut self) -> AsyncNodeFuture<'a, Result<Vec<SignalEnvelope>, NodeError>> {
        Box::pin(async move {
            let emissions = Python::attach(|py| {
                let output = self.node.bind(py).call_method0("flush")?;
                extract_emissions(&output)
            })
            .map_err(node_process_error)?;
            if emissions.is_empty() {
                return Ok(Vec::new());
            }
            let (lineage, timing) = self.last_input.ok_or_else(|| {
                NodeError::Process("operator cannot flush output before input".to_owned())
            })?;
            self.build_outputs(emissions, lineage, timing)
        })
    }

    fn cancel<'a>(&'a mut self) -> AsyncNodeFuture<'a, Result<(), NodeError>> {
        Box::pin(async move {
            Python::attach(|py| {
                self.node
                    .bind(py)
                    .call_method0("cancel")
                    .map(|_| ())
                    .map_err(node_process_error)
            })
        })
    }

    fn close<'a>(&'a mut self) -> AsyncNodeFuture<'a, Result<(), NodeError>> {
        Box::pin(async move {
            Python::attach(|py| {
                self.node
                    .bind(py)
                    .call_method0("close")
                    .map(|_| ())
                    .map_err(node_process_error)
            })
        })
    }
}

impl PythonOperatorNode {
    fn build_outputs(
        &self,
        emissions: Vec<PythonOperatorEmission>,
        lineage: SignalLineage,
        timing: SignalTiming,
    ) -> Result<Vec<SignalEnvelope>, NodeError> {
        emissions
            .into_iter()
            .map(|emission| {
                let derivation = SignalDerivation::new(
                    lineage,
                    timing,
                    self.operator_id.clone(),
                    self.revision,
                    self.generation,
                    None,
                )
                .map_err(|error| NodeError::Process(error.to_string()))?;
                Ok(SignalEnvelope::untracked(
                    emission.payload.into_core(),
                    emission.signal,
                    timing.observed_timestamp_ns(),
                )
                .with_lineage(lineage, timing)
                .with_derivation(derivation))
            })
            .collect()
    }
}

fn python_prepare_context(
    py: Python<'_>,
    context: &AsyncOperatorPrepareContext,
) -> PyResult<Py<PythonOperatorPrepareContext>> {
    let inputs = context
        .inputs()
        .iter()
        .map(|value| python_port_context(py, value))
        .collect::<PyResult<Vec<_>>>()?;
    let outputs = context
        .outputs()
        .iter()
        .map(|value| python_port_context(py, value))
        .collect::<PyResult<Vec<_>>>()?;
    Py::new(
        py,
        PythonOperatorPrepareContext {
            execution_partition: "async-worker",
            inputs,
            outputs,
        },
    )
}

fn python_port_context(
    py: Python<'_>,
    value: &PortPrepareContext,
) -> PyResult<Py<PythonOperatorPortContext>> {
    Py::new(
        py,
        PythonOperatorPortContext {
            edge_id: value.edge_id().map(|edge| u64::from(edge.index())),
            port_name: value.port_name().to_owned(),
            direction: match value.direction() {
                PortDirection::Input => "input",
                PortDirection::Output => "output",
            },
            capacity_signals: value.capacity_signals(),
            signal: Py::new(
                py,
                PythonSignalSpec {
                    value: value.signal().clone(),
                },
            )?,
            media: Py::new(
                py,
                PythonMediaCaps {
                    value: value.media(),
                },
            )?,
            edge: Py::new(
                py,
                PythonEdgeContract {
                    value: value.edge_contract(),
                },
            )?,
        },
    )
}

fn extract_emissions(value: &Bound<'_, PyAny>) -> PyResult<Vec<PythonOperatorEmission>> {
    value
        .try_iter()?
        .map(|value| {
            value?
                .extract::<PyRef<'_, PythonOperatorEmission>>()
                .map(|value| value.clone())
                .map_err(Into::into)
        })
        .collect()
}

fn configuration_dict<'py>(
    py: Python<'py>,
    configuration: &NodeConfig,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    for (key, value) in configuration.iter() {
        values.set_item(key, value)?;
    }
    Ok(values)
}

fn config_error(key: &str, error: PyErr) -> ConfigError {
    ConfigError::Invalid {
        key: key.to_owned(),
        reason: python_error_message(error),
    }
}

fn node_prepare_error(error: PyErr) -> NodeError {
    NodeError::Prepare(python_error_message(error))
}

fn node_process_error(error: PyErr) -> NodeError {
    NodeError::Process(python_error_message(error))
}

fn python_error_message(error: PyErr) -> String {
    Python::attach(|py| {
        error.value(py).str().map_or_else(
            |_| error.to_string(),
            |value| value.to_string_lossy().into_owned(),
        )
    })
}
