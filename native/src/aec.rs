use pocketstation::{EchoAudioInput, EchoCancellationState, EchoCancelledAudio, PlaybackReference};
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;

use crate::graph::{PythonDerivedStream, PythonSourceOutput, PythonStem};

pub(crate) fn audio_input(input: &Bound<'_, PyAny>) -> PyResult<EchoAudioInput> {
    if let Ok(value) = input.extract::<PyRef<'_, PythonStem>>() {
        return Ok((&value.handle).into());
    }
    if let Ok(value) = input.extract::<PyRef<'_, PythonSourceOutput>>() {
        return Ok((&value.handle).into());
    }
    if let Ok(value) = input.extract::<PyRef<'_, PythonDerivedStream>>() {
        return Ok((&value.handle).into());
    }
    Err(PyTypeError::new_err(
        "echo input must be a Stem, SourceOutput or DerivedStream",
    ))
}

#[pyclass(name = "_PlaybackReference", frozen)]
pub(crate) struct PythonPlaybackReference {
    pub(crate) value: PlaybackReference,
}

#[pymethods]
impl PythonPlaybackReference {
    #[staticmethod]
    fn selected_application(input: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Self {
            value: PlaybackReference::selected_application(audio_input(input)?),
        })
    }

    #[staticmethod]
    fn output_mix(input: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Self {
            value: PlaybackReference::output_mix(audio_input(input)?),
        })
    }

    #[staticmethod]
    fn rendered_audio(input: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Self {
            value: PlaybackReference::rendered_audio(audio_input(input)?),
        })
    }
}

#[pyclass(name = "_EchoCancelledAudio", frozen)]
pub(crate) struct PythonEchoCancelledAudio {
    pub(crate) value: EchoCancelledAudio,
}

#[pymethods]
impl PythonEchoCancelledAudio {
    #[getter]
    fn audio(&self) -> PythonStem {
        PythonStem {
            handle: self.value.audio().clone(),
        }
    }

    #[getter]
    fn reference_coverage(&self) -> String {
        self.value.reference_coverage().to_owned()
    }

    fn observations(&self) -> PythonEchoCancellationObservations {
        let value = self.value.observations();
        PythonEchoCancellationObservations {
            state: match value.state {
                EchoCancellationState::WaitingForReference => "waiting-for-reference",
                EchoCancellationState::Processing => "processing",
                EchoCancellationState::Reset => "reset",
                EchoCancellationState::Interrupted => "interrupted",
                EchoCancellationState::Failed => "failed",
                EchoCancellationState::Stopped => "stopped",
            }
            .to_owned(),
            processed_microphone_frames_total: value.processed_microphone_frames_total,
            output_frames_total: value.output_frames_total,
            discarded_output_frames_total: value.discarded_output_frames_total,
            tail_frames_total: value.tail_frames_total,
            tail_padding_samples_total: value.tail_padding_samples_total,
            discarded_tail_generations_total: value.discarded_tail_generations_total,
            nominal_delay_samples: value.nominal_delay_samples,
            drain_duration_ms: value.drain_duration_ms,
            discarded_microphone_frames_total: value.discarded_microphone_frames_total,
            discarded_reference_frames_total: value.discarded_reference_frames_total,
            resets_total: value.resets_total,
            processing_generation: value.processing_generation,
            microphone_queue_depth_frames: value.microphone_queue_depth_frames,
            reference_queue_depth_frames: value.reference_queue_depth_frames,
            queue_capacity_frames: value.queue_capacity_frames,
            latest_processing_duration_ns: value.latest_processing_duration_ns,
            maximum_processing_duration_ns: value.maximum_processing_duration_ns,
            latest_reference_age_ns: value.latest_reference_age_ns,
            latest_reference_lead_ns: value.latest_reference_lead_ns,
            maximum_cadence_error_ns: value.maximum_cadence_error_ns,
            analyzed_reference_frames_total: value.analyzed_reference_frames_total,
            interrupted_requests_total: value.interrupted_requests_total,
            reference_source_id: value.reference_source_id.map(pocketstation::SourceId::get),
            microphone_source_id: value.microphone_source_id.map(pocketstation::SourceId::get),
            qualified_algorithmic_delay_samples: value.qualified_algorithmic_delay_samples,
            last_error: value.last_error,
        }
    }
}

#[pyclass(name = "_EchoCancellationObservations", frozen, get_all)]
pub(crate) struct PythonEchoCancellationObservations {
    state: String,
    processed_microphone_frames_total: u64,
    output_frames_total: u64,
    discarded_output_frames_total: u64,
    tail_frames_total: u64,
    tail_padding_samples_total: u64,
    discarded_tail_generations_total: u64,
    nominal_delay_samples: u32,
    drain_duration_ms: u32,
    discarded_microphone_frames_total: u64,
    discarded_reference_frames_total: u64,
    resets_total: u64,
    processing_generation: u64,
    microphone_queue_depth_frames: usize,
    reference_queue_depth_frames: usize,
    queue_capacity_frames: usize,
    latest_processing_duration_ns: u64,
    maximum_processing_duration_ns: u64,
    latest_reference_age_ns: u64,
    latest_reference_lead_ns: u64,
    maximum_cadence_error_ns: u64,
    analyzed_reference_frames_total: u64,
    interrupted_requests_total: u64,
    reference_source_id: Option<u64>,
    microphone_source_id: Option<u64>,
    qualified_algorithmic_delay_samples: Option<u32>,
    last_error: Option<String>,
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonPlaybackReference>()?;
    module.add_class::<PythonEchoCancelledAudio>()?;
    module.add_class::<PythonEchoCancellationObservations>()?;
    Ok(())
}
