# PocketStation for Python release notes

## 0.1.0 — Capture, inspect, and route live desktop audio

PocketStation for Python captures one desktop application and an optional
microphone as independent live stems. A single native Session can send those
stems to Python model code, PocketStation Relay, and a multistem recording
without mixing their source identities.

The first release includes:

- synchronous and asyncio Session APIs;
- exact application selection and default-microphone capture;
- 10 ms and 20 ms audio profiles;
- bounded audio and typed-signal streams;
- Python-authored Sources, Operators, Connectors, and Endpoints;
- application-owned PCM input and generated-audio output cancellation;
- provider-neutral voice composition with revisable transcripts;
- Relay publication and short-lived browser invitations; and
- source-aware multistem recording with structured outcomes.

The package uses PocketStation Core for capture, routing, timing, recording,
and lifecycle. Python provider work runs on bounded off-realtime workers and
does not execute on native capture callbacks.

### Voice interruption example

`examples/debug_voice_ai.py` connects a physical microphone directly to OpenAI
Realtime, routes generated speech through the normal Session audio path, and
records microphone input, generated output, and browser playback separately.
The resulting timeline distinguishes provider cancellation from Core output
cancellation and receiver delivery.

The current receiver does not acknowledge the exact sample played through a
loudspeaker. PocketStation therefore reports acoustic hearing and exact
provider-history truncation as unavailable instead of inferring them.

### Platform support

- macOS Apple silicon has installed-wheel evidence for application capture,
  physical microphone input, the 10 ms voice path, Relay, Chromium, and
  multistem recording.
- Linux and Windows have Core application-selection and 10 ms capture evidence.
  Installed Python distributions are qualified separately by the release
  workflow.
- WAN and TURN behavior are not yet qualified.

This is the first public Python release. There is no earlier package migration.
