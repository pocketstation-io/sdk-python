# How one Session owns media and failure

`Session` is the lifecycle owner for sources, routes, Operators, Connectors,
recording, observations, and shutdown. Python declares work; the Rust engine
captures and routes audio through finite queues.

```text
application ─┐
microphone ──┼─ Session ─┬─ Python or native Operator
owned PCM ───┘           ├─ Connector or Endpoint
                         ├─ bounded frame iterator
                         └─ multistem recording
```

## Source identity survives fan-out

An audio frame retains source, stream, stem, sequence, timestamp, clock, source
generation, and discontinuity information. Sending one stem to several
destinations does not mix that identity or recapture the source.

## Every crossing is finite

Audio input, polling, Python provider work, signals, Relay, and recording use
declared capacities. When a boundary is full, PocketStation returns or records
pressure according to that route's policy. It does not hide pressure in an
unbounded `asyncio.Queue`.

A slow Python consumer can still lose frames at its own bounded endpoint.
Inspect the route counters and discontinuities whenever complete delivery
matters.

## Python does not run on capture callbacks

Python-authored Sources, Operators, Connectors, and Endpoints execute on
bounded off-realtime workers. Native capture callbacks remain allocation-free,
lock-free, blocking-free, async-free, log-free, and panic-free.

Use a compiled extension when code must stay native. Use a process sidecar when
crash isolation matters. Neither boundary creates a second Session engine.

## Stop and cancel are different

Normal close requests a drain and joins every Session-owned worker. Cancellation
stops active asynchronous work before the same joined shutdown. Inspect the
terminal `StopResult`, recording outcome, provider outcome, and structured
errors before reporting success.

Provider cancellation, Core output cancellation, Connector queue clearing,
receiver playout clearing, and acoustic hearing are separate facts. A sender
must not infer a receiver or loudspeaker result it cannot observe.
