use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use pocketstation::graph::NodeConfig;
use pocketstation::{
    ConfigError, DerivedStreamHandle, EndpointCancellationOutcome, EndpointConfiguration,
    EndpointDriverFactory, EndpointDriverFinalization, EndpointDriverObservations, EndpointFailure,
    EndpointFailureStage, EndpointPortInput, EndpointReceiver, EndpointStartGate,
    ExecutionPartition, Multiplicity, NodeDefinition, NodeDescriptor, NodeTypeId, OperatorId,
    PortDirection, PortSpec, PreparedEndpointDriver, RouteId, RunningEndpointDriver,
    SafetyContract, Session, SignalEnvelope, SignalPayload, SignalSpec, SourceOutputHandle,
};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyMemoryView};

use crate::errors::{coded_reason, session_endpoint_error, session_error};
use crate::graph::{PythonEdgeContract, PythonSignalSpec};

const SUBSCRIPTION_INPUT_PORT: &str = "signal";
const SUBSCRIPTION_CONFIG_KEY: &str = "subscription_id";
const MAXIMUM_WAIT_MS: u64 = 1_000;

enum ReceiptState {
    Declared,
    Active(pocketstation::EndpointSignalReceiver),
    Closed,
    Fault(String),
}

pub(crate) struct SignalReceipt {
    state: Mutex<ReceiptState>,
    received_total: AtomicU64,
    closed: AtomicBool,
}

impl SignalReceipt {
    fn new() -> Self {
        Self {
            state: Mutex::new(ReceiptState::Declared),
            received_total: AtomicU64::new(0),
            closed: AtomicBool::new(false),
        }
    }

    fn activate(
        &self,
        receiver: pocketstation::EndpointSignalReceiver,
    ) -> Result<(), EndpointFailure> {
        let mut state = self.state.lock().map_err(|_| {
            EndpointFailure::new(
                EndpointFailureStage::Start,
                "Python BusSubscription receipt state is unavailable",
            )
        })?;
        if self.closed.load(Ordering::Acquire) {
            *state = ReceiptState::Closed;
            return Ok(());
        }
        if !matches!(*state, ReceiptState::Declared) {
            return Err(EndpointFailure::new(
                EndpointFailureStage::Start,
                "Python BusSubscription receipt was activated more than once",
            ));
        }
        *state = ReceiptState::Active(receiver);
        Ok(())
    }

    fn poll(&self) -> SignalRead {
        let Ok(mut state) = self.state.lock() else {
            return SignalRead::Fault(
                "Python BusSubscription receipt state is unavailable".to_owned(),
            );
        };
        match &mut *state {
            ReceiptState::Declared => SignalRead::Empty,
            ReceiptState::Active(receiver) => {
                if let Some(envelope) = receiver.try_recv() {
                    if let Err(error) = envelope.validate() {
                        let message = format!(
                            "Python BusSubscription received an invalid signal envelope: {error}"
                        );
                        self.closed.store(true, Ordering::Release);
                        *state = ReceiptState::Fault(message.clone());
                        return SignalRead::Fault(message);
                    }
                    self.received_total.fetch_add(1, Ordering::Relaxed);
                    return SignalRead::Item(Box::new(copy_envelope(&envelope)));
                }
                if receiver.is_abandoned() {
                    self.closed.store(true, Ordering::Release);
                    *state = ReceiptState::Closed;
                    SignalRead::Closed
                } else {
                    SignalRead::Empty
                }
            }
            ReceiptState::Closed => SignalRead::Closed,
            ReceiptState::Fault(message) => SignalRead::Fault(message.clone()),
        }
    }

    fn close(&self) {
        self.closed.store(true, Ordering::Release);
        if let Ok(mut state) = self.state.lock() {
            *state = ReceiptState::Closed;
        }
    }

    #[cfg(test)]
    fn fail(&self, message: impl Into<String>) {
        let message = message.into();
        self.closed.store(true, Ordering::Release);
        if let Ok(mut state) = self.state.lock() {
            *state = ReceiptState::Fault(message);
        }
    }

    fn observations(&self) -> EndpointDriverObservations {
        let received = self.received_total.load(Ordering::Relaxed);
        EndpointDriverObservations {
            frames_received_total: received,
            frames_delivered_total: received,
            ..EndpointDriverObservations::default()
        }
    }
}

pub(crate) type SignalReceipts = Arc<Mutex<std::collections::HashMap<u64, Arc<SignalReceipt>>>>;

pub(crate) fn new_signal_receipts() -> SignalReceipts {
    Arc::new(Mutex::new(std::collections::HashMap::new()))
}

struct SubscriptionDefinition {
    descriptor: NodeDescriptor,
    subscription_id: String,
}

impl NodeDefinition for SubscriptionDefinition {
    fn descriptor(&self) -> NodeDescriptor {
        self.descriptor.clone()
    }

    fn validate_config(&self, config: &NodeConfig) -> Result<(), ConfigError> {
        match config.get(SUBSCRIPTION_CONFIG_KEY) {
            Some(value) if value == self.subscription_id => Ok(()),
            Some(_) => Err(ConfigError::Invalid {
                key: SUBSCRIPTION_CONFIG_KEY.to_owned(),
                reason: "does not match the registered BusSubscription".to_owned(),
            }),
            None => Err(ConfigError::Missing(SUBSCRIPTION_CONFIG_KEY.to_owned())),
        }
    }
}

struct SubscriptionFactory {
    subscription_id: String,
    receipt: Arc<SignalReceipt>,
}

impl EndpointDriverFactory for SubscriptionFactory {
    fn prepare(
        &self,
        mut inputs: Vec<EndpointPortInput>,
    ) -> Result<Box<dyn PreparedEndpointDriver>, EndpointFailure> {
        if inputs.len() != 1 {
            return Err(EndpointFailure::new(
                EndpointFailureStage::Prepare,
                "one Python BusSubscription requires exactly one signal input",
            ));
        }
        let input = inputs.pop().expect("length checked");
        if input
            .context()
            .node_configuration()
            .get(SUBSCRIPTION_CONFIG_KEY)
            != Some(self.subscription_id.as_str())
        {
            return Err(EndpointFailure::new(
                EndpointFailureStage::Prepare,
                "Python BusSubscription configuration does not match its receipt",
            ));
        }
        if !matches!(input.receiver(), EndpointReceiver::Signal(_)) {
            return Err(EndpointFailure::new(
                EndpointFailureStage::Prepare,
                "Python BusSubscription accepts typed signal inputs only",
            ));
        }
        Ok(Box::new(PreparedSubscription {
            input,
            receipt: Arc::clone(&self.receipt),
        }))
    }
}

struct PreparedSubscription {
    input: EndpointPortInput,
    receipt: Arc<SignalReceipt>,
}

impl PreparedEndpointDriver for PreparedSubscription {
    fn start(
        self: Box<Self>,
        _start_gate: Arc<EndpointStartGate>,
    ) -> Result<Box<dyn RunningEndpointDriver>, EndpointFailure> {
        let (receiver, _) = self.input.into_parts();
        let EndpointReceiver::Signal(receiver) = receiver else {
            self.receipt.close();
            return Err(EndpointFailure::new(
                EndpointFailureStage::Start,
                "Python BusSubscription received a realtime audio edge",
            ));
        };
        self.receipt.activate(receiver)?;
        Ok(Box::new(RunningSubscription {
            receipt: Arc::clone(&self.receipt),
        }))
    }

    fn cancel_preparation(self: Box<Self>) -> EndpointCancellationOutcome {
        self.receipt.close();
        EndpointCancellationOutcome {
            observations: self.receipt.observations(),
            result: Ok(()),
        }
    }
}

struct RunningSubscription {
    receipt: Arc<SignalReceipt>,
}

impl RunningEndpointDriver for RunningSubscription {
    fn observations(&self) -> EndpointDriverObservations {
        self.receipt.observations()
    }

    fn request_stop(&mut self) -> Result<(), EndpointFailure> {
        self.receipt.close();
        Ok(())
    }

    fn join_and_finalize(self: Box<Self>) -> EndpointDriverFinalization {
        self.receipt.close();
        EndpointDriverFinalization {
            observations: self.receipt.observations(),
            result: Ok(()),
        }
    }
}

#[pyclass(name = "BusSubscription", frozen)]
pub(crate) struct PythonBusSubscription {
    #[pyo3(get)]
    pub(crate) id: u64,
    #[pyo3(get)]
    pub(crate) session_id: u64,
    #[pyo3(get)]
    pub(crate) route_id: u64,
    signal: PythonSignalSpec,
    edge: PythonEdgeContract,
}

#[pymethods]
impl PythonBusSubscription {
    #[getter]
    fn signal(&self) -> PythonSignalSpec {
        self.signal.clone()
    }

    #[getter]
    fn edge(&self) -> PythonEdgeContract {
        self.edge
    }
}

pub(crate) fn subscribe_derived(
    session: &Session,
    stream: &DerivedStreamHandle,
    signal: &PythonSignalSpec,
    edge: &PythonEdgeContract,
    subscription_id: u64,
    receipts: &SignalReceipts,
) -> PyResult<PythonBusSubscription> {
    declare_subscription(
        session,
        stream.session_id().get(),
        signal,
        edge,
        subscription_id,
        receipts,
        |endpoint| stream.send(endpoint),
    )
}

pub(crate) fn subscribe_source_output(
    session: &Session,
    stream: &SourceOutputHandle,
    signal: &PythonSignalSpec,
    edge: &PythonEdgeContract,
    subscription_id: u64,
    receipts: &SignalReceipts,
) -> PyResult<PythonBusSubscription> {
    declare_subscription(
        session,
        stream.session_id().get(),
        signal,
        edge,
        subscription_id,
        receipts,
        |endpoint| stream.send(endpoint),
    )
}

fn declare_subscription(
    session: &Session,
    stream_session_id: u64,
    signal: &PythonSignalSpec,
    edge: &PythonEdgeContract,
    subscription_id: u64,
    receipts: &SignalReceipts,
    send: impl FnOnce(pocketstation::EndpointHandle) -> Result<RouteId, pocketstation::SessionError>,
) -> PyResult<PythonBusSubscription> {
    if stream_session_id != session.id().get() {
        return Err(PyValueError::new_err(coded_reason(
            "session.invalid_route",
            "BusSubscription stream belongs to a different Session",
        )));
    }
    signal.value.validate().map_err(|error| {
        PyValueError::new_err(coded_reason("graph.invalid_contract", error.to_string()))
    })?;
    if !edge.value.media().supports_signal(&signal.value) {
        return Err(PyValueError::new_err(coded_reason(
            "graph.invalid_contract",
            "BusSubscription edge media does not support its SignalSpec",
        )));
    }

    let subscription_key = subscription_id.to_string();
    let node_type_id =
        format!("io.pocketstation.python.bus-subscription.node.v1.{subscription_id}");
    let operator_id = format!("io.pocketstation.python.bus-subscription.v1.{subscription_id}");
    let input = PortSpec::new(
        SUBSCRIPTION_INPUT_PORT,
        PortDirection::Input,
        signal.value.clone(),
        edge.value.media(),
        Multiplicity::Many,
        true,
    )
    .map_err(|error| {
        PyValueError::new_err(coded_reason("graph.invalid_contract", error.to_string()))
    })?;
    let descriptor = NodeDescriptor::new(
        NodeTypeId::from(node_type_id.as_str()),
        "Python BusSubscription",
        vec![input],
        Vec::new(),
        ExecutionPartition::External,
        SafetyContract::ExternalService,
        true,
    )
    .map_err(|error| {
        PyValueError::new_err(coded_reason("graph.invalid_contract", error.to_string()))
    })?;
    let receipt = Arc::new(SignalReceipt::new());
    session
        .register_endpoint(
            OperatorId::new(operator_id.clone()),
            Arc::new(SubscriptionDefinition {
                descriptor,
                subscription_id: subscription_key.clone(),
            }),
            Arc::new(SubscriptionFactory {
                subscription_id: subscription_key.clone(),
                receipt: Arc::clone(&receipt),
            }),
        )
        .map_err(session_endpoint_error)?;
    let endpoint = session
        .endpoint(
            pocketstation::EndpointDescriptor::new(
                NodeTypeId::from(node_type_id.as_str()),
                OperatorId::new(operator_id),
            )
            .with_configuration(
                EndpointConfiguration::new().with(SUBSCRIPTION_CONFIG_KEY, subscription_key),
            )
            .with_input_edge(edge.value),
        )
        .map_err(session_error)?;
    let route_id = send(endpoint).map_err(session_error)?;
    receipts
        .lock()
        .map_err(|_| PyRuntimeError::new_err("BusSubscription registry is unavailable"))?
        .insert(subscription_id, receipt);
    Ok(PythonBusSubscription {
        id: subscription_id,
        session_id: session.id().get(),
        route_id: route_id.get(),
        signal: signal.clone(),
        edge: *edge,
    })
}

pub(crate) enum SignalRead {
    Item(Box<OwnedSignalEnvelope>),
    Empty,
    Closed,
    Fault(String),
}

#[derive(Clone, Copy)]
pub(crate) struct OwnedSignalSubscriptionMetrics {
    capacity_signals: u64,
    max_payload_bytes: u64,
    maximum_buffered_payload_bytes: u64,
    depth_signals: u64,
    peak_depth_signals: u64,
    enqueued_total: u64,
    received_total: u64,
    dropped_total: u64,
}

#[pyclass(name = "_SignalSubscriptionMetrics", frozen)]
pub(crate) struct PythonSignalSubscriptionMetrics {
    #[pyo3(get)]
    capacity_signals: u64,
    #[pyo3(get)]
    max_payload_bytes: u64,
    #[pyo3(get)]
    maximum_buffered_payload_bytes: u64,
    #[pyo3(get)]
    depth_signals: u64,
    #[pyo3(get)]
    peak_depth_signals: u64,
    #[pyo3(get)]
    enqueued_total: u64,
    #[pyo3(get)]
    received_total: u64,
    #[pyo3(get)]
    dropped_total: u64,
}

impl From<OwnedSignalSubscriptionMetrics> for PythonSignalSubscriptionMetrics {
    fn from(value: OwnedSignalSubscriptionMetrics) -> Self {
        Self {
            capacity_signals: value.capacity_signals,
            max_payload_bytes: value.max_payload_bytes,
            maximum_buffered_payload_bytes: value.maximum_buffered_payload_bytes,
            depth_signals: value.depth_signals,
            peak_depth_signals: value.peak_depth_signals,
            enqueued_total: value.enqueued_total,
            received_total: value.received_total,
            dropped_total: value.dropped_total,
        }
    }
}

#[pyclass(name = "_SignalRead", frozen)]
pub(crate) struct PythonSignalRead {
    #[pyo3(get)]
    status: &'static str,
    envelope: Option<Py<PythonSignalEnvelope>>,
    #[pyo3(get)]
    error: Option<String>,
}

#[pymethods]
impl PythonSignalRead {
    #[getter]
    fn envelope(&self, py: Python<'_>) -> Option<Py<PythonSignalEnvelope>> {
        self.envelope.as_ref().map(|value| value.clone_ref(py))
    }
}

#[derive(Clone, Copy)]
struct OwnedSignalTiming {
    source_timestamp_ns: Option<u64>,
    observed_timestamp_ns: u64,
    session_timestamp_ns: Option<u64>,
    duration_ns: Option<u64>,
}

#[derive(Clone, Copy)]
struct OwnedSignalLineage {
    session_id: u64,
    stream_id: u64,
    source_id: u64,
    clock_id: u32,
    sequence_number: u64,
    source_generation: u32,
    discontinuity_epoch: u64,
    policy_epoch: u64,
}

struct OwnedSignalDerivation {
    upstream_lineage: OwnedSignalLineage,
    upstream_timing: OwnedSignalTiming,
    operator_id: String,
    operator_revision: u32,
    operator_generation: u32,
    connector_id: Option<u64>,
}

struct OwnedSignalAudio {
    samples_f32le: Vec<u8>,
    sample_count: usize,
    sample_rate_hz: u32,
    channel_count: u8,
    stream_id: u64,
    source_id: u64,
    sequence_number: u64,
    timestamp_ns: u64,
}

enum OwnedSignalPayload {
    Audio(OwnedSignalAudio),
    Text(String),
    Bytes(Vec<u8>),
}

pub(crate) struct OwnedSignalEnvelope {
    signal: SignalSpec,
    timing: OwnedSignalTiming,
    lineage: Option<OwnedSignalLineage>,
    derivation: Option<OwnedSignalDerivation>,
    payload: OwnedSignalPayload,
}

#[pyclass(name = "_SignalTiming", frozen)]
pub(crate) struct PythonSignalTiming {
    #[pyo3(get)]
    source_timestamp_ns: Option<u64>,
    #[pyo3(get)]
    observed_timestamp_ns: u64,
    #[pyo3(get)]
    session_timestamp_ns: Option<u64>,
    #[pyo3(get)]
    duration_ns: Option<u64>,
}

#[pyclass(name = "_SignalLineage", frozen)]
pub(crate) struct PythonSignalLineage {
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    stream_id: u64,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    clock_id: u32,
    #[pyo3(get)]
    sequence_number: u64,
    #[pyo3(get)]
    source_generation: u32,
    #[pyo3(get)]
    discontinuity_epoch: u64,
    #[pyo3(get)]
    policy_epoch: u64,
}

#[pyclass(name = "_SignalDerivation", frozen)]
pub(crate) struct PythonSignalDerivation {
    upstream_lineage: Py<PythonSignalLineage>,
    upstream_timing: Py<PythonSignalTiming>,
    #[pyo3(get)]
    operator_id: String,
    #[pyo3(get)]
    operator_revision: u32,
    #[pyo3(get)]
    operator_generation: u32,
    #[pyo3(get)]
    connector_id: Option<u64>,
}

#[pymethods]
impl PythonSignalDerivation {
    #[getter]
    fn upstream_lineage(&self, py: Python<'_>) -> Py<PythonSignalLineage> {
        self.upstream_lineage.clone_ref(py)
    }

    #[getter]
    fn upstream_timing(&self, py: Python<'_>) -> Py<PythonSignalTiming> {
        self.upstream_timing.clone_ref(py)
    }
}

#[pyclass(name = "_SignalAudioPayload", frozen)]
pub(crate) struct PythonSignalAudioPayload {
    samples_f32le: Py<PyBytes>,
    #[pyo3(get)]
    sample_count: usize,
    #[pyo3(get)]
    sample_rate_hz: u32,
    #[pyo3(get)]
    channel_count: u8,
    #[pyo3(get)]
    stream_id: u64,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    sequence_number: u64,
    #[pyo3(get)]
    timestamp_ns: u64,
}

#[pymethods]
impl PythonSignalAudioPayload {
    #[getter]
    fn samples<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyMemoryView>> {
        PyMemoryView::from(self.samples_f32le.bind(py).as_any())
    }

    #[getter]
    fn samples_f32le(&self, py: Python<'_>) -> Py<PyBytes> {
        self.samples_f32le.clone_ref(py)
    }

    #[getter]
    #[allow(clippy::unused_self)]
    const fn sample_format(&self) -> &'static str {
        "f32le"
    }
}

#[pyclass(name = "_SignalEnvelope", frozen)]
pub(crate) struct PythonSignalEnvelope {
    signal: PythonSignalSpec,
    timing: Py<PythonSignalTiming>,
    lineage: Option<Py<PythonSignalLineage>>,
    derivation: Option<Py<PythonSignalDerivation>>,
    #[pyo3(get)]
    payload_kind: &'static str,
    #[pyo3(get)]
    text: Option<String>,
    bytes: Option<Py<PyBytes>>,
    audio: Option<Py<PythonSignalAudioPayload>>,
}

#[pymethods]
impl PythonSignalEnvelope {
    #[getter]
    fn signal(&self) -> PythonSignalSpec {
        self.signal.clone()
    }

    #[getter]
    fn timing(&self, py: Python<'_>) -> Py<PythonSignalTiming> {
        self.timing.clone_ref(py)
    }

    #[getter]
    fn lineage(&self, py: Python<'_>) -> Option<Py<PythonSignalLineage>> {
        self.lineage.as_ref().map(|value| value.clone_ref(py))
    }

    #[getter]
    fn derivation(&self, py: Python<'_>) -> Option<Py<PythonSignalDerivation>> {
        self.derivation.as_ref().map(|value| value.clone_ref(py))
    }

    #[getter]
    fn bytes(&self, py: Python<'_>) -> Option<Py<PyBytes>> {
        self.bytes.as_ref().map(|value| value.clone_ref(py))
    }

    #[getter]
    fn audio(&self, py: Python<'_>) -> Option<Py<PythonSignalAudioPayload>> {
        self.audio.as_ref().map(|value| value.clone_ref(py))
    }
}

fn copy_timing(value: pocketstation::SignalTiming) -> OwnedSignalTiming {
    OwnedSignalTiming {
        source_timestamp_ns: value.source_timestamp_ns(),
        observed_timestamp_ns: value.observed_timestamp_ns(),
        session_timestamp_ns: value.session_timestamp_ns(),
        duration_ns: value.duration_ns(),
    }
}

fn copy_lineage(value: pocketstation::SignalLineage) -> OwnedSignalLineage {
    OwnedSignalLineage {
        session_id: value.session_id().get(),
        stream_id: value.stream_id().get(),
        source_id: value.source_id().get(),
        clock_id: value.clock_id().get(),
        sequence_number: value.sequence_number(),
        source_generation: value.source_generation(),
        discontinuity_epoch: value.discontinuity_epoch(),
        policy_epoch: value.policy_epoch(),
    }
}

fn copy_envelope(value: &SignalEnvelope) -> OwnedSignalEnvelope {
    let payload = match value.payload() {
        SignalPayload::Audio(frame) => OwnedSignalPayload::Audio(OwnedSignalAudio {
            samples_f32le: f32_samples_to_le_bytes(frame.samples()),
            sample_count: frame.samples().len(),
            sample_rate_hz: frame.sample_rate_hz(),
            channel_count: frame.channels(),
            stream_id: frame.stream_id().get(),
            source_id: frame.source_id().get(),
            sequence_number: frame.sequence_number(),
            timestamp_ns: frame.timestamp_ns(),
        }),
        SignalPayload::Text(text) => OwnedSignalPayload::Text(text.clone()),
        SignalPayload::Bytes(bytes) => OwnedSignalPayload::Bytes(bytes.clone()),
    };
    let derivation = value.derivation().map(|derivation| OwnedSignalDerivation {
        upstream_lineage: copy_lineage(derivation.upstream_lineage()),
        upstream_timing: copy_timing(derivation.upstream_timing()),
        operator_id: derivation.operator_id().as_str().to_owned(),
        operator_revision: derivation.operator_revision(),
        operator_generation: derivation.operator_generation(),
        connector_id: derivation
            .connector_id()
            .map(pocketstation::ConnectorId::get),
    });
    OwnedSignalEnvelope {
        signal: value.signal_spec().clone(),
        timing: copy_timing(value.timing()),
        lineage: value.lineage().map(copy_lineage),
        derivation,
        payload,
    }
}

fn f32_samples_to_le_bytes(samples: &[f32]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(std::mem::size_of_val(samples));
    for sample in samples {
        bytes.extend_from_slice(&sample.to_le_bytes());
    }
    bytes
}

fn python_timing(py: Python<'_>, value: OwnedSignalTiming) -> PyResult<Py<PythonSignalTiming>> {
    Py::new(
        py,
        PythonSignalTiming {
            source_timestamp_ns: value.source_timestamp_ns,
            observed_timestamp_ns: value.observed_timestamp_ns,
            session_timestamp_ns: value.session_timestamp_ns,
            duration_ns: value.duration_ns,
        },
    )
}

fn python_lineage(py: Python<'_>, value: OwnedSignalLineage) -> PyResult<Py<PythonSignalLineage>> {
    Py::new(
        py,
        PythonSignalLineage {
            session_id: value.session_id,
            stream_id: value.stream_id,
            source_id: value.source_id,
            clock_id: value.clock_id,
            sequence_number: value.sequence_number,
            source_generation: value.source_generation,
            discontinuity_epoch: value.discontinuity_epoch,
            policy_epoch: value.policy_epoch,
        },
    )
}

fn python_envelope(py: Python<'_>, value: OwnedSignalEnvelope) -> PyResult<PythonSignalEnvelope> {
    let timing = python_timing(py, value.timing)?;
    let lineage = value
        .lineage
        .map(|value| python_lineage(py, value))
        .transpose()?;
    let derivation = value
        .derivation
        .map(|value| {
            let upstream_lineage = python_lineage(py, value.upstream_lineage)?;
            let upstream_timing = python_timing(py, value.upstream_timing)?;
            Py::new(
                py,
                PythonSignalDerivation {
                    upstream_lineage,
                    upstream_timing,
                    operator_id: value.operator_id,
                    operator_revision: value.operator_revision,
                    operator_generation: value.operator_generation,
                    connector_id: value.connector_id,
                },
            )
        })
        .transpose()?;
    let (payload_kind, text, bytes, audio) = match value.payload {
        OwnedSignalPayload::Text(text) => ("text", Some(text), None, None),
        OwnedSignalPayload::Bytes(bytes) => {
            ("bytes", None, Some(PyBytes::new(py, &bytes).unbind()), None)
        }
        OwnedSignalPayload::Audio(audio) => {
            let samples_f32le = PyBytes::new(py, &audio.samples_f32le).unbind();
            let audio = Py::new(
                py,
                PythonSignalAudioPayload {
                    samples_f32le,
                    sample_count: audio.sample_count,
                    sample_rate_hz: audio.sample_rate_hz,
                    channel_count: audio.channel_count,
                    stream_id: audio.stream_id,
                    source_id: audio.source_id,
                    sequence_number: audio.sequence_number,
                    timestamp_ns: audio.timestamp_ns,
                },
            )?;
            ("audio", None, None, Some(audio))
        }
    };
    Ok(PythonSignalEnvelope {
        signal: PythonSignalSpec {
            value: value.signal,
        },
        timing,
        lineage,
        derivation,
        payload_kind,
        text,
        bytes,
        audio,
    })
}

fn receipt(
    receipts: &SignalReceipts,
    session_id: u64,
    subscription: &PythonBusSubscription,
) -> PyResult<Arc<SignalReceipt>> {
    if subscription.session_id != session_id {
        return Err(PyValueError::new_err(coded_reason(
            "session.invalid_route",
            "BusSubscription belongs to a different running Session",
        )));
    }
    receipts
        .lock()
        .map_err(|_| PyRuntimeError::new_err("BusSubscription registry is unavailable"))?
        .get(&subscription.id)
        .cloned()
        .ok_or_else(|| {
            PyValueError::new_err(coded_reason(
                "session.invalid_route",
                "BusSubscription is not registered on this Session",
            ))
        })
}

pub(crate) fn poll_signal(
    py: Python<'_>,
    receipts: &SignalReceipts,
    session_id: u64,
    subscription: &PythonBusSubscription,
) -> PyResult<PythonSignalRead> {
    let receipt = receipt(receipts, session_id, subscription)?;
    let read = py.detach(|| receipt.poll());
    python_read(py, read)
}

pub(crate) fn wait_signal(
    py: Python<'_>,
    receipts: &SignalReceipts,
    session_id: u64,
    subscription: &PythonBusSubscription,
    timeout_ms: u64,
) -> PyResult<PythonSignalRead> {
    if timeout_ms > MAXIMUM_WAIT_MS {
        return Err(PyValueError::new_err(format!(
            "timeout_ms must be at most {MAXIMUM_WAIT_MS}"
        )));
    }
    let receipt = receipt(receipts, session_id, subscription)?;
    let read = py.detach(|| {
        let deadline = Instant::now() + Duration::from_millis(timeout_ms);
        loop {
            let read = receipt.poll();
            if !matches!(read, SignalRead::Empty) || Instant::now() >= deadline {
                return read;
            }
            thread::sleep(Duration::from_millis(1));
        }
    });
    python_read(py, read)
}

pub(crate) fn close_signal(
    receipts: &SignalReceipts,
    session_id: u64,
    subscription: &PythonBusSubscription,
) -> PyResult<()> {
    receipt(receipts, session_id, subscription)?.close();
    Ok(())
}

pub(crate) fn validate_signal_subscription(
    receipts: &SignalReceipts,
    session_id: u64,
    subscription: &PythonBusSubscription,
) -> PyResult<()> {
    receipt(receipts, session_id, subscription).map(|_| ())
}

pub(crate) fn copy_signal_metrics(
    running: &pocketstation::RunningSession,
    route_id: u64,
) -> Result<OwnedSignalSubscriptionMetrics, String> {
    let derived_routes = running.derived_route_metrics();
    let metrics = derived_routes
        .iter()
        .find(|metrics| metrics.route_id.get() == route_id)
        .ok_or_else(|| format!("typed signal metrics are unavailable for route {route_id}"))?;
    let value = metrics.output;
    Ok(OwnedSignalSubscriptionMetrics {
        capacity_signals: value.capacity_signals,
        max_payload_bytes: value.max_payload_bytes,
        maximum_buffered_payload_bytes: value.maximum_buffered_payload_bytes,
        depth_signals: value.depth_signals,
        peak_depth_signals: value.peak_depth_signals,
        enqueued_total: value.enqueued_total,
        received_total: value.received_total,
        dropped_total: value.dropped_total,
    })
}

fn python_read(py: Python<'_>, read: SignalRead) -> PyResult<PythonSignalRead> {
    match read {
        SignalRead::Item(envelope) => Ok(PythonSignalRead {
            status: "item",
            envelope: Some(Py::new(py, python_envelope(py, *envelope)?)?),
            error: None,
        }),
        SignalRead::Empty => Ok(PythonSignalRead {
            status: "empty",
            envelope: None,
            error: None,
        }),
        SignalRead::Closed => Ok(PythonSignalRead {
            status: "closed",
            envelope: None,
            error: None,
        }),
        SignalRead::Fault(error) => Ok(PythonSignalRead {
            status: "fault",
            envelope: None,
            error: Some(error),
        }),
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonBusSubscription>()?;
    module.add_class::<PythonSignalRead>()?;
    module.add_class::<PythonSignalSubscriptionMetrics>()?;
    module.add_class::<PythonSignalTiming>()?;
    module.add_class::<PythonSignalLineage>()?;
    module.add_class::<PythonSignalDerivation>()?;
    module.add_class::<PythonSignalAudioPayload>()?;
    module.add_class::<PythonSignalEnvelope>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{ReceiptState, SignalRead, SignalReceipt};

    #[test]
    fn declared_receipt_is_empty_and_close_is_sticky() {
        let receipt = SignalReceipt::new();
        assert!(matches!(receipt.poll(), SignalRead::Empty));
        receipt.close();
        receipt.close();
        assert!(matches!(receipt.poll(), SignalRead::Closed));
        let state = receipt.state.lock().expect("receipt state");
        assert!(matches!(&*state, ReceiptState::Closed));
    }

    #[test]
    fn receipt_fault_is_sticky() {
        let receipt = SignalReceipt::new();
        receipt.fail("fixture fault");
        assert!(matches!(receipt.poll(), SignalRead::Fault(message) if message == "fixture fault"));
        assert!(matches!(receipt.poll(), SignalRead::Fault(message) if message == "fixture fault"));
    }
}
