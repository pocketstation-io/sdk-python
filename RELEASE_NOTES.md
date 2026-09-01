# PocketStation for Python release notes

## 0.1.2 — 2026-09-01

Capture code can now send source-aware audio to an external system through one
function or one focused Python class.

This is the first PocketStation release published to PyPI.

### Create a Connector

Use `Connector(send=...)` when the destination is already open:

```python
async def send_audio(frame):
    await socket.send(frame.samples)

destination = pocketstation.aio.Connector(send=send_audio)
application.send_to(destination)
```

Subclass `pocketstation.Connector` for a synchronous destination or
`pocketstation.aio.Connector` for an asynchronous provider. The class owns its
provider connection. PocketStation owns the bounded routes, source and stem
identity, delivery observations, drain, abort, and joined shutdown.

```python
class WebSocketConnector(pocketstation.aio.Connector):
    def __init__(self, url, token):
        self.url, self.token = url, token

    async def start(self):
        self.socket = await connect(
            self.url,
            additional_headers={"Authorization": f"Bearer {self.token}"},
        )

    async def send(self, frame):
        await self.socket.send(frame.samples)

    async def stop(self):
        await self.socket.close()
```

One Connector object can receive several stems through one provider lifecycle.
Create another object when a backup or second destination needs its own queue,
failure, and shutdown outcome.

### Operate capture safely

The guides now show how to inspect microphone permission without prompting,
persist a discovered source only for its reported scope, recover after a
process or device disappears, reject ambiguous application matches, and make
fallback and provider retry policy explicit.

### Upgrade

```console
python -m pip install --upgrade pocketstation==0.1.2
```

Python Connectors run outside native realtime partitions, but each frame still
crosses the Python interpreter boundary. Use a native Connector when that cost
is not appropriate for the destination.

## 0.1.1 — 2026-09-01

This version was tagged on GitHub but was not published to PyPI. Its changes are
included in 0.1.2.

## 0.1.0 — 2026-08-31

Capture, inspect, and route live desktop audio.

PocketStation for Python captures one desktop application and an optional
microphone as independent live stems. A single native Session can send those
stems to Python model code, PocketStation Relay, and a multistem recording
without mixing their source identities.

### Added

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

### Supported and qualified environments

- macOS Apple silicon has installed-wheel evidence for application capture,
  physical microphone input, the 10 ms voice path, Relay, Chromium, and
  multistem recording.
- Linux and Windows have Core application-selection and 10 ms capture evidence.
  Installed Python distributions are qualified separately by the release
  workflow.
- Python reports Windows microphone permission as `NOT_OBSERVABLE` before
  capture. Opening the microphone remains authoritative and returns its real
  startup outcome. This avoids an unsafe repeated WinRT query in Core 1.1.4.
- WAN and TURN behavior are not yet qualified.

### Distribution

This version was tagged on GitHub but was not published to PyPI. Its package
features are included in 0.1.2.
