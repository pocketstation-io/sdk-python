mod driver;
mod values;

pub(crate) use driver::register_operator;
pub(crate) use values::PythonOperatorManifest;

use pyo3::prelude::*;

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonOperatorManifest>()?;
    module.add_class::<values::PythonOperatorEmission>()?;
    module.add_class::<driver::PythonOperatorPrepareContext>()?;
    module.add_class::<driver::PythonOperatorPortContext>()?;
    Ok(())
}
