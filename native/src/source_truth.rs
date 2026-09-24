//! Direct Python projection of Core's built-in Source observations and recovery.

use std::time::Duration;

use pocketstation::{
    CaptureNativeFormat, CaptureSampleRepresentation, SessionSourceActivityObservations,
    SessionSourceActivityPolicy, SessionSourceActivityState, SessionSourceNativeFormatObservation,
    SessionSourceReplacement, SessionSourceReplacementObservations,
    SessionSourceSignalObservations, SessionSourceSignalPolicy, SessionSourceSignalState,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::errors::coded_reason;

fn sample_representation_name(value: CaptureSampleRepresentation) -> &'static str {
    match value {
        CaptureSampleRepresentation::SignedInteger8 => "signed-integer-8",
        CaptureSampleRepresentation::SignedInteger16 => "signed-integer-16",
        CaptureSampleRepresentation::SignedInteger24 => "signed-integer-24",
        CaptureSampleRepresentation::SignedInteger32 => "signed-integer-32",
        CaptureSampleRepresentation::SignedInteger64 => "signed-integer-64",
        CaptureSampleRepresentation::UnsignedInteger8 => "unsigned-integer-8",
        CaptureSampleRepresentation::UnsignedInteger16 => "unsigned-integer-16",
        CaptureSampleRepresentation::UnsignedInteger24 => "unsigned-integer-24",
        CaptureSampleRepresentation::UnsignedInteger32 => "unsigned-integer-32",
        CaptureSampleRepresentation::UnsignedInteger64 => "unsigned-integer-64",
        CaptureSampleRepresentation::Float32 => "float-32",
        CaptureSampleRepresentation::Float64 => "float-64",
    }
}

#[pyclass(name = "_OpenedNativeFormat", frozen)]
pub(crate) struct PythonOpenedNativeFormat {
    #[pyo3(get)]
    sample_rate_hz: u32,
    #[pyo3(get)]
    channel_count: u16,
    #[pyo3(get)]
    sample_representation: &'static str,
}

impl From<CaptureNativeFormat> for PythonOpenedNativeFormat {
    fn from(value: CaptureNativeFormat) -> Self {
        Self {
            sample_rate_hz: value.sample_rate_hz,
            channel_count: value.channel_count,
            sample_representation: sample_representation_name(value.sample_representation),
        }
    }
}

#[pyclass(name = "_SourceNativeFormatObservation", frozen)]
pub(crate) struct PythonSourceNativeFormatObservation {
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    opened_native_format: Option<Py<PythonOpenedNativeFormat>>,
}

pub(crate) fn native_format_observation(
    py: Python<'_>,
    value: SessionSourceNativeFormatObservation,
) -> PyResult<PythonSourceNativeFormatObservation> {
    Ok(PythonSourceNativeFormatObservation {
        stem_id: value.stem_id.get(),
        opened_native_format: value
            .opened_native_format
            .map(|format| Py::new(py, PythonOpenedNativeFormat::from(format)))
            .transpose()?,
    })
}

#[pyclass(name = "_SourceReplacementObservation", frozen)]
pub(crate) struct PythonSourceReplacementObservation {
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    attempts_total: u64,
    #[pyo3(get)]
    completed_total: u64,
    #[pyo3(get)]
    failed_before_attach_total: u64,
    #[pyo3(get)]
    response_timeouts_total: u64,
    #[pyo3(get)]
    attached_source_id: Option<u64>,
    #[pyo3(get)]
    source_generation: u32,
    #[pyo3(get)]
    discontinuity_epoch: u64,
    #[pyo3(get)]
    latest_completed_at_ns: Option<u64>,
}

impl From<SessionSourceReplacementObservations> for PythonSourceReplacementObservation {
    fn from(value: SessionSourceReplacementObservations) -> Self {
        Self {
            stem_id: value.stem_id.get(),
            attempts_total: value.attempts_total,
            completed_total: value.completed_total,
            failed_before_attach_total: value.failed_before_attach_total,
            response_timeouts_total: value.response_timeouts_total,
            attached_source_id: value.attached_source_id.map(pocketstation::SourceId::get),
            source_generation: value.source_generation,
            discontinuity_epoch: value.discontinuity_epoch,
            latest_completed_at_ns: value.latest_completed_at_ns,
        }
    }
}

#[pyclass(name = "_SourceReplacement", frozen)]
pub(crate) struct PythonSourceReplacement {
    #[pyo3(get)]
    stem_id: u64,
    #[pyo3(get)]
    previous_source_id: u64,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    source_generation: u32,
    #[pyo3(get)]
    discontinuity_epoch: u64,
    #[pyo3(get)]
    opened_native_format: Option<Py<PythonOpenedNativeFormat>>,
}

pub(crate) fn source_replacement(
    py: Python<'_>,
    value: SessionSourceReplacement,
) -> PyResult<PythonSourceReplacement> {
    Ok(PythonSourceReplacement {
        stem_id: value.stem_id.get(),
        previous_source_id: value.previous_source_id.get(),
        source_id: value.source_id.get(),
        source_generation: value.source_generation,
        discontinuity_epoch: value.discontinuity_epoch,
        opened_native_format: value
            .opened_native_format
            .map(|format| Py::new(py, PythonOpenedNativeFormat::from(format)))
            .transpose()?,
    })
}

#[pyclass(name = "_SourceActivityObservation", frozen)]
pub(crate) struct PythonSourceActivityObservation {
    value: SessionSourceActivityObservations,
}

impl From<SessionSourceActivityObservations> for PythonSourceActivityObservation {
    fn from(value: SessionSourceActivityObservations) -> Self {
        Self { value }
    }
}

#[pyclass(name = "_SourceActivityEvaluation", frozen)]
pub(crate) struct PythonSourceActivityEvaluation {
    #[pyo3(get)]
    state: &'static str,
    #[pyo3(get)]
    session_age_ns: u64,
    #[pyo3(get)]
    latest_frame_age_ns: Option<u64>,
}

#[pymethods]
impl PythonSourceActivityObservation {
    #[getter]
    fn session_started_at_ns(&self) -> u64 {
        self.value.session_started_at_ns
    }
    #[getter]
    fn observed_at_ns(&self) -> u64 {
        self.value.observed_at_ns
    }
    #[getter]
    fn first_frame_received_at_ns(&self) -> Option<u64> {
        self.value.first_frame_received_at_ns
    }
    #[getter]
    fn latest_frame_received_at_ns(&self) -> Option<u64> {
        self.value.latest_frame_received_at_ns
    }
    #[getter]
    fn frames_received_total(&self) -> u64 {
        self.value.frames_received_total
    }

    fn evaluate(
        &self,
        first_frame_timeout_ns: u64,
        stall_timeout_ns: u64,
    ) -> PyResult<PythonSourceActivityEvaluation> {
        let policy = SessionSourceActivityPolicy::new(
            Duration::from_nanos(first_frame_timeout_ns),
            Duration::from_nanos(stall_timeout_ns),
        )
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "source.invalid_activity_policy",
                error.to_string(),
            ))
        })?;
        let result = self.value.evaluate(policy);
        let state = match result.state {
            SessionSourceActivityState::AwaitingFirstFrame => "awaiting-first-frame",
            SessionSourceActivityState::Active => "active",
            SessionSourceActivityState::FirstFrameTimedOut => "first-frame-timed-out",
            SessionSourceActivityState::Stalled => "stalled",
        };
        Ok(PythonSourceActivityEvaluation {
            state,
            session_age_ns: result.session_age_ns,
            latest_frame_age_ns: result.latest_frame_age_ns,
        })
    }
}

#[pyclass(name = "_SourceSignalObservation", frozen)]
pub(crate) struct PythonSourceSignalObservation {
    value: SessionSourceSignalObservations,
}

impl From<SessionSourceSignalObservations> for PythonSourceSignalObservation {
    fn from(value: SessionSourceSignalObservations) -> Self {
        Self { value }
    }
}

#[pyclass(name = "_SourceSignalEvaluation", frozen)]
pub(crate) struct PythonSourceSignalEvaluation {
    #[pyo3(get)]
    state: &'static str,
    #[pyo3(get)]
    peak_dbfs: Option<f64>,
    #[pyo3(get)]
    rms_dbfs: Option<f64>,
    #[pyo3(get)]
    consecutive_exact_zero_duration_ns: u64,
}

#[pymethods]
impl PythonSourceSignalObservation {
    #[getter]
    fn observed_at_ns(&self) -> u64 {
        self.value.observed_at_ns
    }
    #[getter]
    fn samples_observed_total(&self) -> u64 {
        self.value.samples_observed_total
    }
    #[getter]
    fn exact_zero_samples_observed_total(&self) -> u64 {
        self.value.exact_zero_samples_observed_total
    }
    #[getter]
    fn nonzero_samples_observed_total(&self) -> u64 {
        self.value.nonzero_samples_observed_total
    }
    #[getter]
    fn nonfinite_samples_observed_total(&self) -> u64 {
        self.value.nonfinite_samples_observed_total
    }
    #[getter]
    fn window_timestamp_start_ns(&self) -> Option<u64> {
        self.value.window_timestamp_start_ns
    }
    #[getter]
    fn window_duration_ns(&self) -> u64 {
        self.value.window_duration_ns
    }
    #[getter]
    fn window_observed_at_ns(&self) -> Option<u64> {
        self.value.window_observed_at_ns
    }
    #[getter]
    fn window_sequence_number(&self) -> Option<u64> {
        self.value.window_sequence_number
    }
    #[getter]
    fn window_source_generation(&self) -> u32 {
        self.value.window_source_generation
    }
    #[getter]
    fn window_discontinuity_epoch(&self) -> u64 {
        self.value.window_discontinuity_epoch
    }
    #[getter]
    fn window_samples_total(&self) -> u64 {
        self.value.window_samples_total
    }
    #[getter]
    fn window_exact_zero_samples_total(&self) -> u64 {
        self.value.window_exact_zero_samples_total
    }
    #[getter]
    fn window_nonzero_samples_total(&self) -> u64 {
        self.value.window_nonzero_samples_total
    }
    #[getter]
    fn window_nonfinite_samples_total(&self) -> u64 {
        self.value.window_nonfinite_samples_total
    }
    #[getter]
    fn consecutive_exact_zero_duration_ns(&self) -> u64 {
        self.value.consecutive_exact_zero_duration_ns
    }
    #[getter]
    fn window_peak_linear(&self) -> Option<f32> {
        self.value.window_peak_linear()
    }
    #[getter]
    fn window_rms_linear(&self) -> Option<f64> {
        self.value.window_rms_linear()
    }
    #[getter]
    fn window_peak_dbfs(&self) -> Option<f64> {
        self.value.window_peak_dbfs()
    }
    #[getter]
    fn window_rms_dbfs(&self) -> Option<f64> {
        self.value.window_rms_dbfs()
    }
    #[getter]
    fn window_exact_zero_ratio(&self) -> Option<f64> {
        self.value.window_exact_zero_ratio()
    }

    fn evaluate(
        &self,
        minimum_peak_dbfs: f64,
        minimum_rms_dbfs: f64,
        exact_zero_timeout_ns: u64,
    ) -> PyResult<PythonSourceSignalEvaluation> {
        let policy = SessionSourceSignalPolicy::new(
            minimum_peak_dbfs,
            minimum_rms_dbfs,
            Duration::from_nanos(exact_zero_timeout_ns),
        )
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "source.invalid_signal_policy",
                error.to_string(),
            ))
        })?;
        let result = self.value.evaluate(policy);
        let state = match result.state {
            SessionSourceSignalState::NoSamplesObserved => "no-samples-observed",
            SessionSourceSignalState::ExactDigitalZeroPending => "exact-digital-zero-pending",
            SessionSourceSignalState::SustainedExactDigitalZero => "sustained-exact-digital-zero",
            SessionSourceSignalState::BelowCallerThresholds => "below-caller-thresholds",
            SessionSourceSignalState::MeetsCallerThresholds => "meets-caller-thresholds",
            SessionSourceSignalState::NonFiniteSamplesObserved => "nonfinite-samples-observed",
        };
        Ok(PythonSourceSignalEvaluation {
            state,
            peak_dbfs: result.peak_dbfs,
            rms_dbfs: result.rms_dbfs,
            consecutive_exact_zero_duration_ns: result.consecutive_exact_zero_duration_ns,
        })
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonOpenedNativeFormat>()?;
    module.add_class::<PythonSourceNativeFormatObservation>()?;
    module.add_class::<PythonSourceReplacementObservation>()?;
    module.add_class::<PythonSourceReplacement>()?;
    module.add_class::<PythonSourceActivityObservation>()?;
    module.add_class::<PythonSourceActivityEvaluation>()?;
    module.add_class::<PythonSourceSignalObservation>()?;
    module.add_class::<PythonSourceSignalEvaluation>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn native_sample_representations_keep_every_core_variant_distinct() {
        let cases = [
            (
                CaptureSampleRepresentation::SignedInteger8,
                "signed-integer-8",
            ),
            (
                CaptureSampleRepresentation::SignedInteger16,
                "signed-integer-16",
            ),
            (
                CaptureSampleRepresentation::SignedInteger24,
                "signed-integer-24",
            ),
            (
                CaptureSampleRepresentation::SignedInteger32,
                "signed-integer-32",
            ),
            (
                CaptureSampleRepresentation::SignedInteger64,
                "signed-integer-64",
            ),
            (
                CaptureSampleRepresentation::UnsignedInteger8,
                "unsigned-integer-8",
            ),
            (
                CaptureSampleRepresentation::UnsignedInteger16,
                "unsigned-integer-16",
            ),
            (
                CaptureSampleRepresentation::UnsignedInteger24,
                "unsigned-integer-24",
            ),
            (
                CaptureSampleRepresentation::UnsignedInteger32,
                "unsigned-integer-32",
            ),
            (
                CaptureSampleRepresentation::UnsignedInteger64,
                "unsigned-integer-64",
            ),
            (CaptureSampleRepresentation::Float32, "float-32"),
            (CaptureSampleRepresentation::Float64, "float-64"),
        ];
        for (representation, expected) in cases {
            let projected = PythonOpenedNativeFormat::from(CaptureNativeFormat {
                sample_rate_hz: 48_000,
                channel_count: 2,
                sample_representation: representation,
            });
            assert_eq!(projected.sample_representation, expected);
            assert_eq!(projected.sample_rate_hz, 48_000);
            assert_eq!(projected.channel_count, 2);
        }
    }
}
