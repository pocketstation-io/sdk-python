use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::mpsc::{sync_channel, Receiver, SyncSender};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::Duration;

use pocketstation_relay::RelayConnector;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use crate::audio_input::{configuration as audio_input_configuration, PythonAudioInput};
use crate::connector::{
    declare_connector, register_connector, register_worker_connector, PythonConnectorConfiguration,
    PythonConnectorManifest, PythonRegisteredConnector,
};
use crate::endpoint_authoring::{
    declare_endpoint, register_endpoint, PythonEndpointManifest, PythonRegisteredEndpoint,
};
use crate::errors::{
    coded_reason, native_extension_error, session_error, session_start_error, validate_nonempty,
};
use crate::extensions::PythonNativeExtensionLibrary;
use crate::graph::{
    make_operator, make_source_configuration, make_source_type_id, PythonDerivedStream,
    PythonEdgeContract, PythonEndpoint, PythonEndpointDescriptor, PythonOperatorInstance,
    PythonSignalSpec, PythonSourceInstance, PythonSourceOutput, PythonStem,
};
use crate::observations::{
    copy_event, copy_event_until, copy_metrics, drain_terminal_event, owned_recording_outcome,
    python_recording_outcome, python_session_event, python_session_metrics, OwnedSessionEvent,
    OwnedSessionMetrics, OwnedStopResult, PythonSessionEvent, PythonSessionMetrics,
    PythonStopResult,
};
use crate::operator_authoring::{register_operator, PythonOperatorManifest};
use crate::relay::{
    owned_relay_outcomes, python_relay_outcome, PythonRelayPublisher, RelayRouteRegistration,
    RelayRuntime,
};
use crate::sidecar::{
    poll_sidecar, runtime_error as sidecar_runtime_error, sidecar_error_message, sidecar_snapshot,
    wait_sidecar, OwnedSidecarRead, PythonSidecarMessage, PythonSidecarProcessSpec,
    PythonSidecarRead, PythonSidecarSnapshot, MAXIMUM_WAIT_MS as MAXIMUM_SIDECAR_WAIT_MS,
};
use crate::signals::{
    close_signal, copy_signal_metrics, new_signal_receipts, poll_signal, subscribe_derived,
    subscribe_source_output, validate_signal_subscription, wait_signal,
    OwnedSignalSubscriptionMetrics, PythonBusSubscription, PythonSignalRead,
    PythonSignalSubscriptionMetrics, SignalReceipts,
};
use crate::source_authoring::{register_source, PythonRegisteredSource, PythonSourceManifest};
use crate::sources::PythonSource;
use crate::streams::{
    copy_audio_batch, copy_audio_batch_until, python_audio_batch, request_audio_batch,
    request_audio_batch_wait, OwnedAudioFrame, PythonAudioBatch,
};

pub(crate) enum SessionCommand {
    PollAudio {
        response: SyncSender<Result<Option<Vec<OwnedAudioFrame>>, String>>,
    },
    WaitAudio {
        timeout: Duration,
        response: SyncSender<Result<Option<Vec<OwnedAudioFrame>>, String>>,
    },
    LifecycleState {
        response: SyncSender<&'static str>,
    },
    PollEvent {
        response: SyncSender<Result<Option<OwnedSessionEvent>, String>>,
    },
    WaitEvent {
        timeout: Duration,
        response: SyncSender<Result<Option<OwnedSessionEvent>, String>>,
    },
    Metrics {
        response: SyncSender<Result<OwnedSessionMetrics, String>>,
    },
    SignalMetrics {
        route_id: u64,
        response: SyncSender<Result<OwnedSignalSubscriptionMetrics, String>>,
    },
    SendSidecar {
        sidecar_id: u64,
        message: pocketstation::SidecarMessage,
        response: SyncSender<Result<(), String>>,
    },
    PollSidecar {
        sidecar_id: u64,
        response: SyncSender<Result<OwnedSidecarRead, String>>,
    },
    WaitSidecar {
        sidecar_id: u64,
        timeout: Duration,
        response: SyncSender<Result<OwnedSidecarRead, String>>,
    },
    SidecarSnapshot {
        sidecar_id: u64,
        response: SyncSender<Result<pocketstation::SessionSidecarMetrics, String>>,
    },
    Stop {
        response: SyncSender<OwnedStopResult>,
    },
    Cancel {
        response: SyncSender<OwnedStopResult>,
    },
    Shutdown,
}

pub(crate) struct SessionWorker {
    pub(crate) commands: SyncSender<SessionCommand>,
    join: Option<JoinHandle<()>>,
}

#[pyclass(name = "Session")]
pub(crate) struct PythonSession {
    session: Arc<Mutex<Option<pocketstation::Session>>>,
    relay_declared: Mutex<bool>,
    relay_connector: Mutex<Option<Arc<RelayConnector>>>,
    relay_routes: Arc<Mutex<Vec<RelayRouteRegistration>>>,
    signal_receipts: SignalReceipts,
    next_signal_subscription_id: Mutex<u64>,
}

#[pyclass(name = "_SessionStartCancellation", frozen)]
pub(crate) struct PythonSessionStartCancellation {
    cancellation: pocketstation::SessionStartCancellation,
}

#[pymethods]
impl PythonSessionStartCancellation {
    #[new]
    fn new() -> Self {
        Self {
            cancellation: pocketstation::SessionStartCancellation::default(),
        }
    }

    fn request(&self) {
        self.cancellation.request();
    }

    fn is_requested(&self) -> bool {
        self.cancellation.is_requested()
    }
}

#[pymethods]
impl PythonSession {
    #[new]
    #[pyo3(signature = (*, recording_root=None, trace_path=None, trace_capacity_records=256, sample_rate_hz=48_000, channels=1))]
    fn new(
        recording_root: Option<PathBuf>,
        trace_path: Option<PathBuf>,
        trace_capacity_records: usize,
        sample_rate_hz: u32,
        channels: u8,
    ) -> PyResult<Self> {
        if trace_path.is_some() && trace_capacity_records == 0 {
            return Err(PyValueError::new_err(coded_reason(
                "trace.invalid_capacity",
                "trace_capacity_records must be greater than zero",
            )));
        }
        if sample_rate_hz == 0 || !matches!(channels, 1 | 2) {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_sample_spec",
                "sample_rate_hz must be non-zero and channels must be 1 or 2",
            )));
        }
        let mut builder =
            pocketstation::Session::builder().sample_spec(pocketstation::SampleSpec::new(
                sample_rate_hz,
                channels,
                pocketstation::SampleFormat::F32Interleaved,
            ));
        if let Some(root) = recording_root {
            builder = builder.recording_root(root);
        }
        if let Some(path) = trace_path {
            builder = builder.session_trace(path, trace_capacity_records);
        }
        let session = builder.build();
        Ok(Self {
            session: Arc::new(Mutex::new(Some(session))),
            relay_declared: Mutex::new(false),
            relay_connector: Mutex::new(None),
            relay_routes: Arc::new(Mutex::new(Vec::new())),
            signal_receipts: new_signal_receipts(),
            next_signal_subscription_id: Mutex::new(0),
        })
    }

    #[cfg(feature = "conformance-fixtures")]
    #[staticmethod]
    #[pyo3(signature = (recording_root, trace_path=None, trace_capacity_records=256))]
    fn conformance(
        recording_root: PathBuf,
        trace_path: Option<PathBuf>,
        trace_capacity_records: usize,
    ) -> PyResult<Self> {
        if trace_path.is_some() && trace_capacity_records == 0 {
            return Err(PyValueError::new_err(coded_reason(
                "trace.invalid_capacity",
                "trace_capacity_records must be greater than zero",
            )));
        }
        let session = match trace_path {
            Some(trace_path) => pocketstation::conformance::session_with_recording_and_trace(
                recording_root,
                trace_path,
                trace_capacity_records,
            ),
            None => pocketstation::conformance::session_with_recording(recording_root),
        }
        .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
        crate::graph::register_graph_conformance_operator(&session)
            .map_err(PyRuntimeError::new_err)?;
        Ok(Self {
            session: Arc::new(Mutex::new(Some(session))),
            relay_declared: Mutex::new(false),
            relay_connector: Mutex::new(None),
            relay_routes: Arc::new(Mutex::new(Vec::new())),
            signal_receipts: new_signal_receipts(),
            next_signal_subscription_id: Mutex::new(0),
        })
    }

    fn capture(&self, source: &PythonSource) -> PyResult<PythonStem> {
        self.with_session(|session| {
            session
                .capture(source.declaration.to_source())
                .map(|handle| PythonStem { handle })
                .map_err(session_error)
        })
    }

    #[pyo3(signature = (sample_rate_hz, channels, capacity_frames=8, frame_samples_per_channel=480))]
    fn audio_input(
        &self,
        sample_rate_hz: u32,
        channels: u8,
        capacity_frames: usize,
        frame_samples_per_channel: usize,
    ) -> PyResult<PythonAudioInput> {
        let configuration = audio_input_configuration(
            sample_rate_hz,
            channels,
            capacity_frames,
            frame_samples_per_channel,
        )?;
        self.with_session(|session| {
            session
                .audio_input(configuration)
                .map(PythonAudioInput::new)
                .map_err(|error| {
                    PyValueError::new_err(coded_reason(
                        "audio_input.declaration_failed",
                        error.to_string(),
                    ))
                })
        })
    }

    #[pyo3(signature = (sample_rate_hz, channels, capacity_frames=8, frame_samples_per_channel=480))]
    fn pcm_source(
        &self,
        sample_rate_hz: u32,
        channels: u8,
        capacity_frames: usize,
        frame_samples_per_channel: usize,
    ) -> PyResult<PythonAudioInput> {
        self.audio_input(
            sample_rate_hz,
            channels,
            capacity_frames,
            frame_samples_per_channel,
        )
    }

    #[getter]
    fn id(&self) -> PyResult<u64> {
        self.with_session(|session| Ok(session.id().get()))
    }

    fn source(
        &self,
        source_type_id: String,
        configuration: HashMap<String, String>,
    ) -> PyResult<PythonSourceInstance> {
        self.with_session(|session| {
            session
                .source(
                    make_source_type_id(source_type_id)?,
                    make_source_configuration(configuration),
                )
                .map(|handle| PythonSourceInstance { handle })
                .map_err(session_error)
        })
    }

    fn operator(
        &self,
        operator_id: String,
        configuration: HashMap<String, String>,
    ) -> PyResult<PythonOperatorInstance> {
        self.with_session(|session| {
            session
                .operator(make_operator(operator_id, configuration))
                .map(|handle| PythonOperatorInstance { handle })
                .map_err(session_error)
        })
    }

    fn endpoint(&self, descriptor: &PythonEndpointDescriptor) -> PyResult<PythonEndpoint> {
        self.with_session(|session| {
            session
                .endpoint(descriptor.value.clone())
                .map(|handle| PythonEndpoint { handle })
                .map_err(session_error)
        })
    }

    #[allow(deprecated)]
    fn connector(
        &self,
        operator_id: String,
        configuration: HashMap<String, String>,
    ) -> PyResult<PythonEndpoint> {
        validate_nonempty("operator ID", &operator_id)?;
        if configuration.keys().any(|key| key.trim().is_empty()) {
            return Err(PyValueError::new_err(coded_reason(
                "graph.invalid_contract",
                "endpoint configuration keys cannot be empty",
            )));
        }
        let configuration = configuration.into_iter().fold(
            pocketstation::EndpointConfiguration::new(),
            |configuration, (key, value)| configuration.with(key, value),
        );
        self.with_session(|session| {
            session
                .connector(pocketstation::OperatorId::new(operator_id), configuration)
                .map(|handle| PythonEndpoint { handle })
                .map_err(session_error)
        })
    }

    fn browser(&self, receiver_uri: String) -> PyResult<PythonEndpoint> {
        validate_nonempty("receiver URI", &receiver_uri)?;
        self.with_session(|session| {
            session
                .browser(receiver_uri)
                .map(|handle| PythonEndpoint { handle })
                .map_err(session_error)
        })
    }

    fn polled_audio(&self) -> PyResult<PythonEndpoint> {
        self.with_session(|session| {
            session
                .polled_audio()
                .map(|handle| PythonEndpoint { handle })
                .map_err(session_error)
        })
    }

    fn register_connector(
        &self,
        manifest: &PythonConnectorManifest,
        factory: Py<PyAny>,
    ) -> PyResult<PythonRegisteredConnector> {
        self.with_session(|session| register_connector(session, manifest, factory))
    }

    fn register_connector_worker(
        &self,
        manifest: &PythonConnectorManifest,
        factory: Py<PyAny>,
        maximum_batch_items: usize,
    ) -> PyResult<PythonRegisteredConnector> {
        self.with_session(|session| {
            register_worker_connector(session, manifest, factory, maximum_batch_items)
        })
    }

    fn register_endpoint_provider(
        &self,
        manifest: &PythonEndpointManifest,
        factory: Py<PyAny>,
    ) -> PyResult<PythonRegisteredEndpoint> {
        self.with_session(|session| register_endpoint(session, manifest, factory))
    }

    fn register_source_provider(
        &self,
        manifest: &PythonSourceManifest,
        factory: Py<PyAny>,
    ) -> PyResult<PythonRegisteredSource> {
        self.with_session(|session| register_source(session, manifest, factory))
    }

    fn register_operator_provider(
        &self,
        manifest: &PythonOperatorManifest,
        factory: Py<PyAny>,
    ) -> PyResult<()> {
        self.with_session(|session| register_operator(session, manifest, factory))
    }

    fn declare_connector(
        &self,
        registered: &PythonRegisteredConnector,
        configuration: &PythonConnectorConfiguration,
        edge: &PythonEdgeContract,
    ) -> PyResult<PythonEndpoint> {
        self.with_session(|session| declare_connector(registered, session, configuration, edge))
    }

    fn declare_registered_endpoint(
        &self,
        registered: &PythonRegisteredEndpoint,
        configuration: HashMap<String, String>,
        edge: &PythonEdgeContract,
    ) -> PyResult<PythonEndpoint> {
        self.with_session(|session| declare_endpoint(session, registered, configuration, edge))
    }

    fn register_sidecar(&self, spec: &PythonSidecarProcessSpec) -> PyResult<u64> {
        self.with_session(|session| {
            session.register_sidecar(spec.to_core()).map_err(|error| {
                PyRuntimeError::new_err(coded_reason(
                    "sidecar.registration_unavailable",
                    error.to_string(),
                ))
            })?;
            Ok(spec.id)
        })
    }

    fn load_native_extension_library(
        &self,
        py: Python<'_>,
        path: PathBuf,
    ) -> PyResult<PythonNativeExtensionLibrary> {
        py.detach(|| {
            self.with_session(|session| {
                // SAFETY: the Python API names and documents this as a trusted
                // native-code boundary. Core still validates every mechanical
                // path, descriptor, and capacity invariant before registration.
                unsafe { session.load_native_extension_library(path) }
                    .map(Into::into)
                    .map_err(native_extension_error)
            })
        })
    }

    fn subscribe_derived(
        &self,
        stream: &PythonDerivedStream,
        signal: &PythonSignalSpec,
        edge: &PythonEdgeContract,
    ) -> PyResult<PythonBusSubscription> {
        let subscription_id = self.allocate_signal_subscription_id()?;
        self.with_session(|session| {
            subscribe_derived(
                session,
                &stream.handle,
                signal,
                edge,
                subscription_id,
                &self.signal_receipts,
            )
        })
    }

    fn subscribe_source_output(
        &self,
        stream: &PythonSourceOutput,
        signal: &PythonSignalSpec,
        edge: &PythonEdgeContract,
    ) -> PyResult<PythonBusSubscription> {
        let subscription_id = self.allocate_signal_subscription_id()?;
        self.with_session(|session| {
            subscribe_source_output(
                session,
                &stream.handle,
                signal,
                edge,
                subscription_id,
                &self.signal_receipts,
            )
        })
    }

    fn relay(
        &self,
        relay_url: String,
        relay_session_id: String,
        source_token: String,
    ) -> PyResult<PythonRelayPublisher> {
        validate_nonempty("relay URL", &relay_url)?;
        validate_nonempty("relay Session ID", &relay_session_id)?;
        validate_nonempty("source token", &source_token)?;
        let mut declared = self
            .relay_declared
            .lock()
            .map_err(|_| PyRuntimeError::new_err("relay declaration state is unavailable"))?;
        if *declared {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_endpoint",
                "a Session supports one relay publisher with multiple named AudioBuses",
            )));
        }
        let connector = Arc::new(
            RelayConnector::new().map_err(|error| PyValueError::new_err(error.to_string()))?,
        );
        let registered = self.with_session(|session| {
            connector
                .register(session)
                .map_err(|error| PyValueError::new_err(error.to_string()))
        })?;
        *self
            .relay_connector
            .lock()
            .map_err(|_| PyRuntimeError::new_err("relay connector state is unavailable"))? =
            Some(Arc::clone(&connector));
        *declared = true;
        drop(declared);
        Ok(PythonRelayPublisher {
            session: Arc::clone(&self.session),
            registered,
            relay_url,
            relay_session_id,
            source_token,
            routes: Arc::clone(&self.relay_routes),
        })
    }

    #[cfg(feature = "conformance-fixtures")]
    fn observed_connector(&self, per_frame_delay_ms: u64) -> PyResult<PythonEndpoint> {
        self.with_session(|session| {
            pocketstation::conformance::observed_connector(
                session,
                Duration::from_millis(per_frame_delay_ms),
            )
            .map(|handle| PythonEndpoint { handle })
            .map_err(|error| PyRuntimeError::new_err(error.to_string()))
        })
    }

    #[cfg(feature = "conformance-fixtures")]
    fn observed_browser(&self, per_frame_delay_ms: u64) -> PyResult<PythonEndpoint> {
        self.with_session(|session| {
            pocketstation::conformance::observed_browser(
                session,
                Duration::from_millis(per_frame_delay_ms),
            )
            .map(|handle| PythonEndpoint { handle })
            .map_err(|error| PyRuntimeError::new_err(error.to_string()))
        })
    }

    #[pyo3(signature = (cancellation=None))]
    fn start(
        &self,
        py: Python<'_>,
        cancellation: Option<&PythonSessionStartCancellation>,
    ) -> PyResult<PythonRunningSession> {
        let session = self
            .session
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Session state is unavailable"))?
            .take()
            .ok_or_else(|| {
                PyRuntimeError::new_err(coded_reason(
                    pocketstation::SessionDeclarationErrorCode::DraftFrozen.as_str(),
                    "Session has already started",
                ))
            })?;
        let relay = self.prepare_relay(&session)?;
        let session_id = session.id().get();
        let cancellation = cancellation
            .map(|value| value.cancellation.clone())
            .unwrap_or_default();
        let running = py
            .detach(|| session.start_cancellable(cancellation))
            .map_err(session_start_error)?;
        PythonRunningSession::spawn(
            running,
            relay,
            Arc::clone(&self.signal_receipts),
            session_id,
        )
    }
}

impl PythonSession {
    fn allocate_signal_subscription_id(&self) -> PyResult<u64> {
        let mut next = self
            .next_signal_subscription_id
            .lock()
            .map_err(|_| PyRuntimeError::new_err("BusSubscription ID state is unavailable"))?;
        *next = next.checked_add(1).ok_or_else(|| {
            PyRuntimeError::new_err(coded_reason(
                "session.capacity_exhausted",
                "BusSubscription ID space is exhausted",
            ))
        })?;
        Ok(*next)
    }

    fn prepare_relay(&self, _session: &pocketstation::Session) -> PyResult<Option<RelayRuntime>> {
        let declared = *self
            .relay_declared
            .lock()
            .map_err(|_| PyRuntimeError::new_err("relay declaration state is unavailable"))?;
        let routes = std::mem::take(
            &mut *self
                .relay_routes
                .lock()
                .map_err(|_| PyRuntimeError::new_err("relay route state is unavailable"))?,
        );
        if !declared {
            return Ok(None);
        }
        if routes.is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_endpoint",
                "relay publisher requires at least one published AudioBus",
            )));
        }
        let route_keys = routes
            .iter()
            .map(|route| (route.bus_id.clone(), route.key))
            .collect();
        drop(routes);
        let connector = self
            .relay_connector
            .lock()
            .map_err(|_| PyRuntimeError::new_err("relay connector state is unavailable"))?
            .clone()
            .ok_or_else(|| PyRuntimeError::new_err("relay connector is not registered"))?;
        Ok(Some(RelayRuntime {
            connector,
            routes: route_keys,
        }))
    }

    #[allow(clippy::significant_drop_tightening)] // The lock owns the borrowed draft Session.
    fn with_session<T>(
        &self,
        operation: impl FnOnce(&pocketstation::Session) -> PyResult<T>,
    ) -> PyResult<T> {
        let guard = self
            .session
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Session state is unavailable"))?;
        let session = guard.as_ref().ok_or_else(|| {
            PyRuntimeError::new_err(coded_reason(
                pocketstation::SessionDeclarationErrorCode::DraftFrozen.as_str(),
                "Session has already started",
            ))
        })?;
        operation(session)
    }
}

#[pyclass(name = "RunningSession")]
pub(crate) struct PythonRunningSession {
    worker: Mutex<Option<SessionWorker>>,
    signal_receipts: SignalReceipts,
    session_id: u64,
    terminal_state: Mutex<Option<&'static str>>,
}

#[pymethods]
impl PythonRunningSession {
    #[getter]
    const fn session_id(&self) -> u64 {
        self.session_id
    }

    #[getter]
    fn lifecycle_state(&self, py: Python<'_>) -> PyResult<&'static str> {
        let guard = self
            .worker
            .lock()
            .map_err(|_| PyRuntimeError::new_err("running Session state is unavailable"))?;
        let (response, receiver) = sync_channel(1);
        let has_worker = guard.is_some();
        let requested = match guard.as_ref() {
            Some(worker) => worker
                .commands
                .try_send(SessionCommand::LifecycleState { response })
                .map_err(|error| {
                    PyRuntimeError::new_err(coded_reason(
                        "session.lifecycle_unavailable",
                        format!("native Session lifecycle query is unavailable: {error}"),
                    ))
                })
                .map(|()| true)?,
            None => false,
        };
        drop(guard);
        if requested {
            return py
                .detach(move || receiver.recv_timeout(Duration::from_millis(100)))
                .map_err(|error| {
                    PyRuntimeError::new_err(coded_reason(
                        "session.lifecycle_unavailable",
                        format!("native Session did not return lifecycle state: {error}"),
                    ))
                });
        }
        debug_assert!(!has_worker);
        Ok(self
            .terminal_state
            .lock()
            .map_err(|_| PyRuntimeError::new_err("terminal Session state is unavailable"))?
            .unwrap_or("stopping"))
    }

    fn poll_audio(&self, py: Python<'_>) -> PyResult<Option<PythonAudioBatch>> {
        let commands = self.commands()?;
        let owned = py.detach(|| request_audio_batch(&commands))?;
        python_audio_batch(py, owned)
    }

    #[pyo3(signature = (timeout_ms=100))]
    fn wait_audio(&self, py: Python<'_>, timeout_ms: u64) -> PyResult<Option<PythonAudioBatch>> {
        const MAXIMUM_TIMEOUT_MS: u64 = 1_000;
        if timeout_ms > MAXIMUM_TIMEOUT_MS {
            return Err(PyValueError::new_err(format!(
                "timeout_ms must be at most {MAXIMUM_TIMEOUT_MS}"
            )));
        }
        let commands = self.commands()?;
        let owned =
            py.detach(|| request_audio_batch_wait(&commands, Duration::from_millis(timeout_ms)))?;
        python_audio_batch(py, owned)
    }

    fn poll_event(&self, py: Python<'_>) -> PyResult<Option<PythonSessionEvent>> {
        let commands = self.commands()?;
        let event = py.detach(|| crate::observations::request_event(&commands))?;
        event
            .map(|event| python_session_event(py, event))
            .transpose()
    }

    #[pyo3(signature = (timeout_ms=100))]
    fn wait_event(&self, py: Python<'_>, timeout_ms: u64) -> PyResult<Option<PythonSessionEvent>> {
        const MAXIMUM_TIMEOUT_MS: u64 = 1_000;
        if timeout_ms > MAXIMUM_TIMEOUT_MS {
            return Err(PyValueError::new_err(format!(
                "timeout_ms must be at most {MAXIMUM_TIMEOUT_MS}"
            )));
        }
        let commands = self.commands()?;
        let event = py.detach(|| {
            crate::observations::request_event_wait(&commands, Duration::from_millis(timeout_ms))
        })?;
        event
            .map(|event| python_session_event(py, event))
            .transpose()
    }

    fn poll_signal(
        &self,
        py: Python<'_>,
        subscription: &PythonBusSubscription,
    ) -> PyResult<PythonSignalRead> {
        poll_signal(py, &self.signal_receipts, self.session_id, subscription)
    }

    #[pyo3(signature = (subscription, timeout_ms=100))]
    fn wait_signal(
        &self,
        py: Python<'_>,
        subscription: &PythonBusSubscription,
        timeout_ms: u64,
    ) -> PyResult<PythonSignalRead> {
        wait_signal(
            py,
            &self.signal_receipts,
            self.session_id,
            subscription,
            timeout_ms,
        )
    }

    fn close_signal(&self, subscription: &PythonBusSubscription) -> PyResult<()> {
        close_signal(&self.signal_receipts, self.session_id, subscription)
    }

    fn signal_metrics(
        &self,
        py: Python<'_>,
        subscription: &PythonBusSubscription,
    ) -> PyResult<PythonSignalSubscriptionMetrics> {
        validate_signal_subscription(&self.signal_receipts, self.session_id, subscription)?;
        let commands = self.commands()?;
        let (response, receiver) = sync_channel(1);
        commands
            .send(SessionCommand::SignalMetrics {
                route_id: subscription.route_id,
                response,
            })
            .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
        let metrics = py.detach(move || {
            receiver
                .recv()
                .map_err(|_| "native Session worker did not return signal metrics".to_owned())?
        });
        metrics
            .map(PythonSignalSubscriptionMetrics::from)
            .map_err(PyRuntimeError::new_err)
    }

    fn send_sidecar(
        &self,
        py: Python<'_>,
        sidecar_id: u64,
        message: &PythonSidecarMessage,
    ) -> PyResult<()> {
        let commands = self.commands()?;
        let (response, receiver) = sync_channel(1);
        commands
            .send(SessionCommand::SendSidecar {
                sidecar_id,
                message: message.value.clone(),
                response,
            })
            .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
        py.detach(move || {
            receiver
                .recv()
                .map_err(|_| "native Session worker did not send sidecar signal".to_owned())?
        })
        .map_err(sidecar_runtime_error)
    }

    fn poll_sidecar(&self, py: Python<'_>, sidecar_id: u64) -> PyResult<PythonSidecarRead> {
        self.request_sidecar_read(py, sidecar_id, None)
    }

    #[pyo3(signature = (sidecar_id, timeout_ms=100))]
    fn wait_sidecar(
        &self,
        py: Python<'_>,
        sidecar_id: u64,
        timeout_ms: u64,
    ) -> PyResult<PythonSidecarRead> {
        if timeout_ms > MAXIMUM_SIDECAR_WAIT_MS {
            return Err(PyValueError::new_err(coded_reason(
                "sidecar.invalid_timeout",
                "timeout_ms must be between 0 and 1000",
            )));
        }
        self.request_sidecar_read(py, sidecar_id, Some(Duration::from_millis(timeout_ms)))
    }

    fn sidecar_snapshot(&self, py: Python<'_>, sidecar_id: u64) -> PyResult<PythonSidecarSnapshot> {
        let commands = self.commands()?;
        let (response, receiver) = sync_channel(1);
        commands
            .send(SessionCommand::SidecarSnapshot {
                sidecar_id,
                response,
            })
            .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
        py.detach(move || {
            receiver
                .recv()
                .map_err(|_| "native Session worker did not return sidecar metrics".to_owned())?
        })
        .map(PythonSidecarSnapshot::from)
        .map_err(sidecar_runtime_error)
    }

    fn metrics(&self, py: Python<'_>) -> PyResult<PythonSessionMetrics> {
        let commands = self.commands()?;
        let metrics = py.detach(|| crate::observations::request_metrics(&commands))?;
        python_session_metrics(py, metrics)
    }

    fn stop(&self, py: Python<'_>) -> PyResult<PythonStopResult> {
        let worker = self
            .worker
            .lock()
            .map_err(|_| PyRuntimeError::new_err("running Session state is unavailable"))?
            .take()
            .ok_or_else(|| PyRuntimeError::new_err("Session has stopped"))?;
        let owned = match py.detach(|| stop_worker(worker)) {
            Ok(owned) => owned,
            Err(error) => {
                self.cache_terminal_state("failed")?;
                return Err(error);
            }
        };
        self.cache_terminal_state(owned.lifecycle_state)?;
        let recording = owned
            .recording
            .map(|recording| python_recording_outcome(py, recording))
            .transpose()?;
        let relay = owned
            .relay
            .into_iter()
            .map(|outcome| python_relay_outcome(py, outcome))
            .collect::<PyResult<Vec<_>>>()?;
        let sidecars = owned
            .sidecars
            .into_iter()
            .map(|outcome| Py::new(py, PythonSidecarSnapshot::from(outcome)))
            .collect::<PyResult<Vec<_>>>()?;
        let trace = owned
            .trace
            .map(|outcome| {
                Py::new(
                    py,
                    crate::observations::PythonSessionTraceRecorderOutcome::from(outcome),
                )
            })
            .transpose()?;
        let terminal_event = owned
            .terminal_event
            .map(|event| python_session_event(py, event))
            .transpose()?
            .map(|event| Py::new(py, event))
            .transpose()?;
        Ok(PythonStopResult {
            success: owned.success,
            already_stopped: owned.already_stopped,
            disposition: owned.disposition,
            runtime_worker_panicked: owned.runtime_worker_panicked,
            capture_finalization_failures_total: owned.capture_finalization_failures_total,
            operator_finalization_failures_total: owned.operator_finalization_failures_total,
            endpoint_finalization_failures_total: owned.endpoint_finalization_failures_total,
            runtime_failures_total: owned.runtime_failures_total,
            lineage_failures_total: owned.lineage_failures_total,
            source_send_rejections_total: owned.source_send_rejections_total,
            runtime_events_total: owned.runtime_events_total,
            recording,
            trace,
            trace_error: owned.trace_error,
            terminal_event,
            relay,
            sidecars,
        })
    }

    fn cancel(&self, py: Python<'_>) -> PyResult<PythonStopResult> {
        let worker = self
            .worker
            .lock()
            .map_err(|_| PyRuntimeError::new_err("running Session state is unavailable"))?
            .take()
            .ok_or_else(|| PyRuntimeError::new_err("Session has stopped"))?;
        let owned = match py.detach(|| cancel_worker(worker)) {
            Ok(owned) => owned,
            Err(error) => {
                self.cache_terminal_state("failed")?;
                return Err(error);
            }
        };
        self.cache_terminal_state(owned.lifecycle_state)?;
        let recording = owned
            .recording
            .map(|recording| python_recording_outcome(py, recording))
            .transpose()?;
        let relay = owned
            .relay
            .into_iter()
            .map(|outcome| python_relay_outcome(py, outcome))
            .collect::<PyResult<Vec<_>>>()?;
        let sidecars = owned
            .sidecars
            .into_iter()
            .map(|outcome| Py::new(py, PythonSidecarSnapshot::from(outcome)))
            .collect::<PyResult<Vec<_>>>()?;
        let trace = owned
            .trace
            .map(|outcome| {
                Py::new(
                    py,
                    crate::observations::PythonSessionTraceRecorderOutcome::from(outcome),
                )
            })
            .transpose()?;
        let terminal_event = owned
            .terminal_event
            .map(|event| python_session_event(py, event))
            .transpose()?
            .map(|event| Py::new(py, event))
            .transpose()?;
        Ok(PythonStopResult {
            success: owned.success,
            already_stopped: owned.already_stopped,
            disposition: owned.disposition,
            runtime_worker_panicked: owned.runtime_worker_panicked,
            capture_finalization_failures_total: owned.capture_finalization_failures_total,
            operator_finalization_failures_total: owned.operator_finalization_failures_total,
            endpoint_finalization_failures_total: owned.endpoint_finalization_failures_total,
            runtime_failures_total: owned.runtime_failures_total,
            lineage_failures_total: owned.lineage_failures_total,
            source_send_rejections_total: owned.source_send_rejections_total,
            runtime_events_total: owned.runtime_events_total,
            recording,
            trace,
            trace_error: owned.trace_error,
            terminal_event,
            relay,
            sidecars,
        })
    }
}

impl PythonRunningSession {
    fn cache_terminal_state(&self, state: &'static str) -> PyResult<()> {
        *self
            .terminal_state
            .lock()
            .map_err(|_| PyRuntimeError::new_err("terminal Session state is unavailable"))? =
            Some(state);
        Ok(())
    }

    fn request_sidecar_read(
        &self,
        py: Python<'_>,
        sidecar_id: u64,
        timeout: Option<Duration>,
    ) -> PyResult<PythonSidecarRead> {
        let commands = self.commands()?;
        let (response, receiver) = sync_channel(1);
        let command = match timeout {
            Some(timeout) => SessionCommand::WaitSidecar {
                sidecar_id,
                timeout,
                response,
            },
            None => SessionCommand::PollSidecar {
                sidecar_id,
                response,
            },
        };
        commands
            .send(command)
            .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
        py.detach(move || {
            receiver
                .recv()
                .map_err(|_| "native Session worker did not return sidecar signal".to_owned())?
        })
        .map(PythonSidecarRead::from)
        .map_err(sidecar_runtime_error)
    }

    fn commands(&self) -> PyResult<SyncSender<SessionCommand>> {
        self.worker
            .lock()
            .map_err(|_| PyRuntimeError::new_err("running Session state is unavailable"))?
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("Session has stopped"))
            .map(|worker| worker.commands.clone())
    }

    fn spawn(
        running: pocketstation::RunningSession,
        relay: Option<RelayRuntime>,
        signal_receipts: SignalReceipts,
        session_id: u64,
    ) -> PyResult<Self> {
        const COMMAND_CAPACITY_COUNT: usize = 8;
        let (commands, receiver) = sync_channel(COMMAND_CAPACITY_COUNT);
        let join = thread::Builder::new()
            .name("pocketstation-python-session".to_owned())
            .spawn(move || session_worker(running, receiver, relay))
            .map_err(|error| {
                PyRuntimeError::new_err(format!("failed to start Session worker: {error}"))
            })?;
        Ok(Self {
            worker: Mutex::new(Some(SessionWorker {
                commands,
                join: Some(join),
            })),
            signal_receipts,
            session_id,
            terminal_state: Mutex::new(None),
        })
    }
}

impl Drop for PythonRunningSession {
    fn drop(&mut self) {
        let Ok(worker) = self.worker.get_mut() else {
            return;
        };
        let Some(worker) = worker.take() else {
            return;
        };
        let _ = worker.commands.try_send(SessionCommand::Shutdown);
        // Destruction must not wait on capture or finalization. Dropping the
        // JoinHandle detaches the worker, which still owns and stops Session.
        drop(worker);
    }
}

#[allow(clippy::needless_pass_by_value)] // Thread entry owns receiver and relay lifetime.
fn session_worker(
    mut running: pocketstation::RunningSession,
    receiver: Receiver<SessionCommand>,
    relay: Option<RelayRuntime>,
) {
    while let Ok(command) = receiver.recv() {
        match command {
            SessionCommand::PollAudio { response } => {
                let _ = response.send(copy_audio_batch(&running));
            }
            SessionCommand::WaitAudio { timeout, response } => {
                let _ = response.send(copy_audio_batch_until(&running, timeout));
            }
            SessionCommand::LifecycleState { response } => {
                let _ = response.send(core_lifecycle_state_name(running.state()));
            }
            SessionCommand::PollEvent { response } => {
                let _ = response.send(copy_event(&running));
            }
            SessionCommand::WaitEvent { timeout, response } => {
                let _ = response.send(copy_event_until(&running, timeout));
            }
            SessionCommand::Metrics { response } => {
                let _ = response.send(copy_metrics(&running));
            }
            SessionCommand::SignalMetrics { route_id, response } => {
                let _ = response.send(copy_signal_metrics(&running, route_id));
            }
            SessionCommand::SendSidecar {
                sidecar_id,
                message,
                response,
            } => {
                let _ = response.send(
                    running
                        .try_send_sidecar_signal(sidecar_id, message)
                        .map_err(sidecar_error_message),
                );
            }
            SessionCommand::PollSidecar {
                sidecar_id,
                response,
            } => {
                let _ = response.send(poll_sidecar(&running, sidecar_id));
            }
            SessionCommand::WaitSidecar {
                sidecar_id,
                timeout,
                response,
            } => {
                let _ = response.send(wait_sidecar(&running, sidecar_id, timeout));
            }
            SessionCommand::SidecarSnapshot {
                sidecar_id,
                response,
            } => {
                let _ = response.send(sidecar_snapshot(&running, sidecar_id));
            }
            SessionCommand::Stop { response } => {
                let stop = running.stop();
                let outcome = stop.outcome();
                let already_stopped = matches!(
                    stop.disposition(),
                    pocketstation::SessionStopDisposition::AlreadyStopped
                );
                let _ = response.send(OwnedStopResult {
                    lifecycle_state: core_lifecycle_state_name(running.state()),
                    success: stop.is_success(),
                    already_stopped,
                    disposition: if already_stopped {
                        "already-stopped".to_owned()
                    } else {
                        "stopped".to_owned()
                    },
                    runtime_worker_panicked: outcome.runtime_worker_panicked(),
                    capture_finalization_failures_total: outcome
                        .capture_finalization_failures_total(),
                    operator_finalization_failures_total: outcome
                        .operator_finalization_failures_total(),
                    endpoint_finalization_failures_total: outcome
                        .endpoint_finalization_failures_total(),
                    runtime_failures_total: outcome.runtime_failures_total(),
                    lineage_failures_total: outcome.lineage_failures_total(),
                    source_send_rejections_total: outcome.source_send_rejections_total(),
                    runtime_events_total: outcome.runtime_events_total(),
                    recording: owned_recording_outcome(&running),
                    trace: running
                        .session_trace_outcome()
                        .and_then(Result::ok)
                        .cloned(),
                    trace_error: running
                        .session_trace_outcome()
                        .and_then(Result::err)
                        .map(ToString::to_string),
                    terminal_event: drain_terminal_event(&running),
                    relay: owned_relay_outcomes(relay.as_ref()),
                    sidecars: running.sidecar_metrics().into_vec(),
                });
                return;
            }
            SessionCommand::Cancel { response } => {
                let cancel = running.cancel();
                let outcome = cancel.outcome();
                let already_stopped = matches!(
                    cancel.disposition(),
                    pocketstation::SessionCancelDisposition::AlreadyStopped
                );
                let _ = response.send(OwnedStopResult {
                    lifecycle_state: core_lifecycle_state_name(running.state()),
                    success: cancel.is_success(),
                    already_stopped,
                    disposition: if already_stopped {
                        "already-stopped".to_owned()
                    } else {
                        "cancelled".to_owned()
                    },
                    runtime_worker_panicked: outcome.runtime_worker_panicked(),
                    capture_finalization_failures_total: outcome
                        .capture_finalization_failures_total(),
                    operator_finalization_failures_total: outcome
                        .operator_finalization_failures_total(),
                    endpoint_finalization_failures_total: outcome
                        .endpoint_finalization_failures_total(),
                    runtime_failures_total: outcome.runtime_failures_total(),
                    lineage_failures_total: outcome.lineage_failures_total(),
                    source_send_rejections_total: outcome.source_send_rejections_total(),
                    runtime_events_total: outcome.runtime_events_total(),
                    recording: owned_recording_outcome(&running),
                    trace: running
                        .session_trace_outcome()
                        .and_then(Result::ok)
                        .cloned(),
                    trace_error: running
                        .session_trace_outcome()
                        .and_then(Result::err)
                        .map(ToString::to_string),
                    terminal_event: drain_terminal_event(&running),
                    relay: owned_relay_outcomes(relay.as_ref()),
                    sidecars: running.sidecar_metrics().into_vec(),
                });
                return;
            }
            SessionCommand::Shutdown => {
                let _ = running.stop();
                return;
            }
        }
    }
    let _ = running.stop();
}

const fn core_lifecycle_state_name(state: pocketstation::SessionLifecycleState) -> &'static str {
    match state {
        pocketstation::SessionLifecycleState::Starting => "starting",
        pocketstation::SessionLifecycleState::Running => "running",
        pocketstation::SessionLifecycleState::Stopping => "stopping",
        pocketstation::SessionLifecycleState::Stopped => "stopped",
        pocketstation::SessionLifecycleState::Failed => "failed",
    }
}

pub(crate) fn stop_worker(mut worker: SessionWorker) -> PyResult<OwnedStopResult> {
    let (response, receiver) = sync_channel(1);
    worker
        .commands
        .send(SessionCommand::Stop { response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    let result = receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not finalize"))?;
    if let Some(join) = worker.join.take() {
        join.join()
            .map_err(|_| PyRuntimeError::new_err("native Session worker panicked"))?;
    }
    Ok(result)
}

pub(crate) fn cancel_worker(mut worker: SessionWorker) -> PyResult<OwnedStopResult> {
    let (response, receiver) = sync_channel(1);
    worker
        .commands
        .send(SessionCommand::Cancel { response })
        .map_err(|_| PyRuntimeError::new_err("native Session worker has stopped"))?;
    let result = receiver
        .recv()
        .map_err(|_| PyRuntimeError::new_err("native Session worker did not cancel"))?;
    if let Some(join) = worker.join.take() {
        join.join()
            .map_err(|_| PyRuntimeError::new_err("native Session worker panicked"))?;
    }
    Ok(result)
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonSession>()?;
    module.add_class::<PythonSessionStartCancellation>()?;
    module.add_class::<PythonRunningSession>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::time::{Duration, Instant};

    use pocketstation::{ApplicationSelector, Source};

    use super::{stop_worker, PythonRunningSession};
    use crate::observations::{request_event, request_metrics};
    use crate::signals::new_signal_receipts;
    use crate::streams::request_audio_batch_wait;

    #[test]
    fn given_native_python_worker_when_polled_then_batches_preserve_both_stems() {
        let recording_root = tempfile::tempdir().expect("temporary recording root");
        let session = pocketstation::conformance::session_with_recording(recording_root.path())
            .expect("conformance Session");
        let application = session
            .capture(Source::application(ApplicationSelector::name(
                "PocketStation Python Fixture",
            )))
            .expect("application stem");
        let microphone = session
            .capture(Source::microphone_default())
            .expect("microphone stem");
        let audio = session.polled_audio().expect("polled audio endpoint");
        let connector = pocketstation::conformance::observed_connector(&session, Duration::ZERO)
            .expect("observed connector");
        let browser =
            pocketstation::conformance::observed_browser(&session, Duration::from_millis(25))
                .expect("observed browser");
        application.send(audio).expect("application route");
        microphone.send(audio).expect("microphone route");
        let application_connector_route = application
            .send(connector)
            .expect("application connector route");
        let microphone_connector_route = microphone
            .send(connector)
            .expect("microphone connector route");
        let application_browser_route = application
            .send(browser)
            .expect("application browser route");
        let microphone_browser_route = microphone.send(browser).expect("microphone browser route");
        application
            .record("application")
            .expect("application recording");
        microphone
            .record("microphone")
            .expect("microphone recording");

        let session_id = session.id().get();
        let running = session.start().expect("running conformance Session");
        let python_running =
            PythonRunningSession::spawn(running, None, new_signal_receipts(), session_id)
                .expect("Python Session worker");
        let worker = python_running
            .worker
            .lock()
            .expect("worker state")
            .take()
            .expect("live worker");
        let first_event = request_event(&worker.commands)
            .expect("event poll")
            .expect("starting or running event");
        assert_eq!(first_event.kind, "lifecycle");
        let external_route_ids = [
            application_connector_route.get(),
            microphone_connector_route.get(),
            application_browser_route.get(),
            microphone_browser_route.get(),
        ];
        let deadline = Instant::now() + Duration::from_secs(5);
        let mut stems = BTreeSet::new();
        let metrics = loop {
            if let Some(batch) =
                request_audio_batch_wait(&worker.commands, Duration::from_millis(100))
                    .expect("bounded batch wait")
            {
                stems.extend(batch.into_iter().map(|frame| frame.stem_id));
            }
            let metrics = request_metrics(&worker.commands).expect("metrics snapshot");
            let external_routes: Vec<_> = metrics
                .routes
                .iter()
                .filter(|route| external_route_ids.contains(&route.route_id))
                .collect();
            let external_routes_ready = external_routes.len() == external_route_ids.len()
                && external_routes.iter().all(|route| {
                    route.frames_delivered_total > 0 && route.endpoint_frames_received_total > 0
                });
            if stems.len() == 2 && external_routes_ready {
                break metrics;
            }
            assert!(
                Instant::now() < deadline,
                "both stems and all external routes must deliver before deadline"
            );
            std::thread::sleep(Duration::from_millis(1));
        };
        assert_eq!(metrics.source_count, 2);
        assert_eq!(metrics.route_count, 8);
        assert_eq!(
            stems.len(),
            2,
            "both source-aware stems must cross the batch"
        );

        let stop = stop_worker(worker).expect("worker stop");
        assert!(stop.success, "native Session must finalize successfully");
        let recording = stop.recording.expect("recording outcome");
        assert!(recording.complete);
        assert_eq!(recording.stems.len(), 2);
    }
}
