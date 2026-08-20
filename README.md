# PocketStation for Python

> **Development status: PARTIAL.** This is not yet the complete Python SDK and
> does not have full Rust capability parity. The binding program has accepted
> the exhaustive capability matrix, Pythonic stream slice, package ownership,
> typed source lifecycle, Rust-backed graph declarations, bounded typed signal
> streams, process sidecars, compiled native extensions, complete observations,
> application-owned PCM ingress, and independently installable wheel/sdist
> artifacts. Real relay/browser composition, notebook proof, platform
> qualification, and OSS readiness remain gated.

Capture one application and one microphone as independent, source-aware live
audio stems. Consume both from a bounded Python endpoint while the native Rust
runtime records each stem separately and preserves lineage, timing, drops, and
discontinuities. The same Session model extends to devices and explicit network
endpoints without changing the identity contract.

```python
import pocketstation

with pocketstation.capture(
    application="PocketStation Demo",
    microphone=True,
    record_to="recordings",
) as live:
    for frame in live.audio:
        print(frame)
```

The concise recipe and the explicit API use the same native `Session`. Python
does not reimplement capture, routing, timing, backpressure, or recording.

## Current implementation truth

The accepted stream, structure, source-lifecycle, graph, typed-signal,
extension, and sidecar slices are `SAFE-TO-MERGE`; the SDK as a whole remains
`PARTIAL`. Their component and
canonical-Session evidence is not release evidence:

- native application and microphone declarations;
- independent stem and source identity on every delivered frame;
- one bounded managed-language polling boundary;
- frame-first sync and async streams that lazily flatten one native batch,
  reject mixed reader modes, and fail immediately on concurrent readers;
- typed sync and async lifecycle/failure event streams backed by bounded native
  waits rather than user-written polling loops;
- immutable sync and async source discovery over the canonical Rust provider,
  including stable source identity, selector persistence, process-tree scope,
  and exact native state;
- seven-state microphone permission observation with no implicit prompt and no
  boolean collapse of `NotObservable`;
- typed source-unavailable/backend-failure events carrying source identity,
  generation, failure detail, and the explicit recovery requirement;
- canonical Rust-backed `SignalSpec`, media, port, edge, operator, source, and
  endpoint declarations with open stable identifiers and named ports;
- bounded application-owned float32 PCM input with preallocated Core buffers,
  explicit full/closed/cancelled/invalid outcomes, source/stream identity,
  discontinuity propagation, sync/async writers, and normal Session fan-out;
- operator chaining and concrete generated-audio reentry through the Rust
  compiler/runtime, preserving lineage and recording without a Python hot-path
  callback;
- real bounded `BusSubscription` endpoints for PCM, text, and bytes with
  Pythonic sync/async read and iteration, immutable payloads, complete generic
  timing/lineage/derivation, and distinct timeout, EOF, fault, and close states;
- immutable native extension descriptors and trusted absolute-path compiled
  libraries validated by the linked ABI 1.2 authority, transactionally imported
  into the canonical native `Session`, and retained for its full lifetime;
- typed process-sidecar specs, messages, sync/async streams, bounded queue
  saturation, deadlines, cancellation, graceful close, forced kill, wait, reap,
  and live/final observations, all owned by the same native `Session`;
- in-process Python Connector authoring over Core's bounded off-realtime
  Connector worker, with typed configuration, redacted secrets, full input
  contracts, structured failures, readiness/health/recovery control, and
  drain/abort shutdown;
- sync and asyncio Source authoring over Core's blocking Source worker, with
  typed output contracts, Session-owned lineage, finite async deadlines,
  cancellation, and exact provider cleanup;
- sync and asyncio Operator authoring over Core's bounded async Operator
  runtime, with compiled port/edge preparation, typed derived outputs,
  finite async deadlines, cancellation, and derivation metadata;
- native blocking waits release the interpreter, and executable tests prove
  Python remains responsive while a hung child is terminated and reaped;
- immutable Session snapshots covering event and audio queues, source ingress,
  routes, operator inputs/workers, external sources, derived routes, and
  generated-audio reentry with capacities, bytes, depths, peaks, loss causes,
  discontinuities, and named nanosecond latency boundaries;
- bounded native trace configuration, final recorder accounting, offline read,
  rolling hash, and deterministic lifecycle/terminal validation;
- deterministic, idempotent Python shutdown;
- distinct stop/cancel dispositions with the native terminal event retained so
  source, endpoint, rollback, and finalization fault categories are not lost;
- complete/incomplete per-stem recording outcomes with stable error codes,
  queue/write/drop counters, and typed gap detail;
- synchronous and `asyncio` ownership models;
- typed Session lifecycle client for the current control-plane HTTP API.

The SDK is not complete:

- Core's normal public API does not name raw trace-record values or the typed
  component/stage enums behind rollback and finalization failures. Python
  therefore exposes validated trace summary/terminal truth and stable failure
  stages, but does not claim a stable raw-record or fully typed control-failure
  owner projection;
- capture authorization snapshots and permission-transition ownership are not
  attached to the canonical running Session; the SDK preserves discovery and
  the authoritative seven-state platform observation without inventing either;
- real relay/browser composition and notebook proof remain later gates;
- isolated macOS wheel and independently rebuilt sdist consumers exist; Linux,
  Windows, and real-device matrices remain release gates;
- the control client creates remote Session credentials but does not publish
  media or invent a browser join URL.

The ordinary API is frame iteration over the native bounded endpoint; explicit
reads and native batch iteration remain advanced modes. The accepted stream
gate proves that no second Python queue exists and reader modes cannot be mixed
or consumed concurrently. Python is never invoked from an audio callback or
realtime partition.

## Compiled native extensions

Load a trusted C or Rust dynamic library before starting the Session. This is a
raw native-code trust boundary, not package authentication: PocketStation does
not verify its publisher, signature, or checksum and does not sandbox it. The
path must be absolute; Core canonicalizes it, validates the ABI and complete
descriptor set, imports every registration transactionally, and retains the
library until the Session is destroyed.

```python
from pathlib import Path

import pocketstation

session = pocketstation.Session()
library = session.load_native_extension_library(
    Path("extensions/libacme_processor.dylib").resolve()
)

source = session.source("acme.source")
operator = session.operator(pocketstation.Operator("acme.operator"))
source.output("out").connect(operator.input("in"))
```

The receipt exposes the canonical path and immutable source, operator, and
endpoint registrations. Loading is a synchronous pre-start declaration in
both `pocketstation.Session` and `pocketstation.aio.Session`; it does not run
Python in foreign callbacks or admit PCM callbacks onto realtime partitions.
Process sidecars remain available when crash isolation or a separately managed
process is wanted. They are not required for ordinary Python Connector
authoring.

## Python Sources and Operators

Python can define typed non-PCM Sources and Operators without implementing a
second Session runtime. These providers execute only on Core-owned blocking or
async worker partitions; application-owned PCM continues to use the dedicated
bounded `Session.audio_input()` path.

```python
import pocketstation

text = pocketstation.SignalSpec.text(role="request")
source_manifest = pocketstation.SourceManifest(
    "io.example.source.requests.v1",
    outputs=(pocketstation.PortSpec.output("events", text),),
)

@pocketstation.source(source_manifest)
def requests(configuration):
    yield pocketstation.SourceEmission.text(
        "events", configuration["text"], signal=text
    )
```

Operators receive immutable envelopes and emit values whose lineage and
derivation are attached by Core:

```python
result = pocketstation.SignalSpec.text(role="result.final")
operator_manifest = pocketstation.OperatorManifest(
    "io.example.operator.uppercase.v1",
    inputs=(pocketstation.PortSpec.input("input", text),),
    outputs=(pocketstation.PortSpec.output("output", result),),
)

@pocketstation.operator(operator_manifest)
def uppercase(_port, envelope):
    return (pocketstation.OperatorEmission.text(envelope.payload.upper(), signal=result),)
```

`pocketstation.aio.source` and `pocketstation.aio.operator` accept async
iterables and coroutine handlers with explicit finite deadlines. The same
native Session remains authoritative for registration, compilation,
backpressure, cancellation, and terminal outcomes.

## Python Connectors

The concise path declares an audio contract and handles items directly. Core
still owns bounded receiver polling, route accounting, readiness, failure
containment, and shutdown; Python executes only on the Connector's
off-realtime worker.

```python
import pocketstation

manifest = pocketstation.ConnectorManifest.audio(
    "io.example.connector.stdout.v1",
    package_version="1.0.0",
)

@pocketstation.connector(manifest)
def stdout(item, context):
    print(item.input.port_name, item.audio.sequence_number)

session = pocketstation.Session()
endpoint = session.register_connector(stdout).declare()
```

Stateful providers implement `ConnectorDriver` and register with
`Connector.with_driver(...)`. Their factory receives every resolved input
descriptor, including `SignalSpec`, `MediaCaps`, `EdgeContract`, route identity,
and typed configuration. `ConnectorConfigurationValue.secret(...)` is redacted
by default and requires explicit provider access. Provider exceptions can use
`ConnectorError` to preserve a stable error code, stage, and retryability in the
final Session outcome.

The capability matrix distinguishes declaration-level `REAL` rows from
component-only `PARTIAL` rows and completely `ABSENT` projections. A row marked
`REAL` is evidence-scoped; it does not upgrade the SDK, a platform, or a
deployment to production readiness.

## Application-owned audio

When an application already owns PCM, feed it directly into the Session instead
of recapturing the application through the operating system:

```python
from array import array

from pocketstation import Session

session = Session()
playback = session.audio_input("playback", frame_samples_per_channel=480)
playback.output.send(session.polled_audio())
playback.output.record("playback")

with session.start() as running:
    playback.write(array("f", [0.0] * 480))
    frame = running.audio.read(timeout_s=1.0)
```

`write()` accepts one C-contiguous float32 frame and never grows the native
queue. Advanced integrations can use `Session.pcm_source(AudioInputConfig(...))`
to retain explicit source-output and writer ownership. The asyncio API exposes
the same contract without executing Python on realtime partitions.

## Explicit Session API

Use the explicit surface when route identifiers and lifecycle control matter:

```python
from itertools import islice

from pocketstation import Session, Source

session = Session(recording_root="recordings")
application = session.capture(Source.application("PocketStation Demo"))
microphone = session.capture(Source.microphone_default())
audio = session.polled_audio()

application_route = application.send(audio)
microphone_route = microphone.send(audio)
application.record("application")
microphone.record("microphone")

with session.start() as running:
    for frame in islice(running.audio, 500):
        print(frame)

    metrics = running.metrics()
    print(metrics.polled_audio.queue_capacity_frames)
    print(metrics.polled_audio.queue_full_drops_total)
    for route in metrics.routes:
        print(route.route_id, route.edge.frames_dropped_total)

stop = running.stop_result
assert stop is not None
recording = stop.recording
terminal = stop.terminal_event
```

Enable a finite diagnostic trace at Session declaration time and validate it
offline after shutdown:

```python
from pocketstation import Session, SessionTrace, SessionTraceConfiguration

session = Session(trace=SessionTraceConfiguration("session.trace", 256))
# declare sources and routes, start, then stop the Session
trace = SessionTrace.read("session.trace")
validation = trace.validate()
print(validation.terminal_state, trace.outcome.rolling_hash)
```

Snapshots and outcomes are frozen, slotted Python values copied from the
canonical native owner. PocketStation does not start an exporter or a Python
telemetry thread; a future OpenTelemetry adapter must remain optional and
outside the realtime runtime.

Application selectors also support bundle ID, process ID, stable source ID, and
an exact process instance. Microphones support the default device or a stable
device ID.

## Typed graph declarations

The expert surface remains Pythonic without creating a Python graph engine.
Each declaration immediately becomes an opaque handle in the same Rust
`Session`; the Rust compiler remains authoritative for registration, ports,
media, exclusivity, and route errors.

```python
from pocketstation import Operator, Session, Source

session = Session(recording_root="recordings")
microphone = session.capture(Source.microphone_default())
transcribed = microphone.through(
    Operator("org.example.transcriber.v1"),
    input_port="audio-in",
    output_port="transcript",
)
transcribed.send(
    session.connector("org.example.transcript-sink.v1"),
    input_port="events",
)
```

`SignalSpec`, `MediaCaps`, `PortSpec`, and `EdgeContract` project the canonical
Rust value contracts. Operator and connector IDs remain open strings—there is
no closed model/provider enum. Generated PCM uses
`derived.reenter_audio()` and returns a normal source-aware `Stem`; concrete
media and exclusive consumption are checked before runtime start.

## Typed signal subscriptions

Operators and external sources can expose non-audio signals without creating a
second Python graph or queue. A subscription is a real bounded endpoint in the
same Rust `Session`:

```python
from pocketstation import Operator, Session, SignalSpec, Source

session = Session()
microphone = session.capture(Source.microphone_default())
transcript = microphone.through(
    Operator("org.example.transcriber.v1"),
    input_port="audio-in",
    output_port="transcript",
)
subscription = session.subscribe(transcript, signal=SignalSpec.text())

with session.start() as running:
    for envelope in running.signals(subscription):
        print(envelope.payload, envelope.lineage, envelope.derivation)
```

`read()` returns `None` only when its bounded wait expires and `STREAM_EOF`
after permanent endpoint closure. Faults raise `StreamError`. A stream fixes its
reader mode on first use and rejects concurrent readers. The default edge is a
finite bounded-async contract with media inferred from the exact `SignalSpec`.

## Discovery and permission truth

Discovery is a point-in-time immutable snapshot from the Rust source provider;
Python does not maintain a second registry or reinterpret platform state:

```python
import pocketstation

for source in pocketstation.discover_sources(
    pocketstation.SourceQuery.kind(pocketstation.SourceKind.APPLICATION)
):
    print(source.stable_id, source.state, source.identity_strength)

permission = pocketstation.microphone_permission_observation()
if permission is pocketstation.PermissionObservation.NOT_DETERMINED:
    print("The host application must request permission explicitly.")
```

Observation never prompts. macOS and eligible Windows application contexts can
provide authoritative states; Linux and other backends return
`NOT_OBSERVABLE` unless the native backend can establish authority. That value
does not mean allowed or denied. Source disappearance is delivered through
`running.events` with the stable identity, source generation, failure detail,
and an explicit `EXPLICIT_REDISCOVERY_AND_NEW_SESSION` recovery requirement.

Each `AudioFrame.samples` is a read-only `memoryview` over owned little-endian
`f32` PCM bytes. The view adds no further copy, but transferring a realtime
frame into Python ownership does copy it out of the native bounded batch. Use
`numpy.frombuffer(frame.samples, dtype="<f4")` when NumPy is already part of the
application; NumPy is not a required SDK dependency.

## Asyncio

The async namespace has the same declarations and outcomes. Native start, wait,
and stop work never blocks the event-loop thread, and cancellation requests the
native startup cancellation token before `CancelledError` is re-raised.

```python
from pocketstation import aio

async with aio.capture(
    application="PocketStation Demo",
    microphone=True,
    record_to="recordings",
) as live:
    async for frame in live.audio:
        ...
```

## Control plane

Media capture and control-plane lifecycle remain separate on purpose:

```python
from pocketstation import ControlClient

with ControlClient("https://control.example") as control:
    credentials = control.create_session()
    snapshot = control.session(credentials.session_id)
    subscriber = control.issue_subscriber_credentials(credentials.session_id)
    control.delete_session(credentials.session_id, credentials.source_token)
```

`pocketstation.aio.ControlClient` provides the symmetric async API. Both clients
reuse connections, apply finite default timeouts, bound response bodies, validate
Session IDs, and redact source credentials. They do not automatically retry
state-changing requests because the service does not yet define idempotency
keys.

## Package structure

```text
pocketstation/
  __init__.py       synchronous public surface
  audio_input.py    bounded application-owned PCM input
  capture.py        concise app + mic recipe
  connector.py      provider-facing outbound Connector authoring
  source_authoring.py typed non-PCM Source authoring on Core workers
  operator_authoring.py typed Operator authoring on Core workers
  session.py        explicit Session lifecycle and declarations
  sources.py        source selectors, discovery, permission, failure identity
  graph.py          Stem / Endpoint / SignalSpec and route declarations
  extensions.py     ABI descriptors and compiled-library registration receipts
  sidecar.py        managed process-extension declarations and streams
  signal.py         immutable payload, envelope, lineage, and subscription values
  streams.py        exclusive audio and typed-signal consumption over native queues
  observations.py   typed events, metrics, traces, recording and stop outcomes
  control.py        typed synchronous control-plane client
  errors.py         stable SDK exception hierarchy
  aio/              symmetric asyncio lifecycle, sources, streams, and control
  _native.pyi       static contract for the compiled extension
  py.typed          PEP 561 marker
native/src/
  lib.rs            module registration only
  connector/        Connector values, worker adapter, and observations
  source_authoring/ Source manifest and SourceFactory/SourceDriver adapter
  operator_authoring/ Operator manifest and AsyncOperator adapter
  audio_input.rs    Core AudioInput projection and buffer crossing
  graph.rs          exact graph values, handles, routes, and reentry projection
  extensions.rs     ABI validation and immutable library-registration receipts
  sidecar.rs        Session-owned process-extension lifecycle and messages
  sources.rs        source declarations, discovery, permission projection
  observations.rs   immutable event/metrics/outcome projection
  session.rs        Rust Session worker and lifecycle projection
  signals.rs        bounded typed endpoint receipt and immutable payload crossing
```

Native builds resolve the exact published `pocketstation 1.1.1` and
`pocketstation-relay 0.1.1` crates. Wheels contain the compiled runtime and do
not require Rust on the user's machine. The sdist contains only this SDK's Rust
and Python sources and rebuilds against those immutable registry releases; it
does not depend on a sibling checkout.

## Development gates

From this repository:

```bash
cargo fmt --manifest-path native/Cargo.toml -- --check
cargo test --manifest-path native/Cargo.toml --all-features --locked
cargo clippy --manifest-path native/Cargo.toml --all-targets --all-features --locked -- -D warnings
ruff check python tests
ruff format --check python tests
mypy python
python -m pytest -q
uv build
```
