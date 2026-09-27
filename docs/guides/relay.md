# Publish a named AudioBus through Relay

Use `RelaySession` when a Session stem must reach a browser or another remote
receiver. The Python control client creates credentials and invitations; the
shared Rust Connector handles WebRTC publication.

## Connect to services you operate

```python
import pocketstation.aio as pks

remote = await pks.RelaySession.create(
    control_plane_url="https://control.example.com",
    required_buses=("application",),
)
live = pks.capture(application="Spotify", stream_audio=False)
live.application_stem.publish(remote.publisher(live.session), "application")

async with remote, live:
    invitation = await remote.wait_for_publisher_and_invitation(
        bus_id="application",
        timeout_seconds=30,
    )
    print(invitation.share_alias, invitation.expose_url())
    await remote.wait_for_receiver(timeout_seconds=30)
```

Declare every bus before starting the Session. Create an invitation only after
publisher readiness succeeds, and delete the remote Session during shutdown.

Readable words are navigation labels. Every link carries the original opaque
join credential in `#join=…`; possession of words alone never grants access.
Omit formatting options to use the Relay service setting: its default tries
two words, then three when names collide. Set `word_count` to an integer from 2 through 15 for an explicit length.
Omission or Python `None` keeps the service default; booleans and fractions
are rejected. The returned invitation exposes its validated `word_count`.
New long-name responses must declare that count and fit within 134 ASCII bytes.
Older two/three-word responses remain supported without the count field.
An explicit requested count must match the returned name. `visibility` remains a deprecated two-word (`PUBLIC`)
or three-word (`PRIVATE`) compatibility option; conflicting options fail. Both formats redact their credential and
URL in `str()`, `repr()`, and ordinary JSON serialization. Use `expose_url()`
only when intentionally displaying, copying, or opening the complete link.

The lower-level `ControlClient` uses the existing single-use join requests:

```python
metadata = await control.inspect_invitation(invitation.share_alias)
access = await control.redeem_invitation(
    invitation.share_alias,
    join_code=invitation.join_code,
)
print(metadata.expires_at, access.bus_id)
```

Inspection accepts readable labels, uses `GET`, and never consumes access.
Redemption uses `POST /v1/join/{words}` with `join_code` in the JSON body.
Passing the opaque `SecretToken` directly uses `POST /v1/join`, keeping the
credential out of HTTP URLs. Both return the same exact-bus subscriber access;
invalid, expired, revoked, and already-used credentials raise
`InvitationUnavailableError`. The deprecated `secret` argument and
`expose_secret()` link method alias this same credential, never a separate factor.

## Use the shared demo service for a quick test

`examples/stream_any_app_audio.py` uses the small rate-limited demo deployment
through `pocketstation_demo`. The deployment may reject a session when its
capacity is in use and is not a hosted production service.

Set the control-plane URL to run the same example against services you operate.
The control plane returns the authoritative Relay endpoints; the application
does not configure a second service URL:

```bash
export POCKETSTATION_CONTROL_URL="https://control.example.com"
python examples/stream_any_app_audio.py
```

Do not put control-plane secrets, signing keys, or shared internal credentials
in application code. Applications receive scoped session credentials from the
control plane.

## Know what readiness proves

Publisher readiness confirms that Relay accepted the declared publication.
Receiver readiness confirms an active subscription. Browser WebRTC statistics
can report received and jitter-buffered samples.

Those observations do not prove which sample a loudspeaker played. End-to-end
audible cancellation requires a receiver capability that clears playout and
acknowledges the last rendered sample.

Readable names such as `owl-sun`, `rice-river`, `silly-mountain` and
`lemon-corpus` are navigation only. Use the complete generated share URL or
matching opaque join code. The client accepts short words and retained legacy
compound syntax; Relay owns the vocabulary and never exposes a grammar prefix
in the readable address.
