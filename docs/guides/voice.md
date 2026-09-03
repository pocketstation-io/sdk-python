# Compose a voice workflow

`pocketstation.voice` defines provider-neutral Python protocols.
`pocketstation.aio.Session` composes those providers around one native Session.
The package does not contain a model provider, capture engine, Relay
implementation, or agent framework.

Start with a declared asyncio Session, one input stem, one `AudioInput` for
generated speech, and provider objects that implement the selected protocols.

## Choose one provider shape

Use separate components when the application selects independent stages:

```python
conversation = session.conversation(
    input=microphone,
    output=assistant,
    stt=transcriber,
    llm=response_model,
    tts=synthesizer,
    vad=speech_detector,
)
```

Each object implements the matching provider-neutral protocol:
`StreamingTranscriber`, `ResponseModel`, `SpeechSynthesizer`, or
`SpeechDetector`.

Use a duplex model when one stateful provider accepts audio and produces audio:

```python
conversation = session.conversation(
    input=microphone,
    output=assistant,
    voice_model=voice_model,
)
```

The two forms are mutually exclusive. Declaration fails before capture starts
when required components are missing or their capabilities do not satisfy the
selected configuration.

## Preserve transcript revisions

`TranscriptUpdate` carries one utterance identity, a monotonic revision,
current text, stable prefix when the provider guarantees it, final state, audio
time, and source lineage. Partial text may be replaced. A final update commits
one `ConversationTurn`.

PocketStation can prepare a response from stable partial text, but external
side effects still need an application commit barrier or idempotency policy.

## Interrupt without stopping input

When new speech begins, the conversation can cancel the active provider work
and the matching pending output while microphone capture, transcript input,
recording, and unrelated routes continue. Finite deadlines and retained-state
limits live in `ConversationConfig`.

An interruption report separates:

- provider task cancellation;
- Core output discarded before local delivery;
- Connector queue clearing when supported;
- receiver playout observation when supported;
- acoustic hearing, which may remain unavailable.

Do not describe sender cancellation as complete audible interruption when the
receiver cannot acknowledge playout.

## Run the current provider proof

`examples/debug_voice_ai.py` uses the example-owned OpenAI Realtime adapter so
its provider code remains visible and replaceable. Install the optional extra,
export `OPENAI_API_KEY`, and follow the example instructions:

```bash
python -m pip install 'pocketstation[voice-agent-debug]'
export OPENAI_API_KEY="..."
python examples/debug_voice_ai.py
```

The example records microphone, assistant output, and browser application
output separately. It does not claim AEC, exact loudspeaker playout, or
provider-history truncation.

After the Session stops, inspect `ConversationOutcome`, retained `VoiceEvent`
values, Session route metrics, and the recording outcome. A successful provider
close does not replace those media and lifecycle checks.
