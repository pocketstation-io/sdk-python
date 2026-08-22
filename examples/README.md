# Debug both sides of a live voice application

Use this demo when you need to see what a desktop voice application produced
and what the person said into the microphone without mixing the two sides
together. It transcribes both sides, sends them to a browser, and records each
side as a separate stem.

## Prerequisites

- macOS Screen Recording and Microphone permission;
- Python 3.11 or newer;
- an installed PocketStation wheel with the `transcription` extra;
- network access for the first model download and the configured Relay services.

## Run

```bash
pocketstation-demo
```

Enter an application display name, process ID, or bundle identifier when
prompted. The command uses PocketStation's small, rate-limited demonstration
deployment by default. It can return `HTTP 429` when the shared capacity is in
use. Set `POCKETSTATION_CONTROL_URL` and `POCKETSTATION_RELAY_URL` to use a
deployment you operate.

The checkout runner calls the same installed entry point:
[`debug_voice_ai.py`](debug_voice_ai.py). The complete installed command is a
program under 50 lines: [`demo.py`](../python/pocketstation_examples/demo.py).
Model buffering and provider code stay in the example-owned
`pocketstation_examples` package, outside the `pocketstation` SDK namespace.

## Expected result

After Relay confirms publication, the command opens a browser invitation. It
then prints transcript events produced by
`faster_whisper.WhisperModel`, including the source identity for each result.

```text
voice application ─┐
physical microphone┼─ independent local transcripts
                   ├─ two browser buses
                   └─ two recording stems
```

Press `Ctrl-C` to stop. The Session cancels pending model work, deletes the
remote RelaySession, and finalizes both recordings under `recordings/`.

## Evidence boundary

The Lab gate installs the built wheel and uses faster-whisper inference,
the Rust Relay connector, the Go Relay service, Chromium, and finalized
recording artifacts. Its network path is same-host and remains
`LOOPBACK-ONLY`; it does not prove WAN or TURN behavior. The model runs on a
bounded off-realtime worker. The Rust-to-Python audio boundary is not zero-copy.
