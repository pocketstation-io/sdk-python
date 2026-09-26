# Publish a named AudioBus through Relay

Use `RelaySession` when a Session stem must reach a browser or another remote
receiver. The Python control client creates credentials and invitations; the
shared Rust Connector handles WebRTC publication.

## Connect to services you operate

```python
import pocketstation.aio as pks
from pocketstation.control import InvitationVisibility

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

Private invitations are the default. Their readable three-word URL contains an
independent secret in the URL fragment. `str()`, `repr()`, and ordinary JSON
serialization redact that URL; `expose_url()` is the explicit call for
displaying, copying, or opening it. Use
`visibility=InvitationVisibility.PUBLIC` only when possession of the
two-word alias itself should grant access.

The lower-level `ControlClient` also exposes the complete single-use lifecycle:

```python
metadata = await control.inspect_invitation(invitation.share_alias)
secret = invitation.share_link.expose_secret()
access = await control.redeem_invitation(
    invitation.share_alias,
    secret=secret,
)
print(metadata.expires_at, access.bus_id)
```

Inspection uses `GET` and never consumes access. Redemption always uses
`POST /v1/invitations/{locator}/redeem`; it returns one subscriber capability
for the exact selected AudioBus. Invalid, expired, revoked, and already-used
invitations all raise `InvitationUnavailableError` without revealing which
condition occurred.

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
