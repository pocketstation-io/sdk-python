use std::path::PathBuf;
use std::time::{Duration, Instant};

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::errors::coded_reason;

pub(crate) const MAXIMUM_WAIT_MS: u64 = 1_000;

#[pyclass(name = "_SidecarProcessSpec", frozen)]
pub(crate) struct PythonSidecarProcessSpec {
    #[pyo3(get)]
    pub(crate) id: u64,
    #[pyo3(get)]
    program: PathBuf,
    #[pyo3(get)]
    arguments: Vec<String>,
    configuration: Vec<u8>,
    #[pyo3(get)]
    data_capacity_messages: usize,
    #[pyo3(get)]
    max_signal_id_bytes: usize,
    #[pyo3(get)]
    max_role_bytes: usize,
    #[pyo3(get)]
    max_schema_bytes: usize,
    #[pyo3(get)]
    max_payload_bytes: usize,
    #[pyo3(get)]
    ready_timeout_ms: u64,
    #[pyo3(get)]
    processing_timeout_ms: u64,
    #[pyo3(get)]
    shutdown_timeout_ms: u64,
}

#[pymethods]
impl PythonSidecarProcessSpec {
    #[new]
    #[pyo3(signature = (
        id,
        program,
        arguments=Vec::new(),
        configuration=Vec::new(),
        data_capacity_messages=64,
        max_signal_id_bytes=256,
        max_role_bytes=256,
        max_schema_bytes=1024,
        max_payload_bytes=1048576,
        ready_timeout_ms=5000,
        processing_timeout_ms=5000,
        shutdown_timeout_ms=2000,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        id: u64,
        program: PathBuf,
        arguments: Vec<String>,
        configuration: Vec<u8>,
        data_capacity_messages: usize,
        max_signal_id_bytes: usize,
        max_role_bytes: usize,
        max_schema_bytes: usize,
        max_payload_bytes: usize,
        ready_timeout_ms: u64,
        processing_timeout_ms: u64,
        shutdown_timeout_ms: u64,
    ) -> PyResult<Self> {
        if id == 0 {
            return Err(invalid_spec("sidecar ID must be non-zero"));
        }
        if program.as_os_str().is_empty() {
            return Err(invalid_spec("program must not be empty"));
        }
        if data_capacity_messages == 0 {
            return Err(invalid_spec(
                "data_capacity_messages must be greater than zero",
            ));
        }
        if max_signal_id_bytes == 0
            || max_role_bytes == 0
            || max_schema_bytes == 0
            || max_payload_bytes == 0
        {
            return Err(invalid_spec("protocol limits must be greater than zero"));
        }
        if ready_timeout_ms == 0 || processing_timeout_ms == 0 || shutdown_timeout_ms == 0 {
            return Err(invalid_spec("sidecar deadlines must be greater than zero"));
        }
        Ok(Self {
            id,
            program,
            arguments,
            configuration,
            data_capacity_messages,
            max_signal_id_bytes,
            max_role_bytes,
            max_schema_bytes,
            max_payload_bytes,
            ready_timeout_ms,
            processing_timeout_ms,
            shutdown_timeout_ms,
        })
    }

    #[getter]
    fn configuration(&self, py: Python<'_>) -> Py<PyBytes> {
        PyBytes::new(py, &self.configuration).unbind()
    }
}

impl PythonSidecarProcessSpec {
    pub(crate) fn to_core(&self) -> pocketstation::SidecarProcessSpec {
        let mut spec = pocketstation::SidecarProcessSpec::new(self.id, self.program.clone());
        spec.arguments = self.arguments.iter().map(Into::into).collect();
        spec.configuration.clone_from(&self.configuration);
        spec.data_capacity_messages = self.data_capacity_messages;
        spec.protocol_limits = pocketstation::SidecarProtocolLimits {
            max_signal_id_bytes: self.max_signal_id_bytes,
            max_role_bytes: self.max_role_bytes,
            max_schema_bytes: self.max_schema_bytes,
            max_payload_bytes: self.max_payload_bytes,
        };
        spec.deadlines = pocketstation::SidecarDeadlines {
            ready: Duration::from_millis(self.ready_timeout_ms),
            processing: Duration::from_millis(self.processing_timeout_ms),
            shutdown: Duration::from_millis(self.shutdown_timeout_ms),
        };
        spec
    }
}

#[pyclass(name = "_SidecarMessage", frozen)]
#[derive(Clone)]
pub(crate) struct PythonSidecarMessage {
    pub(crate) value: pocketstation::SidecarMessage,
}

#[pymethods]
impl PythonSidecarMessage {
    #[new]
    #[pyo3(signature = (
        *,
        kind,
        stream_id,
        sequence_number,
        timestamp_ns,
        signal_id,
        payload,
        terminal=false,
        role=None,
        schema=None,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        kind: &str,
        stream_id: u64,
        sequence_number: u64,
        timestamp_ns: u64,
        signal_id: String,
        payload: Vec<u8>,
        terminal: bool,
        role: Option<String>,
        schema: Option<String>,
    ) -> PyResult<Self> {
        if signal_id.is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "sidecar.invalid_message",
                "signal_id must not be empty",
            )));
        }
        Ok(Self {
            value: pocketstation::SidecarMessage {
                kind: parse_kind(kind)?,
                terminal,
                stream_id,
                sequence_number,
                timestamp_ns,
                signal_id,
                role,
                schema,
                payload,
            },
        })
    }

    #[getter]
    fn kind(&self) -> &'static str {
        kind_name(self.value.kind)
    }

    #[getter]
    const fn terminal(&self) -> bool {
        self.value.terminal
    }

    #[getter]
    const fn stream_id(&self) -> u64 {
        self.value.stream_id
    }

    #[getter]
    const fn sequence_number(&self) -> u64 {
        self.value.sequence_number
    }

    #[getter]
    const fn timestamp_ns(&self) -> u64 {
        self.value.timestamp_ns
    }

    #[getter]
    fn signal_id(&self) -> &str {
        &self.value.signal_id
    }

    #[getter]
    fn role(&self) -> Option<&str> {
        self.value.role.as_deref()
    }

    #[getter]
    fn schema(&self) -> Option<&str> {
        self.value.schema.as_deref()
    }

    #[getter]
    fn payload(&self, py: Python<'_>) -> Py<PyBytes> {
        PyBytes::new(py, &self.value.payload).unbind()
    }
}

impl From<pocketstation::SidecarMessage> for PythonSidecarMessage {
    fn from(value: pocketstation::SidecarMessage) -> Self {
        Self { value }
    }
}

#[pyclass(name = "_SidecarSnapshot", frozen)]
pub(crate) struct PythonSidecarSnapshot {
    #[pyo3(get)]
    pub(crate) sidecar_id: u64,
    #[pyo3(get)]
    state: &'static str,
    #[pyo3(get)]
    state_transitions: u64,
    #[pyo3(get)]
    data_enqueued_total: u64,
    #[pyo3(get)]
    data_received_total: u64,
    #[pyo3(get)]
    data_dropped_total: u64,
    #[pyo3(get)]
    protocol_failures_total: u64,
    #[pyo3(get)]
    timeouts_total: u64,
    #[pyo3(get)]
    forced_kills_total: u64,
    #[pyo3(get)]
    reaps_total: u64,
}

#[pymethods]
impl PythonSidecarSnapshot {
    fn visited(&self, state: &str) -> PyResult<bool> {
        let state = parse_state(state)?;
        Ok(self.state_transitions & (1u64 << state as u8) != 0)
    }
}

impl From<pocketstation::SessionSidecarMetrics> for PythonSidecarSnapshot {
    fn from(value: pocketstation::SessionSidecarMetrics) -> Self {
        Self {
            sidecar_id: value.sidecar_id,
            state: state_name(value.host.state),
            state_transitions: value.host.state_transitions,
            data_enqueued_total: value.host.data_enqueued_total,
            data_received_total: value.host.data_received_total,
            data_dropped_total: value.host.data_dropped_total,
            protocol_failures_total: value.host.protocol_failures_total,
            timeouts_total: value.host.timeouts_total,
            forced_kills_total: value.host.forced_kills_total,
            reaps_total: value.host.reaps_total,
        }
    }
}

pub(crate) enum OwnedSidecarRead {
    Item(pocketstation::SidecarMessage),
    Empty,
    Closed,
}

#[pyclass(name = "_SidecarRead", frozen)]
pub(crate) struct PythonSidecarRead {
    #[pyo3(get)]
    status: &'static str,
    message: Option<PythonSidecarMessage>,
}

#[pymethods]
impl PythonSidecarRead {
    #[getter]
    fn message(&self) -> Option<PythonSidecarMessage> {
        self.message.clone()
    }
}

impl From<OwnedSidecarRead> for PythonSidecarRead {
    fn from(value: OwnedSidecarRead) -> Self {
        match value {
            OwnedSidecarRead::Item(message) => Self {
                status: "item",
                message: Some(message.into()),
            },
            OwnedSidecarRead::Empty => Self {
                status: "empty",
                message: None,
            },
            OwnedSidecarRead::Closed => Self {
                status: "closed",
                message: None,
            },
        }
    }
}

pub(crate) fn poll_sidecar(
    running: &pocketstation::RunningSession,
    sidecar_id: u64,
) -> Result<OwnedSidecarRead, String> {
    match running.try_receive_sidecar_signal(sidecar_id) {
        Ok(Some(message)) => Ok(OwnedSidecarRead::Item(message)),
        Ok(None) => Ok(OwnedSidecarRead::Empty),
        Err(pocketstation::SidecarHostError::Closed) => Ok(OwnedSidecarRead::Closed),
        Err(error) => Err(sidecar_error_message(error)),
    }
}

pub(crate) fn wait_sidecar(
    running: &pocketstation::RunningSession,
    sidecar_id: u64,
    timeout: Duration,
) -> Result<OwnedSidecarRead, String> {
    let deadline = Instant::now() + timeout;
    loop {
        match poll_sidecar(running, sidecar_id)? {
            OwnedSidecarRead::Empty if Instant::now() < deadline => {
                std::thread::sleep(Duration::from_millis(1));
            }
            value => return Ok(value),
        }
    }
}

pub(crate) fn sidecar_snapshot(
    running: &pocketstation::RunningSession,
    sidecar_id: u64,
) -> Result<pocketstation::SessionSidecarMetrics, String> {
    running
        .sidecar_metrics()
        .into_vec()
        .into_iter()
        .find(|metrics| metrics.sidecar_id == sidecar_id)
        .ok_or_else(|| {
            coded_reason(
                "sidecar.unknown",
                format!("sidecar process ID {sidecar_id} is not owned by this Session"),
            )
        })
}

pub(crate) fn sidecar_error_message(error: pocketstation::SidecarHostError) -> String {
    let code = match error {
        pocketstation::SidecarHostError::InvalidConfiguration(_) => "sidecar.invalid_configuration",
        pocketstation::SidecarHostError::Spawn(_) => "sidecar.spawn_failed",
        pocketstation::SidecarHostError::ThreadSpawn(_) => "sidecar.thread_spawn_failed",
        pocketstation::SidecarHostError::MissingPipe(_) => "sidecar.missing_pipe",
        pocketstation::SidecarHostError::Io(_) => "sidecar.io",
        pocketstation::SidecarHostError::Protocol(_) => "sidecar.protocol",
        pocketstation::SidecarHostError::FrameTooLarge => "sidecar.frame_too_large",
        pocketstation::SidecarHostError::DataQueueFull => "sidecar.queue_full",
        pocketstation::SidecarHostError::ControlQueueFull => "sidecar.control_queue_full",
        pocketstation::SidecarHostError::Closed => "sidecar.closed",
        pocketstation::SidecarHostError::UnexpectedEof => "sidecar.unexpected_eof",
        pocketstation::SidecarHostError::UnexpectedMessage { .. } => "sidecar.unexpected_message",
        pocketstation::SidecarHostError::Timeout(_) => "sidecar.timeout",
        pocketstation::SidecarHostError::ProcessingTimeout => "sidecar.processing_timeout",
        pocketstation::SidecarHostError::InvalidState { .. } => "sidecar.invalid_state",
        pocketstation::SidecarHostError::InvalidDataKind(_) => "sidecar.invalid_message_kind",
        pocketstation::SidecarHostError::Wait(_) => "sidecar.wait_failed",
        pocketstation::SidecarHostError::Kill(_) => "sidecar.kill_failed",
        pocketstation::SidecarHostError::AlreadyReaped => "sidecar.already_reaped",
        pocketstation::SidecarHostError::UnknownSidecar(_) => "sidecar.unknown",
    };
    coded_reason(code, error.to_string())
}

fn invalid_spec(reason: &str) -> PyErr {
    PyValueError::new_err(coded_reason("sidecar.invalid_configuration", reason))
}

fn parse_kind(value: &str) -> PyResult<pocketstation::SidecarMessageKind> {
    match value {
        "signal" => Ok(pocketstation::SidecarMessageKind::Signal),
        "ready" => Ok(pocketstation::SidecarMessageKind::Ready),
        "error" => Ok(pocketstation::SidecarMessageKind::Error),
        "cancel" => Ok(pocketstation::SidecarMessageKind::Cancel),
        "close" => Ok(pocketstation::SidecarMessageKind::Close),
        "hello" => Ok(pocketstation::SidecarMessageKind::Hello),
        "manifest" => Ok(pocketstation::SidecarMessageKind::Manifest),
        "configure" => Ok(pocketstation::SidecarMessageKind::Configure),
        "observation" => Ok(pocketstation::SidecarMessageKind::Observation),
        "closed" => Ok(pocketstation::SidecarMessageKind::Closed),
        _ => Err(PyValueError::new_err(coded_reason(
            "sidecar.invalid_message_kind",
            "kind must be signal, ready, error, cancel, close, hello, manifest, configure, observation, or closed",
        ))),
    }
}

const fn kind_name(value: pocketstation::SidecarMessageKind) -> &'static str {
    match value {
        pocketstation::SidecarMessageKind::Signal => "signal",
        pocketstation::SidecarMessageKind::Ready => "ready",
        pocketstation::SidecarMessageKind::Error => "error",
        pocketstation::SidecarMessageKind::Cancel => "cancel",
        pocketstation::SidecarMessageKind::Close => "close",
        pocketstation::SidecarMessageKind::Hello => "hello",
        pocketstation::SidecarMessageKind::Manifest => "manifest",
        pocketstation::SidecarMessageKind::Configure => "configure",
        pocketstation::SidecarMessageKind::Observation => "observation",
        pocketstation::SidecarMessageKind::Closed => "closed",
    }
}

fn parse_state(value: &str) -> PyResult<pocketstation::SidecarState> {
    match value {
        "spawned" => Ok(pocketstation::SidecarState::Spawned),
        "hello" => Ok(pocketstation::SidecarState::Hello),
        "manifest" => Ok(pocketstation::SidecarState::Manifest),
        "configure" => Ok(pocketstation::SidecarState::Configure),
        "ready" => Ok(pocketstation::SidecarState::Ready),
        "running" => Ok(pocketstation::SidecarState::Running),
        "cancelling" => Ok(pocketstation::SidecarState::Cancelling),
        "closing" => Ok(pocketstation::SidecarState::Closing),
        "closed" => Ok(pocketstation::SidecarState::Closed),
        "reaped" => Ok(pocketstation::SidecarState::Reaped),
        "failed" => Ok(pocketstation::SidecarState::Failed),
        _ => Err(PyValueError::new_err(coded_reason(
            "sidecar.invalid_state",
            "unknown sidecar state",
        ))),
    }
}

const fn state_name(value: pocketstation::SidecarState) -> &'static str {
    match value {
        pocketstation::SidecarState::Spawned => "spawned",
        pocketstation::SidecarState::Hello => "hello",
        pocketstation::SidecarState::Manifest => "manifest",
        pocketstation::SidecarState::Configure => "configure",
        pocketstation::SidecarState::Ready => "ready",
        pocketstation::SidecarState::Running => "running",
        pocketstation::SidecarState::Cancelling => "cancelling",
        pocketstation::SidecarState::Closing => "closing",
        pocketstation::SidecarState::Closed => "closed",
        pocketstation::SidecarState::Reaped => "reaped",
        pocketstation::SidecarState::Failed => "failed",
    }
}

pub(crate) fn runtime_error(error: String) -> PyErr {
    PyRuntimeError::new_err(error)
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonSidecarProcessSpec>()?;
    module.add_class::<PythonSidecarMessage>()?;
    module.add_class::<PythonSidecarRead>()?;
    module.add_class::<PythonSidecarSnapshot>()?;
    Ok(())
}
