use std::sync::mpsc::{sync_channel, SyncSender};
use std::time::Duration;

use pocketstation::PolledAudioPollError;
use pyo3::exceptions::{PyIndexError, PyRuntimeError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyMemoryView};

use crate::session::SessionCommand;

#[derive(Clone, Copy)]
#[pyclass(name = "ClockDomainDescriptor", frozen)]
pub(crate) struct PythonClockDomainDescriptor {
    #[pyo3(get)]
    id: u32,
    #[pyo3(get)]
    kind: &'static str,
    #[pyo3(get)]
    origin: &'static str,
    #[pyo3(get)]
    tick_rate_hz: Option<u64>,
}

#[pymethods]
impl PythonClockDomainDescriptor {
    fn __eq__(&self, other: &Self) -> bool {
        self.id == other.id
            && self.kind == other.kind
            && self.origin == other.origin
            && self.tick_rate_hz == other.tick_rate_hz
    }
}

pub(crate) fn clock_domain_descriptor(
    id: pocketstation::ClockDomainId,
) -> PythonClockDomainDescriptor {
    let descriptor = pocketstation::timing::describe_clock_domain(id);
    let kind = match descriptor.kind() {
        pocketstation::timing::ClockDomainKind::Unspecified => "unspecified",
        pocketstation::timing::ClockDomainKind::ProcessMonotonic => "process-monotonic",
        pocketstation::timing::ClockDomainKind::ProviderDefined => "provider-defined",
    };
    let origin = match descriptor.origin() {
        pocketstation::timing::ClockDomainOrigin::Unspecified => "unspecified",
        pocketstation::timing::ClockDomainOrigin::ProcessStart => "process-start",
        pocketstation::timing::ClockDomainOrigin::ProviderDefined => "provider-defined",
    };
    PythonClockDomainDescriptor {
        id: descriptor.id().get(),
        kind,
        origin,
        tick_rate_hz: descriptor.tick_rate_hz(),
    }
}

#[pyclass(name = "AudioFrame", frozen)]
pub(crate) struct PythonAudioFrame {
    samples_f32le: Py<PyBytes>,
    sample_count: usize,
    #[pyo3(get)]
    sample_rate_hz: u32,
    #[pyo3(get)]
    channel_count: u8,
    #[pyo3(get)]
    session_id: u64,
    #[pyo3(get)]
    stream_id: u64,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    clock_id: u32,
    sequence_number: u64,
    #[pyo3(get)]
    timestamp_start_ns: u64,
    #[pyo3(get)]
    duration_ns: u64,
    #[pyo3(get)]
    source_generation: u32,
    #[pyo3(get)]
    discontinuity_epoch: u64,
    #[pyo3(get)]
    permission_epoch: u64,
    #[pyo3(get)]
    endpoint_id: u64,
    #[pyo3(get)]
    connector_id: Option<u64>,
    #[pyo3(get)]
    route_id: u64,
    #[pyo3(get)]
    route_enqueued_at_ns: u64,
    #[pyo3(get)]
    route_received_at_ns: u64,
    #[pyo3(get)]
    endpoint_enqueued_at_ns: Option<u64>,
    #[pyo3(get)]
    polled_at_ns: Option<u64>,
}

#[pymethods]
impl PythonAudioFrame {
    fn __repr__(&self) -> String {
        format!(
            "AudioFrame(stem_id={}, source_id={}, sequence_number={}, timestamp_start_ns={}, sample_count={}, sample_rate_hz={}, channel_count={}, discontinuity_epoch={})",
            self.stem_id,
            self.source_id,
            self.sequence_number,
            self.timestamp_start_ns,
            self.sample_count,
            self.sample_rate_hz,
            self.channel_count,
            self.discontinuity_epoch,
        )
    }

    /// Read-only view over the frame's Python-owned PCM copy.
    #[getter]
    fn samples<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyMemoryView>> {
        PyMemoryView::from(self.samples_f32le.bind(py).as_any())
    }

    /// Owned bytes suitable for numpy.frombuffer(..., dtype="<f4").
    #[getter]
    fn samples_f32le(&self, py: Python<'_>) -> Py<PyBytes> {
        self.samples_f32le.clone_ref(py)
    }

    #[getter]
    const fn sample_count(&self) -> usize {
        self.sample_count
    }

    #[getter]
    #[allow(clippy::unused_self)] // PyO3 property getter is instance-shaped.
    const fn sample_format(&self) -> &'static str {
        "f32le"
    }

    #[getter]
    const fn sequence_number(&self) -> u64 {
        self.sequence_number
    }

    #[getter]
    fn clock(&self) -> PythonClockDomainDescriptor {
        clock_domain_descriptor(pocketstation::ClockDomainId::new(self.clock_id))
    }
}

#[pyclass(name = "AudioBatch", frozen)]
pub(crate) struct PythonAudioBatch {
    frames: Vec<Py<PythonAudioFrame>>,
}

#[pymethods]
impl PythonAudioBatch {
    const fn __len__(&self) -> usize {
        self.frames.len()
    }

    fn frames(&self, py: Python<'_>) -> Vec<Py<PythonAudioFrame>> {
        self.frames
            .iter()
            .map(|frame| frame.clone_ref(py))
            .collect()
    }

    fn __getitem__(&self, index: isize, py: Python<'_>) -> PyResult<Py<PythonAudioFrame>> {
        let length = self.frames.len().cast_signed();
        let normalized = if index < 0 { length + index } else { index };
        if normalized < 0 || normalized >= length {
            return Err(PyIndexError::new_err("audio batch index out of range"));
        }
        Ok(self.frames[normalized.cast_unsigned()].clone_ref(py))
    }
}

pub(crate) struct OwnedAudioFrame {
    pub(crate) samples_f32le: Vec<u8>,
    pub(crate) sample_count: usize,
    pub(crate) sample_rate_hz: u32,
    pub(crate) channel_count: u8,
    pub(crate) session_id: u64,
    pub(crate) stream_id: u64,
    pub(crate) source_id: u64,
    pub(crate) stem_id: u64,
    pub(crate) clock_id: u32,
    pub(crate) sequence_number: u64,
    pub(crate) timestamp_start_ns: u64,
    pub(crate) duration_ns: u64,
    pub(crate) source_generation: u32,
    pub(crate) discontinuity_epoch: u64,
    pub(crate) permission_epoch: u64,
    pub(crate) endpoint_id: u64,
    pub(crate) connector_id: Option<u64>,
    pub(crate) route_id: u64,
    pub(crate) route_enqueued_at_ns: u64,
    pub(crate) route_received_at_ns: u64,
    pub(crate) endpoint_enqueued_at_ns: Option<u64>,
    pub(crate) polled_at_ns: Option<u64>,
}

pub(crate) fn request_audio_batch(
    commands: &SyncSender<SessionCommand>,
) -> PyResult<Option<Vec<OwnedAudioFrame>>> {
    let (response, receiver) = sync_channel(1);
    commands
        .send(SessionCommand::PollAudio { response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not return audio"))?
        .map_err(PyRuntimeError::new_err)
}

pub(crate) fn request_audio_batch_wait(
    commands: &SyncSender<SessionCommand>,
    timeout: Duration,
) -> PyResult<Option<Vec<OwnedAudioFrame>>> {
    let (response, receiver) = sync_channel(1);
    commands
        .send(SessionCommand::WaitAudio { timeout, response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not return audio"))?
        .map_err(PyRuntimeError::new_err)
}

pub(crate) fn copy_audio_batch(
    running: &pocketstation::RunningSession,
) -> Result<Option<Vec<OwnedAudioFrame>>, String> {
    let batch = match running.try_poll_audio() {
        Ok(batch) => batch,
        Err(PolledAudioPollError::Empty) => return Ok(None),
        Err(error) => return Err(error.to_string()),
    };
    copy_polled_audio_batch(batch).map(Some)
}

fn copy_polled_audio_batch(
    batch: pocketstation::PolledAudioBatchLease,
) -> Result<Vec<OwnedAudioFrame>, String> {
    let mut frames = Vec::with_capacity(batch.len());
    for index in 0..batch.len() {
        let frame = batch
            .frame(index)
            .ok_or_else(|| "native audio batch changed during copy".to_owned())?;
        let lineage = frame.lineage();
        frames.push(OwnedAudioFrame {
            samples_f32le: f32_samples_to_le_bytes(frame.samples()),
            sample_count: frame.samples().len(),
            sample_rate_hz: frame.sample_rate_hz(),
            channel_count: frame.channels(),
            session_id: lineage.session_id().get(),
            stream_id: frame.stream_id().get(),
            source_id: lineage.source_id().get(),
            stem_id: lineage.stem_id().get(),
            clock_id: lineage.clock_id().get(),
            sequence_number: lineage.sequence_number(),
            timestamp_start_ns: lineage.timestamp_start_ns(),
            duration_ns: lineage.duration_ns(),
            source_generation: lineage.source_generation(),
            discontinuity_epoch: lineage.discontinuity_epoch(),
            permission_epoch: lineage.permission_epoch(),
            endpoint_id: frame.endpoint_id().get(),
            connector_id: Some(frame.connector_id().get()),
            route_id: frame.route_id().get(),
            route_enqueued_at_ns: frame.route_enqueued_at_ns(),
            route_received_at_ns: frame.route_received_at_ns(),
            endpoint_enqueued_at_ns: Some(frame.endpoint_enqueued_at_ns()),
            polled_at_ns: Some(frame.polled_at_ns()),
        });
    }
    Ok(frames)
}

pub(crate) fn copy_audio_batch_until(
    running: &pocketstation::RunningSession,
    timeout: Duration,
) -> Result<Option<Vec<OwnedAudioFrame>>, String> {
    match running
        .wait_audio(timeout)
        .map_err(|error| error.to_string())?
    {
        Some(batch) => copy_polled_audio_batch(batch).map(Some),
        None => Ok(None),
    }
}

pub(crate) fn python_audio_batch(
    py: Python<'_>,
    owned: Option<Vec<OwnedAudioFrame>>,
) -> PyResult<Option<PythonAudioBatch>> {
    let Some(owned) = owned else {
        return Ok(None);
    };
    let frames = owned
        .into_iter()
        .map(|frame| Py::new(py, python_audio_frame(py, frame)))
        .collect::<PyResult<Vec<_>>>()?;
    Ok(Some(PythonAudioBatch { frames }))
}

pub(crate) fn owned_endpoint_audio_frame(
    frame: pocketstation::EndpointAudioFrame,
    input: &pocketstation::connector::ConnectorInputDescriptor,
) -> OwnedAudioFrame {
    owned_endpoint_audio_frame_for_route(
        frame,
        input.endpoint_id().get(),
        input.connector_id().map(pocketstation::ConnectorId::get),
        input.route_id().get(),
    )
}

pub(crate) fn owned_endpoint_audio_frame_for_route(
    frame: pocketstation::EndpointAudioFrame,
    endpoint_id: u64,
    connector_id: Option<u64>,
    route_id: u64,
) -> OwnedAudioFrame {
    let route_enqueued_at_ns = frame.route_enqueued_at_ns();
    let route_received_at_ns = frame.route_received_at_ns();
    let lineage = frame.lineage();
    OwnedAudioFrame {
        samples_f32le: f32_samples_to_le_bytes(frame.samples()),
        sample_count: frame.samples().len(),
        sample_rate_hz: frame.sample_rate_hz(),
        channel_count: frame.channels(),
        session_id: lineage.session_id().get(),
        stream_id: frame.stream_id().get(),
        source_id: lineage.source_id().get(),
        stem_id: lineage.stem_id().get(),
        clock_id: lineage.clock_id().get(),
        sequence_number: lineage.sequence_number(),
        timestamp_start_ns: lineage.timestamp_start_ns(),
        duration_ns: lineage.duration_ns(),
        source_generation: lineage.source_generation(),
        discontinuity_epoch: lineage.discontinuity_epoch(),
        permission_epoch: lineage.permission_epoch(),
        endpoint_id,
        connector_id,
        route_id,
        route_enqueued_at_ns,
        route_received_at_ns,
        endpoint_enqueued_at_ns: None,
        polled_at_ns: None,
    }
}

pub(crate) fn python_audio_frame(py: Python<'_>, frame: OwnedAudioFrame) -> PythonAudioFrame {
    PythonAudioFrame {
        sample_count: frame.sample_count,
        samples_f32le: PyBytes::new(py, &frame.samples_f32le).unbind(),
        sample_rate_hz: frame.sample_rate_hz,
        channel_count: frame.channel_count,
        session_id: frame.session_id,
        stream_id: frame.stream_id,
        source_id: frame.source_id,
        stem_id: frame.stem_id,
        clock_id: frame.clock_id,
        sequence_number: frame.sequence_number,
        timestamp_start_ns: frame.timestamp_start_ns,
        duration_ns: frame.duration_ns,
        source_generation: frame.source_generation,
        discontinuity_epoch: frame.discontinuity_epoch,
        permission_epoch: frame.permission_epoch,
        endpoint_id: frame.endpoint_id,
        connector_id: frame.connector_id,
        route_id: frame.route_id,
        route_enqueued_at_ns: frame.route_enqueued_at_ns,
        route_received_at_ns: frame.route_received_at_ns,
        endpoint_enqueued_at_ns: frame.endpoint_enqueued_at_ns,
        polled_at_ns: frame.polled_at_ns,
    }
}

fn f32_samples_to_le_bytes(samples: &[f32]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(std::mem::size_of_val(samples));
    for sample in samples {
        bytes.extend_from_slice(&sample.to_le_bytes());
    }
    bytes
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonClockDomainDescriptor>()?;
    module.add_class::<PythonAudioFrame>()?;
    module.add_class::<PythonAudioBatch>()?;
    Ok(())
}
