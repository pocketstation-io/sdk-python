# Build a Source, Operator, Connector, or Endpoint

Choose the boundary by the direction and ownership of the work. All four use
the same Session compiler, finite queues, lifecycle, observations, and joined
shutdown.

| Boundary | Use it when |
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

## What a Connector solves

A Connector is the outbound boundary between one PocketStation Session and an
external system. Use it to publish source-aware audio to a WebSocket, call
transport, monitoring service, storage API, or provider SDK without rebuilding
capture, buffering, routing, and shutdown in every integration.

```text
application ─┐
microphone ──┼→ independent bounded Session routes
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
and outbound boundaries while the Session remains the only runtime.

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
bounded routes, calls `start()` once, preserves each frame's source and stem
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

## Lifecycle and delivery contract

| Method | Provider responsibility | PocketStation responsibility |
|---|---|---|
| `start()` | Open and authenticate the configured destination. | Run on the managed worker after the Session start gate, apply a finite async deadline, retain failure in the terminal outcome, and close once. |
| `send(frame)` | Encode or publish one frame without retaining it indefinitely. | Deliver off realtime from a bounded route and preserve frame lineage. |
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
shutdown. A mock proves only the adapter contract; a network integration needs
provider and receiver evidence.
