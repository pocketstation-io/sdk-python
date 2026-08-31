mod driver;
mod observations;
mod values;
mod worker;

use pyo3::prelude::*;

pub(crate) use driver::{declare_connector, register_connector, PythonRegisteredConnector};
pub(crate) use values::{PythonConnectorConfiguration, PythonConnectorManifest};
pub(crate) use worker::register_worker_connector;

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    values::register(module)?;
    observations::register(module)?;
    driver::register(module)?;
    Ok(())
}
