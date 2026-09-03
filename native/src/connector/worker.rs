use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;

use pocketstation::connector::{
    Connector, ConnectorConfiguration, ConnectorConfigurationValue,
    ConnectorConfigurationValueKind, ConnectorContext, ConnectorError, ConnectorErrorCode,
    ConnectorErrorStage, ConnectorFactory, ConnectorRetryability, ConnectorRunOutcome,
    ConnectorSecret, ConnectorWorker, ResolvedConnectorConfiguration,
};
use pocketstation::{
    EndpointGroupId, EndpointPortInput, EndpointPreparationGroup, EndpointReceiver,
    EndpointShutdownMode, RouteId, Session,
};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::driver::{
    internal_error, python_context, python_error, PythonConnectorInputDescriptor,
    PythonConnectorItem, PythonRegisteredConnector,
};
use super::values::{
    configuration_values, PythonConnectorConfigurationValue, PythonConnectorManifest,
};
use crate::errors::coded_reason;
use crate::graph::{PythonMediaCaps, PythonRouteSettings, PythonSignalSpec};
use crate::signals::{copy_envelope, python_envelope};
use crate::streams::{owned_endpoint_audio_frame_for_route, python_audio_frame, PythonAudioFrame};

const WORKER_IDLE_WAIT: Duration = Duration::from_millis(1);
const MAXIMUM_BATCH_ITEMS: usize = 1_024;

struct PythonConnectorFactory {
    factory: Py<PyAny>,
    manifest: pocketstation::connector::ConnectorManifest,
    maximum_batch_items: usize,
}

impl ConnectorFactory for PythonConnectorFactory {
    fn preparation_group(
        &self,
        route_id: RouteId,
        configuration: &pocketstation::graph::NodeConfig,
    ) -> Result<EndpointPreparationGroup, ConnectorError> {
        let resolved = resolve_configuration(&self.manifest, configuration)?;
        Python::attach(|py| {
            let result = (|| -> PyResult<EndpointPreparationGroup> {
                let configuration = python_configuration(py, &resolved)?;
                let group = self
                    .factory
                    .bind(py)
                    .call_method1("preparation_group", (route_id.get(), configuration))?;
                if group.is_none() {
                    return Ok(EndpointPreparationGroup::Route(route_id));
                }
                let group = group.extract::<String>()?;
                if group.trim().is_empty() {
                    return Err(PyValueError::new_err(
                        "Connector preparation group cannot be empty",
                    ));
                }
                Ok(EndpointPreparationGroup::Shared(EndpointGroupId::new(
                    group,
                )))
            })();
            result.map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))
        })
    }

    fn prepare(
        &self,
        inputs: Vec<EndpointPortInput>,
    ) -> Result<Box<dyn ConnectorWorker>, ConnectorError> {
        Python::attach(|py| {
            let mut worker_inputs = Vec::with_capacity(inputs.len());
            let mut descriptors = Vec::with_capacity(inputs.len());
            for input in inputs {
                let resolved =
                    resolve_configuration(&self.manifest, input.context().node_configuration())?;
                let descriptor = python_input_descriptor(py, &input, &resolved)
                    .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))?;
                let endpoint_id = input.context().endpoint_id().get();
                let connector_id = input
                    .context()
                    .connector_id()
                    .map_or(0, pocketstation::ConnectorId::get);
                let route_id = input.context().route_context().route_id().get();
                let (receiver, _) = input.into_parts();
                descriptors.push(descriptor.clone_ref(py));
                worker_inputs.push(WorkerInput {
                    descriptor,
                    endpoint_id,
                    connector_id,
                    route_id,
                    receiver,
                    last_discontinuity_epoch: None,
                });
            }
            let worker = self
                .factory
                .bind(py)
                .call_method1("prepare", (descriptors,))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare))?
                .unbind();
            let idle_enabled = worker
                .bind(py)
                .getattr("_pocketstation_idle_enabled")
                .and_then(|value| value.extract::<bool>())
                .unwrap_or(false);
            Ok(Box::new(PythonConnectorWorker {
                worker,
                inputs: worker_inputs,
                maximum_batch_items: self.maximum_batch_items,
                active: Arc::new(AtomicBool::new(true)),
                idle_enabled,
            }) as Box<dyn ConnectorWorker>)
        })
    }
}

struct WorkerInput {
    descriptor: Py<PythonConnectorInputDescriptor>,
    endpoint_id: u64,
    connector_id: u64,
    route_id: u64,
    receiver: EndpointReceiver,
    last_discontinuity_epoch: Option<u64>,
}

enum PendingItem {
    Audio {
        input_index: usize,
        frame: pocketstation::EndpointAudioFrame,
    },
    Signal {
        input_index: usize,
        signal: Arc<pocketstation::SignalEnvelope>,
    },
}

struct PythonConnectorWorker {
    worker: Py<PyAny>,
    inputs: Vec<WorkerInput>,
    maximum_batch_items: usize,
    active: Arc<AtomicBool>,
    idle_enabled: bool,
}

impl Drop for PythonConnectorWorker {
    fn drop(&mut self) {
        self.active.store(false, Ordering::Release);
    }
}

impl ConnectorWorker for PythonConnectorWorker {
    fn run(mut self: Box<Self>, context: ConnectorContext) -> ConnectorRunOutcome {
        if let Err(error) =
            self.call_context_method("start", &context, ConnectorErrorStage::Startup)
        {
            return ConnectorRunOutcome::failure(error);
        }
        loop {
            if context.is_abort_requested() {
                break;
            }
            let pending = self.collect_batch(&context);
            if !pending.is_empty() {
                let amount = u64::try_from(pending.len()).unwrap_or(u64::MAX);
                context.record_frame_received(amount);
                match self.deliver_batch(pending, &context) {
                    Ok((delivered, dropped)) => {
                        context.record_frame_delivered(delivered);
                        context.record_frame_dropped(dropped);
                    }
                    Err(error) => return ConnectorRunOutcome::failure(error),
                }
                continue;
            }
            if context.shutdown_mode() == Some(EndpointShutdownMode::Drain) {
                break;
            }
            if self.idle_enabled {
                if let Err(error) =
                    self.call_context_method("idle", &context, ConnectorErrorStage::Delivery)
                {
                    return ConnectorRunOutcome::failure(error);
                }
            }
            let _ = context.wait_for_stop(WORKER_IDLE_WAIT);
        }
        let mode = context
            .shutdown_mode()
            .unwrap_or(EndpointShutdownMode::Abort);
        match self.shutdown(mode, &context) {
            Ok(()) => ConnectorRunOutcome::success(),
            Err(error) => ConnectorRunOutcome::failure(error),
        }
    }

    fn cancel_preparation(self: Box<Self>) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let result = self
                .worker
                .bind(py)
                .call_method0("cancel_preparation")
                .map(|_| ())
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Prepare));
            self.active.store(false, Ordering::Release);
            result
        })
    }
}

impl PythonConnectorWorker {
    fn collect_batch(&mut self, context: &ConnectorContext) -> Vec<PendingItem> {
        let mut batch = Vec::with_capacity(self.maximum_batch_items);
        while batch.len() < self.maximum_batch_items {
            let mut progressed = false;
            for (input_index, input) in self.inputs.iter_mut().enumerate() {
                if batch.len() >= self.maximum_batch_items {
                    break;
                }
                let pending = match &mut input.receiver {
                    EndpointReceiver::Audio { receiver, .. } => receiver.try_recv().map(|frame| {
                        record_discontinuity(
                            context,
                            &mut input.last_discontinuity_epoch,
                            frame.lineage().discontinuity_epoch(),
                        );
                        PendingItem::Audio { input_index, frame }
                    }),
                    EndpointReceiver::Signal(receiver) => receiver.try_recv().map(|signal| {
                        if let Some(lineage) = signal.lineage() {
                            record_discontinuity(
                                context,
                                &mut input.last_discontinuity_epoch,
                                lineage.discontinuity_epoch(),
                            );
                        }
                        PendingItem::Signal {
                            input_index,
                            signal,
                        }
                    }),
                };
                if let Some(pending) = pending {
                    batch.push(pending);
                    progressed = true;
                }
            }
            if !progressed {
                break;
            }
        }
        batch
    }

    fn deliver_batch(
        &self,
        pending: Vec<PendingItem>,
        context: &ConnectorContext,
    ) -> Result<(u64, u64), ConnectorError> {
        Python::attach(|py| {
            let count = pending.len();
            let items = pending
                .into_iter()
                .map(|item| self.python_item(py, item))
                .collect::<PyResult<Vec<_>>>()
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            let outcome = self
                .worker
                .bind(py)
                .call_method1("deliver_batch", (items, context))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Delivery))?;
            parse_batch_outcomes(outcome, count)
        })
    }

    fn python_item(&self, py: Python<'_>, item: PendingItem) -> PyResult<Py<PythonConnectorItem>> {
        match item {
            PendingItem::Audio { input_index, frame } => {
                let input = &self.inputs[input_index];
                let frame = owned_endpoint_audio_frame_for_route(
                    frame,
                    input.endpoint_id,
                    Some(input.connector_id),
                    input.route_id,
                );
                let audio: Py<PythonAudioFrame> = Py::new(py, python_audio_frame(py, frame))?;
                Py::new(
                    py,
                    PythonConnectorItem {
                        kind: "audio",
                        input: input.descriptor.clone_ref(py),
                        audio: Some(audio),
                        signal: None,
                    },
                )
            }
            PendingItem::Signal {
                input_index,
                signal,
            } => {
                let input = &self.inputs[input_index];
                let signal = Py::new(py, python_envelope(py, copy_envelope(&signal))?)?;
                Py::new(
                    py,
                    PythonConnectorItem {
                        kind: "signal",
                        input: input.descriptor.clone_ref(py),
                        audio: None,
                        signal: Some(signal),
                    },
                )
            }
        }
    }

    fn call_context_method(
        &self,
        method: &str,
        context: &ConnectorContext,
        stage: ConnectorErrorStage,
    ) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, stage))?;
            self.worker
                .bind(py)
                .call_method1(method, (context,))
                .map(|_| ())
                .map_err(|error| python_error(py, error, stage))
        })
    }

    fn shutdown(
        &self,
        mode: EndpointShutdownMode,
        context: &ConnectorContext,
    ) -> Result<(), ConnectorError> {
        Python::attach(|py| {
            let context = python_context(py, context, Arc::clone(&self.active))
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Shutdown))?;
            let mode = match mode {
                EndpointShutdownMode::Drain => "drain",
                EndpointShutdownMode::Abort => "abort",
            };
            self.worker
                .bind(py)
                .call_method1("shutdown", (mode, context))
                .map(|_| ())
                .map_err(|error| python_error(py, error, ConnectorErrorStage::Shutdown))
        })
    }
}

fn python_input_descriptor(
    py: Python<'_>,
    input: &EndpointPortInput,
    configuration: &pocketstation::connector::ResolvedConnectorConfiguration,
) -> PyResult<Py<PythonConnectorInputDescriptor>> {
    let configuration = configuration_values(configuration)
        .into_iter()
        .map(|(name, value)| Py::new(py, value).map(|value| (name, value)))
        .collect::<PyResult<Vec<_>>>()?;
    let signal = Py::new(
        py,
        PythonSignalSpec {
            value: input.signal_spec().clone(),
        },
    )?;
    let media = Py::new(
        py,
        PythonMediaCaps {
            value: *input.media(),
        },
    )?;
    let route_settings = Py::new(
        py,
        PythonRouteSettings {
            value: *input.route_settings(),
        },
    )?;
    Py::new(
        py,
        PythonConnectorInputDescriptor {
            endpoint_id: input.context().endpoint_id().get(),
            connector_id: input
                .context()
                .connector_id()
                .map(pocketstation::ConnectorId::get),
            route_id: input.context().route_context().route_id().get(),
            port_name: input.port_name().to_owned(),
            signal_wire_id: input.signal_spec().wire_id().to_owned(),
            signal,
            media,
            route_settings,
            configuration,
        },
    )
}

fn python_configuration(
    py: Python<'_>,
    configuration: &pocketstation::connector::ResolvedConnectorConfiguration,
) -> PyResult<Py<PyDict>> {
    let values = PyDict::new(py);
    for (name, value) in configuration_values(configuration) {
        let value: Py<PythonConnectorConfigurationValue> = Py::new(py, value)?;
        values.set_item(name, value)?;
    }
    Ok(values.unbind())
}

fn parse_batch_outcomes(
    value: Bound<'_, PyAny>,
    count: usize,
) -> Result<(u64, u64), ConnectorError> {
    if value.is_none() {
        return Ok((u64::try_from(count).unwrap_or(u64::MAX), 0));
    }
    if let Ok(outcome) = value.extract::<String>() {
        return match outcome.as_str() {
            "delivered" => Ok((u64::try_from(count).unwrap_or(u64::MAX), 0)),
            "dropped" => Ok((0, u64::try_from(count).unwrap_or(u64::MAX))),
            _ => Err(invalid_batch_outcome()),
        };
    }
    let outcomes = value
        .extract::<Vec<String>>()
        .map_err(|_| invalid_batch_outcome())?;
    if outcomes.len() != count {
        return Err(internal_error(
            "python.invalid_batch_outcome_count",
            ConnectorErrorStage::Delivery,
            "Python Connector deliver_batch() returned the wrong number of outcomes",
        ));
    }
    let mut delivered = 0_u64;
    let mut dropped = 0_u64;
    for outcome in outcomes {
        match outcome.as_str() {
            "delivered" => delivered = delivered.saturating_add(1),
            "dropped" => dropped = dropped.saturating_add(1),
            _ => return Err(invalid_batch_outcome()),
        }
    }
    Ok((delivered, dropped))
}

fn invalid_batch_outcome() -> ConnectorError {
    internal_error(
        "python.invalid_batch_outcome",
        ConnectorErrorStage::Delivery,
        "Python Connector deliver_batch() must return None, one outcome, or one outcome per item",
    )
}

fn configuration_error(
    error: pocketstation::connector::ConnectorConfigurationError,
) -> ConnectorError {
    ConnectorError::new(
        ConnectorErrorCode::new(error.code().as_str()).unwrap_or_else(|_| {
            ConnectorErrorCode::new("connector.configuration.invalid")
                .expect("valid internal error code")
        }),
        ConnectorErrorStage::Configuration,
        ConnectorRetryability::RetryAfterReconfiguration,
        error.to_string(),
    )
    .unwrap_or_else(|_| {
        internal_error(
            "connector.configuration.invalid",
            ConnectorErrorStage::Configuration,
            "Connector configuration is invalid",
        )
    })
}

fn resolve_configuration(
    manifest: &pocketstation::connector::ConnectorManifest,
    node: &pocketstation::graph::NodeConfig,
) -> Result<ResolvedConnectorConfiguration, ConnectorError> {
    let mut configuration = ConnectorConfiguration::new();
    for field in manifest.configuration().fields() {
        let Some(encoded) = node.get(field.name()) else {
            continue;
        };
        let sensitive = node.is_sensitive(field.name());
        let value = match field.value_kind() {
            ConnectorConfigurationValueKind::Text if !sensitive => {
                ConnectorConfigurationValue::Text(encoded.to_owned())
            }
            ConnectorConfigurationValueKind::Boolean if !sensitive => encoded
                .parse()
                .map(ConnectorConfigurationValue::Boolean)
                .map_err(|_| invalid_encoded_configuration())?,
            ConnectorConfigurationValueKind::SignedInteger if !sensitive => encoded
                .parse()
                .map(ConnectorConfigurationValue::SignedInteger)
                .map_err(|_| invalid_encoded_configuration())?,
            ConnectorConfigurationValueKind::UnsignedInteger if !sensitive => encoded
                .parse()
                .map(ConnectorConfigurationValue::UnsignedInteger)
                .map_err(|_| invalid_encoded_configuration())?,
            ConnectorConfigurationValueKind::DurationMilliseconds if !sensitive => encoded
                .parse()
                .map(ConnectorConfigurationValue::DurationMilliseconds)
                .map_err(|_| invalid_encoded_configuration())?,
            ConnectorConfigurationValueKind::ByteCount if !sensitive => encoded
                .parse()
                .map(ConnectorConfigurationValue::ByteCount)
                .map_err(|_| invalid_encoded_configuration())?,
            ConnectorConfigurationValueKind::Secret if sensitive => ConnectorSecret::new(encoded)
                .map(ConnectorConfigurationValue::Secret)
                .map_err(|_| invalid_encoded_configuration())?,
            _ => return Err(invalid_encoded_configuration()),
        };
        configuration.insert(field.name(), value);
    }
    manifest
        .configuration()
        .resolve(&configuration)
        .map_err(configuration_error)
}

fn invalid_encoded_configuration() -> ConnectorError {
    internal_error(
        "connector.configuration.invalid_representation",
        ConnectorErrorStage::Configuration,
        "Connector configuration has an invalid encoded representation",
    )
}

fn record_discontinuity(context: &ConnectorContext, previous: &mut Option<u64>, current: u64) {
    if previous.is_some_and(|value| value != current) {
        context.record_discontinuity(1);
    }
    *previous = Some(current);
}

pub(crate) fn register_worker_connector(
    session: &Session,
    manifest: &PythonConnectorManifest,
    factory: Py<PyAny>,
    maximum_batch_items: usize,
) -> PyResult<PythonRegisteredConnector> {
    if !(1..=MAXIMUM_BATCH_ITEMS).contains(&maximum_batch_items) {
        return Err(PyValueError::new_err(coded_reason(
            "connector.invalid_contract",
            format!("maximum_batch_items must be between 1 and {MAXIMUM_BATCH_ITEMS}"),
        )));
    }
    let connector = Connector::new(
        manifest.value.clone(),
        Arc::new(PythonConnectorFactory {
            factory,
            manifest: manifest.value.clone(),
            maximum_batch_items,
        }),
    )
    .map_err(|error| {
        PyValueError::new_err(coded_reason(
            "connector.invalid_contract",
            error.to_string(),
        ))
    })?;
    session
        .register_connector(connector)
        .map(|registered| PythonRegisteredConnector { registered })
        .map_err(|error| {
            PyRuntimeError::new_err(coded_reason(
                "connector.registration_failed",
                error.to_string(),
            ))
        })
}
