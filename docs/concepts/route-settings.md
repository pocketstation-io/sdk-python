# Set media and delivery behavior for a route

Every destination receives data through its own finite queue. PocketStation
chooses suitable settings for common capture, recording, Connector, and signal
subscription work. Use `RouteSettings` when an integration needs to state those
choices explicitly.

`RouteSettings` keeps two decisions together without mixing their APIs:

- `MediaCaps` describes the media accepted by the route.
- `DeliveryPolicy` describes timing, queue pressure, loss, copying, and
  observations.

## Use a preset first

Realtime PCM should keep capture moving when one destination falls behind:

```python
from pocketstation.graph import RouteSettings

settings = RouteSettings.realtime_audio()
```

Typed signals use a finite asynchronous queue:

```python
settings = RouteSettings.bounded_async()
```

Connected ports still negotiate the concrete sample rate, channel layout, and
signal schema.

## Change delivery without changing media

```python
from pocketstation.graph import (
    BackpressurePolicy,
    DeliveryPolicy,
    RouteSettings,
)

delivery = DeliveryPolicy.realtime_audio().with_backpressure(
    BackpressurePolicy.DROP_OLDEST
)
settings = RouteSettings.realtime_audio().with_delivery_policy(delivery)
```

Pass the result to a Connector destination:

```python
destination = session.destination(connector, route_settings=settings)
application.send(destination)
```

Use `DROP_OLDEST` only when fresh realtime media matters more than queued
media. Use the default `DROP_NEWEST` when preserving items already accepted by
the destination is more important. A blocking policy is not valid on a capture
callback or realtime worker.

## Read what the Session compiled

Advanced Connector and Endpoint preparation objects expose `route_settings`.
`RouteMetrics.delivery` returns `RouteDeliveryMetrics` for queue depth,
attempted delivery, drops, and discontinuities. Typed signals use
`SignalQueueMetrics`. Check those observations before increasing capacity: a
larger finite queue can hold older audio without solving the slow destination.

`EdgeContract` remains an import-compatible name for `RouteSettings` in the
0.1.x series. Existing `edge=` keyword arguments continue to work. New code
should use `route_settings=` so the decision is clear at the call site.
`EdgeMetrics` and `TypedEdgeMetrics` remain compatibility names for the clearer
metrics types.
