use std::mem::size_of;
use std::path::PathBuf;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use crate::errors::coded_reason;

#[repr(C)]
#[derive(Clone, Copy)]
struct RawStatus {
    code: u32,
    detail: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct RawUtf8 {
    data: *const u8,
    len_bytes: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct RawAbiVersion {
    struct_size_bytes: u32,
    abi_major: u16,
    abi_minor: u16,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct RawDescriptor {
    struct_size_bytes: u32,
    abi_major: u16,
    abi_minor: u16,
    kind: u32,
    revision: u32,
    generation: u32,
    port_count: u32,
    extension_id: RawUtf8,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct RawPort {
    struct_size_bytes: u32,
    abi_major: u16,
    abi_minor: u16,
    direction: u32,
    required: u32,
    name: RawUtf8,
    signal_id: RawUtf8,
    semantic_role: RawUtf8,
    schema: RawUtf8,
}

unsafe extern "C" {
    fn pks_extension_abi_get_version(output_version: *mut RawAbiVersion) -> RawStatus;
    fn pks_extension_abi_is_compatible(
        requested_abi_major: u16,
        requested_abi_minor: u16,
        requested_struct_size_bytes: u32,
    ) -> RawStatus;
    fn pks_extension_descriptor_validate(
        descriptor: *const RawDescriptor,
        ports: *const RawPort,
        port_count: u32,
    ) -> RawStatus;
}

#[pyclass(name = "_ExtensionAbiVersion", frozen)]
struct PythonExtensionAbiVersion {
    #[pyo3(get)]
    struct_size_bytes: u32,
    #[pyo3(get)]
    abi_major: u16,
    #[pyo3(get)]
    abi_minor: u16,
}

#[pyclass(name = "_NativeExtensionRegistration", frozen)]
#[derive(Clone)]
pub(crate) struct PythonNativeExtensionRegistration {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    kind: &'static str,
    #[pyo3(get)]
    revision: u32,
    #[pyo3(get)]
    generation: u32,
}

#[pyclass(name = "_NativeExtensionLibrary", frozen)]
pub(crate) struct PythonNativeExtensionLibrary {
    #[pyo3(get)]
    canonical_path: PathBuf,
    registrations: Vec<PythonNativeExtensionRegistration>,
}

#[pymethods]
impl PythonNativeExtensionLibrary {
    #[getter]
    fn registrations(&self) -> Vec<PythonNativeExtensionRegistration> {
        self.registrations.clone()
    }
}

impl From<pocketstation::native_extension::NativeExtensionLibrary>
    for PythonNativeExtensionLibrary
{
    fn from(value: pocketstation::native_extension::NativeExtensionLibrary) -> Self {
        let registrations = value
            .registrations()
            .iter()
            .map(|registration| PythonNativeExtensionRegistration {
                id: registration.id().to_owned(),
                kind: match registration.kind() {
                    pocketstation::native_extension::NativeExtensionKind::Source => "source",
                    pocketstation::native_extension::NativeExtensionKind::Operator => "operator",
                    pocketstation::native_extension::NativeExtensionKind::Endpoint => "endpoint",
                },
                revision: registration.revision(),
                generation: registration.generation(),
            })
            .collect();
        Self {
            canonical_path: value.canonical_path().to_owned(),
            registrations,
        }
    }
}

#[pyfunction]
fn extension_abi_version() -> PyResult<PythonExtensionAbiVersion> {
    let mut version = RawAbiVersion {
        struct_size_bytes: 0,
        abi_major: 0,
        abi_minor: 0,
    };
    // SAFETY: version is one writable, aligned current-process record.
    let status = unsafe { pks_extension_abi_get_version(&raw mut version) };
    check_status(status)?;
    Ok(PythonExtensionAbiVersion {
        struct_size_bytes: version.struct_size_bytes,
        abi_major: version.abi_major,
        abi_minor: version.abi_minor,
    })
}

#[pyfunction]
fn extension_abi_is_compatible(
    abi_major: u16,
    abi_minor: u16,
    struct_size_bytes: u32,
) -> PyResult<()> {
    // SAFETY: this ABI function accepts values only and retains no memory.
    let status =
        unsafe { pks_extension_abi_is_compatible(abi_major, abi_minor, struct_size_bytes) };
    check_status(status)
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn validate_extension_descriptor(
    extension_id: String,
    kind: String,
    revision: u32,
    generation: u32,
    abi_major: u16,
    abi_minor: u16,
    ports: Vec<(String, String, bool, String, String, String)>,
) -> PyResult<()> {
    let port_count = u32::try_from(ports.len()).map_err(|_| {
        PyValueError::new_err(coded_reason(
            "extension.invalid_descriptor",
            "port count exceeds the extension ABI range",
        ))
    })?;
    let raw_ports = ports
        .iter()
        .map(
            |(name, direction, required, signal_id, semantic_role, schema)| {
                Ok(RawPort {
                    struct_size_bytes: size_of::<RawPort>() as u32,
                    abi_major,
                    abi_minor,
                    direction: parse_direction(direction)?,
                    required: u32::from(*required),
                    name: raw_utf8(name)?,
                    signal_id: raw_utf8(signal_id)?,
                    semantic_role: raw_utf8(semantic_role)?,
                    schema: raw_utf8(schema)?,
                })
            },
        )
        .collect::<PyResult<Vec<_>>>()?;
    let descriptor = RawDescriptor {
        struct_size_bytes: size_of::<RawDescriptor>() as u32,
        abi_major,
        abi_minor,
        kind: parse_kind(&kind)?,
        revision,
        generation,
        port_count,
        extension_id: raw_utf8(&extension_id)?,
    };
    // SAFETY: all records and UTF-8 byte strings remain alive and readable for
    // this synchronous validation call, which copies and retains no memory.
    let status = unsafe {
        pks_extension_descriptor_validate(&raw const descriptor, raw_ports.as_ptr(), port_count)
    };
    check_status(status)
}

fn raw_utf8(value: &str) -> PyResult<RawUtf8> {
    let len_bytes = u32::try_from(value.len()).map_err(|_| {
        PyValueError::new_err(coded_reason(
            "extension.invalid_descriptor",
            "extension text exceeds the ABI range",
        ))
    })?;
    Ok(RawUtf8 {
        data: value.as_ptr(),
        len_bytes,
    })
}

fn parse_kind(value: &str) -> PyResult<u32> {
    match value {
        "source" => Ok(1),
        "operator" => Ok(2),
        "endpoint" => Ok(3),
        _ => Err(PyValueError::new_err(coded_reason(
            "extension.invalid_descriptor",
            "kind must be source, operator, or endpoint",
        ))),
    }
}

fn parse_direction(value: &str) -> PyResult<u32> {
    match value {
        "input" => Ok(1),
        "output" => Ok(2),
        _ => Err(PyValueError::new_err(coded_reason(
            "extension.invalid_descriptor",
            "port direction must be input or output",
        ))),
    }
}

fn check_status(status: RawStatus) -> PyResult<()> {
    if status.code == 0 {
        return Ok(());
    }
    let (code, reason) = match status.code {
        1 => (
            "extension.null_argument",
            "the native ABI received a null pointer",
        ),
        3 => (
            "extension.unsupported_abi_major",
            "unsupported extension ABI major",
        ),
        4 => (
            "extension.invalid_struct_size",
            "invalid extension ABI struct size",
        ),
        8 => (
            "extension.internal_panic",
            "native extension ABI trapped a panic",
        ),
        9 => (
            "extension.misaligned_pointer",
            "misaligned extension ABI pointer",
        ),
        10 => (
            "extension.invalid_descriptor",
            "invalid extension descriptor or ports",
        ),
        17 => (
            "extension.unsupported_abi_minor",
            "unsupported extension ABI minor",
        ),
        _ => (
            "extension.abi_error",
            "native extension ABI rejected the request",
        ),
    };
    Err(PyRuntimeError::new_err(coded_reason(
        code,
        format!("{reason} (detail={})", status.detail),
    )))
}

#[cfg(feature = "conformance-fixtures")]
#[pyclass(name = "ExtensionConformanceReport", frozen)]
struct PythonExtensionConformanceReport {
    #[pyo3(get)]
    signal_id: String,
    #[pyo3(get)]
    schema_id: String,
    #[pyo3(get)]
    role_id: String,
    #[pyo3(get)]
    source_type_id: String,
    #[pyo3(get)]
    operator_id: String,
    #[pyo3(get)]
    endpoint_id: String,
    #[pyo3(get)]
    input_payload: String,
    #[pyo3(get)]
    output_payload: String,
    #[pyo3(get)]
    failure_requested: bool,
    #[pyo3(get)]
    source_prepared_total: u64,
    #[pyo3(get)]
    source_emitted_total: u64,
    #[pyo3(get)]
    source_closed_total: u64,
    #[pyo3(get)]
    operator_prepared_total: u64,
    #[pyo3(get)]
    operator_processed_total: u64,
    #[pyo3(get)]
    operator_output_total: u64,
    #[pyo3(get)]
    operator_failure_total: u64,
    #[pyo3(get)]
    operator_closed_total: u64,
    #[pyo3(get)]
    endpoint_prepared_total: u64,
    #[pyo3(get)]
    endpoint_received_total: u64,
    #[pyo3(get)]
    endpoint_stopped_total: u64,
    #[pyo3(get)]
    endpoint_finalized_total: u64,
    #[pyo3(get)]
    lifecycle_event_total: u64,
    #[pyo3(get)]
    terminal_event_total: u64,
    #[pyo3(get)]
    queue_capacity_signals: u64,
    #[pyo3(get)]
    queue_peak_signals: u64,
    #[pyo3(get)]
    route_capacity_signals: u64,
    #[pyo3(get)]
    route_peak_signals: u64,
    #[pyo3(get)]
    route_delivered_total: u64,
    #[pyo3(get)]
    maximum_buffered_payload_bytes: u64,
    #[pyo3(get)]
    stop_success: bool,
}

#[cfg(feature = "conformance-fixtures")]
#[pyfunction]
fn run_extension_conformance(
    failure_requested: bool,
) -> PyResult<PythonExtensionConformanceReport> {
    let report = pocketstation::conformance::run_extension_vector(failure_requested)
        .map_err(PyRuntimeError::new_err)?;
    Ok(PythonExtensionConformanceReport {
        signal_id: report.signal_id.to_owned(),
        schema_id: report.schema_id.to_owned(),
        role_id: report.role_id.to_owned(),
        source_type_id: report.source_type_id.to_owned(),
        operator_id: report.operator_id.to_owned(),
        endpoint_id: report.endpoint_id.to_owned(),
        input_payload: report.input_payload.to_owned(),
        output_payload: report.output_payload.to_owned(),
        failure_requested: report.failure_requested,
        source_prepared_total: report.source_prepared_total,
        source_emitted_total: report.source_emitted_total,
        source_closed_total: report.source_closed_total,
        operator_prepared_total: report.operator_prepared_total,
        operator_processed_total: report.operator_processed_total,
        operator_output_total: report.operator_output_total,
        operator_failure_total: report.operator_failure_total,
        operator_closed_total: report.operator_closed_total,
        endpoint_prepared_total: report.endpoint_prepared_total,
        endpoint_received_total: report.endpoint_received_total,
        endpoint_stopped_total: report.endpoint_stopped_total,
        endpoint_finalized_total: report.endpoint_finalized_total,
        lifecycle_event_total: report.lifecycle_event_total,
        terminal_event_total: report.terminal_event_total,
        queue_capacity_signals: report.queue_capacity_signals,
        queue_peak_signals: report.queue_peak_signals,
        route_capacity_signals: report.route_capacity_signals,
        route_peak_signals: report.route_peak_signals,
        route_delivered_total: report.route_delivered_total,
        maximum_buffered_payload_bytes: report.maximum_buffered_payload_bytes,
        stop_success: report.stop_success,
    })
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonExtensionAbiVersion>()?;
    module.add_class::<PythonNativeExtensionRegistration>()?;
    module.add_class::<PythonNativeExtensionLibrary>()?;
    module.add_function(wrap_pyfunction!(extension_abi_version, module)?)?;
    module.add_function(wrap_pyfunction!(extension_abi_is_compatible, module)?)?;
    module.add_function(wrap_pyfunction!(validate_extension_descriptor, module)?)?;
    #[cfg(feature = "conformance-fixtures")]
    {
        module.add_class::<PythonExtensionConformanceReport>()?;
        module.add_function(wrap_pyfunction!(run_extension_conformance, module)?)?;
    }
    Ok(())
}
