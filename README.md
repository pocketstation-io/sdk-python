# PocketStation Python SDK

PocketStation lets you inspect both sides of a live desktop voice application.
It keeps the application's output separate from the physical microphone while
one native Session transcribes, publishes, and records both sides.

The Python SDK uses the PocketStation Rust engine. Python owns application and
model logic; it does not reimplement capture, routing, timing, recording, or
Relay media transport.

> **Status: PARTIAL.** The installed macOS wheel has completed the Lab workflow
> described below. The package is not published to PyPI. Linux and Windows
> wheels, WAN/TURN evidence, and a standalone source distribution remain
> release gates.

## Debug a live voice application

The demo requires:

- macOS with Screen Recording and Microphone permission;
- Python 3.11 or newer;
- a PocketStation development wheel built for your Python and macOS target;
- internet access on the first run to download the default faster-whisper
  model;
- access to the configured PocketStation control plane and Relay.

Install the wheel with its transcription dependency, then run one command:

```bash
python -m pip install 'pocketstation[transcription] @ file:///absolute/path/to/pocketstation-0.1.0-cp311-abi3-macosx_11_0_arm64.whl'
pocketstation-demo
```

The command asks which desktop application to inspect. It then starts one
Session and:

- opens the browser invitation after Relay confirms the publisher;
- prints each transcript with its original source identity;
- writes the application and microphone to separate recording stems.

The Session runs this path concurrently:

```text
voice application ─┐
physical microphone┼─ faster-whisper transcripts
                   ├─ two named Relay/browser buses
                   └─ two aligned recording stems
```

Press `Ctrl-C` to stop. PocketStation cancels pending model work, closes the
RelaySession, and finalizes the recording.

The installed command is implemented in one program under 50 lines:
[`python/pocketstation_examples/demo.py`](python/pocketstation_examples/demo.py).
The example package imports `faster_whisper.WhisperModel` when it starts. Its
adapter is example-owned and is not part of the `pocketstation` SDK namespace.

This demo does not claim speaker diarization, conversational-agent behavior,
WAN/TURN qualification, or a zero-copy Rust-to-Python model boundary.

## Capture application and microphone audio

Use `capture()` when you want frames in Python as well as separate recordings:

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

## Relay ownership

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

## Release qualification

| Gate | Current evidence |
|---|---|
| Native Rust, Python, Ruff, MyPy | Passing locally |
| Installed macOS wheel | REAL |
| Real faster-whisper inference | REAL |
| Same-host Relay and Chromium receiver | LOOPBACK-ONLY |
| Physical application and microphone | REAL-DEVICE-PROVEN on the recorded host |
| Linux wheel | Pending external qualification |
| Windows wheel | Pending external qualification |
| WAN/TURN receiver | Pending external qualification |
| Standalone sdist | Qualified from the immutable Core 1.1.2 dependency |
| PyPI release | Requires explicit release authorization |

The native binding pins published Core `1.1.2` and the shared Relay connector
`0.1.1`. Wheel and source-distribution builds resolve those immutable registry
artifacts without a sibling repository checkout.

The Rust-to-Python audio read currently copies native samples into Python-owned
bytes before exposing a `memoryview`. The view avoids another Python-side copy;
the complete boundary is not zero-copy.

## Develop and verify

```bash
uv sync --extra transcription
uv run pytest -q
uv run ruff check python tests examples
uv run ruff format --check python tests examples
uv run mypy python tests/qualification/typing_contract.py examples
```

Run the installed product gate from the workspace root:

```bash
bash pocketstation-lab/tests/test-w21-python-batch-transcription-artifact.sh
```

That gate builds and installs the wheel, runs faster-whisper inference,
publishes through the shared Relay connector, receives audio in Chromium, and
verifies the finalized multistem recording. Same-host evidence remains labeled
`LOOPBACK-ONLY`.

## Reference

- [`examples/README.md`](examples/README.md) — product demo behavior and
  prerequisites.
- `pocketstation.capture` — concise application and microphone capture.
- `pocketstation.session` — Session declarations and lifecycle.
- `pocketstation.graph` — stems, ports, routes, and signal contracts.
- `pocketstation.connector` — outbound provider authoring.
- `pocketstation.operator_authoring` — computation authoring.
- `pocketstation.source_authoring` — inbound provider authoring.
- `pocketstation.aio` — asyncio projection of the same engine.
