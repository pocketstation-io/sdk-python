# Support

Use [GitHub issues](https://github.com/pocketstation-io/sdk-python/issues) for
bugs and documentation questions. Include the installed version, Python and
OS versions, CPU architecture, a minimal generated-input reproduction and
redacted error output. For security reports, follow [SECURITY.md](SECURITY.md).

The native runtime is tested with CPython 3.11–3.14 on macOS Apple silicon and
Intel, Linux glibc x86-64 and ARM64, and Windows x86-64. Windows ARM64 is tested
with CPython 3.13–3.14. Musl, PyPy and free-threaded CPython are unqualified.
See [platform operations](docs/operations/platform-support.md) for capture
permissions and the separate device evidence.

An ABI3 tag specifies binary compatibility; it is not evidence that every older
OS, interpreter build or physical device was tested. Package tests execute
Sessions with application-owned PCM. They do not establish physical capture,
device latency, WAN or TURN performance.

Demonstration services are rate-limited, have no availability SLA, and may run
an older service revision. Self-host compatible services when you need control
over deployment. Installed SDK support does not establish that a hosted service
has deployed the same invitation or authorization features.

Compatibility values are available through `pocketstation.compatibility`.
Version 0.1.5 uses Core 1.1.11 and Relay Connector 0.1.5. Prefer exact version
pins for reproducible applications; review release notes before upgrading.
Maintainer support is best effort. There is no paid support or response-time
commitment attached to this package.

The unreleased source candidate pins Core 1.1.12 for the microphone timestamp
correction. Published 0.1.5 remains unchanged; consult the Unreleased release
notes before building this candidate.
