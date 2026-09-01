# PocketStation for Python

PocketStation captures one desktop application and an optional microphone as
separate live audio stems. A single native Session can send those stems to
Python model code, a remote browser, and a multistem recording without mixing
their source identities.

The Python package uses the PocketStation Rust engine for capture, routing,
timing, recording, and Relay transport. Your Python code owns the model and
application logic.

## Capture a desktop application

Install PocketStation:

```bash
python -m pip install pocketstation
```

Capture one application without opening a microphone or writing files:

```python
import pocketstation

with pocketstation.capture(application="Spotify") as live:
    for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

Add `microphone=True` when you need the default microphone as a second
independent stem. Add `record_to="recordings"` when you want each selected stem
recorded. Both behaviors are off by default.

## Handle permissions and source changes

PocketStation does not prompt during import or discovery. Check microphone
permission without prompting, then let Source opening report the authoritative
result. Application capture and microphone capture use separate permissions.

When an application or device disappears, PocketStation reports the change and
does not switch to another Source. Stop the current Session, discover again,
confirm any changed selection, and create a new Session. Store a discovered
identity only for its reported persistence scope. Keep fallback and provider
retry policy explicit and finite.

See [Prepare and qualify each Python platform](docs/operations/platform-support.md)
for the permission states, persistence scopes, and recovery sequence.

## Debug a voice interruption

[`examples/debug_voice_ai.py`](examples/debug_voice_ai.py) sends a physical
microphone to OpenAI Realtime without another voice framework. PocketStation
keeps microphone input, generated assistant audio, and the selected browser's
output as independent recorded stems. Provider events and media events share
one monotonic timeline, so you can see whether delay occurred before the model,
inside the provider, in local output, or after Relay delivery.

See the [voice-agent debugger instructions](examples/README.md#debug-a-voice-agent-interruption-from-the-media-boundary).
Run repository examples from a source checkout or source archive. The installed
`pocketstation-demo` command is the packaged application-and-microphone demo.

```bash
python -m pip install 'pocketstation[transcription]'
pocketstation-demo
```

## Transcribe both sides of a voice application

Install the transcription extra, then run the example:

```bash
python -m pip install 'pocketstation[transcription]'
python examples/transcribe_voice_app.py
```

The program asks which desktop voice application to inspect. It declares one
faster-whisper Operator, connects both stems to its audio input, and prints each
transcript with its original source identity. It does not start Relay or write a
recording.

The Session runs this path concurrently:

```text
voice application ─┐
                   ├─ one bounded faster-whisper Operator ─ transcripts
physical microphone┘
```

The complete composition is visible in
[`examples/transcribe_voice_app.py`](examples/transcribe_voice_app.py). The
example adapter imports `faster_whisper.WhisperModel` when the Operator starts;
the provider is not part of the `pocketstation` namespace.

This example does not debug turn handling, interruption, agent latency, or
browser playout. PocketStation does not receive those events in this program.

## Stream any application audio to a browser

Run the Relay example when you want another person to listen in a browser:

```bash
python examples/stream_any_app_audio.py
```

Choose any running application that is producing audio. The example publishes
that application as one named AudioBus, waits for Relay readiness, and prints a
single-use word code and browser URL. It does not open the microphone or record
audio.

The example uses PocketStation's small, rate-limited demo service unless you set
`POCKETSTATION_CONTROL_URL` and `POCKETSTATION_RELAY_URL` to services you
operate. The shared URLs live in `pocketstation_demo`; application code does
not contain service credentials.

## Read application and microphone audio

Set the optional microphone and recording parameters when the workflow needs
both sides:

```python
import pocketstation

with pocketstation.capture(
    application="Zoom",
    microphone=True,
    record_to="recordings",
) as live:
    for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

The iterator reads a bounded native endpoint. A slow Python consumer produces
observable pressure and discontinuities; it does not create an unbounded Python
audio queue.

## Send application-owned audio into a Session

Use `audio_input()` when your application already owns PCM, such as generated
speech or audio received from a call provider:

```python
session = pocketstation.Session(recording_root="recordings")
agent = session.audio_input("agent-output")
agent.output.record("agent")

with session.start():
    agent.write(samples)
```

The input uses finite preallocated Core buffers. Writes report full, closed,
cancelled, and invalid-buffer outcomes explicitly.

## Create an integration

PocketStation uses four open boundaries:

| Boundary | Use it when |
|---|---|
| `Source` | Media or signals enter the Session. |
| `Operator` | Work transforms media or emits typed signals. |
| `Connector` | Media or signals leave for an external system. |
| `Endpoint` | You need the lower-level outbound execution contract. |

Pass one function when the destination is already open:

```python
import pocketstation as pks
import pocketstation.aio as pks_aio

async def send_audio(frame: pks.AudioFrame) -> None:
    await socket.send(frame.samples)

destination = pks_aio.Connector(send=send_audio)
application.send_to(destination)
```

Subclass the synchronous or asyncio contract when the provider opens and
closes resources. The provider class owns its connection; the Session owns
bounded delivery, lineage, observations, drain, abort, and joined shutdown:

```python
class WebSocketConnector(pks_aio.Connector):
    def __init__(self, url, token):
        self.url, self.token = url, token

    async def start(self):
        self.socket = await connect(self.url, token=self.token)

    async def send(self, frame: pks.AudioFrame):
        await self.socket.send(frame.samples)

    async def stop(self):
        await self.socket.close()
```

Attach one configured object to one or more stems:

```python
destination = WebSocketConnector(url, token)
application.send_to(destination)
microphone.send_to(destination)
```

PocketStation calls `start()` once, interleaves both source-aware stems through
`send()`, and calls `stop()` once. A second Connector object creates a separate
destination. See [Create an integration](docs/guides/integrations.md) for
deadlines, failures, and the advanced SPI.

Python provider callbacks execute on bounded off-realtime workers. They cannot
be used as native capture callbacks. Compiled native extensions remain the path
for native provider code, and process sidecars remain available when crash
isolation is required.

## Use Relay from Python

Python creates and deletes RelaySessions through the typed HTTP control client.
The shared Rust `pocketstation-relay` connector publishes media. The Go Relay
service forwards WebRTC audio. Python does not encode Opus, write RTP, or own a
second media plane.

The control client uses finite request deadlines, bounded response bodies,
redacted secrets, and matching synchronous and asyncio APIs.

## Sync and asyncio

`pocketstation` and `pocketstation.aio` operate the same native Session. The
asyncio namespace provides awaitable lifecycle, stream, Relay, provider, and
audio-input operations without creating another audio queue.

Python callbacks still cross the interpreter boundary. Capture, routing,
recording, and Relay transport remain native-speed; arbitrary Python model code
does not have the same execution cost as Rust.

## Platform support

| Area | Support |
|---|---|
| Python | 3.11 and newer |
| macOS Apple silicon | Installed wheel, application capture, physical microphone, 10 ms voice path, Relay, Chromium, and multistem recording tested |
| Linux | Core application selection and 10 ms capture tested; installed Python distribution qualification in progress |
| Windows 11 ARM64 | Core application selection and 10 ms capture tested in a VM; installed Python distribution and physical-device qualification in progress |
| WAN and TURN | Not yet qualified |

The native binding uses PocketStation Core `1.1.4` and the shared Relay
Connector `0.1.2`.

The Rust-to-Python audio read currently copies native samples into Python-owned
bytes before exposing a `memoryview`. The view avoids another Python-side copy;
the complete boundary is not zero-copy.

## Develop the SDK

```bash
uv sync --extra transcription
uv run pytest -q
uv run ruff check python tests examples
uv run ruff format --check python tests examples
uv run mypy python tests/qualification/typing_contract.py examples
```

## Reference

- [`RELEASE_NOTES.md`](RELEASE_NOTES.md) — user-visible changes and upgrade
  guidance.
- [`docs/README.md`](docs/README.md) — task guides, concepts, operations, and
  API ownership.
- [Write application-owned audio](docs/guides/application-audio.md) — bounded
  PCM input and selective output cancellation.
- [Record and observe a Session](docs/guides/record-and-observe.md) — multistem
  outcomes, route metrics, and lifecycle events.
- [Prepare each platform](docs/operations/platform-support.md) — permissions,
  source persistence, explicit rediscovery, and fallback policy.
- [`examples/README.md`](examples/README.md) — runnable examples and
  prerequisites.
- `pocketstation.capture` — concise application and microphone capture.
- `pocketstation.session` — Session declarations and lifecycle.
- `pocketstation.graph` — stems, ports, routes, and signal contracts.
- `pocketstation.connector` — outbound provider authoring.
- `pocketstation.operator_authoring` — computation authoring.
- `pocketstation.source_authoring` — inbound provider authoring.
- `pocketstation.aio` — asyncio projection of the same engine.
