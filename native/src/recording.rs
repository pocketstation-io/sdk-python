//! Blocking-control projection of Core-owned finalized recording clips.

use std::path::PathBuf;

use pocketstation::{
    RecordedAudio, RecordedStem, RecordingClip, RecordingClipWindow, SessionId, StemId,
};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::errors::coded_reason;
use crate::observations::PythonRecordingDiscontinuity;

fn clip_error(error: pocketstation::RecordingClipError) -> PyErr {
    PyRuntimeError::new_err(coded_reason(error.code(), error.to_string()))
}

#[pyclass(name = "RecordingClipWindow", frozen)]
pub(crate) struct PythonRecordingClipWindow {
    inner: RecordingClipWindow,
}

#[pymethods]
impl PythonRecordingClipWindow {
    #[new]
    fn new(start_ns: u64, end_ns: u64) -> PyResult<Self> {
        Ok(Self {
            inner: RecordingClipWindow::new(start_ns, end_ns).map_err(clip_error)?,
        })
    }

    #[staticmethod]
    fn around(start_ns: u64, end_ns: u64, before_ns: u64, after_ns: u64) -> PyResult<Self> {
        Ok(Self {
            inner: RecordingClipWindow::around(start_ns, end_ns, before_ns, after_ns)
                .map_err(clip_error)?,
        })
    }

    #[getter]
    fn start_ns(&self) -> u64 {
        self.inner.start_ns()
    }
    #[getter]
    fn end_ns(&self) -> u64 {
        self.inner.end_ns()
    }
}

#[pyclass(name = "RecordedStem", frozen, get_all)]
pub(crate) struct PythonRecordedStem {
    label: String,
    session_id: u64,
    source_id: u64,
    stem_id: u64,
    clock_id: u32,
    source_generation: u32,
    permission_epoch: u64,
    sample_rate_hz: u32,
    channels: u16,
    first_timestamp_ns: u64,
    final_timestamp_ns: u64,
}

impl From<RecordedStem> for PythonRecordedStem {
    fn from(value: RecordedStem) -> Self {
        Self {
            label: value.label,
            session_id: value.session_id.get(),
            source_id: value.source_id.get(),
            stem_id: value.stem_id.get(),
            clock_id: value.clock_id.get(),
            source_generation: value.source_generation,
            permission_epoch: value.permission_epoch,
            sample_rate_hz: value.sample_rate_hz,
            channels: value.channels,
            first_timestamp_ns: value.first_timestamp_ns,
            final_timestamp_ns: value.final_timestamp_ns,
        }
    }
}

#[pyclass(name = "RecordingClip", frozen)]
pub(crate) struct PythonRecordingClip {
    wav: Vec<u8>,
    #[pyo3(get)]
    stem: Py<PythonRecordedStem>,
    #[pyo3(get)]
    requested: Py<PythonRecordingClipWindow>,
    #[pyo3(get)]
    actual: Py<PythonRecordingClipWindow>,
    #[pyo3(get)]
    first_sample_frame: u64,
    #[pyo3(get)]
    sample_frames: u64,
    discontinuities: Vec<Py<PythonRecordingDiscontinuity>>,
}

#[pymethods]
impl PythonRecordingClip {
    #[getter]
    fn wav<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.wav)
    }
    fn discontinuities(&self, py: Python<'_>) -> Vec<Py<PythonRecordingDiscontinuity>> {
        self.discontinuities
            .iter()
            .map(|value| value.clone_ref(py))
            .collect()
    }
}

fn python_clip(py: Python<'_>, value: RecordingClip) -> PyResult<PythonRecordingClip> {
    Ok(PythonRecordingClip {
        wav: value.wav,
        stem: Py::new(py, PythonRecordedStem::from(value.stem))?,
        requested: Py::new(
            py,
            PythonRecordingClipWindow {
                inner: value.requested,
            },
        )?,
        actual: Py::new(
            py,
            PythonRecordingClipWindow {
                inner: value.actual,
            },
        )?,
        first_sample_frame: value.first_sample_frame,
        sample_frames: value.sample_frames,
        discontinuities: value
            .discontinuities
            .into_iter()
            .map(|gap| Py::new(py, PythonRecordingDiscontinuity::from(gap)))
            .collect::<PyResult<_>>()?,
    })
}

#[pyclass(name = "RecordedAudio", frozen)]
pub(crate) struct PythonRecordedAudio {
    inner: RecordedAudio,
}

#[pymethods]
impl PythonRecordedAudio {
    #[new]
    fn new(py: Python<'_>, directory: PathBuf, session_id: u64) -> PyResult<Self> {
        let inner = py
            .detach(move || RecordedAudio::open(directory, SessionId::new(session_id)))
            .map_err(clip_error)?;
        Ok(Self { inner })
    }

    fn stems(&self, py: Python<'_>) -> PyResult<Vec<Py<PythonRecordedStem>>> {
        self.inner
            .stems()
            .iter()
            .cloned()
            .map(|value| Py::new(py, PythonRecordedStem::from(value)))
            .collect()
    }

    fn read_clip(
        &self,
        py: Python<'_>,
        stem_id: u64,
        window: &PythonRecordingClipWindow,
    ) -> PyResult<PythonRecordingClip> {
        let interval = window.inner;
        let value = py
            .detach(|| self.inner.read_clip(StemId::new(stem_id), interval))
            .map_err(clip_error)?;
        python_clip(py, value)
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonRecordingClipWindow>()?;
    module.add_class::<PythonRecordedStem>()?;
    module.add_class::<PythonRecordingClip>()?;
    module.add_class::<PythonRecordedAudio>()?;
    Ok(())
}
