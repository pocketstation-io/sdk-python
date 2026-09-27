# Create a Source, Operator, Connector, or Endpoint

Choose the API by the direction of the work. All four use
the same Session compiler, finite queues, lifecycle, observations, and joined
shutdown.

| API | Use it when |
|---|---|
| `Source` | Media or signals enter the Session. |
| `Operator` | Computation transforms media or emits signals. |
| `Connector` | Media or signals leave for an external provider. |
| `Endpoint` | An outbound integration needs the lower-level execution SPI. |

## Keep provider code outside Core

Provider packages own credentials, protocol framing, codecs, provider
deadlines, retry behavior, and provider-specific errors. PocketStation Core
owns Session lifecycle, route bounds, lineage, observations, and shutdown.

Python integrations run off realtime. They must not capture audio again, create
another Session, or hide an unbounded queue behind a provider callback.

## Choose a Connector for outbound delivery

A Connector sends data from one PocketStation Session to an external system.
Use it to publish source-aware audio to a WebSocket, call
transport, monitoring service, storage API, or provider SDK without rebuilding
capture, buffering, routing, and shutdown in every integration.

```text
application ─┐
microphone ──┼→ independent Session routes
generated ───┘              ↓
                    one Connector lifecycle
                             ↓
                       external system
```

The configured Connector object owns provider state. PocketStation owns the
Session, route queues, source and stem lineage, delivery observations, and
terminal outcome. The concise API changes how the destination is declared; it
does not create a second media engine or skip Core.

Do not use a Connector for work that changes audio into another signal. A
transcriber is an `Operator`. Audio arriving from a provider is a `Source` or
an application-owned `AudioInput`. A duplex integration can compose inbound
and outbound APIs while the Session remains the only runtime.

## Send audio to a provider

Use one function when the provider connection is already open:

```python
import pocketstation as pks
import pocketstation.aio as pks_aio


async def send_audio(frame: pks.AudioFrame) -> None:
    await socket.send(frame.samples)


destination = pks_aio.Connector(send=send_audio)
application.send_to(destination)
```

Add lifecycle callbacks without creating a class:

```python
destination = pks_aio.Connector(
    start=open_connection,
    send=send_audio,
    stop=close_connection,
)
```

Use a class when the integration is reused or owns provider state:

```python
import pocketstation as pks
import pocketstation.aio as pks_aio


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

Use the configured object directly:

```python
destination = WebSocketConnector(url, token)
application.send_to(destination)
microphone.send_to(destination)
```

One Connector object is one provider lifecycle. PocketStation creates two
routes with separate delivery queues, calls `start()` once, preserves each frame's source and stem
identity, and calls `stop()` once. Two Connector objects create two independent
destinations.

This lets one authenticated connection carry application, microphone, and
generated-audio stems without mixing their identities. Use separate objects
for a primary and backup service, different credentials, or destinations that
must fail and stop independently.

Use `pocketstation.Connector` for synchronous file or library calls that are
already finite. Use `pocketstation.aio.Connector` for network providers so
PocketStation can apply finite startup, delivery, and shutdown deadlines.

Plain exceptions become structured failures for the lifecycle stage that
raised them. Raise `ConnectorError` when the provider has a stable error code
or retryability classification. Other routes continue independently when one
Connector is slow or fails.

## Lifecycle and delivery behavior

| Method | Provider responsibility | PocketStation responsibility |
|---|---|---|
| `start()` | Open and authenticate the configured destination. | Run on the managed worker after the Session start gate, apply a finite async deadline, retain failure in the terminal outcome, and close once. |
| `send(frame)` | Encode or publish one frame without retaining it indefinitely. | Deliver off realtime from a route with a configured queue capacity and preserve frame lineage. |
| `stop()` | Close sockets, files, tasks, and provider resources. | Call once after drain, abort, startup rollback, timeout, or delivery failure. |

`AudioFrame` includes source, stream, stem, sequence, timestamp, clock,
discontinuity, route, and output identity. Use those fields when the receiving
protocol supports named streams or diagnostic metadata.

Async calls default to finite preparation, startup, delivery, and shutdown
deadlines through `ConnectorDeadlines`. Adjust a deadline only when the
provider has a documented bound. A deadline is not a retry policy; provider
packages own finite reconnect and retry behavior.

The complete runnable program uses the function form:
[`examples/send_audio_to_websocket.py`](../../examples/send_audio_to_websocket.py).

## Use the advanced SPI

Import `ConnectorManifest`, `ConnectorDriver`, or `ConnectorWorker` from
`pocketstation.connector` when the integration needs typed configuration
schemas, signal inputs, custom readiness state, explicit delivery outcomes, or
finite native-owned batches. `Session.register_connector()` can then declare
multiple Endpoint configurations from one implementation.

Choose the concise API for one configured audio destination. Choose the
advanced SPI only when the integration needs portable package identity, typed
configuration schemas, secret fields, signal inputs, custom readiness and
recovery observations, or native-owned batching. Both use the same Core
Connector worker and Endpoint lifecycle.

## Declare capabilities and limits

An advanced integration manifest should expose stable identity, named ports,
signal and media capabilities, typed configuration, secret classification,
finite startup and request deadlines, and structured failures. Reject
unsupported combinations before the Session starts.

Secret values may be read during provider setup, but they must not appear in
errors, logs, metrics, observations, or object representations.

## Prove the package outside its repository

Build and install the distribution into a clean environment. Run the provider
through a normal Session, cause saturation and cancellation, and verify joined
shutdown. A mock proves only the adapter calls; a network integration needs
provider and receiver evidence.


## Live transcription scheduling

`FasterWhisper.attach_many` gives each selected stem one window assembler and
feeds complete windows to one shared inference Operator by default. The private boundary
contains mono 16 kHz PCM16, original source/time metadata, and a 1 MiB byte bound.
Core's audio input edges hold eight frames; typed window edges hold eight windows
per producer. The authoring `queue_capacity_signals` does not enlarge compiled
audio edges. Overload remains visible in route metrics and is independent of
recording and Relay.

Windows shorter than 500 ms (or a smaller configured window) emit
`processing_outcome="skipped-short-window"` without inference. Their duration is
accounted separately from transcribed coverage. Keep draining transcripts through
EOF during graceful `stop()` to receive each source's final partial window.
Direct `provider()` and `sync_provider()` are lower-level single-Operator adapters;
use `attach`/`attach_many` for the independently drained live pipeline.

Python-authored Operator callbacks run serially on one owned worker thread per
node, with a capacity-one command mailbox. They do not block Core's shared async
runtime. A process-wide maximum of 64 callback workers rejects excess admission.
Successful shutdown joins the worker. Python cannot safely interrupt an arbitrary
blocked callback: timeout makes finalization fail, retains the worker's capacity
permit, and closes the node only after that callback returns. Repeated timed-out
callbacks cannot create unlimited workers. This thread boundary does not make a
Python callback realtime-safe and does not change the audio callback contract.

### Explicit parallel model policy and vocabulary

`FasterWhisperConfiguration(inference_concurrency=2, cpu_threads=4)` uses two
source-affine inference workers, each with two CPU threads. Concurrency defaults
to one, is bounded to eight, and cannot exceed the total CPU budget. Actual
worker count also cannot exceed selected sources. Parallel mode requires
`num_workers=1` to prevent nested model workers multiplying the CPU budget.
Remainder threads go to the first workers. Each worker owns a model instance,
so additional concurrency increases resident model memory. Cross-source result
order is unspecified; source/time lineage and per-source ordering remain intact.
A tiny typed MANY-input merge Operator forwards transcripts using existing Core
queues and lifecycle, without a second scheduler or unbounded queue.

`initial_prompt` optionally supplies application vocabulary/context (at most
2048 UTF-8 bytes, non-empty and without NUL). It is passed to the underlying
model without special-case vocabulary. Use identical prompts and decoding
settings for live/reference comparisons; ASR-generated references are not human
ground truth. The demo CLI accepts `--cpu-threads`, `--inference-concurrency`
and `--initial-prompt`. Existing defaults stay unchanged. Direct `provider()`
and `sync_provider()` remain single-Operator adapters; parallel scheduling is
provided by `attach`/`attach_many`.

Cancellation joins finite callbacks but cannot forcibly interrupt arbitrary
Python code. Existing callback deadlines and the process-wide64-worker limit
still apply. Queue loss is visible and isolated from recording/Relay; this
configuration by itself is not evidence of latency or transcription quality.

### A responsive two-source CPU profile

For earlier complete-window results, an explicit three-second profile is available
through the Python API. With an existing local English tiny-model directory in
`model_path`, configure the adapter as follows:

```python
from pocketstation_demo import FasterWhisper, FasterWhisperConfiguration

transcriber = FasterWhisper(FasterWhisperConfiguration(
    model=model_path,
    allow_model_download=False,
    device="cpu",
    compute_type="int8",
    window_seconds=3,
    cpu_threads=4,
    inference_concurrency=2,
    num_workers=1,
    beam_size=1,
    language="en",
    vad_filter=True,
))
```

Use `attach_many` with the two source outputs and keep draining the subscription
through graceful stop. Shorter windows trade language context for earlier output;
measure recognition quality with representative speech before choosing them.
The five-second default and the demo CLI remain unchanged; this is an explicit
API configuration, not a new CLI option or a default latency guarantee.

This profile passed one local macOS arm64, installed-package replay with two
45-second stems and independently supplied corpus text. That run includes model
startup in first-result timing, but does not establish cold-machine timing,
physical capture, other platforms, or behavior for arbitrary models/languages.
