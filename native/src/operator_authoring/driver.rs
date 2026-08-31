use std::sync::Arc;

use pocketstation::graph::NodeConfig;
use pocketstation::{
    AsyncNode, AsyncNodeFuture, AsyncOperatorFactory, AsyncOperatorPrepareContext, AudioBufferPool,
    AudioFrame, ChannelLayout, ConfigError, MediaCaps, NodeError, OperatorId, PortDirection,
    PortPrepareContext, SampleFormat, SampleSpec, SignalDerivation, SignalEnvelope, SignalLineage,
    SignalPayload, SignalTiming,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::values::{PythonOperatorEmission, PythonOperatorManifest, PythonOperatorPayload};
use crate::errors::coded_reason;
use crate::graph::{PythonEdgeContract, PythonMediaCaps, PythonSignalSpec};
use crate::signals::{copy_envelope, python_envelope};

pub(crate) fn register_operator(
    session: &pocketstation::Session,
    manifest: &PythonOperatorManifest,
    factory: Py<PyAny>,
) -> PyResult<()> {
    let audio_output = audio_output_spec(&manifest.value)?;
    session
        .register_operator(Arc::new(PythonOperatorFactory {
            manifest: manifest.value.clone(),
            factory,
            audio_output,
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
    audio_output: Option<OperatorAudioOutputSpec>,
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
                audio_output: self.audio_output.map(OperatorAudioOutput::new),
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
    audio_output: Option<OperatorAudioOutput>,
}

// AudioBufferPool's public constructor uses a 64-bit ownership mask. Keep the
// binding-side request finite even when a provider declares a larger signal
// queue; Core remains the pool implementation and runtime authority.
const AUDIO_OUTPUT_POOL_MAX_SLOTS: usize = u64::BITS as usize;

#[derive(Clone, Copy)]
struct OperatorAudioOutputSpec {
    sample_spec: SampleSpec,
    frame_samples_per_channel: usize,
    pool_slots: usize,
}

struct OperatorAudioOutput {
    pool: Arc<AudioBufferPool>,
    sample_spec: SampleSpec,
    samples_per_frame: usize,
}

impl OperatorAudioOutput {
    fn new(spec: OperatorAudioOutputSpec) -> Self {
        let samples_per_frame = spec
            .frame_samples_per_channel
            .saturating_mul(usize::from(spec.sample_spec.channels));
        Self {
            pool: AudioBufferPool::new(spec.pool_slots, samples_per_frame),
            sample_spec: spec.sample_spec,
            samples_per_frame,
        }
    }

    fn frame(
        &self,
        samples: &[f32],
        lineage: SignalLineage,
        timing: SignalTiming,
    ) -> Result<AudioFrame, NodeError> {
        if samples.len() != self.samples_per_frame {
            return Err(NodeError::Process(format!(
                "operator audio emission has {} samples; expected {}",
                samples.len(),
                self.samples_per_frame
            )));
        }
        let mut buffer = self.pool.acquire().ok_or_else(|| {
            NodeError::Process("operator audio emission buffer pool is full".to_owned())
        })?;
        buffer
            .try_copy_from_slice(samples)
            .map_err(|error| NodeError::Process(error.to_string()))?;
        let timestamp_ns = timing
            .session_timestamp_ns()
            .or(timing.source_timestamp_ns())
            .unwrap_or(timing.observed_timestamp_ns());
        AudioFrame::try_new(
            lineage.stream_id(),
            lineage.source_id(),
            lineage.sequence_number(),
            timestamp_ns,
            self.sample_spec,
            buffer,
        )
        .map_err(|error| NodeError::Process(error.to_string()))
    }
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
                let payload = match emission.payload {
                    PythonOperatorPayload::Audio(samples) => {
                        let audio_output = self.audio_output.as_ref().ok_or_else(|| {
                            NodeError::Process(
                                "operator audio emission requires one concrete PCM output"
                                    .to_owned(),
                            )
                        })?;
                        SignalPayload::Audio(audio_output.frame(&samples, lineage, timing)?)
                    }
                    payload => payload.into_non_audio_core().ok_or_else(|| {
                        NodeError::Process("operator emitted an unsupported payload".to_owned())
                    })?,
                };
                Ok(SignalEnvelope::untracked(
                    payload,
                    emission.signal,
                    timing.observed_timestamp_ns(),
                )
                .with_lineage(lineage, timing)
                .with_derivation(derivation))
            })
            .collect()
    }
}

fn audio_output_spec(
    manifest: &pocketstation::AsyncOperatorManifest,
) -> PyResult<Option<OperatorAudioOutputSpec>> {
    let Some(MediaCaps::Audio(caps)) = manifest.output_ports().next().map(|port| port.media())
    else {
        return Ok(None);
    };
    let sample_rate_hz = caps.sample_rate_hz.ok_or_else(|| {
        PyValueError::new_err(coded_reason(
            "operator.invalid_contract",
            "Python Operator PCM output requires an exact sample rate",
        ))
    })?;
    if sample_rate_hz == 0 {
        return Err(PyValueError::new_err(coded_reason(
            "operator.invalid_contract",
            "Python Operator PCM output sample rate must be non-zero",
        )));
    }
    let frame_samples_per_channel = caps.frame_samples.ok_or_else(|| {
        PyValueError::new_err(coded_reason(
            "operator.invalid_contract",
            "Python Operator PCM output requires an exact frame sample count",
        ))
    })?;
    if frame_samples_per_channel == 0 {
        return Err(PyValueError::new_err(coded_reason(
            "operator.invalid_contract",
            "Python Operator PCM output frame sample count must be non-zero",
        )));
    }
    let channels = match caps.channel_layout {
        ChannelLayout::Mono => 1,
        ChannelLayout::Stereo => 2,
        ChannelLayout::Any => {
            return Err(PyValueError::new_err(coded_reason(
                "operator.invalid_contract",
                "Python Operator PCM output requires a concrete channel layout",
            )))
        }
    };
    let samples_per_frame = frame_samples_per_channel
        .checked_mul(usize::from(channels))
        .ok_or_else(|| {
            PyValueError::new_err(coded_reason(
                "operator.invalid_contract",
                "Python Operator PCM frame size exceeds the platform limit",
            ))
        })?;
    let payload_bytes = samples_per_frame
        .checked_mul(std::mem::size_of::<f32>())
        .ok_or_else(|| {
            PyValueError::new_err(coded_reason(
                "operator.invalid_contract",
                "Python Operator PCM payload size exceeds the platform limit",
            ))
        })?;
    if manifest
        .output_edge()
        .max_payload_bytes()
        .is_some_and(|maximum| payload_bytes > maximum)
    {
        return Err(PyValueError::new_err(coded_reason(
            "operator.invalid_contract",
            "Python Operator PCM frame exceeds its output edge payload bound",
        )));
    }
    Ok(Some(OperatorAudioOutputSpec {
        sample_spec: SampleSpec::new(sample_rate_hz, channels, SampleFormat::F32Interleaved),
        frame_samples_per_channel,
        pool_slots: manifest
            .queue_capacity_frames()
            .min(AUDIO_OUTPUT_POOL_MAX_SLOTS),
    }))
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
