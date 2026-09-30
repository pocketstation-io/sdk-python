# Contributing

Discuss a focused developer problem in an issue, then submit a small change
with its expected behavior and relevant checks. Keep provider integrations in
examples or external packages. Rust Core owns capture, timing, routing and
recording; Python manages the application and provider code.

Use Rust 1.95 and CPython 3.11 or newer. Linux source builds need the ALSA and
PipeWire development packages. The development AEC build also requires a C++
compiler, libclang, pkg-config, Meson 1.7.2, Ninja 1.11.1.4 and the Rust
`llvm-tools` component. The bundled native engine invokes POSIX `cp` and `nm`;
Windows/MSVC support must pass the complete native matrix before publication.
From a checkout:

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check python tests examples build_backend.py tools
uv run ruff format --check python tests examples build_backend.py tools
uv run mypy python examples tests/qualification
cargo fmt --manifest-path native/Cargo.toml -- --check
cargo test --manifest-path native/Cargo.toml --all-features --locked
cargo clippy --manifest-path native/Cargo.toml --all-targets --all-features --locked -- -D warnings
```

Use the conformance-fixture build described by CI for tests that need the native
test entry points. Release wheels omit that build feature. Hardware-dependent
checks must identify their actual device and permission state.

Preserve unrelated work. Explain any API or compatibility change and update
examples and release notes. Keep credentials and captured personal audio out
of commits. Python callbacks never run on capture callbacks; native realtime
code cannot allocate, lock, block, log, panic or perform model inference.

A pull request records purpose, changed files, the developer workflow enabled,
owning components, tests, actual evidence, remaining simulated behavior and a
review decision. New placeholders must be explicit. A green component test is
not a physical-device result. Package changes must also pass isolated installed
wheel/source consumers and removal checks.

Keep dependency notices reproducible from exact source versions. See
[release operations](docs/operations/releasing.md) before changing packaging
or publication. Contributions use the repository's MIT license; third-party
code retains its own license and notices.
