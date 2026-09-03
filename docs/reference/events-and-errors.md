# Read events, metrics, outcomes, and errors

PocketStation reports setup failures, live observations, and terminal results
separately. A Session that started successfully may still receive no media,
drop frames on one route, fail one provider, or finish an incomplete recording.

## Setup failures

| Operation | Main error |
|---|---|
| Select or open a Source | `CaptureError` |
| Declare an invalid Session | `SessionError` |
| Write incompatible application PCM | `AudioInputWriteError` |
| Configure a provider | feature-specific `PocketStationError` subclass |

Preserve the stable error code and human-readable message. Do not retry every
failure. Permission denial, ambiguous selection, invalid media, and missing
credentials require a different action from a temporary provider failure.

## Session events

`running.events` is a finite stream of `SessionEvent` values. Events identify
the component and Session time for lifecycle changes, Source failures, Endpoint
failures, rollback, finalization, and terminal state.

The event queue has its own capacity and drop observations. A dropped diagnostic
event does not prove that audio was dropped; inspect media route metrics too.

## Metrics

`running.metrics()` returns one immutable `SessionMetrics` snapshot. It groups
Source, route, polling, Operator, Endpoint, application-owned audio, recording,
and sidecar measurements.

For a route, inspect:

- declared and current queue depth;
- peak queue depth;
- delivered and dropped frames;
- discontinuity counts; and
- latency only when the measurement definition and unit are present.

Missing measurements remain `None`. Sender time, Relay receive time, browser
jitter-buffer time, and acoustic playout are different observations.
`RouteMetrics.source_latency_measurement` returns a
`RouteLatencyMeasurement`; `source_latency_unit` gives its unit.
## Terminal results

After stop or cancellation, inspect `StopResult` before reporting success:

```python
result = running.stop()
if not result.success and result.terminal_event is not None:
    for failure in result.terminal_event.failures:
        print(failure.error_code, failure.stage, failure.message)
```

When recording was requested, also require a complete `RecordingOutcome` and
inspect every stem. When a Connector or voice provider was required, inspect
its final result separately.

Normal close requests a drain of accepted finite work. Cancellation asks active
workers to abort before the same joined shutdown. Neither mode may leave an
unjoined provider task or child process and still report success.

## Voice observations

`VoiceEvent` and `ConversationOutcome` keep transcript, response, synthesis,
output cancellation, and provider failure observations on the Session
timeline. They distinguish provider task cancellation, Core queued-output
cancellation, Connector queue clearing, receiver observation, and acoustic
hearing.

An unavailable receiver or acoustic observation must remain unavailable. It is
not equivalent to zero delay or successful interruption.

Continue with [troubleshooting](../troubleshooting.md) for recovery steps.
