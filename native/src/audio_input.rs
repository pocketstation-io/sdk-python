use std::sync::Mutex;

use pocketstation::{
    AudioInput, AudioInputConfig, AudioInputObservations, AudioInputWriteError,
    AudioInputWriteErrorKind,
};
use pyo3::buffer::PyBuffer;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use crate::errors::coded_reason;
use crate::graph::PythonSourceOutput;

#[pyclass(name = "_AudioInputObservations", frozen)]
pub(crate) struct PythonAudioInputObservations {
    observations: AudioInputObservations,
}

#[pymethods]
impl PythonAudioInputObservations {
    #[getter]
    fn capacity_frames(&self) -> u64 {
        self.observations.capacity_frames
    }

    #[getter]
    fn buffer_slots(&self) -> u64 {
        self.observations.buffer_slots
    }

    #[getter]
    fn available_buffers(&self) -> u64 {
        self.observations.available_buffers
    }

    #[getter]
    fn accepted_total(&self) -> u64 {
        self.observations.accepted_total
    }

    #[getter]
    fn full_total(&self) -> u64 {
        self.observations.full_total
    }

    #[getter]
    fn invalid_total(&self) -> u64 {
        self.observations.invalid_total
    }

    #[getter]
    fn cancelled(&self) -> bool {
        self.observations.cancelled
    }

    #[getter]
    fn closed(&self) -> bool {
        self.observations.closed
    }
}

#[pyclass(name = "_AudioInput")]
pub(crate) struct PythonAudioInput {
    input: Mutex<AudioInput>,
}

impl PythonAudioInput {
    pub(crate) const fn new(input: AudioInput) -> Self {
        Self {
            input: Mutex::new(input),
        }
    }

    fn with_input<Result>(
        &self,
        operation: impl FnOnce(&mut AudioInput) -> PyResult<Result>,
    ) -> PyResult<Result> {
        let mut input = self.input.lock().map_err(|_| {
            PyRuntimeError::new_err(coded_reason(
                "audio_input.state_unavailable",
                "audio input state is unavailable",
            ))
        })?;
        operation(&mut input)
    }
}

#[pymethods]
impl PythonAudioInput {
    #[getter]
    fn source_id(&self) -> PyResult<u64> {
        self.with_input(|input| Ok(input.source().source_id().get()))
    }

    #[getter]
    fn stream_id(&self) -> PyResult<u64> {
        self.with_input(|input| Ok(input.output().stream_id().get()))
    }

    #[getter]
    fn output(&self) -> PyResult<PythonSourceOutput> {
        self.with_input(|input| {
            Ok(PythonSourceOutput {
                handle: input.output().clone(),
            })
        })
    }

    #[pyo3(signature = (samples, *, discontinuity=false))]
    fn try_write(
        &self,
        py: Python<'_>,
        samples: PyBuffer<f32>,
        discontinuity: bool,
    ) -> PyResult<()> {
        let source = samples.as_slice(py).ok_or_else(|| {
            PyValueError::new_err(coded_reason(
                "audio_input.invalid_buffer",
                "samples must be a C-contiguous float32 buffer",
            ))
        })?;
        self.with_input(|input| {
            let mut buffer = input.try_acquire().map_err(audio_input_acquire_error)?;
            buffer
                .try_set_sample_count(source.len())
                .map_err(|error| invalid_buffer(error.to_string()))?;
            for (destination, value) in buffer.samples_mut().iter_mut().zip(source) {
                *destination = value.get();
            }
            if discontinuity {
                buffer.mark_discontinuity();
            }
            input.try_send(buffer).map_err(audio_input_write_error)
        })
    }

    fn close(&self) -> PyResult<()> {
        self.with_input(|input| {
            input.close();
            Ok(())
        })
    }

    fn observations(&self) -> PyResult<PythonAudioInputObservations> {
        self.with_input(|input| {
            Ok(PythonAudioInputObservations {
                observations: input.observations(),
            })
        })
    }
}

fn audio_input_acquire_error(error: pocketstation::AudioInputBufferAcquireError) -> PyErr {
    let (code, message) = match error {
        pocketstation::AudioInputBufferAcquireError::Full => {
            ("audio_input.full", "audio input is full")
        }
        pocketstation::AudioInputBufferAcquireError::Closed => {
            ("audio_input.closed", "audio input is closed")
        }
        pocketstation::AudioInputBufferAcquireError::Cancelled => {
            ("audio_input.cancelled", "audio input Session was cancelled")
        }
    };
    PyRuntimeError::new_err(coded_reason(code, message))
}

fn audio_input_write_error(error: AudioInputWriteError) -> PyErr {
    let code = match error.kind() {
        AudioInputWriteErrorKind::Full => "audio_input.full",
        AudioInputWriteErrorKind::Closed => "audio_input.closed",
        AudioInputWriteErrorKind::Cancelled => "audio_input.cancelled",
        AudioInputWriteErrorKind::InvalidBuffer(_) => "audio_input.invalid_buffer",
    };
    let message = error.to_string();
    match error.kind() {
        AudioInputWriteErrorKind::InvalidBuffer(_) => invalid_buffer(message),
        _ => PyRuntimeError::new_err(coded_reason(code, message)),
    }
}

fn invalid_buffer(message: String) -> PyErr {
    PyValueError::new_err(coded_reason("audio_input.invalid_buffer", message))
}

pub(crate) fn configuration(
    sample_rate_hz: u32,
    channels: u8,
    capacity_frames: usize,
    frame_samples_per_channel: usize,
) -> PyResult<AudioInputConfig> {
    AudioInputConfig::new(
        pocketstation::SampleSpec::new(
            sample_rate_hz,
            channels,
            pocketstation::SampleFormat::F32Interleaved,
        ),
        capacity_frames,
        frame_samples_per_channel,
    )
    .map_err(|error| {
        PyValueError::new_err(coded_reason(
            "audio_input.invalid_configuration",
            error.to_string(),
        ))
    })
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonAudioInput>()?;
    module.add_class::<PythonAudioInputObservations>()?;
    Ok(())
}
