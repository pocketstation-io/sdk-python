# Call and agent audio

PocketStation does not need a second media engine or a provider enum to work
with LiveKit, Daily, Pipecat, Vapi, SIP, or a custom WebSocket. An adapter maps
the provider's decoded PCM into `AudioInput` and maps a Session stream into an
async audio Connector.

```python
import pocketstation.aio as pks_aio

session = pks_aio.Session(sample_rate_hz=16_000)
caller = session.audio_input("caller", sample_rate_hz=16_000)
publisher = attach_audio_sender(
    session,
    agent_audio,
    call.send_pcm,
    connector_id="io.acme.call.v1",
    package_version="1.0.0",
)
await ingest_audio(caller, call.incoming_pcm())
```

The provider adapter still owns authentication, codec conversion, track or
participant selection, resampling into the Session's one concrete sample
contract, reconnect policy, and remote metadata transport. Core
owns the source/stream/stem identity, bounded queues, discontinuities, routing,
recording, Operator execution, Connector lifecycle, and terminal outcome.

`call.send_pcm` must accept PocketStation's `AudioFrame` and convert it to the
provider's required frame type. `call.incoming_pcm()` yields `IncomingAudio`
with C-contiguous float32 samples and marks provider reconnects or packet gaps
as discontinuities. No Python function runs on a capture callback or realtime
partition.
