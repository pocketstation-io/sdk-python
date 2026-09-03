# PocketStation for Python

Capture one desktop application and an optional microphone as separate live
audio stems. Use the same native Session for Python model code, browser
delivery, and one recording file per stem.

[![PyPI](https://img.shields.io/pypi/v/pocketstation.svg)](https://pypi.org/project/pocketstation/)
[![Python](https://img.shields.io/pypi/pyversions/pocketstation.svg)](https://pypi.org/project/pocketstation/)
[![License](https://img.shields.io/pypi/l/pocketstation.svg)](LICENSE)

```text
desktop application ─┐
microphone ──────────┼─ native Session ─┬─ Python model code
generated PCM ───────┘                  ├─ Relay and a browser
                                       └─ separate recording stems
```

PocketStation runs capture, frame timing, routing, recording, and Relay
publication in Rust. Python owns the application and provider code. A slow
Python integration cannot run on the operating-system capture callback.

## Capture a desktop application

You need Python 3.11 or newer, a supported desktop operating system, and one
running application that is producing audio.

```bash
python -m pip install pocketstation
```

```python
import pocketstation

with pocketstation.capture(application="Spotify") as live:
    for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

Replace `Spotify` with the display name or application identifier shown by the
operating system. You may also pass a positive process ID. Selection must match
one running application; PocketStation does not guess when several processes
match.

The context manager starts one native Session and joins it when the block
exits. No microphone opens and no file is written unless you request them.

## Add a microphone or recording

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

The application and microphone keep different source and stem identities.
Recording writes a separate stem for each source and reports its final result
when the Session stops.

Use a microphone device ID instead of `True` when the application must select a
specific input. See [capture one application](docs/getting-started/capture.md)
for source discovery, permissions, and asyncio.

## Use each source independently

One Session can send a stem to more than one destination:

- iterate over frames in Python;
- transcribe or process audio with an `Operator`;
- publish audio with a `Connector`;
- send a named `AudioBus` through Relay;
- record the original source;
- add generated PCM without mixing it into captured audio.

Every destination receives source, stream, stem, sequence, timestamp, clock,
and discontinuity information. Application and microphone audio do not have to
be mixed before model processing or remote delivery.

The default Python audio queue holds 32 frames. If Python stops reading and the
queue fills, new frames are dropped and the Session reports the queue depth,
dropped-frame count, and discontinuity. Other destinations continue according
to their own delivery settings.

## Build a voice workflow

`pocketstation.voice` defines the interfaces for streaming transcription,
response generation, speech synthesis, speech detection, and duplex voice
models. Provider packages implement those interfaces; PocketStation does not
embed a model catalog or API key.

Use separate providers when the application chooses each stage:

```python
conversation = session.conversation(
    input=microphone,
    output=assistant,
    stt=transcriber,
    llm=response_model,
    tts=synthesizer,
    vad=speech_detector,
)
```

Use one duplex provider when it accepts audio and returns audio through one
stateful connection:

```python
conversation = session.conversation(
    input=microphone,
    output=assistant,
    voice_model=voice_model,
)
```

The two forms cannot be combined. Provider capabilities are checked before the
Session starts. Generated speech enters the Session through `audio_input()`, so
it can be recorded, published, observed, or removed from pending local output
without stopping microphone capture.

This API does not provide model intelligence, acoustic echo cancellation, or a
hosted inference service. Provider-side cancellation and receiver playout
remain separate observations; PocketStation does not report that a person
stopped hearing audio unless the receiver can prove it.

Read [compose a voice workflow](docs/guides/voice.md) for transcript revisions,
provider capabilities, interruption, retained history, and current limits.

## Debug a voice interruption

[`examples/debug_voice_ai.py`](examples/debug_voice_ai.py) shows the complete
Session declaration. It connects a physical microphone to OpenAI Realtime,
returns assistant PCM to PocketStation, publishes named buses through Relay,
captures the browser application playing the assistant, and records the three
sources separately.

```bash
python -m pip install 'pocketstation[voice-agent-debug]'
export OPENAI_API_KEY='...'
python examples/debug_voice_ai.py
```

Speak while the assistant is replying. The final report separates provider
events from what PocketStation observed:

- microphone capture and continuity;
- transcript and response events reported by the provider;
- assistant PCM accepted by the Session;
- pending output removed after cancellation;
- Relay and browser WebRTC observations;
- the browser application's captured output;
- finalized recording stems.

The example does not prove the exact loudspeaker sample a person heard, AEC, or
provider-history truncation. Those fields remain unavailable when the provider
or receiver cannot report them. Read the
[example instructions](examples/README.md#debug-a-voice-agent-interruption)
before running it.

## Transcribe both sides of a voice application

The transcription example sends application and microphone audio through one
faster-whisper model while keeping the resulting text attributed to its source:

```bash
python -m pip install 'pocketstation[transcription]'
python examples/transcribe_voice_app.py
```

The program asks which running application to inspect. It opens the default
microphone because that example explicitly requests both sides. It does not
start Relay or record audio.

faster-whisper processes finite audio windows and emits final transcripts. This
is batch transcription, not a claim of streaming interim text or voice-agent
turn handling. The adapter is example code and imports
`faster_whisper.WhisperModel` only when transcription starts.

## Stream any application to a browser

```bash
python examples/stream_any_app_audio.py
```

Choose a running application. The example publishes it as one named AudioBus,
waits for Relay readiness, and prints a single-use word code and browser URL.
It does not open a microphone or record audio.

The example uses PocketStation's small, rate-limited demonstration services
unless you set `POCKETSTATION_CONTROL_URL` and `POCKETSTATION_RELAY_URL` to
services you operate. Shared service URLs live in `pocketstation_demo`; they are
not repeated in application code. The demonstration is not a hosted service or
SLA and can return `HTTP 429` when its configured capacity is in use.

## Send audio to your own provider

A Connector sends Session audio to an API, socket, file, or provider. Pass one
async function when the connection is already open:

```python
import pocketstation as pks
import pocketstation.aio as pks_aio


async def send_audio(frame: pks.AudioFrame) -> None:
    await socket.send(frame.samples)


destination = pks_aio.Connector(send=send_audio)
application.send_to(destination)
```

Use a class when the Connector opens and closes provider resources:

```python
class WebSocketConnector(pks_aio.Connector):
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    async def start(self) -> None:
        self.socket = await connect(self.url, token=self.token)

    async def send(self, frame: pks.AudioFrame) -> None:
        await self.socket.send(frame.samples)

    async def stop(self) -> None:
        await self.socket.close()
```

One Connector object represents one configured provider connection:

```python
destination = WebSocketConnector(url, token)
application.send_to(destination)
microphone.send_to(destination)
```

PocketStation calls `start()` once, sends both source-aware stems, and calls
`stop()` once. Each stem retains its own delivery queue and observations.
Create another Connector object when credentials, failure handling, or shutdown
must be independent.

The [integration guide](docs/guides/integrations.md) covers deadlines, failures,
sync Connectors, Sources, Operators, Endpoints, native extensions, and managed
processes. The manifest and driver APIs are for distributable integrations that
need typed configuration or custom service status; they are not required for a
normal Python Connector.

## Write PCM into a Session

Use `audio_input()` for generated speech, call audio, or decoded network media:

```python
session = pocketstation.Session(recording_root="recordings")
assistant = session.audio_input("assistant")
assistant.output.record("assistant")

with session.start():
    assistant.write(samples)
```

Core preallocates the input buffers. A write reports whether it was accepted,
full, closed, cancelled, or invalid. Read
[application-owned audio](docs/guides/application-audio.md) before selecting a
queue capacity or cancelling pending output.

## Handle permissions and source changes

PocketStation does not prompt during import or discovery. Check microphone
permission without prompting with
`pocketstation.sources.microphone_permission_observation()`, then let source
opening report the operating system's final result. Application and microphone
capture use separate permissions.

If an application or microphone disappears, PocketStation reports the change
and does not choose a replacement. Stop the Session, discover sources again,
confirm the new selection, and start another Session. Store a discovered source
only for its reported persistence scope.

See [platform operations](docs/operations/platform-support.md) for permission
states, persistence, recovery, and native dependencies.

## Sync and asyncio

`pocketstation` and `pocketstation.aio` control the same Rust Session. The
asyncio API adds awaitable lifecycle, streams, Relay calls, provider callbacks,
and audio writes; it does not create another capture or routing engine.

Python callbacks enter the interpreter and pay Python scheduling and conversion
costs. Capture, routing, recording, and the shared Relay Connector remain
native. Python-authored model and provider code does not have identical cost to
Rust code.

## Platform support

| Area | Published support and evidence |
|---|---|
| Python | 3.11 and newer |
| macOS Apple silicon | installed wheel; physical application and microphone capture; 10 ms voice capture; deployed Relay; Chromium; multistem recording on the recorded host |
| macOS Intel | published wheel and package tests |
| Linux x86-64 and ARM64 | published wheels; Core application selection and 10 ms capture in automated Ubuntu environments; physical-device qualification remains separate |
| Windows x86-64 and ARM64 | published wheels; Core selection and 10 ms capture in a Windows 11 ARM64 VM; physical-device and latency qualification remain separate |
| WAN and TURN | not yet qualified |

Version 0.1.3 uses PocketStation Core 1.1.7 and the shared Relay Connector
0.1.5.

Reading native audio into Python copies samples into Python-owned bytes before
exposing a `memoryview`. The view avoids another Python-side copy; the
Rust-to-Python call is not zero-copy.

## Continue from the task you have

| Task | Guide |
|---|---|
| Capture one application | [Python quickstart](docs/getting-started/capture.md) |
| Write generated or received PCM | [Application audio](docs/guides/application-audio.md) |
| Process audio and typed signals | [Operators and signals](docs/guides/process-audio-and-signals.md) |
| Record stems and inspect delivery | [Record and observe](docs/guides/record-and-observe.md) |
| Compose voice providers | [Voice](docs/guides/voice.md) |
| Publish through Relay | [Relay](docs/guides/relay.md) |
| Create an integration | [Integrations](docs/guides/integrations.md) |
| Understand Session queues and shutdown | [Session behavior](docs/concepts/session-and-bounds.md) |
| Understand source identity and time | [Source identity](docs/concepts/source-identity-and-time.md) |
| Prepare or troubleshoot a platform | [Platform support](docs/operations/platform-support.md) and [troubleshooting](docs/troubleshooting.md) |
| Find a public Python API | [API map](docs/reference/api-map.md) |
| Check an upgrade | [Release notes](RELEASE_NOTES.md) |

## Develop the SDK

```bash
uv sync --extra transcription
uv run pytest -q
uv run ruff check python tests examples
uv run ruff format --check python tests examples
uv run mypy python tests/qualification/typing_contract.py examples
```

## License

PocketStation for Python is available under the MIT or Apache-2.0 license.
