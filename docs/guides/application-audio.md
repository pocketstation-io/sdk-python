# Write application-owned audio into a Session

Use `Session.audio_input()` when your application already has PCM. Common
examples include generated speech, decoded call audio, and media received from
another SDK. The input becomes a source-aware stem that can use the same
recording, polling, Operator, and Connector routes as captured audio.

## Match the Session audio format

This example declares a 48 kHz mono Session with 10 ms frames. Each write
contains exactly 480 interleaved `float32` samples:

```python
from array import array

import pocketstation

session = pocketstation.Session(
    recording_root="recordings",
    frame_duration_ms=10,
)
assistant = session.audio_input(
    "assistant",
    frame_samples_per_channel=480,
)
assistant.output.record("assistant")

with session.start():
    assistant.write(array("f", [0.0]) * 480)
    assistant.close()
```

Declare routes before starting the Session. Call `close()` after the producer
has submitted its last frame so normal Session shutdown can drain accepted
audio.

## Handle backpressure explicitly

`write()` waits only until its finite `timeout_s` expires. Use `try_write()`
when the producer must receive an immediate `AudioInputFullError` instead.
Neither method adds an unbounded Python queue.

Inspect `assistant.observations()` for accepted, full, invalid, discarded, and
cancelled-write counts. Choose whether the application retries, drops, or slows
its producer; PocketStation does not choose that policy silently.

## Cancel replaceable output

Generated speech may stop being relevant when a person interrupts it. Attach
those frames to one owned output, then cancel only that output:

```python
generation = assistant.begin_output()
assistant.write(samples, generation=generation)
generation.cancel()
```

Core discards matching frames that are still waiting in its sender queues.
Microphone capture, recording, and unrelated outputs continue.

This operation cannot recall audio already accepted by a remote service or
playback device. A Connector and receiver need their own clear operation and
playout acknowledgement before an application can claim audible cancellation.

Continue with [multistem recording and observations](record-and-observe.md) or
[voice composition](voice.md).
