# PocketStation Python SDK

PocketStation lets Python applications capture one desktop application and an
optional microphone as separate live audio stems. One native Session can route
those stems to Python model code, Relay, and recording without mixing their
source identities.

The Python SDK uses the PocketStation Rust engine. Python owns application and
model logic; it does not reimplement capture, routing, timing, recording, or
Relay media transport.

> **Status: preview.** The package is not published to PyPI. The macOS wheel has
> been tested with the workflow below. Linux and Windows wheels, plus WAN and
> TURN testing, are still in progress. The source distribution builds against
> PocketStation Core `1.1.2` and Relay `0.1.1`.

## Capture a desktop application

Install a development wheel:

```bash
python -m pip install 'pocketstation @ file:///absolute/path/to/pocketstation-0.1.0-cp311-abi3-macosx_11_0_arm64.whl'
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

## Find where a voice agent lost time

[`examples/debug_voice_ai.py`](examples/debug_voice_ai.py) sends a physical
microphone to OpenAI Realtime without another voice framework. PocketStation
keeps the microphone, generated assistant audio, and the selected browser's
output as independent recorded stems. It also records provider lifecycle and
interruption events on the same monotonic timeline.

See the [voice-agent debugger instructions](examples/README.md#debug-a-voice-agent-interruption-from-the-media-boundary).

## Transcribe both sides of a voice application

The transcription example requires:

- macOS with Screen Recording and Microphone permission;
- Python 3.11 or newer;
- a PocketStation development wheel built for your Python and macOS target;
- internet access on the first run to download the default faster-whisper
  model.

Install the transcription extra, then run the example:

```bash
python -m pip install 'pocketstation[transcription] @ file:///absolute/path/to/pocketstation-0.1.0-cp311-abi3-macosx_11_0_arm64.whl'
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
[`examples/transcribe_voice_app.py`](examples/transcribe_voice_app.py). The example-owned
adapter imports `faster_whisper.WhisperModel` when the Operator starts; it is
not built into the `pocketstation` SDK namespace.

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

The example uses PocketStation's small rate-limited demo service unless you set
`POCKETSTATION_CONTROL_URL` and `POCKETSTATION_RELAY_URL` to services you
operate. The shared URLs live in `pocketstation_examples`; application code does
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

## Choose the right extension point

PocketStation uses four open boundaries:

| Boundary | Use it when |
|---|---|
| `Source` | Media or signals enter the Session. |
| `Operator` | Work transforms media or emits typed signals. |
| `Connector` | Media or signals leave for an external system. |
| `Endpoint` | You need the lower-level outbound execution contract. |

Import advanced contracts from their owning module so application code shows
which boundary it uses:

```python
from pocketstation.connector import Connector, ConnectorManifest
from pocketstation.operator_authoring import OperatorProvider
from pocketstation.source_authoring import SourceProvider
```

The package root contains only the common Session, capture, audio-input, and
error contracts. Advanced imports name the boundary they use; there is no
second flat compatibility API.

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

## Current package status

| Area | Current status |
|---|---|
| Native Rust, Python, Ruff, and MyPy checks | Pass locally |
| Installed macOS wheel | Tested |
| Real faster-whisper inference | Tested |
| Relay and Chromium receiver | Tested on the publisher host only |
| Physical application and microphone | Tested on the recorded macOS host |
| Linux wheel | Not yet tested externally |
| Windows wheel | Not yet tested externally |
| Receiver over WAN or TURN | Not yet tested externally |
| Standalone source distribution | Builds from the published Core 1.1.2 dependency |
| PyPI release | Not published |

The native binding pins published Core `1.1.2` and the shared Relay connector
`0.1.1`. Wheel and source-distribution builds resolve those immutable registry
artifacts without a sibling repository checkout.

The Rust-to-Python audio read currently copies native samples into Python-owned
bytes before exposing a `memoryview`. The view avoids another Python-side copy;
the complete boundary is not zero-copy.

## Verify a local change

```bash
uv sync --extra transcription
uv run pytest -q
uv run ruff check python tests examples
uv run ruff format --check python tests examples
uv run mypy python tests/qualification/typing_contract.py examples
```

## Reference

- [`examples/README.md`](examples/README.md) — runnable examples and
  prerequisites.
- `pocketstation.capture` — concise application and microphone capture.
- `pocketstation.session` — Session declarations and lifecycle.
- `pocketstation.graph` — stems, ports, routes, and signal contracts.
- `pocketstation.connector` — outbound provider authoring.
- `pocketstation.operator_authoring` — computation authoring.
- `pocketstation.source_authoring` — inbound provider authoring.
- `pocketstation.aio` — asyncio projection of the same engine.
