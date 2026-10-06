# Source-aware recording clips

Use `RecordedAudio` to extract context from a finalized Session recording without
opening a microphone or recapturing an application. Core owns file validation,
sample slicing and provenance. The Python layer only projects its results.

```python
from pocketstation import RecordedAudio, RecordingClipWindow

# `outcome` is running.stop().recording; authorize its directory in your app.
reader = RecordedAudio.open(outcome.session_directory, outcome.session_id)
stem = next(item for item in reader.stems if item.label == "application")
origin = stem.first_timestamp_ns
window = RecordingClipWindow.around(
    origin + 60_000_000, origin + 100_000_000,
    before_ns=20_000_000, after_ns=20_000_000,
)
clip = reader.read_clip(stem.stem_id, window)
assert clip.stem.source_id == stem.source_id
assert clip.stem.channels == stem.channels
# clip.wav contains owned float32 WAV bytes, preserving every channel.
```

`outcome.read_clip(stem_id, window)` is a convenience for the same reader and
rejects incomplete outcomes. Advanced result types and `RecordingClipError`
are available from `pocketstation.recording`.

All intervals use half-open Session nanoseconds, not wall-clock dates or source
device timestamps. Start from the persisted `first_timestamp_ns`; it is WAV
sample zero after recorder normalization. Core floors the start and ceils the
end to sample boundaries, then clips to available audio. `requested` preserves
the original interval; `actual`, `first_sample_frame` and `sample_frames` report
what was returned. Sample frames count samples per channel, not capture buffers.

Identity includes Session, source, stem, original clock, source generation and
permission epoch. `discontinuities` contains original gap observations that
intersect the actual interval; it does not invent a continuous capture history.
All 64-bit identifiers, counts and timestamps remain exact Python integers.

In an asyncio application use the same API through worker threads:

```python
from pocketstation.aio.recording import RecordedAudio

reader = await RecordedAudio.open(outcome.session_directory, outcome.session_id)
clip = await reader.read_clip(stem.stem_id, window)
```

The synchronous native I/O releases the GIL. The asyncio projection keeps that
I/O off the event loop. Cancelling an await does not forcibly stop file I/O
already running; applications must bound their concurrent requests.

Core accepts complete schema-2 float32 WAV recordings only. Limits are 120
seconds per requested interval, 32 MiB per encoded clip, 1 GiB per selected
source WAV, 2 MiB per manifest, 64 stems and 1,024 gaps per stem. Invalid windows,
unknown stems, missing audio, changed recordings, unsupported manifests and I/O
failures produce `RecordingClipError` with stable `recording.clip_*` codes.

Core checks manifests and the selected WAV's recorder checksum on each read.
The checksum detects corruption; it is not a cryptographic signature. The
application owns directory authorization and must prevent hostile concurrent
writers. The reader never broadens capture scope or authorizes a recording.

This API reads finalized recordings. Live rolling retention, wake-word
recognition and detector models are separate capabilities. External detectors
may supply intervals; this reader neither classifies speech nor chooses a model.
