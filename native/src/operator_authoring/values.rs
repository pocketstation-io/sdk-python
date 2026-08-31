use std::sync::Arc;

use pocketstation::{
    AsyncOperatorManifest, BackpressurePolicy, CopyPolicy, EdgeContract, ExecutionPartition,
    MediaCaps, NodeDescriptor, NodeTypeId, OperatorCancellationPolicy, OperatorDeadlinePolicy,
    OperatorFailurePolicy, OperatorId, OperatorOutputRolePolicy, OperatorPermissionPolicy,
    PortDirection, SafetyContract, SemanticRole, SignalPayload, SignalSpec,
};
use pyo3::buffer::PyBuffer;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::errors::coded_reason;
use crate::graph::{PythonPortSpec, PythonSignalSpec};

fn invalid_operator(reason: impl Into<String>) -> PyErr {
    PyValueError::new_err(coded_reason("operator.invalid_contract", reason.into()))
}

#[pyclass(name = "_OperatorManifest", frozen)]
#[derive(Clone)]
pub(crate) struct PythonOperatorManifest {
    pub(crate) value: AsyncOperatorManifest,
}

#[pymethods]
impl PythonOperatorManifest {
    #[new]
    #[pyo3(signature = (operator_id, inputs, outputs, revision=1, implementation_generation=1, queue_capacity_signals=8, process_timeout_ms=30_000, network_allowed=false, filesystem_allowed=false, drain_queued=false, continue_on_failure=false, terminal_roles=Vec::new()))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        py: Python<'_>,
        operator_id: String,
        inputs: Vec<Py<PythonPortSpec>>,
        outputs: Vec<Py<PythonPortSpec>>,
        revision: u32,
        implementation_generation: u32,
        queue_capacity_signals: usize,
        process_timeout_ms: u32,
        network_allowed: bool,
        filesystem_allowed: bool,
        drain_queued: bool,
        continue_on_failure: bool,
        terminal_roles: Vec<String>,
    ) -> PyResult<Self> {
        let inputs = inputs
            .into_iter()
            .map(|value| value.borrow(py).value.clone())
            .collect::<Vec<_>>();
        let outputs = outputs
            .into_iter()
            .map(|value| value.borrow(py).value.clone())
            .collect::<Vec<_>>();
        if inputs
            .iter()
            .any(|port| port.direction() != PortDirection::Input)
            || outputs
                .iter()
                .any(|port| port.direction() != PortDirection::Output)
        {
            return Err(invalid_operator(
                "operator inputs and outputs must use their corresponding port directions",
            ));
        }
        let input_media = common_media(&inputs, "input")?;
        let output_media = common_media(&outputs, "output")?;
        let input_edge = if matches!(input_media, MediaCaps::Audio(_)) {
            EdgeContract::realtime_audio()
                .with_media(input_media)
                .with_copy_policy(CopyPolicy::CopyToBranchPool)
        } else {
            EdgeContract::bounded_async()
                .with_media(input_media)
                .with_backpressure(BackpressurePolicy::DropNewest)
                .with_copy_policy(CopyPolicy::CopyToBranchPool)
        };
        let output_edge = EdgeContract::bounded_async()
            .with_media(output_media)
            .with_copy_policy(CopyPolicy::CopyToBranchPool);
        let roles = outputs
            .iter()
            .filter_map(|port| {
                port.signal()
                    .role()
                    .map(|role| SemanticRole::new(role.as_str()))
            })
            .collect::<Vec<_>>();
        let terminal = terminal_roles
            .into_iter()
            .map(SemanticRole::new)
            .collect::<Vec<_>>();
        let descriptor = NodeDescriptor::new(
            NodeTypeId::from(operator_id.as_str()),
            "Python operator",
            inputs,
            outputs,
            ExecutionPartition::AsyncWorker,
            SafetyContract::AllocationAllowed,
            true,
        )
        .map_err(|error| invalid_operator(error.to_string()))?;
        AsyncOperatorManifest::new(
            OperatorId::new(operator_id),
            revision,
            implementation_generation,
            descriptor,
            input_edge,
            output_edge,
            queue_capacity_signals,
            OperatorPermissionPolicy {
                network_allowed,
                filesystem_allowed,
            },
            OperatorDeadlinePolicy { process_timeout_ms },
            if drain_queued {
                OperatorCancellationPolicy::DrainQueued
            } else {
                OperatorCancellationPolicy::DiscardQueued
            },
            if continue_on_failure {
                OperatorFailurePolicy::Continue
            } else {
                OperatorFailurePolicy::StopWorker
            },
            OperatorOutputRolePolicy {
                allowed: roles,
                terminal,
            },
        )
        .map(|value| Self { value })
        .map_err(|error| invalid_operator(error.to_string()))
    }

    #[getter]
    fn operator_id(&self) -> String {
        self.value.operator_id().as_str().to_owned()
    }
}

fn common_media(ports: &[pocketstation::PortSpec], kind: &str) -> PyResult<MediaCaps> {
    let first = ports
        .first()
        .ok_or_else(|| invalid_operator(format!("operator requires at least one {kind} port")))?
        .media();
    if ports
        .iter()
        .any(|port| !port.media().is_compatible_with(&first))
    {
        return Err(invalid_operator(format!(
            "operator {kind} ports must share one compatible edge media contract"
        )));
    }
    Ok(first)
}

#[derive(Clone)]
pub(super) enum PythonOperatorPayload {
    Audio(Arc<[f32]>),
    Text(String),
    Bytes(Vec<u8>),
}

impl PythonOperatorPayload {
    pub(super) fn into_non_audio_core(self) -> Option<SignalPayload> {
        match self {
            Self::Audio(_) => None,
            Self::Text(value) => Some(SignalPayload::Text(value)),
            Self::Bytes(value) => Some(SignalPayload::Bytes(value)),
        }
    }
}

#[pyclass(name = "_OperatorEmission", frozen)]
#[derive(Clone)]
pub(crate) struct PythonOperatorEmission {
    pub(super) signal: SignalSpec,
    pub(super) payload: PythonOperatorPayload,
}

#[pymethods]
impl PythonOperatorEmission {
    #[staticmethod]
    fn audio(py: Python<'_>, samples: PyBuffer<f32>, signal: &PythonSignalSpec) -> PyResult<Self> {
        let samples = samples.as_slice(py).ok_or_else(|| {
            invalid_operator("audio samples must be a C-contiguous float32 buffer")
        })?;
        let owned = samples
            .iter()
            .map(|sample| sample.get())
            .collect::<Vec<_>>();
        Self::new(PythonOperatorPayload::Audio(Arc::from(owned)), signal)
    }

    #[staticmethod]
    fn text(payload: String, signal: &PythonSignalSpec) -> PyResult<Self> {
        Self::new(PythonOperatorPayload::Text(payload), signal)
    }

    #[staticmethod]
    fn bytes(payload: Vec<u8>, signal: &PythonSignalSpec) -> PyResult<Self> {
        Self::new(PythonOperatorPayload::Bytes(payload), signal)
    }
}

impl PythonOperatorEmission {
    fn new(payload: PythonOperatorPayload, signal: &PythonSignalSpec) -> PyResult<Self> {
        let supported = match &payload {
            PythonOperatorPayload::Audio(_) => matches!(
                signal.value.class(),
                pocketstation::SignalClass::Any | pocketstation::SignalClass::PcmAudio
            ),
            PythonOperatorPayload::Text(_) => {
                SignalPayload::Text(String::new()).supports(&signal.value)
            }
            PythonOperatorPayload::Bytes(_) => {
                SignalPayload::Bytes(Vec::new()).supports(&signal.value)
            }
        };
        if !supported {
            return Err(invalid_operator(
                "operator emission payload does not match its SignalSpec",
            ));
        }
        Ok(Self {
            signal: signal.value.clone(),
            payload,
        })
    }
}
