# Python examples

Each example is a complete Python program. Start with the task you want to try.

## Debug a voice-agent interruption from the media boundary

[`debug_voice_ai.py`](debug_voice_ai.py) connects PocketStation directly to
OpenAI Realtime. PocketStation owns the physical microphone, generated
assistant PCM, browser delivery, independent recording stems, bounded queues,
and sender-side output cancellation. The provider owns speech recognition and
the model response.

The example observes three separate audio paths:

- the microphone sent to the model;
- generated assistant audio sent to Relay;
- output captured from the browser application playing the assistant.

It also puts speech, transcript, response, synthesis, cancellation, and failure
events on the Session timeline. This makes it possible to distinguish model
delay, local queue delay, Relay delivery, and browser output without treating
provider logs as media evidence.

Install the optional dependencies and provide an OpenAI API key:

```bash
python -m pip install 'pocketstation[voice-agent-debug]'
export OPENAI_API_KEY='...'
```

Run the example and enter the name of the browser application that will play
the assistant:

```bash
python examples/debug_voice_ai.py
```

The example creates a short-lived Relay invitation and opens it in a browser.
Speak, interrupt the assistant while it is replying, then press `Ctrl-C`. Use
headphones for this run: the example does not provide acoustic echo
cancellation.

The final report includes source continuity, bounded queue drops, provider
events, and PocketStation's output-cancellation events. The receiver reports
WebRTC statistics, but it does not acknowledge the exact sample played through
the loudspeaker. The example therefore reports acoustic hearing and exact
provider-history truncation as unavailable.

The installed examples use the small shared demo service by default. It has
strict admission limits. Set `POCKETSTATION_CONTROL_URL` and
`POCKETSTATION_RELAY_URL` to use your own deployment.

## Transcribe both sides of a voice application

Use this example to inspect what a desktop voice application produced and what
the person said into the microphone. PocketStation keeps both sources separate
while one faster-whisper Operator transcribes them.

```bash
python examples/transcribe_voice_app.py
```

The example asks which running application to capture. Microphone capture is
explicit in the source, and no recording or cloud service starts.

Install the optional model dependency before the first run:

```bash
python -m pip install 'pocketstation[transcription]'
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

## Run the complete demo

The installed `pocketstation-demo` command combines independent application and
microphone capture, faster-whisper transcripts, two Relay/browser AudioBuses,
and a finalized two-stem recording.

The current physical voice proof runs the browser on the publisher host through
the deployed Relay. WAN and TURN behavior have not been qualified yet.
