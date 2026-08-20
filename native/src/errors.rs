use pocketstation::{Platform, SessionStartError};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

#[allow(clippy::needless_pass_by_value)] // Direct adapter for Result::map_err.
pub(crate) fn session_error(error: pocketstation::SessionError) -> PyErr {
    PyValueError::new_err(coded_reason(
        pocketstation::session_declaration_error_code(&error).as_str(),
        error.to_string(),
    ))
}

#[allow(clippy::needless_pass_by_value)] // Direct adapter for Result::map_err.
pub(crate) fn session_endpoint_error(error: pocketstation::SessionEndpointError) -> PyErr {
    PyRuntimeError::new_err(coded_reason(
        "session.endpoint_registration_unavailable",
        error.to_string(),
    ))
}

#[allow(clippy::needless_pass_by_value)] // Direct adapter for Result::map_err.
pub(crate) fn session_start_error(error: SessionStartError) -> PyErr {
    let exception = PyRuntimeError::new_err(coded_reason(error.code().as_str(), error.to_string()));
    if let Some(diagnostic) = error.compile_diagnostic() {
        Python::attach(|py| {
            let value = exception.value(py);
            let _ = value.setattr("_pocketstation_compile_code", diagnostic.code());
            let _ = value.setattr("_pocketstation_compile_node_index", diagnostic.node_index());
            let _ = value.setattr("_pocketstation_compile_edge_index", diagnostic.edge_index());
            let _ = value.setattr(
                "_pocketstation_compile_operator_id",
                diagnostic.operator_id(),
            );
            let _ = value.setattr(
                "_pocketstation_compile_operator_instance_id",
                diagnostic.operator_instance_id(),
            );
            let _ = value.setattr(
                "_pocketstation_compile_node_type_id",
                diagnostic.node_type_id(),
            );
            let _ = value.setattr(
                "_pocketstation_compile_source_type_id",
                diagnostic.source_type_id(),
            );
            let _ = value.setattr("_pocketstation_compile_port_name", diagnostic.port_name());
            let _ = value.setattr("_pocketstation_compile_direction", diagnostic.direction());
            let _ = value.setattr("_pocketstation_compile_expected", diagnostic.expected());
            let _ = value.setattr("_pocketstation_compile_actual", diagnostic.actual());
        });
    }
    exception
}

#[allow(clippy::needless_pass_by_value)] // Direct adapter for Result::map_err.
pub(crate) fn native_extension_error(
    error: pocketstation::native_extension::NativeExtensionLibraryError,
) -> PyErr {
    use pocketstation::native_extension::NativeExtensionLibraryErrorCode;

    let code = match error.code() {
        NativeExtensionLibraryErrorCode::PathNotAbsolute => "extension.path_not_absolute",
        NativeExtensionLibraryErrorCode::PathCanonicalizationFailed => {
            "extension.path_canonicalization_failed"
        }
        NativeExtensionLibraryErrorCode::PathNotFile => "extension.path_not_file",
        NativeExtensionLibraryErrorCode::LibraryLoadFailed => "extension.library_load_failed",
        NativeExtensionLibraryErrorCode::EntrypointMissing => "extension.entrypoint_missing",
        NativeExtensionLibraryErrorCode::EntrypointPanicked => "extension.entrypoint_panicked",
        NativeExtensionLibraryErrorCode::EntrypointFailed => "extension.entrypoint_failed",
        NativeExtensionLibraryErrorCode::UnsupportedAbiMajor => "extension.unsupported_abi_major",
        NativeExtensionLibraryErrorCode::UnsupportedAbiMinor => "extension.unsupported_abi_minor",
        NativeExtensionLibraryErrorCode::InvalidLibraryDescriptor => {
            "extension.invalid_library_descriptor"
        }
        NativeExtensionLibraryErrorCode::RegistrationAcquisitionPanicked => {
            "extension.registration_acquisition_panicked"
        }
        NativeExtensionLibraryErrorCode::RegistrationAcquisitionFailed => {
            "extension.registration_acquisition_failed"
        }
        NativeExtensionLibraryErrorCode::InvalidRegistration => "extension.invalid_registration",
        NativeExtensionLibraryErrorCode::DuplicateRegistration => {
            "extension.duplicate_registration"
        }
        NativeExtensionLibraryErrorCode::RegistrationStateUnavailable => {
            "extension.registration_state_unavailable"
        }
    };
    PyRuntimeError::new_err(coded_reason(code, error.to_string()))
}

pub(crate) fn coded_reason(code: &str, reason: impl AsRef<str>) -> String {
    format!("[{code}] {}", reason.as_ref())
}

pub(crate) fn validate_nonempty(label: &str, value: &str) -> PyResult<()> {
    if value.trim().is_empty() {
        return Err(PyValueError::new_err(coded_reason(
            "session.invalid_selector",
            format!("{label} must not be empty"),
        )));
    }
    Ok(())
}

pub(crate) fn validate_process_id(process_id: u32) -> PyResult<()> {
    if process_id == 0 {
        return Err(PyValueError::new_err(coded_reason(
            "session.invalid_selector",
            "application process ID must be non-zero",
        )));
    }
    Ok(())
}

pub(crate) fn parse_platform(value: &str) -> PyResult<Platform> {
    match value.trim().to_ascii_lowercase().as_str() {
        "macos" => Ok(Platform::Macos),
        "windows" => Ok(Platform::Windows),
        "linux" => Ok(Platform::Linux),
        "ios" => Ok(Platform::Ios),
        "android" => Ok(Platform::Android),
        "web" => Ok(Platform::Web),
        "unknown" => Ok(Platform::Unknown),
        _ => Err(PyValueError::new_err(coded_reason(
            "session.invalid_selector",
            "platform must be macos, windows, linux, ios, android, web, or unknown",
        ))),
    }
}
