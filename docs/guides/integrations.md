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

Use `pocketstation.Connector` for synchronous file or library calls that are
already finite. Use `pocketstation.aio.Connector` for network providers so
PocketStation can apply finite startup, delivery, and shutdown deadlines.

Plain exceptions become structured failures for the lifecycle stage that
raised them. Raise `ConnectorError` when the provider has a stable error code
or retryability classification. Other routes continue independently when one
Connector is slow or fails.

The complete runnable program uses the function form:
[`examples/send_audio_to_websocket.py`](../../examples/send_audio_to_websocket.py).

## Use the advanced SPI

Import `ConnectorManifest`, `ConnectorDriver`, or `ConnectorWorker` from
`pocketstation.connector` when the integration needs typed configuration
schemas, signal inputs, custom readiness state, explicit delivery outcomes, or
finite native-owned batches. `Session.register_connector()` can then declare
multiple Endpoint configurations from one implementation.

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
