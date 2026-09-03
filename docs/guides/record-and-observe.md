# Record stems and inspect Session delivery

Recording and observations follow the same source-aware routes as model and
network destinations. Add recording before the Session starts, inspect live
metrics while it runs, and require a successful terminal outcome after it
stops.

## Record independent stems

```python
import pocketstation

live = pocketstation.capture(
    application="Zoom",
    microphone=True,
    record_to="recordings",
)

with live:
    for index, frame in enumerate(live.audio):
        print(frame.source_id, frame.stem_id)
        if index == 99:
            break

result = live.stop_result
if result is None or not result.success:
    raise RuntimeError("PocketStation did not stop cleanly")
if result.recording is None or not result.recording.complete:
    raise RuntimeError("PocketStation did not complete the recording")
```

The recording manifest and WAV files are written beneath the directory passed
to `record_to`. Application and microphone stems retain separate source,
stream, stem, timing, and discontinuity information.

## Inspect live delivery

Call `live.metrics()` while the context is active. `SessionMetrics` reports
finite source, route, polling, event, Operator, and reentry state. For each
route, inspect its declared capacity, current and peak depth, delivered frames,
drops, and latency fields where that route can measure them.

Read `live.events` for permission, source, Endpoint, rollback, and terminal
lifecycle events. Metrics are snapshots; events explain changes between
snapshots.

Unavailable measurements remain unavailable. A sender timestamp is not a
receiver playout timestamp, and a completed local recording is not proof that
a browser played the same sample.

## Stop or cancel deliberately

Leaving the context requests normal stop and drains work already accepted by
the route queues.
Call `cancel()` on the explicit `RunningSession` API when active provider or
sidecar work must abort. Both shutdown modes join Session workers before returning
a terminal `StopResult`.

After shutdown, inspect:

- `StopResult.success` and structured errors;
- `RecordingOutcome.complete` and every stem outcome;
- frame drops and recorded discontinuities; and
- provider or Connector outcomes required by the workflow.

A successful start establishes lifecycle readiness. It does not prove that a
source produced media or that every destination received it.

Continue with [Session ownership and bounds](../concepts/session-and-bounds.md)
or [Relay publication](relay.md).
