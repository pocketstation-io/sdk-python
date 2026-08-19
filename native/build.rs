use std::env;
use std::ffi::OsString;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-env-changed=PYO3_PYTHON");
    println!("cargo:rerun-if-env-changed=VIRTUAL_ENV");
    println!("cargo:rerun-if-env-changed=CONDA_PREFIX");

    if env::var_os("CARGO_CFG_TARGET_OS").as_deref() != Some("macos".as_ref()) {
        return;
    }

    let Some(python) = selected_python() else {
        return;
    };
    let Ok(output) = Command::new(python)
        .args([
            "-c",
            "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')",
        ])
        .output()
    else {
        return;
    };
    if !output.status.success() {
        return;
    }

    let Ok(directory) = String::from_utf8(output.stdout) else {
        return;
    };
    let directory = PathBuf::from(directory.trim());
    if directory.as_os_str().is_empty() || !contains_python_dylib(&directory) {
        return;
    }

    println!("cargo:rustc-link-arg=-Wl,-rpath,{}", directory.display());
}

fn selected_python() -> Option<OsString> {
    if let Some(python) = env::var_os("PYO3_PYTHON") {
        return Some(python);
    }
    for environment in ["VIRTUAL_ENV", "CONDA_PREFIX"] {
        if let Some(prefix) = env::var_os(environment) {
            let python = PathBuf::from(prefix).join("bin/python");
            if python.is_file() {
                return Some(python.into_os_string());
            }
        }
    }
    let workspace_python = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()?
        .join(".venv/bin/python");
    if workspace_python.is_file() {
        return Some(workspace_python.into_os_string());
    }
    Some(OsString::from("python3"))
}

fn contains_python_dylib(directory: &Path) -> bool {
    let Ok(entries) = fs::read_dir(directory) else {
        return false;
    };
    entries.filter_map(Result::ok).any(|entry| {
        let name = entry.file_name();
        let name = name.to_string_lossy();
        name.starts_with("libpython") && name.ends_with(".dylib")
    })
}
