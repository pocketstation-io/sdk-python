# Find the Python API for a task

Use the package root for capture and Session lifecycle. Import advanced graph,
provider, Relay, and diagnostic contracts from the module that owns them.

## Start and stop a Session

| Task | API |
|---|---|
| Capture one application | `pocketstation.capture` |
| Declare a synchronous Session | `pocketstation.Session` |
| Declare an asyncio Session | `pocketstation.aio.Session` |
| Select a source | `pocketstation.Source` |
| Discover running sources | `pocketstation.discover_sources` |
| Feed application-owned PCM | `Session.audio_input` |

`capture()` is the short path. Use `Session` when you need more than one
destination, custom route policies, provider composition, Relay, or detailed
observations. Both paths use the same Rust engine.

## Compose and route media

| Task | Module |
|---|---|
| Stems, ports, and routes | `pocketstation.graph` |
| Typed signals and subscriptions | `pocketstation.signal` |
| Source declarations and discovery | `pocketstation.sources` |
| Application-owned PCM | `pocketstation.audio_input` |
| Runtime events, metrics, and outcomes | `pocketstation.observations` |

## Connect external systems

| Task | Module |
|---|---|
| Publish through Relay | `pocketstation.relay` or `pocketstation.aio.relay` |
| Author an outbound Connector | `pocketstation.connector` |
| Author a computation | `pocketstation.operator_authoring` |
| Author an inbound Source | `pocketstation.source_authoring` |
| Author a lower-level Endpoint | `pocketstation.endpoint_authoring` |
| Run a managed process | `pocketstation.sidecar` |
| Load a trusted native extension | `pocketstation.extensions` |

Provider callbacks run on bounded off-realtime workers. Native capture
callbacks never call Python.

## Build a voice workflow

`pocketstation.voice` contains the provider-neutral contracts.
`pocketstation.aio.Session.conversation()` composes either:

- a `StreamingTranscriber`, `ResponseModel`, and `SpeechSynthesizer`, with an
  optional `SpeechDetector`; or
- one `DuplexVoiceModel`.

Provider implementations remain in example or separately installed provider
packages. Read [Compose a bounded voice workflow](../guides/voice.md) before
depending on interruption or playout observations.

## Handle failures

Start with `PocketStationError`, `CaptureError`, and `SessionError` from the
package root. Advanced modules expose errors for their own boundary. Preserve
the structured error and inspect the Session outcome before retrying.

Continue with [Session ownership, bounds, and shutdown](../concepts/session-and-bounds.md)
or [troubleshooting](../troubleshooting.md).
