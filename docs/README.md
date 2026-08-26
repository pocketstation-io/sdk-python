# PocketStation Python documentation

Start with the task you want to run. Open the module reference only when you
need the lower-level API.

## Get started

- [Capture one desktop application](../README.md#capture-a-desktop-application)
- [Debug both sides of a voice application](../README.md#debug-a-live-voice-application)
- [Stream any application audio to a browser](../README.md#stream-any-application-audio-to-a-browser)
- [Browse the runnable examples](../examples/README.md)

## Build an integration

- [`pocketstation.session`](../python/pocketstation/session.py) owns synchronous
  Session declaration and lifecycle.
- [`pocketstation.aio`](../python/pocketstation/aio/__init__.py) provides the
  asyncio projection of the same native Session.
- [`pocketstation.graph`](../python/pocketstation/graph.py) declares stems,
  routes, ports, and typed signals.
- [`pocketstation.source_authoring`](../python/pocketstation/source_authoring.py),
  [`pocketstation.operator_authoring`](../python/pocketstation/operator_authoring.py),
  and [`pocketstation.connector`](../python/pocketstation/connector.py) are the
  open provider boundaries.

For package status and current qualification limits, read the
[repository README](../README.md#current-package-status).
