# Find the Python API for a task

Use the package root for capture and Session lifecycle. Import advanced graph,
provider, Relay, and diagnostic APIs from the module that implements them.

## Start and stop a Session

| Task | API |
|---|---|
| Capture one application | `pocketstation.capture` |
| Capture all desktop output | `Session.capture(Source.system_audio())` |
| Declare a synchronous Session | `pocketstation.Session` |
| Declare an asyncio Session | `pocketstation.aio.Session` |
| Select a source | `pocketstation.Source` |
| Discover running sources | `pocketstation.discover_sources` |
| Feed application-owned PCM | `Session.audio_input` |

`capture()` is the convenience API. Use `Session` when you need more than one
destination, explicit route settings, provider composition, Relay, or detailed
observations. Both forms use the same Rust engine.

## Compose and route media

| Task | Module |
|---|---|
| Stems, ports, and routes | `pocketstation.graph` |
| Typed signals and subscriptions | `pocketstation.signal` |
| Source declarations and discovery | `pocketstation.sources` |
| Application-owned PCM | `pocketstation.audio_input` |
| Runtime events, metrics, and outcomes | `pocketstation.observations` |
| Accepted media and delivery behavior | `pocketstation.graph.RouteSettings` and `DeliveryPolicy` |

Read [source identity and time](../concepts/source-identity-and-time.md) before
persisting selectors or correlating provider events with recorded media.
Read [route settings](../concepts/route-settings.md) before changing queue or
loss behavior.

## Connect external systems

| Task | Module |
|---|---|
| Publish through Relay | `pocketstation.relay` or `pocketstation.aio.relay` |
| Send audio with one function | `Connector(send=...)` |
| Author a reusable audio Connector | subclass `pocketstation.Connector` or `pocketstation.aio.Connector` |
| Use the advanced Connector SPI | `pocketstation.connector` |
| Author a computation | `pocketstation.operator_authoring` |
| Author an inbound Source | `pocketstation.source_authoring` |
| Author a lower-level Endpoint | `pocketstation.endpoint_authoring` |
| Run a managed process | `pocketstation.sidecar` |
| Load a trusted native extension | `pocketstation.extensions` |

Provider callbacks run on off-realtime workers. Native capture
callbacks never call Python.

## Build a voice workflow

`pocketstation.voice` contains the provider-neutral Python protocols.
`pocketstation.aio.Session.conversation()` composes either:

- a `StreamingTranscriber`, `ResponseModel`, and `SpeechSynthesizer`, with an
  optional `SpeechDetector`; or
- one `DuplexVoiceModel`.

Provider implementations remain in example or separately installed provider
packages. Read [Compose a voice workflow](../guides/voice.md) before
depending on interruption or playout observations.

## Handle failures

Start with `PocketStationError`, `CaptureError`, and `SessionError` from the
package root. Advanced modules expose errors for the feature they implement. Preserve
the structured error and inspect the Session outcome before retrying.

Continue with [Session ownership, bounds, and shutdown](../concepts/session-and-bounds.md)
or [events, metrics, outcomes, and errors](events-and-errors.md).
