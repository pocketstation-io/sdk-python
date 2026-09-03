# Process audio and typed signals

Use an `Operator` when work consumes Session media or signals and emits a
derived result. Transcription, classification, translation, speech synthesis,
and policy checks are Operators when their outputs remain inside the Session.

A Python Operator runs on an off-realtime worker. Capture and unrelated
destinations continue while the Operator works. The Operator does not create a
second Session or call Python from a native capture callback.

## Declare the inputs and outputs

Each port has a name, a `SignalSpec`, and media requirements. The declaration
lets PocketStation reject incompatible connections before capture begins.

```python
from pocketstation.aio.operator_authoring import operator
from pocketstation.graph import PortSpec, SignalSpec
from pocketstation.operator_authoring import OperatorEmission, OperatorManifest

request = SignalSpec.text(role="request")
result = SignalSpec.text(role="result.final")

manifest = OperatorManifest(
    "io.example.uppercase.v1",
    inputs=(PortSpec.input("input", request),),
    outputs=(PortSpec.output("output", result),),
)


@operator(manifest)
async def uppercase(input_port, envelope):
    assert input_port == "input"
    return (OperatorEmission.text(str(envelope.payload).upper(), signal=result),)
```

Register the implementation once, declare an instance, then connect named
ports:

```python
operator = session.register_operator(uppercase).declare()
source.output("events").connect(operator.input("input"))
results = session.subscribe(operator.output("output"), signal=result)
```

`SignalSpec` supplies runtime and cross-language identity. Python type hints
help local development but are not used as a wire format.

## Emit generated audio

An Operator can return one exact PCM frame with `OperatorEmission.audio()`.
Call `reenter_audio()` on the declared output to turn that generated signal
into a normal audio stem:

```python
generated = operator.output("audio").reenter_audio()
generated.record("generated")
generated.send_to(destination)
```

The reentered stem can be recorded, polled, sent to a Connector, or connected
to another Operator. Core assigns its stream and stem identity and retains the
derivation from the Operator output.

## Keep model work finite

Set finite queue capacity and processing time in `OperatorManifest`. Implement
`cancel()` when provider work can be interrupted and `close()` to release the
provider exactly once. Return terminal signals only when the provider has
actually produced a terminal result.

Slow inference may saturate its own input. Inspect Operator input metrics,
route drops, and discontinuities. Do not run model inference in a frame iterator
that must keep another destination drained.

Use a `Connector` instead when the result leaves the Session and the provider
does not emit a Session signal. Use `AudioInput` when application or provider
code already owns PCM that should enter the Session.

Continue with [creating an integration](integrations.md) or [voice
composition](voice.md).
