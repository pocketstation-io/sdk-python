use std::time::Duration;

use pocketstation::connector::ConnectorCapability;
use pocketstation::connector::{
    ConnectorConfiguration, ConnectorConfigurationConstraint, ConnectorConfigurationField,
    ConnectorConfigurationRequirement, ConnectorConfigurationSchema, ConnectorConfigurationValue,
    ConnectorConfigurationValueKind, ConnectorManifest, ConnectorReadinessPolicy,
    ConnectorRequirement, ConnectorSecret,
};
use pocketstation::{
    ExecutionPartition, NodeDescriptor, NodeTypeId, OperatorId, PortDirection, SafetyContract,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::errors::coded_reason;
use crate::graph::PythonPortSpec;

fn invalid_connector(reason: impl Into<String>) -> PyErr {
    PyValueError::new_err(coded_reason("connector.invalid_contract", reason.into()))
}

#[pyclass(name = "_ConnectorConfigurationValue", frozen)]
#[derive(Clone)]
pub(crate) struct PythonConnectorConfigurationValue {
    pub(crate) value: ConnectorConfigurationValue,
}

#[pymethods]
impl PythonConnectorConfigurationValue {
    #[staticmethod]
    fn text(value: String) -> Self {
        Self {
            value: ConnectorConfigurationValue::Text(value),
        }
    }

    #[staticmethod]
    fn boolean(value: bool) -> Self {
        Self {
            value: ConnectorConfigurationValue::Boolean(value),
        }
    }

    #[staticmethod]
    fn signed_integer(value: i64) -> Self {
        Self {
            value: ConnectorConfigurationValue::SignedInteger(value),
        }
    }

    #[staticmethod]
    fn unsigned_integer(value: u64) -> Self {
        Self {
            value: ConnectorConfigurationValue::UnsignedInteger(value),
        }
    }

    #[staticmethod]
    fn duration_milliseconds(value: u64) -> Self {
        Self {
            value: ConnectorConfigurationValue::DurationMilliseconds(value),
        }
    }

    #[staticmethod]
    fn byte_count(value: u64) -> Self {
        Self {
            value: ConnectorConfigurationValue::ByteCount(value),
        }
    }

    #[staticmethod]
    fn secret(value: String) -> PyResult<Self> {
        ConnectorSecret::new(value)
            .map(|value| Self {
                value: ConnectorConfigurationValue::Secret(value),
            })
            .map_err(|error| invalid_connector(error.to_string()))
    }

    #[getter]
    fn kind(&self) -> &'static str {
        kind_name(self.value.kind())
    }

    fn expose_secret(&self) -> PyResult<String> {
        match &self.value {
            ConnectorConfigurationValue::Secret(value) => Ok(value.expose_secret().to_owned()),
            _ => Err(PyValueError::new_err(coded_reason(
                "connector.configuration.not_secret",
                "only a secret connector value can be exposed",
            ))),
        }
    }

    fn as_text(&self) -> Option<String> {
        match &self.value {
            ConnectorConfigurationValue::Text(value) => Some(value.clone()),
            _ => None,
        }
    }

    fn as_boolean(&self) -> Option<bool> {
        match &self.value {
            ConnectorConfigurationValue::Boolean(value) => Some(*value),
            _ => None,
        }
    }

    fn as_signed_integer(&self) -> Option<i64> {
        match &self.value {
            ConnectorConfigurationValue::SignedInteger(value) => Some(*value),
            _ => None,
        }
    }

    fn as_unsigned_integer(&self) -> Option<u64> {
        match &self.value {
            ConnectorConfigurationValue::UnsignedInteger(value)
            | ConnectorConfigurationValue::DurationMilliseconds(value)
            | ConnectorConfigurationValue::ByteCount(value) => Some(*value),
            _ => None,
        }
    }

    fn __repr__(&self) -> String {
        match &self.value {
            ConnectorConfigurationValue::Secret(_) => {
                "ConnectorConfigurationValue.secret(<redacted>)".to_owned()
            }
            _ => format!(
                "ConnectorConfigurationValue.{}(...)",
                kind_name(self.value.kind())
            ),
        }
    }
}

#[pyclass(name = "_ConnectorConfigurationConstraint", frozen)]
#[derive(Clone)]
pub(crate) struct PythonConnectorConfigurationConstraint {
    value: ConnectorConfigurationConstraint,
}

#[pymethods]
impl PythonConnectorConfigurationConstraint {
    #[staticmethod]
    fn non_empty() -> Self {
        Self {
            value: ConnectorConfigurationConstraint::NonEmpty,
        }
    }

    #[staticmethod]
    fn text_length_bytes(minimum: usize, maximum: usize) -> Self {
        Self {
            value: ConnectorConfigurationConstraint::TextLengthBytes { minimum, maximum },
        }
    }

    #[staticmethod]
    fn signed_range(minimum: i64, maximum: i64) -> Self {
        Self {
            value: ConnectorConfigurationConstraint::SignedRange { minimum, maximum },
        }
    }

    #[staticmethod]
    fn unsigned_range(minimum: u64, maximum: u64) -> Self {
        Self {
            value: ConnectorConfigurationConstraint::UnsignedRange { minimum, maximum },
        }
    }

    #[staticmethod]
    fn one_of(values: Vec<String>) -> Self {
        Self {
            value: ConnectorConfigurationConstraint::OneOf(values),
        }
    }
}

#[pyclass(name = "_ConnectorConfigurationField", frozen)]
#[derive(Clone)]
pub(crate) struct PythonConnectorConfigurationField {
    value: ConnectorConfigurationField,
}

#[pymethods]
impl PythonConnectorConfigurationField {
    #[new]
    #[pyo3(signature = (name, kind, requirement, documentation, default=None, constraints=Vec::new(), deprecation=None))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        py: Python<'_>,
        name: String,
        kind: String,
        requirement: String,
        documentation: String,
        default: Option<Py<PythonConnectorConfigurationValue>>,
        constraints: Vec<Py<PythonConnectorConfigurationConstraint>>,
        deprecation: Option<String>,
    ) -> PyResult<Self> {
        let kind = parse_kind(&kind)?;
        let has_default = default.is_some();
        let requirement = match requirement.as_str() {
            "required" => ConnectorConfigurationRequirement::Required,
            "optional" => ConnectorConfigurationRequirement::Optional,
            "default" => ConnectorConfigurationRequirement::Default(
                default
                    .ok_or_else(|| invalid_connector("default requirement needs a value"))?
                    .borrow(py)
                    .value
                    .clone(),
            ),
            _ => return Err(invalid_connector("configuration requirement is invalid")),
        };
        if !matches!(requirement, ConnectorConfigurationRequirement::Default(_)) && has_default {
            return Err(invalid_connector(
                "only a default field can provide a default value",
            ));
        }
        let mut value = ConnectorConfigurationField::new(name, kind, requirement, documentation);
        for constraint in constraints {
            value = value.with_constraint(constraint.borrow(py).value.clone());
        }
        if let Some(message) = deprecation {
            value = value.deprecated(message);
        }
        Ok(Self { value })
    }
}

#[pyclass(name = "_ConnectorConfigurationSchema", frozen)]
#[derive(Clone)]
pub(crate) struct PythonConnectorConfigurationSchema {
    pub(crate) value: ConnectorConfigurationSchema,
}

#[pymethods]
impl PythonConnectorConfigurationSchema {
    #[new]
    #[pyo3(signature = (revision=1, fields=Vec::new()))]
    fn new(
        py: Python<'_>,
        revision: u32,
        fields: Vec<Py<PythonConnectorConfigurationField>>,
    ) -> PyResult<Self> {
        let fields = fields
            .iter()
            .map(|field| field.borrow(py).value.clone())
            .collect();
        ConnectorConfigurationSchema::new(revision, fields)
            .map(|value| Self { value })
            .map_err(|error| invalid_connector(error.to_string()))
    }
}

#[pyclass(name = "_ConnectorConfiguration", frozen)]
#[derive(Clone, Default)]
pub(crate) struct PythonConnectorConfiguration {
    pub(crate) value: ConnectorConfiguration,
}

#[pymethods]
impl PythonConnectorConfiguration {
    #[new]
    #[pyo3(signature = (entries=Vec::new()))]
    fn new(py: Python<'_>, entries: Vec<(String, Py<PythonConnectorConfigurationValue>)>) -> Self {
        let mut value = ConnectorConfiguration::new();
        for (name, entry) in entries {
            value.insert(name, entry.borrow(py).value.clone());
        }
        Self { value }
    }
}

#[pyclass(name = "_ConnectorManifest", frozen)]
#[derive(Clone)]
pub(crate) struct PythonConnectorManifest {
    pub(crate) value: ConnectorManifest,
}

#[pymethods]
impl PythonConnectorManifest {
    #[new]
    #[pyo3(signature = (operator_id, node_type_id, package_version, inputs, configuration, manifest_revision=1, startup_timeout_ms=5_000, probe_interval_ms=100, success_threshold=1, failure_threshold=1, capabilities=Vec::new(), requirements=Vec::new()))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        py: Python<'_>,
        operator_id: String,
        node_type_id: String,
        package_version: String,
        inputs: Vec<Py<PythonPortSpec>>,
        configuration: &PythonConnectorConfigurationSchema,
        manifest_revision: u32,
        startup_timeout_ms: u64,
        probe_interval_ms: u64,
        success_threshold: u32,
        failure_threshold: u32,
        capabilities: Vec<(String, String)>,
        requirements: Vec<(String, bool, String)>,
    ) -> PyResult<Self> {
        let inputs = inputs
            .iter()
            .map(|port| port.borrow(py).value.clone())
            .collect::<Vec<_>>();
        if inputs
            .iter()
            .any(|port| port.direction() != PortDirection::Input)
        {
            return Err(invalid_connector(
                "connector manifest ports must all be inputs",
            ));
        }
        let node = NodeDescriptor::new(
            NodeTypeId::from(node_type_id.as_str()),
            "Python Connector",
            inputs,
            Vec::new(),
            ExecutionPartition::AsyncWorker,
            SafetyContract::AllocationAllowed,
            true,
        )
        .map_err(|error| invalid_connector(error.to_string()))?;
        let readiness = ConnectorReadinessPolicy::new(
            Duration::from_millis(startup_timeout_ms),
            Duration::from_millis(probe_interval_ms),
            success_threshold,
            failure_threshold,
        )
        .map_err(|error| invalid_connector(error.to_string()))?;
        let mut manifest = ConnectorManifest::new(
            manifest_revision,
            OperatorId::new(operator_id),
            package_version,
            node,
            configuration.value.clone(),
            readiness,
        )
        .map_err(|error| invalid_connector(error.to_string()))?;
        for (id, documentation) in capabilities {
            let capability = ConnectorCapability::new(id, documentation)
                .map_err(|error| invalid_connector(error.to_string()))?;
            manifest = manifest.with_capability(capability);
        }
        for (id, required, documentation) in requirements {
            let requirement = ConnectorRequirement::new(id, required, documentation)
                .map_err(|error| invalid_connector(error.to_string()))?;
            manifest = manifest.with_requirement(requirement);
        }
        manifest
            .validate()
            .map(|()| Self { value: manifest })
            .map_err(|error| invalid_connector(error.to_string()))
    }
}

pub(crate) fn configuration_values(
    configuration: &pocketstation::connector::ResolvedConnectorConfiguration,
) -> Vec<(String, PythonConnectorConfigurationValue)> {
    configuration
        .iter()
        .map(|(name, value)| {
            (
                name.to_owned(),
                PythonConnectorConfigurationValue {
                    value: value.clone(),
                },
            )
        })
        .collect()
}

fn parse_kind(value: &str) -> PyResult<ConnectorConfigurationValueKind> {
    match value {
        "text" => Ok(ConnectorConfigurationValueKind::Text),
        "boolean" => Ok(ConnectorConfigurationValueKind::Boolean),
        "signed-integer" => Ok(ConnectorConfigurationValueKind::SignedInteger),
        "unsigned-integer" => Ok(ConnectorConfigurationValueKind::UnsignedInteger),
        "duration-milliseconds" => Ok(ConnectorConfigurationValueKind::DurationMilliseconds),
        "byte-count" => Ok(ConnectorConfigurationValueKind::ByteCount),
        "secret" => Ok(ConnectorConfigurationValueKind::Secret),
        _ => Err(invalid_connector("connector configuration kind is invalid")),
    }
}

const fn kind_name(value: ConnectorConfigurationValueKind) -> &'static str {
    match value {
        ConnectorConfigurationValueKind::Text => "text",
        ConnectorConfigurationValueKind::Boolean => "boolean",
        ConnectorConfigurationValueKind::SignedInteger => "signed-integer",
        ConnectorConfigurationValueKind::UnsignedInteger => "unsigned-integer",
        ConnectorConfigurationValueKind::DurationMilliseconds => "duration-milliseconds",
        ConnectorConfigurationValueKind::ByteCount => "byte-count",
        ConnectorConfigurationValueKind::Secret => "secret",
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonConnectorConfigurationValue>()?;
    module.add_class::<PythonConnectorConfigurationConstraint>()?;
    module.add_class::<PythonConnectorConfigurationField>()?;
    module.add_class::<PythonConnectorConfigurationSchema>()?;
    module.add_class::<PythonConnectorConfiguration>()?;
    module.add_class::<PythonConnectorManifest>()?;
    Ok(())
}
