use pocketstation::{
    ExecutionPartition, PortDirection, SafetyContract, SignalPayload, SignalSpec, SourceManifest,
    SourceTypeId,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::errors::coded_reason;
use crate::graph::{PythonPortSpec, PythonSignalSpec};

fn invalid_source(reason: impl Into<String>) -> PyErr {
    PyValueError::new_err(coded_reason("source.invalid_contract", reason.into()))
}

#[pyclass(name = "_SourceManifest", frozen)]
#[derive(Clone)]
pub(crate) struct PythonSourceManifest {
    pub(crate) value: SourceManifest,
}

#[pymethods]
impl PythonSourceManifest {
    #[new]
    #[pyo3(signature = (source_type_id, outputs, revision=1, implementation_generation=1))]
    fn new(
        py: Python<'_>,
        source_type_id: String,
        outputs: Vec<Py<PythonPortSpec>>,
        revision: u32,
        implementation_generation: u32,
    ) -> PyResult<Self> {
        let outputs = outputs
            .into_iter()
            .map(|output| output.borrow(py).value.clone())
            .collect::<Vec<_>>();
        if outputs.iter().any(|output| {
            output.direction() != PortDirection::Output || output.signal().class().is_audio()
        }) {
            return Err(invalid_source(
                "Python-authored sources require non-PCM output ports; use Session.audio_input() for application-owned PCM",
            ));
        }
        let source_type_id =
            SourceTypeId::new(source_type_id).map_err(|error| invalid_source(error.to_string()))?;
        SourceManifest::new(
            source_type_id,
            revision,
            implementation_generation,
            outputs,
            ExecutionPartition::BlockingWorker,
            SafetyContract::AllocationAllowed,
        )
        .map(|value| Self { value })
        .map_err(|error| invalid_source(error.to_string()))
    }

    #[getter]
    fn source_type_id(&self) -> String {
        self.value.source_type_id().as_str().to_owned()
    }

    #[getter]
    fn revision(&self) -> u32 {
        self.value.revision()
    }

    #[getter]
    fn implementation_generation(&self) -> u32 {
        self.value.implementation_generation()
    }
}

#[derive(Clone)]
pub(super) enum PythonSourcePayload {
    Text(String),
    Bytes(Vec<u8>),
}

impl PythonSourcePayload {
    pub(super) fn into_core(self) -> SignalPayload {
        match self {
            Self::Text(value) => SignalPayload::Text(value),
            Self::Bytes(value) => SignalPayload::Bytes(value),
        }
    }
}

#[pyclass(name = "_SourceEmission", frozen)]
#[derive(Clone)]
pub(crate) struct PythonSourceEmission {
    pub(super) output_port: String,
    pub(super) signal: SignalSpec,
    pub(super) payload: PythonSourcePayload,
    pub(super) source_timestamp_ns: Option<u64>,
    pub(super) observed_timestamp_ns: Option<u64>,
    pub(super) duration_ns: Option<u64>,
    pub(super) source_generation: u32,
    pub(super) discontinuity_epoch: u64,
    pub(super) policy_epoch: u64,
    pub(super) clock_domain_id: u32,
    pub(super) terminal: bool,
}

#[pymethods]
impl PythonSourceEmission {
    #[staticmethod]
    #[pyo3(signature = (output_port, payload, signal, source_timestamp_ns=None, observed_timestamp_ns=None, duration_ns=None, source_generation=1, discontinuity_epoch=0, policy_epoch=0, clock_domain_id=1, terminal=false))]
    #[allow(clippy::too_many_arguments)]
    fn text(
        output_port: String,
        payload: String,
        signal: &PythonSignalSpec,
        source_timestamp_ns: Option<u64>,
        observed_timestamp_ns: Option<u64>,
        duration_ns: Option<u64>,
        source_generation: u32,
        discontinuity_epoch: u64,
        policy_epoch: u64,
        clock_domain_id: u32,
        terminal: bool,
    ) -> PyResult<Self> {
        Self::new(
            output_port,
            PythonSourcePayload::Text(payload),
            signal,
            source_timestamp_ns,
            observed_timestamp_ns,
            duration_ns,
            source_generation,
            discontinuity_epoch,
            policy_epoch,
            clock_domain_id,
            terminal,
        )
    }

    #[staticmethod]
    #[pyo3(signature = (output_port, payload, signal, source_timestamp_ns=None, observed_timestamp_ns=None, duration_ns=None, source_generation=1, discontinuity_epoch=0, policy_epoch=0, clock_domain_id=1, terminal=false))]
    #[allow(clippy::too_many_arguments)]
    fn bytes(
        output_port: String,
        payload: Vec<u8>,
        signal: &PythonSignalSpec,
        source_timestamp_ns: Option<u64>,
        observed_timestamp_ns: Option<u64>,
        duration_ns: Option<u64>,
        source_generation: u32,
        discontinuity_epoch: u64,
        policy_epoch: u64,
        clock_domain_id: u32,
        terminal: bool,
    ) -> PyResult<Self> {
        Self::new(
            output_port,
            PythonSourcePayload::Bytes(payload),
            signal,
            source_timestamp_ns,
            observed_timestamp_ns,
            duration_ns,
            source_generation,
            discontinuity_epoch,
            policy_epoch,
            clock_domain_id,
            terminal,
        )
    }
}

impl PythonSourceEmission {
    #[allow(clippy::too_many_arguments)]
    fn new(
        output_port: String,
        payload: PythonSourcePayload,
        signal: &PythonSignalSpec,
        source_timestamp_ns: Option<u64>,
        observed_timestamp_ns: Option<u64>,
        duration_ns: Option<u64>,
        source_generation: u32,
        discontinuity_epoch: u64,
        policy_epoch: u64,
        clock_domain_id: u32,
        terminal: bool,
    ) -> PyResult<Self> {
        if output_port.trim().is_empty() {
            return Err(invalid_source(
                "source emission output port cannot be empty",
            ));
        }
        if source_generation == 0 {
            return Err(invalid_source(
                "source emission generation must be greater than zero",
            ));
        }
        let payload_supported = match &payload {
            PythonSourcePayload::Text(_) => {
                SignalPayload::Text(String::new()).supports(&signal.value)
            }
            PythonSourcePayload::Bytes(_) => {
                SignalPayload::Bytes(Vec::new()).supports(&signal.value)
            }
        };
        if !payload_supported {
            return Err(invalid_source(
                "source emission payload does not match its SignalSpec",
            ));
        }
        Ok(Self {
            output_port,
            signal: signal.value.clone(),
            payload,
            source_timestamp_ns,
            observed_timestamp_ns,
            duration_ns,
            source_generation,
            discontinuity_epoch,
            policy_epoch,
            clock_domain_id,
            terminal,
        })
    }
}
