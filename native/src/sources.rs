use pocketstation::{
    ApplicationPolicyObservation, ApplicationSelector, CaptureAuthorizationSnapshot,
    CaptureOpenOutcome, CapturePermissionLifecycle, CaptureScope, CaptureSessionGrant,
    CaptureSource, DeviceId, DeviceSelector, PermissionEpoch, PermissionObservation, Platform,
    ProcessId, ProcessTreeScope, SelectorPersistenceScope, Source, SourceIdentityStrength,
    SourceKind, SourceQuery, SourceState, StableSourceId,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::sync::Mutex;

use crate::errors::{coded_reason, parse_platform, validate_nonempty, validate_process_id};

#[derive(Clone)]
pub(crate) enum SourceDeclaration {
    ApplicationName(String),
    ApplicationBundleId(String),
    ApplicationProcessId(u32),
    ApplicationStableId {
        platform: Platform,
        stable_key: String,
    },
    ApplicationProcessInstance {
        process_id: u32,
        platform: Platform,
        stable_key: String,
    },
    MicrophoneDefault,
    MicrophoneId(String),
    SystemMix,
}

impl SourceDeclaration {
    pub(crate) fn to_source(&self) -> Source {
        match self {
            Self::ApplicationName(name) => {
                Source::application(ApplicationSelector::name(name.clone()))
            }
            Self::ApplicationBundleId(bundle_id) => {
                Source::application(ApplicationSelector::bundle_id(bundle_id.clone()))
            }
            Self::ApplicationProcessId(process_id) => {
                Source::application(ApplicationSelector::process_id(ProcessId::new(*process_id)))
            }
            Self::ApplicationStableId {
                platform,
                stable_key,
            } => Source::application(ApplicationSelector::stable_id(StableSourceId::new(
                *platform,
                SourceKind::Application,
                stable_key.clone(),
            ))),
            Self::ApplicationProcessInstance {
                process_id,
                platform,
                stable_key,
            } => Source::application(ApplicationSelector::process_instance(
                ProcessId::new(*process_id),
                StableSourceId::new(*platform, SourceKind::Application, stable_key.clone()),
            )),
            Self::MicrophoneDefault => Source::microphone_default(),
            Self::MicrophoneId(device_id) => {
                Source::microphone(DeviceSelector::id(DeviceId::new(device_id.clone())))
            }
            Self::SystemMix => Source::system_mix(),
        }
    }
}

#[pyclass(name = "Source", frozen)]
pub(crate) struct PythonSource {
    pub(crate) declaration: SourceDeclaration,
}

#[pyclass(name = "DiscoveredSource", frozen)]
pub(crate) struct PythonDiscoveredSource {
    source: CaptureSource,
    #[pyo3(get)]
    platform: String,
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    stable_key: String,
    #[pyo3(get)]
    source_id: u64,
    #[pyo3(get)]
    name: String,
    #[pyo3(get)]
    process_id: Option<u32>,
    #[pyo3(get)]
    application_id: Option<String>,
    #[pyo3(get)]
    device_uid: Option<String>,
    #[pyo3(get)]
    state: String,
    #[pyo3(get)]
    sample_rate_hz: u32,
    #[pyo3(get)]
    channel_count: u16,
    #[pyo3(get)]
    identity_strength: String,
    #[pyo3(get)]
    selector_persistence_scope: Option<String>,
    #[pyo3(get)]
    process_tree_scope: Option<String>,
}

#[pyclass(name = "CaptureAuthorizationSnapshot", frozen)]
pub(crate) struct PythonCaptureAuthorizationSnapshot {
    #[pyo3(get)]
    capability: String,
    #[pyo3(get)]
    os_permission: String,
    #[pyo3(get)]
    application_policy: String,
    #[pyo3(get)]
    session_grant: String,
    #[pyo3(get)]
    capture_scope: String,
    #[pyo3(get)]
    scope_stable_id: Option<String>,
    #[pyo3(get)]
    identity_strength: String,
    #[pyo3(get)]
    permission_epoch: u64,
    #[pyo3(get)]
    observed_at_ns: u64,
    #[pyo3(get)]
    open_outcome: String,
}

#[pymethods]
impl PythonDiscoveredSource {
    #[pyo3(signature = (
        os_permission="not-observable",
        application_policy="not-observable",
        session_grant="not-evaluated",
        permission_epoch=1
    ))]
    fn authorization_before_open(
        &self,
        os_permission: &str,
        application_policy: &str,
        session_grant: &str,
        permission_epoch: u64,
    ) -> PyResult<PythonCaptureAuthorizationSnapshot> {
        if permission_epoch == 0 {
            return Err(PyValueError::new_err(coded_reason(
                "capture.invalid_permission_epoch",
                "permission epoch must be greater than zero",
            )));
        }
        let snapshot = CaptureAuthorizationSnapshot::from_open_observations(
            &self.source,
            parse_session_grant(session_grant)?,
            PermissionEpoch(permission_epoch),
            parse_permission_observation(os_permission)?,
            parse_application_policy(application_policy)?,
            CaptureOpenOutcome::NotAttempted,
        );
        Ok(PythonCaptureAuthorizationSnapshot::from(snapshot))
    }
}

#[pyclass(name = "CapturePermissionTransition", frozen)]
pub(crate) struct PythonCapturePermissionTransition {
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    previous: String,
    #[pyo3(get)]
    current: String,
    #[pyo3(get)]
    permission_epoch: u64,
}

#[pyclass(name = "CapturePermissionLifecycle")]
pub(crate) struct PythonCapturePermissionLifecycle {
    lifecycle: Mutex<CapturePermissionLifecycle>,
}

#[pymethods]
impl PythonCapturePermissionLifecycle {
    #[new]
    fn new(current: &str) -> PyResult<Self> {
        Ok(Self {
            lifecycle: Mutex::new(CapturePermissionLifecycle::new(
                parse_permission_observation(current)?,
            )),
        })
    }

    #[getter]
    fn current(&self) -> PyResult<&'static str> {
        let lifecycle = self
            .lifecycle
            .lock()
            .map_err(|_| PyValueError::new_err("capture permission state is unavailable"))?;
        Ok(permission_observation_name(lifecycle.current()))
    }

    #[getter]
    fn permission_epoch(&self) -> PyResult<u64> {
        let lifecycle = self
            .lifecycle
            .lock()
            .map_err(|_| PyValueError::new_err("capture permission state is unavailable"))?;
        Ok(lifecycle.permission_epoch().0)
    }

    fn observe(&self, current: &str) -> PyResult<Option<PythonCapturePermissionTransition>> {
        let mut lifecycle = self
            .lifecycle
            .lock()
            .map_err(|_| PyValueError::new_err("capture permission state is unavailable"))?;
        Ok(lifecycle
            .observe(parse_permission_observation(current)?)
            .map(|transition| PythonCapturePermissionTransition {
                kind: match transition.kind {
                    pocketstation::SourceLifecycleEventKind::PermissionChanged => {
                        "permission-changed"
                    }
                    pocketstation::SourceLifecycleEventKind::PermissionRevoked => {
                        "permission-revoked"
                    }
                    _ => "unrecognized-permission-transition",
                }
                .to_owned(),
                previous: permission_observation_name(transition.previous).to_owned(),
                current: permission_observation_name(transition.current).to_owned(),
                permission_epoch: transition.permission_epoch.0,
            }))
    }
}

#[pymethods]
impl PythonSource {
    #[staticmethod]
    fn application(name: String) -> PyResult<Self> {
        if name.trim().is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_selector",
                "application name must not be empty",
            )));
        }
        Ok(Self {
            declaration: SourceDeclaration::ApplicationName(name),
        })
    }

    #[staticmethod]
    fn application_bundle_id(bundle_id: String) -> PyResult<Self> {
        validate_nonempty("application bundle ID", &bundle_id)?;
        Ok(Self {
            declaration: SourceDeclaration::ApplicationBundleId(bundle_id),
        })
    }

    #[staticmethod]
    fn application_process_id(process_id: u32) -> PyResult<Self> {
        validate_process_id(process_id)?;
        Ok(Self {
            declaration: SourceDeclaration::ApplicationProcessId(process_id),
        })
    }

    #[staticmethod]
    fn application_stable_id(platform: &str, stable_key: String) -> PyResult<Self> {
        validate_nonempty("application stable ID", &stable_key)?;
        Ok(Self {
            declaration: SourceDeclaration::ApplicationStableId {
                platform: parse_platform(platform)?,
                stable_key,
            },
        })
    }

    #[staticmethod]
    fn application_process_instance(
        process_id: u32,
        platform: &str,
        stable_key: String,
    ) -> PyResult<Self> {
        validate_process_id(process_id)?;
        validate_nonempty("application stable ID", &stable_key)?;
        Ok(Self {
            declaration: SourceDeclaration::ApplicationProcessInstance {
                process_id,
                platform: parse_platform(platform)?,
                stable_key,
            },
        })
    }

    #[staticmethod]
    const fn microphone_default() -> Self {
        Self {
            declaration: SourceDeclaration::MicrophoneDefault,
        }
    }

    #[staticmethod]
    fn microphone_id(device_id: String) -> PyResult<Self> {
        if device_id.trim().is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_selector",
                "microphone device ID must not be empty",
            )));
        }
        Ok(Self {
            declaration: SourceDeclaration::MicrophoneId(device_id),
        })
    }

    #[staticmethod]
    const fn system_mix() -> Self {
        Self {
            declaration: SourceDeclaration::SystemMix,
        }
    }
}

fn platform_name(platform: Platform) -> &'static str {
    match platform {
        Platform::Macos => "macos",
        Platform::Windows => "windows",
        Platform::Linux => "linux",
        Platform::Ios => "ios",
        Platform::Android => "android",
        Platform::Web => "web",
        Platform::Unknown => "unknown",
    }
}

fn source_kind_name(kind: SourceKind) -> &'static str {
    match kind {
        SourceKind::Application => "application",
        SourceKind::OutputDevice => "output-device",
        SourceKind::InputDevice => "input-device",
        SourceKind::SystemMix => "system-mix",
    }
}

fn source_state_name(state: SourceState) -> &'static str {
    match state {
        SourceState::Available => "available",
        SourceState::Playing => "playing",
        SourceState::Silent => "silent",
        SourceState::Unavailable => "unavailable",
        SourceState::PermissionBlocked => "permission-blocked",
    }
}

fn identity_strength_name(strength: SourceIdentityStrength) -> &'static str {
    match strength {
        SourceIdentityStrength::ApplicationIdAndProcessId => "application-id-and-process-id",
        SourceIdentityStrength::StableApplicationId => "stable-application-id",
        SourceIdentityStrength::ProcessId => "process-id",
        SourceIdentityStrength::StableDeviceUid => "stable-device-uid",
        SourceIdentityStrength::PlatformStableId => "platform-stable-id",
    }
}

fn selector_persistence_scope_name(scope: SelectorPersistenceScope) -> &'static str {
    match scope {
        SelectorPersistenceScope::ProcessLifetime => "process-lifetime",
        SelectorPersistenceScope::ApplicationIdentity => "application-identity",
        SelectorPersistenceScope::DeviceIdentity => "device-identity",
        SelectorPersistenceScope::SessionDefaultDevice => "session-default-device",
        SelectorPersistenceScope::PlatformIdentity => "platform-identity",
    }
}

fn process_tree_scope_name(scope: ProcessTreeScope) -> &'static str {
    match scope {
        ProcessTreeScope::SelectedProcessOnly => "selected-process-only",
        ProcessTreeScope::SelectedProcessAndDescendants => "selected-process-and-descendants",
        ProcessTreeScope::ApplicationIdentity => "application-identity",
        ProcessTreeScope::NotApplicable => "not-applicable",
    }
}

pub(crate) fn permission_observation_name(observation: PermissionObservation) -> &'static str {
    match observation {
        PermissionObservation::Allowed => "allowed",
        PermissionObservation::Denied => "denied",
        PermissionObservation::Restricted => "restricted",
        PermissionObservation::NotDetermined => "not-determined",
        PermissionObservation::Revoked => "revoked",
        PermissionObservation::NotObservable => "not-observable",
        PermissionObservation::NotApplicable => "not-applicable",
    }
}

fn parse_permission_observation(value: &str) -> PyResult<PermissionObservation> {
    match value {
        "allowed" => Ok(PermissionObservation::Allowed),
        "denied" => Ok(PermissionObservation::Denied),
        "restricted" => Ok(PermissionObservation::Restricted),
        "not-determined" => Ok(PermissionObservation::NotDetermined),
        "revoked" => Ok(PermissionObservation::Revoked),
        "not-observable" => Ok(PermissionObservation::NotObservable),
        "not-applicable" => Ok(PermissionObservation::NotApplicable),
        _ => Err(PyValueError::new_err(coded_reason(
            "capture.invalid_permission_observation",
            "permission observation is not recognized",
        ))),
    }
}

fn parse_application_policy(value: &str) -> PyResult<ApplicationPolicyObservation> {
    match value {
        "allowed" => Ok(ApplicationPolicyObservation::Allowed),
        "denied" => Ok(ApplicationPolicyObservation::Denied),
        "not-observable" => Ok(ApplicationPolicyObservation::NotObservable),
        "not-applicable" => Ok(ApplicationPolicyObservation::NotApplicable),
        _ => Err(PyValueError::new_err(coded_reason(
            "capture.invalid_application_policy",
            "application policy observation is not recognized",
        ))),
    }
}

fn parse_session_grant(value: &str) -> PyResult<CaptureSessionGrant> {
    match value {
        "granted-by-explicit-selection" => Ok(CaptureSessionGrant::GrantedByExplicitSelection),
        "denied" => Ok(CaptureSessionGrant::Denied),
        "not-evaluated" => Ok(CaptureSessionGrant::NotEvaluated),
        _ => Err(PyValueError::new_err(coded_reason(
            "capture.invalid_session_grant",
            "capture Session grant is not recognized",
        ))),
    }
}

pub(crate) fn stable_source_parts(
    stable_id: &StableSourceId,
) -> (&'static str, &'static str, &str) {
    (
        platform_name(stable_id.platform),
        source_kind_name(stable_id.kind),
        &stable_id.stable_key,
    )
}

fn discovered_source(source: CaptureSource) -> PythonDiscoveredSource {
    let platform = platform_name(source.stable_id.platform).to_owned();
    let kind = source_kind_name(source.stable_id.kind).to_owned();
    let source_id = source.stable_id.source_id().get();
    let identity_strength = identity_strength_name(source.identity_strength()).to_owned();
    let selector_persistence_scope = source
        .selector_persistence_scope()
        .map(selector_persistence_scope_name)
        .map(str::to_owned);
    let process_tree_scope = source
        .process_tree_scope()
        .map(process_tree_scope_name)
        .map(str::to_owned);
    PythonDiscoveredSource {
        source: source.clone(),
        platform,
        kind,
        stable_key: source.stable_id.stable_key,
        source_id,
        name: source.name,
        process_id: source.process_id,
        application_id: source.app_id,
        device_uid: source.device_uid,
        state: source_state_name(source.state).to_owned(),
        sample_rate_hz: source.sample_rate_hz,
        channel_count: source.channels,
        identity_strength,
        selector_persistence_scope,
        process_tree_scope,
    }
}

impl From<CaptureAuthorizationSnapshot> for PythonCaptureAuthorizationSnapshot {
    fn from(snapshot: CaptureAuthorizationSnapshot) -> Self {
        let (capture_scope, scope_stable_id) = match snapshot.capture_scope {
            CaptureScope::ExactApplication { stable_id } => ("exact-application", Some(stable_id)),
            CaptureScope::ExactInputDevice { stable_id } => ("exact-input-device", Some(stable_id)),
            CaptureScope::ExactOutputDevice { stable_id } => {
                ("exact-output-device", Some(stable_id))
            }
            CaptureScope::SystemMix => ("system-mix", None),
        };
        Self {
            capability: match snapshot.capability {
                pocketstation::CaptureCapabilityState::Available => "available",
                pocketstation::CaptureCapabilityState::Unavailable => "unavailable",
                pocketstation::CaptureCapabilityState::Unsupported => "unsupported",
            }
            .to_owned(),
            os_permission: permission_observation_name(snapshot.os_permission).to_owned(),
            application_policy: match snapshot.application_policy {
                ApplicationPolicyObservation::Allowed => "allowed",
                ApplicationPolicyObservation::Denied => "denied",
                ApplicationPolicyObservation::NotObservable => "not-observable",
                ApplicationPolicyObservation::NotApplicable => "not-applicable",
            }
            .to_owned(),
            session_grant: match snapshot.session_grant {
                CaptureSessionGrant::GrantedByExplicitSelection => "granted-by-explicit-selection",
                CaptureSessionGrant::Denied => "denied",
                CaptureSessionGrant::NotEvaluated => "not-evaluated",
            }
            .to_owned(),
            capture_scope: capture_scope.to_owned(),
            scope_stable_id,
            identity_strength: identity_strength_name(snapshot.identity_strength).to_owned(),
            permission_epoch: snapshot.permission_epoch.0,
            observed_at_ns: snapshot.observed_at_ns,
            open_outcome: match snapshot.open_outcome {
                CaptureOpenOutcome::NotAttempted => "not-attempted",
                CaptureOpenOutcome::Succeeded => "succeeded",
                CaptureOpenOutcome::PermissionDenied => "permission-denied",
                CaptureOpenOutcome::SourceUnavailable => "source-unavailable",
                CaptureOpenOutcome::BackendFailed => "backend-failed",
            }
            .to_owned(),
        }
    }
}

fn parse_source_kind(value: &str) -> PyResult<SourceKind> {
    match value {
        "application" => Ok(SourceKind::Application),
        "output-device" => Ok(SourceKind::OutputDevice),
        "input-device" => Ok(SourceKind::InputDevice),
        "system-mix" => Ok(SourceKind::SystemMix),
        _ => Err(PyValueError::new_err(coded_reason(
            "source.invalid_query",
            "source kind must be application, output-device, input-device, or system-mix",
        ))),
    }
}

fn parse_source_query(query_kind: &str, value: Option<String>) -> PyResult<SourceQuery> {
    match (query_kind, value) {
        ("any", None) => Ok(SourceQuery::Any),
        ("application", Some(value)) => {
            validate_nonempty("application query", &value)?;
            Ok(SourceQuery::App(value))
        }
        ("kind", Some(value)) => Ok(SourceQuery::ByKind(parse_source_kind(&value)?)),
        ("stable-key", Some(value)) => {
            validate_nonempty("stable source key", &value)?;
            Ok(SourceQuery::ByStableKey(value))
        }
        ("playing", None) => Ok(SourceQuery::Playing),
        ("any" | "playing", Some(_)) => Err(PyValueError::new_err(coded_reason(
            "source.invalid_query",
            "this source query does not accept a value",
        ))),
        ("application" | "kind" | "stable-key", None) => Err(PyValueError::new_err(coded_reason(
            "source.invalid_query",
            "this source query requires a value",
        ))),
        _ => Err(PyValueError::new_err(coded_reason(
            "source.invalid_query",
            "query kind must be any, application, kind, stable-key, or playing",
        ))),
    }
}

#[pyfunction(name = "discover_sources")]
#[pyo3(signature = (query_kind="any", value=None))]
fn python_discover_sources(
    query_kind: &str,
    value: Option<String>,
) -> PyResult<Vec<PythonDiscoveredSource>> {
    let query = parse_source_query(query_kind, value)?;
    Ok(
        pocketstation::resolve_query(&query, &pocketstation::discover_sources())
            .into_iter()
            .map(discovered_source)
            .collect(),
    )
}

#[pyfunction(name = "application_capture_available")]
fn python_application_capture_available() -> bool {
    pocketstation::application_capture_available()
}

#[pyfunction(name = "microphone_permission_observation")]
fn python_microphone_permission_observation() -> &'static str {
    permission_observation_name(pocketstation::microphone_permission_observation())
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonSource>()?;
    module.add_class::<PythonDiscoveredSource>()?;
    module.add_class::<PythonCaptureAuthorizationSnapshot>()?;
    module.add_class::<PythonCapturePermissionTransition>()?;
    module.add_class::<PythonCapturePermissionLifecycle>()?;
    module.add_function(wrap_pyfunction!(python_discover_sources, module)?)?;
    module.add_function(wrap_pyfunction!(
        python_application_capture_available,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        python_microphone_permission_observation,
        module
    )?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture_source() -> CaptureSource {
        CaptureSource {
            stable_id: StableSourceId::new(Platform::Linux, SourceKind::Application, "pw-app:42"),
            name: "Fixture".to_owned(),
            process_id: Some(42),
            app_id: Some("io.pocketstation.fixture".to_owned()),
            device_uid: None,
            state: SourceState::Playing,
            sample_rate_hz: 48_000,
            channels: 2,
        }
    }

    #[test]
    fn discovered_projection_preserves_identity_and_selector_truth() {
        let source = fixture_source();
        let expected_source_id = source.stable_id.source_id().get();
        let projected = discovered_source(source);
        assert_eq!(projected.platform, "linux");
        assert_eq!(projected.kind, "application");
        assert_eq!(projected.stable_key, "pw-app:42");
        assert_eq!(projected.source_id, expected_source_id);
        assert_eq!(projected.process_id, Some(42));
        assert_eq!(
            projected.application_id.as_deref(),
            Some("io.pocketstation.fixture")
        );
        assert_eq!(projected.state, "playing");
        assert_eq!(projected.identity_strength, "application-id-and-process-id");
        assert_eq!(
            projected.selector_persistence_scope.as_deref(),
            Some("application-identity")
        );
        assert_eq!(
            projected.process_tree_scope.as_deref(),
            Some("application-identity")
        );
    }

    #[test]
    fn permission_projection_keeps_every_core_state_distinct() {
        let values = [
            (PermissionObservation::Allowed, "allowed"),
            (PermissionObservation::Denied, "denied"),
            (PermissionObservation::Restricted, "restricted"),
            (PermissionObservation::NotDetermined, "not-determined"),
            (PermissionObservation::Revoked, "revoked"),
            (PermissionObservation::NotObservable, "not-observable"),
            (PermissionObservation::NotApplicable, "not-applicable"),
        ];
        for (value, expected) in values {
            assert_eq!(permission_observation_name(value), expected);
        }
    }

    #[test]
    fn authorization_snapshot_preserves_exact_pre_open_evidence() {
        let source = discovered_source(fixture_source());
        let snapshot = source
            .authorization_before_open("allowed", "allowed", "granted-by-explicit-selection", 7)
            .expect("authorization snapshot");
        assert_eq!(snapshot.capability, "available");
        assert_eq!(snapshot.os_permission, "allowed");
        assert_eq!(snapshot.application_policy, "allowed");
        assert_eq!(snapshot.capture_scope, "exact-application");
        assert_eq!(snapshot.scope_stable_id.as_deref(), Some("pw-app:42"));
        assert_eq!(snapshot.permission_epoch, 7);
        assert_eq!(snapshot.open_outcome, "not-attempted");
    }

    #[test]
    fn query_parser_rejects_missing_or_surplus_values() {
        assert!(parse_source_query("application", None).is_err());
        assert!(parse_source_query("playing", Some("unexpected".to_owned())).is_err());
        assert_eq!(
            parse_source_query("kind", Some("input-device".to_owned())).expect("typed query"),
            SourceQuery::ByKind(SourceKind::InputDevice)
        );
    }
}
