#![allow(clippy::redundant_pub_crate)]

pub(crate) mod audio_input;
pub(crate) mod connector;
pub(crate) mod errors;
pub(crate) mod extensions;
pub(crate) mod graph;
pub(crate) mod observations;
pub(crate) mod relay;
pub(crate) mod session;
pub(crate) mod sidecar;
pub(crate) mod signals;
pub(crate) mod sources;
pub(crate) mod streams;

use pyo3::prelude::*;

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    audio_input::register(module)?;
    connector::register(module)?;
    extensions::register(module)?;
    sources::register(module)?;
    graph::register(module)?;
    signals::register(module)?;
    sidecar::register(module)?;
    relay::register(module)?;
    streams::register(module)?;
    observations::register(module)?;
    session::register(module)?;
    Ok(())
}
