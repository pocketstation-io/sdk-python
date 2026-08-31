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

## Start with the focused authoring module

```python
from pocketstation.connector import Connector, ConnectorManifest
from pocketstation.operator_authoring import OperatorProvider
from pocketstation.source_authoring import SourceProvider
```

Use `session.destination(connector)` for one configured outbound destination.
Use `session.register_connector(connector)` when the same implementation must
declare several independently configured Endpoints.

## Declare capabilities and limits

An integration manifest should expose stable identity, named ports, signal and
media capabilities, typed configuration, secret classification, finite startup
and request deadlines, and structured failures. Reject unsupported
combinations before the Session starts.

Secret values may be read during provider setup, but they must not appear in
errors, logs, metrics, observations, or object representations.

## Prove the package outside its repository

Build and install the distribution into a clean environment. Run the provider
through a normal Session, cause saturation and cancellation, and verify joined
shutdown. A mock proves only the adapter contract; a network integration needs
provider and receiver evidence.
