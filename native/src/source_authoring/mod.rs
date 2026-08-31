mod driver;
mod values;

pub(crate) use driver::{register_source, PythonRegisteredSource};
pub(crate) use values::{PythonSourceEmission, PythonSourceManifest};

use pyo3::prelude::*;

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonSourceManifest>()?;
    module.add_class::<PythonSourceEmission>()?;
    module.add_class::<driver::PythonSourcePrepareContext>()?;
    module.add_class::<driver::PythonSourceOutputIdentity>()?;
    module.add_class::<driver::PythonSourceCancellation>()?;
    module.add_class::<PythonRegisteredSource>()?;
    Ok(())
}
