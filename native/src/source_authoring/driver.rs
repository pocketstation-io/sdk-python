use std::collections::BTreeMap;
use std::sync::Arc;

use pocketstation::{
    ClockDomainId, ConfigError, SignalEnvelope, SignalLineage, SignalTiming, SourceCancellation,
    SourceConfiguration, SourceDriver, SourceDriverError, SourceEmission, SourceFactory,
    SourceOutputIdentity, SourcePrepareContext, SourceSessionContext,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::values::{PythonSourceEmission, PythonSourceManifest};
use crate::errors::coded_reason;

#[pyclass(name = "_SourceOutputIdentity", frozen)]
pub(crate) struct PythonSourceOutputIdentity {
    #[pyo3(get)]
    output_port: String,
    #[pyo3(get)]
    stream_id: u64,
}

impl From<&SourceOutputIdentity> for PythonSourceOutputIdentity {
    fn from(value: &SourceOutputIdentity) -> Self {
        Self {
            output_port: value.output_port.clone(),
            stream_id: value.stream_id.get(),
        }
    }
}

#[pyclass(name = "_SourcePrepareContext", frozen)]
pub(crate) struct PythonSourcePrepareContext {
    #[pyo3(get)]
    source_type_id: String,
    #[pyo3(get)]
    session_id: Option<u64>,
    #[pyo3(get)]
    source_id: Option<u64>,
    outputs: Vec<Py<PythonSourceOutputIdentity>>,
}

#[pymethods]
impl PythonSourcePrepareContext {
    #[getter]
    fn outputs(&self, py: Python<'_>) -> Vec<Py<PythonSourceOutputIdentity>> {
        self.outputs
            .iter()
            .map(|value| value.clone_ref(py))
            .collect()
    }
}

#[pyclass(name = "_SourceCancellation", frozen)]
pub(crate) struct PythonSourceCancellation {
    value: SourceCancellation,
}

#[pymethods]
impl PythonSourceCancellation {
    #[getter]
    fn cancelled(&self) -> bool {
        self.value.is_cancelled()
    }
}

#[pyclass(name = "_RegisteredSource", frozen)]
pub(crate) struct PythonRegisteredSource {
    #[pyo3(get)]
    source_type_id: String,
}

pub(crate) fn register_source(
    session: &pocketstation::Session,
    manifest: &PythonSourceManifest,
    factory: Py<PyAny>,
) -> PyResult<PythonRegisteredSource> {
    let source_type_id = manifest.value.source_type_id().as_str().to_owned();
    session
        .register_source(Arc::new(PythonSourceFactory {
            manifest: manifest.value.clone(),
            factory,
        }))
        .map_err(|error| {
            PyValueError::new_err(coded_reason(
                "source.registration_failed",
                error.to_string(),
            ))
        })?;
    Ok(PythonRegisteredSource { source_type_id })
}

struct PythonSourceFactory {
    manifest: pocketstation::SourceManifest,
    factory: Py<PyAny>,
}

impl SourceFactory for PythonSourceFactory {
    fn manifest(&self) -> &pocketstation::SourceManifest {
        &self.manifest
    }

    fn validate_config(&self, configuration: &SourceConfiguration) -> Result<(), ConfigError> {
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

    fn create(
        &self,
        configuration: &SourceConfiguration,
    ) -> Result<Box<dyn SourceDriver>, SourceDriverError> {
        Python::attach(|py| {
            let values = configuration_dict(py, configuration).map_err(driver_error)?;
            let driver = self
                .factory
                .bind(py)
                .call_method1("create", (values,))
                .map_err(driver_error)?
                .unbind();
            Ok(Box::new(PythonSourceDriver {
                driver,
                session: None,
                sequences: BTreeMap::new(),
            }) as Box<dyn SourceDriver>)
        })
    }
}

struct PythonSourceDriver {
    driver: Py<PyAny>,
    session: Option<SourceSessionContext>,
    sequences: BTreeMap<String, u64>,
}

impl SourceDriver for PythonSourceDriver {
    fn prepare(&mut self, context: &SourcePrepareContext) -> Result<(), SourceDriverError> {
        Python::attach(|py| {
            let outputs = context
                .session
                .as_ref()
                .map(|session| {
                    session
                        .outputs
                        .iter()
                        .map(|output| Py::new(py, PythonSourceOutputIdentity::from(output)))
                        .collect::<PyResult<Vec<_>>>()
                })
                .transpose()
                .map_err(driver_error)?
                .unwrap_or_default();
            let prepared = Py::new(
                py,
                PythonSourcePrepareContext {
                    source_type_id: context.manifest.source_type_id().as_str().to_owned(),
                    session_id: context.session.as_ref().map(|value| value.session_id.get()),
                    source_id: context.session.as_ref().map(|value| value.source_id.get()),
                    outputs,
                },
            )
            .map_err(driver_error)?;
            self.driver
                .bind(py)
                .call_method1("prepare", (prepared,))
                .map_err(driver_error)?;
            self.session = context.session.clone();
            Ok(())
        })
    }

    fn next(
        &mut self,
        cancellation: &SourceCancellation,
    ) -> Result<Option<SourceEmission>, SourceDriverError> {
        let emission = Python::attach(|py| {
            let cancellation = Py::new(
                py,
                PythonSourceCancellation {
                    value: cancellation.clone(),
                },
            )
            .map_err(driver_error)?;
            let value = self
                .driver
                .bind(py)
                .call_method1("next", (cancellation,))
                .map_err(driver_error)?;
            if value.is_none() {
                return Ok(None);
            }
            value
                .extract::<PyRef<'_, PythonSourceEmission>>()
                .map(|value| Some(value.clone()))
                .map_err(|error| driver_error(error.into()))
        })?;
        emission
            .map(|emission| self.build_core_emission(emission))
            .transpose()
    }

    fn close(&mut self) -> Result<(), SourceDriverError> {
        Python::attach(|py| {
            self.driver
                .bind(py)
                .call_method0("close")
                .map(|_| ())
                .map_err(driver_error)
        })
    }
}

impl PythonSourceDriver {
    fn build_core_emission(
        &mut self,
        emission: PythonSourceEmission,
    ) -> Result<SourceEmission, SourceDriverError> {
        let session = self.session.as_ref().ok_or_else(|| {
            SourceDriverError::Failed("Python source has no Session prepare context".to_owned())
        })?;
        let output = session.output(&emission.output_port).ok_or_else(|| {
            SourceDriverError::Failed(format!(
                "Python source emitted unknown output {:?}",
                emission.output_port
            ))
        })?;
        let sequence = self
            .sequences
            .entry(emission.output_port.clone())
            .or_default();
        let sequence_number = *sequence;
        *sequence = sequence.saturating_add(1);
        let observed_timestamp_ns = emission
            .observed_timestamp_ns
            .unwrap_or_else(pocketstation::timing::monotonic_timestamp_ns);
        let timing = SignalTiming::try_new(
            emission.source_timestamp_ns,
            observed_timestamp_ns,
            emission.source_timestamp_ns,
            emission.duration_ns,
        )
        .map_err(|error| SourceDriverError::Failed(error.to_string()))?;
        let lineage = SignalLineage::try_new(
            session.session_id,
            output.stream_id,
            session.source_id,
            ClockDomainId::new(emission.clock_domain_id),
            sequence_number,
            emission.source_generation,
            emission.discontinuity_epoch,
            emission.policy_epoch,
        )
        .map_err(|error| SourceDriverError::Failed(error.to_string()))?;
        let envelope = SignalEnvelope::untracked(
            emission.payload.into_core(),
            emission.signal,
            observed_timestamp_ns,
        )
        .with_lineage(lineage, timing);
        Ok(SourceEmission {
            output_port: emission.output_port,
            envelope,
            terminal: emission.terminal,
        })
    }
}

fn configuration_dict<'py>(
    py: Python<'py>,
    configuration: &SourceConfiguration,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    for (key, value) in configuration.iter() {
        values.set_item(key, value)?;
    }
    Ok(values)
}

fn config_error(stage: &str, error: PyErr) -> ConfigError {
    ConfigError::Invalid {
        key: stage.to_owned(),
        reason: Python::attach(|py| error.value(py).to_string()),
    }
}

fn driver_error(error: PyErr) -> SourceDriverError {
    SourceDriverError::Failed(Python::attach(|py| {
        error.value(py).str().map_or_else(
            |_| error.to_string(),
            |value| value.to_string_lossy().into_owned(),
        )
    }))
}
