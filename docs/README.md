# PocketStation Python documentation

Start with the task you want to run. Open the module reference only when you
need the lower-level API.

## Get started

- [Capture one desktop application](getting-started/capture.md)
- [Transcribe both sides of a voice application](../README.md#transcribe-both-sides-of-a-voice-application)
- [Stream any application audio to a browser](../README.md#stream-any-application-audio-to-a-browser)
- [Browse the runnable examples](../examples/README.md)

## Create an integration

- [Write application-owned audio into a Session](guides/application-audio.md)
- [Process audio and typed signals](guides/process-audio-and-signals.md)
- [Record stems and inspect Session delivery](guides/record-and-observe.md)
- [Compose a voice workflow](guides/voice.md)
- [Publish a named AudioBus through Relay](guides/relay.md)
- [Create a Source, Operator, Connector, or Endpoint](guides/integrations.md)

## Understand the system

- [Session ownership, bounds, and shutdown](concepts/session-and-bounds.md)
- [Source identity, timestamps, and discontinuities](concepts/source-identity-and-time.md)
- [Media and delivery settings for each route](concepts/route-settings.md)

## Operate and upgrade

- [Prepare and qualify each platform](operations/platform-support.md)
- [Troubleshoot capture, delivery, and shutdown](troubleshooting.md)
- [Read the release notes](../RELEASE_NOTES.md)

## Reference

- [`pocketstation.session`](../python/pocketstation/session.py) — synchronous
  Session declaration and lifecycle.
- [`pocketstation.aio`](../python/pocketstation/aio/__init__.py) — asyncio over
  the same native Session.
- [`pocketstation.voice`](../python/pocketstation/voice/__init__.py) —
  provider-neutral voice composition protocols.
- [`pocketstation.graph`](../python/pocketstation/graph.py) — stems, routes,
  ports, and signals.
- [`pocketstation.observations`](../python/pocketstation/observations.py) —
  runtime metrics and outcomes.
- [Python API map](reference/api-map.md) — public entry points and advanced
  modules by task.
- [Events, metrics, outcomes, and errors](reference/events-and-errors.md)

For supported platforms and current qualification limits, read the
[repository README](../README.md#platform-support).
