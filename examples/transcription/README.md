# Source-aware transcription

The primary Python path uses `faster-whisper`, the local Whisper backend also
used by Pipecat's standard Python Whisper service. PocketStation hosts it as a
bounded async Operator and emits typed JSON transcript signals containing
source, stream, sequence, and discontinuity identity.

```sh
pip install 'pocketstation[transcription]'
```

```python
transcriber = FasterWhisper(FasterWhisperConfiguration(model="base"))
transcripts = transcriber.attach(session, microphone)
```

Named models may be downloaded through the provider library. Deployments that
require an offline trust boundary can point at a provisioned model directory
and disable network access explicitly:

```python
configuration = FasterWhisperConfiguration(
    model="/opt/models/whisper-base-ct2",
    allow_model_download=False,
)
```

Executable WAV proof:

```sh
python -m examples.transcription.run_faster_whisper \
  --model base \
  --wav /path/to/speech.wav \
  --record-to recordings
```

The same two-line attachment accepts a captured `Stem`, application-owned
`SourceOutput`, or generated `DerivedStream`. Model loading and inference run
outside capture and realtime partitions. Core owns the finite Operator input
queue; `FasterWhisperConfiguration` bounds window duration, source count,
output size, and operation deadlines. An asyncio deadline bounds the Session
operation, but it cannot preempt an already-running CTranslate2 call in a
Python worker thread. Use the subprocess alternative below when forced provider
termination is required.

## Hard-isolated whisper.cpp alternative

The subprocess example remains useful when killing and reaping the provider at
a hard deadline matters more than the normal Python model API:

```sh
python -m examples.transcription.run \
  --whisper-cli "$(command -v whisper-cli)" \
  --model /path/to/ggml-tiny.en.bin \
  --wav /path/to/speech.wav \
  --record-to recordings
```

The subprocess defaults to CPU inference. Provider processes have finite startup,
execution, output, and shutdown limits. Each Session route retains its own
bounded queue, so a slow transcription branch does not become the Relay or
recording queue.

The notebook uses the same function and can be executed without storing output:

```sh
python -m examples.notebooks.execute \
  examples/notebooks/source_aware_transcription.ipynb
```
