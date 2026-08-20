# Source-aware transcription

This example consumes PocketStation PCM signals on a bounded async Operator,
runs a local `whisper-cli` process outside capture and realtime partitions, and
emits finite JSON transcript signals containing source, stream, sequence, and
discontinuity identity.

```sh
python -m examples.transcription.run \
  --whisper-cli "$(command -v whisper-cli)" \
  --model /path/to/ggml-tiny.en.bin \
  --wav /path/to/speech.wav \
  --record-to recordings
```

The example defaults to CPU inference. Provider processes have finite startup,
execution, output, and shutdown limits. Each Session route retains its own
bounded queue, so a slow transcription branch does not become the Relay or
recording queue.

The notebook uses the same function and can be executed without storing output:

```sh
python -m examples.notebooks.execute \
  examples/notebooks/source_aware_transcription.ipynb
```
