# Keep each source identifiable

PocketStation keeps application audio, microphone audio, and application-owned
PCM separate even when they use the same Operator, Connector, RelaySession, or
recording. A frame does not become anonymous when it leaves capture.

## Read the identities carried by a frame

`AudioFrame` exposes the identifiers needed to correlate live delivery with
provider observations and recorded stems:

| Value | Meaning |
|---|---|
| `source_id` | The Source instance that produced the media. |
| `stream_id` | One output stream declared by that Source. |
| `stem_id` | The independently routed and recorded audio stem. |
| `sequence_number` | The frame order within the current source generation. |
| `timestamp_start_ns` | The first sample time in its declared clock domain. |
| `source_generation` | The current attachment of a recoverable Source. |
| `discontinuity_epoch` | A change that prevents the timeline from being treated as continuous. |

Use these values together. A display name such as `Zoom` helps a person choose
an application; it is not a media identity.

## Select an application before capture starts

The concise API accepts an exact display name, an application identifier, or a
positive process ID:

```python
import pocketstation as pks
from pocketstation.sources import SourceQuery

with pks.capture(application="Zoom") as live:
    for frame in live.audio:
        print(frame.source_id, frame.stream_id, frame.sequence_number)
```

PocketStation rejects zero matches and ambiguous matches. It does not select
the first process silently.

Use discovery when the application must display choices or remember one:

```python
matches = pks.discover_sources(SourceQuery.application("Zoom"))
if len(matches) != 1:
    raise RuntimeError("Select one running Zoom source")

selected = matches[0]
source = pks.Source.from_discovered(selected)
```

Store the discovered selector only for its reported persistence scope. A
process ID ends with that process. A platform application identity may survive
a normal restart, but should still be resolved again before a new Session.

## Treat discontinuity as data

A sequence gap, timestamp gap, source restart, or dropped route frame changes
what downstream code may infer. PocketStation records those changes instead of
inserting silent continuity.

An Operator can preserve the input lineage and add derivation for its output.
A Connector receives the source-aware `AudioFrame`. A recording manifest keeps
the same source and stem identity beside the WAV file.

Do not rewrite a missing timestamp as zero, merge two source generations, or
claim that a remote receiver played a sample from a sender timestamp alone.

Continue with [recording and observations](../guides/record-and-observe.md) or
[platform source persistence](../operations/platform-support.md).
