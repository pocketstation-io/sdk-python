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
exits. The iterator reads a finite native Endpoint; it does not create an
unbounded Python audio queue.

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
