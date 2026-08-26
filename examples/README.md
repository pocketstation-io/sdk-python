# Python examples

Each example is a complete Python program. Start with the task you want to try.

## Debug both sides of a voice application

Use this example to inspect what a desktop voice application produced and what
the person said into the microphone. PocketStation keeps both sources separate
while one faster-whisper Operator transcribes them.

```bash
python examples/debug_voice_ai.py
```

The example asks which running application to capture. Microphone capture is
explicit in the source, and no recording or cloud service starts.

Install the optional model dependency before the first run:

```bash
python -m pip install 'pocketstation[transcription] @ file:///absolute/path/to/pocketstation-0.1.0-cp311-abi3-macosx_11_0_arm64.whl'
```

The first run may download the configured faster-whisper model. Model work runs
on a bounded off-realtime Operator worker, not on a capture callback.

## Stream application audio to a browser

Use this example to stream one selected application's audio as a named AudioBus
and open a browser invitation:

```bash
python examples/stream_any_app_audio.py
```

The example prints the single-use word code and browser URL returned by the
control plane. It does not open a microphone or write a recording. The shared
Fly deployment is a small, rate-limited demonstration service and may return
`HTTP 429` when capacity is in use. It is not a hosted production service.

To use services you operate, set `POCKETSTATION_CONTROL_URL` and
`POCKETSTATION_RELAY_URL` before running the command. No shared secret belongs
in application code.

## Run capture, transcription, browser audio, and recording together

The installed `pocketstation-demo` command combines independent application and
microphone capture, faster-whisper transcripts, two Relay/browser AudioBuses,
and a finalized two-stem recording.

The current browser test runs on the same host as the publisher. WAN and TURN
behavior have not been verified yet.
