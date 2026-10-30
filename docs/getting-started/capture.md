# Capture one desktop application

Install PocketStation, select one running application, and read its
source-aware audio frames. Microphone capture and recording remain off unless
you request them.

## Prerequisites

- Python 3.11 or newer;
- a supported desktop operating system and native capture permissions;
- one application producing audio.

Install the package:

```bash
python -m pip install pocketstation
```

## Capture an application

```python
import pocketstation

with pocketstation.capture(application="Spotify") as live:
    for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

Replace `Spotify` with a display name or application identifier. Pass a
positive integer, such as `application=1234`, when you already have a process
ID. Selection must resolve one running application before the Session starts.

A process ID lasts only for that process instance. If the application restarts,
discover it again. For a saved selection, use
`pocketstation.discover_sources()` and `Source.from_discovered()` as described
in [Persist a source at its supported scope](../operations/platform-support.md#persist-a-source-at-its-supported-scope).

The context manager starts one native Session and joins it when the block
exits. The iterator receives audio through a native queue that holds 32 frames
by default. If Python stops reading and the queue fills, PocketStation drops
new frames and reports the loss.

## Capture an explicitly selected process set

The local development candidate adds `discover_process_instances()` and
`Session.capture_process_set()`. These require the matching native candidate;
published 0.1.6 does not expose them. Acquisition requires macOS 26 or newer
with native capture enabled and ordinary operating-system consent. Other
platforms or builds report `capture.unsupported`.

Use this when one deliberately selected source consists of several processes.
The host must first establish which process IDs belong to its authorized source.
Discovery alone does not prove complete browser membership or tab isolation.
Never pass the complete discovery inventory merely because it is available.

```python
import pocketstation as pks


def declare_selected_processes(selected_process_ids: set[int]):
    observed = pks.discover_process_instances()
    selected = tuple(
        member for member in observed if member.process_id in selected_process_ids
    )
    if {member.process_id for member in selected} != selected_process_ids:
        raise ValueError("rediscover the complete selected source before capture")
    session = pks.Session(channels=2)
    audio = session.capture_process_set(selected)
    audio.send(session.polled_audio())
    return session, audio
```

Each frozen `pocketstation.sources.ObservedProcessInstance` contains its original
process ID, `StableSourceId`, and positive `process_start_time_ns`. Python keeps
the timestamp as an exact unsigned 64-bit integer; do not convert it to a float.
One set contains 1 through 32 distinct process IDs on one platform. Declaration
copies and orders the selection without refreshing its original observations.
Core admits every original member before delivery and does not follow a new
process that happens to reuse a PID or application identity.

The result is the existing `pocketstation.graph.SourceOutput`, so its normal
polled-audio, recording, history, Connector and Relay routes remain available.
Start and close the Session through the existing lifecycle. If one original
member exits, remaining originally selected members may continue. Replacement
processes are never followed; loss of all original members produces a typed
source-unavailable failure. Changing membership requires explicit rediscovery
and a new Session, not an automatic replacement.
Invalid selections raise `SessionDeclarationError` with code
`session.invalid_process_set`; existing draft and capture errors keep their codes.

`await pocketstation.aio.discover_process_instances()` performs discovery off the
event loop. Asyncio Session declaration stays immediate:
`audio = session.capture_process_set(selected)` uses the same Core source.

## Capture all desktop output

Use `Source.system_audio()` when the workflow needs every sound playing
through the computer. This is an explicit choice because notifications, music,
and unrelated applications can be included.

```python
import pocketstation as pks

session = pks.Session()
desktop = session.capture(pks.Source.system_audio())
desktop.send(session.polled_audio())

with session.start() as running:
    for frame in running.audio:
        print(frame.source_id, frame.stem_id)
```

Use `Source.application("Zoom")` when the user selected one application and
other desktop audio must remain private. Do not open both sources unless the
application needs both; their audio can overlap.

## Add a microphone or recording

```python
import pocketstation

with pocketstation.capture(
    application="Zoom",
    microphone=True,
    record_to="recordings",
) as live:
    for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

Application and microphone frames retain different source and stem identities.
Recording writes a separate stem for each selected source.

## Use asyncio

```python
import pocketstation.aio as pks

async with pks.capture(application="Spotify") as live:
    async for frame in live.audio:
        print(frame.source_id, frame.stem_id)
```

The synchronous and asyncio APIs control the same Rust Session. Capture,
routing, recording, and Relay remain native; only application and provider work
crosses into Python.

## Handle setup and delivery failures

Application selection, permission, graph validation, and provider preparation
fail before a running Session is returned. During execution, inspect route
metrics and discontinuities instead of treating missing frames as silence.

Continue with [Session bounds and shutdown](../concepts/session-and-bounds.md)
or [Relay publication](../guides/relay.md).
