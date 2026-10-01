# Reduce playback echo in microphone audio

The development candidate exposes Core's built-in echo processor through
`Session.echo_cancel()`. This API is not in the published Python 0.1.5 wheels.
Installed native platform and physical-device qualification remains required
before a release can promise those results.

Select the microphone and playback reference explicitly:

```python
import pocketstation as pks
from pocketstation.aec import PlaybackReference

session = pks.Session(frame_duration_ms=10, recording_root="recordings")
application = session.capture(pks.Source.application("Zoom"))
microphone = session.capture(pks.Source.microphone_default())
cleaned = session.echo_cancel(
    microphone,
    PlaybackReference.selected_application(application),
)

application.record("application")
cleaned.audio.record("microphone")
cleaned.audio.send(session.polled_audio())

with session.start() as running:
    for frame in running.audio:
        # Process each source-aware frame in the application.
        print(frame.source_id, frame.timestamp_start_ns)

print(cleaned.observations())
```

The declaration registers the native processor automatically. The returned
`audio` is an ordinary `Stem`, so its `send`, `send_to`, `record`, and `publish`
methods use the existing Session. Python does not receive each microphone
frame to perform cancellation. The original microphone and application remain
independently usable. Application-only capture still opens no microphone.

Both inputs must belong to the same Session and identify different streams.
The current processor accepts 48 kHz mono or stereo with 10 ms or 20 ms frames.
Core negotiates each input's channel count separately: a mono microphone can
use a stereo application reference, and processed output retains the microphone
channel count. Native capture declarations retain their own source formats.
This does not establish acoustic qualification for arbitrary device pairs.

The current `AudioInput` provider still requires its writers within one Session
to share the same sample rate, channel count and frame size. Passing different `channels`
values to two `session.audio_input()` calls does not bypass that restriction.
Preserve reference channel information; do not average opposite-polarity
stereo into silence. Core owns timing checks and processing. Unrelated device
clocks and arbitrary reference timing do not become supported merely because
the Python declaration succeeds.

## Choose the reference deliberately

Each constructor uses an audio stream that is already declared:

- `PlaybackReference.selected_application(application)` uses the selected app.
  Audio from other applications is absent from this reference.
- `PlaybackReference.output_mix(output)` uses a separately authorized complete
  output mix, for example `session.capture(pks.Source.system_audio())`.
- `PlaybackReference.rendered_audio(output)` uses caller-owned audio that is
  also submitted to a playback device.

None of these constructors opens another capture device. A complete output mix
can include private audio from other applications, so select it intentionally
and do not record or publish it unless that is the requested behavior.

The chosen stream remains in `cleaned.reference.input`; `cleaned.microphone`
retains the original microphone declaration. `reference_coverage` describes
the selected scope. It does not prove that this stream includes everything
heard through a particular speaker.

## Observe processing and shutdown

`cleaned.observations()` returns an immutable snapshot, including the native
state, processed/discarded frame counts, queue depths and capacity, processing
duration, reference age and lead, cadence error, resets, interrupted requests,
source identities and the last error. Observations remain readable after stop.

`processing` means native processing is running. It does not assert acoustic
convergence or useful speech recognition. `interrupted` reports a cancelled
wait for native work; it does not identify its cause as a device failure.
The Session stop result and events remain necessary to assess the complete run.
Unknown `qualified_algorithmic_delay_samples` is `None`.
`latest_processing_duration_ns` and `maximum_processing_duration_ns` measure
the complete native request, including queue wait, reset, reference analysis
and microphone processing. They are not the signal's algorithmic delay.
`discarded_output_frames_total` counts produced frames discarded when their
awaiting request was interrupted; inspect it alongside input and route discard
counters.

Cancellation does not mute the microphone when playback is active. Simultaneous
speech must survive. Missing references, timing errors and source changes need
explicit observations and recovery. Inspect both the Session outcome and the
processor snapshot rather than assuming a quiet output demonstrates success.

Processed frames keep their own derived source and stream identities.
`frame.processing` is an immutable `AudioProcessing` record from
`pocketstation.signal`: it identifies the most recent actual microphone input,
its sequence, timestamp, duration, source generation and discontinuity epoch,
plus the processor's adaptation generation. Raw frames have `processing=None`.
The record does not describe every sample retained in adaptive filter history.

The native processor reports a nominal delay of 432 samples per channel.
This is frequency-dependent filter delay, not a qualified timestamp correction
or an assurance of sample alignment. `qualified_algorithmic_delay_samples`
remains `None` until that property is qualified.

Graceful finalization limits the drain to 40 ms. `tail_frames_total` and
`tail_padding_samples_total` distinguish that output from actual microphone
capture; `output_frames_total` includes ordinary output and tail frames.
Tail metadata retains the last real input identity and reports internal padding
and a tail offset in samples per channel. This policy does not establish that
all adaptive processor state has decayed to zero. Recordings retain processing
metadata alongside the audio. After `running.stop()`, the existing audio stream
retains accepted frames for reading until `STREAM_EOF`. `audio.is_closed` reports
that the producer has stopped; it does not mean those accepted frames have
already been read. Explicit `running.close()` or `running.cancel()` discards
unread audio. Asyncio uses the same semantics with `aclose()` and `cancel()`.

## Use asyncio

`pocketstation.aio.Session` provides the same immediate `echo_cancel`
declaration. It is called before `await session.start()` and does not need an
`await` itself. Audio reads and Session stop use the normal asyncio API.
Observations are immediate snapshots in both APIs.
