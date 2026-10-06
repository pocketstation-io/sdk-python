# Source-aware recording clips

Use `RecordedAudio` to extract context from a finalized Session recording without
opening a microphone or recapturing an application. Core owns file validation,
sample slicing and provenance. The Python API returns Core's results.

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

The synchronous native I/O releases the GIL. The asyncio API keeps that
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

For recent audio during capture, declare history with explicit limits before starting and
route only the authorized sources you want to retain:

```python
from pocketstation import Session
from pocketstation.recording import AudioHistoryConfig

session = Session()
history = session.audio_history(AudioHistoryConfig())
source = session.audio_input("authorized-audio")
source.output.retain_audio()
running = session.start()
# Feed/capture audio; stem metadata appears after its first frame arrives.
# clip = history.read_clip(exact_stem_id, detector_window)
source.close()
running.stop()
```

Defaults share 30 seconds, 16 MiB PCM and 4096 buffers across at most 64 stems.
Configure `retention_ns`, `max_pcm_bytes` and `max_buffers` explicitly for your
workload. History keeps original channels and source identity. A source reset
discards that stem's older generation. `clear()` discards retained audio while
capture and its other destinations continue. Graceful stop keeps the retained
tail; cancellation discards it.

`AudioHistoryError.code` distinguishes `recording.history_not_ready` (post-context
has not arrived), `recording.history_expired`, `recording.history_missing_context`,
`recording.history_ended`, cancellation, failure and invalid limits. Live history
does not shorten missing context or invent silence. Limit retries and concurrent
requests in your application; each returned clip owns its WAV bytes. Observe
shared retention and delivery through `history.observations()`.

For asyncio use `pocketstation.aio.Session`: history methods are awaited,
including `get_stems()`, `read_clip()`, `clear()` and `observations()`. Declaration
and `retain_audio()` stay synchronous. Do not forget to await async input writes,
close and Session stop. Native history operations run off the event loop.

These APIs are qualified against matching local builds. Registry publication
and physical capture qualification are separate. External detectors supply
Session-time intervals; neither reader recognizes speech nor chooses a model.
