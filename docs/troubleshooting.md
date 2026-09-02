# Troubleshoot capture, delivery, and shutdown

Start with the component that did not produce the expected result. PocketStation
keeps source opening, bounded delivery, provider work, Relay delivery,
recording, and receiver playout as separate observations.

## No application audio arrives

1. Call `pocketstation.discover_sources()` and confirm the application is
   present and producing audio.
2. Pass its display name or application identifier, or pass its process ID as
   a positive integer.
3. Check operating-system capture permission for the process running Python.
4. Inspect Session events for permission, source-open, and source-unavailable
   failures.

Do not treat an empty iterator as proof of silence when source opening failed.

If the application restarted, do not reuse its old process ID. Stop the current
Session, discover the source again, and create a new Session with
`Source.from_discovered()`. PocketStation reports
`EXPLICIT_REDISCOVERY_AND_NEW_SESSION` instead of silently selecting another
process or device.

## Permission changes are not reflected

`pocketstation.sources.microphone_permission_observation()` never prompts.
Treat `NOT_OBSERVABLE` as
unknown and use the typed Source open result. On macOS, restart the Python host
after changing screen-recording or microphone consent. On Windows and Linux,
verify that the current desktop user or service can access the selected audio
session and device.

Do not fall back from denied application capture to system mix or the default
microphone without a visible user choice. The fallback changes what audio the
application receives.

## Python misses frames

Inspect route capacity, queue depth, delivered frames, drops, and
discontinuities. The Python iterator is bounded; a consumer that does not read
on time can lose frames according to its route policy.

Move expensive model work into an Operator or provider worker. Do not perform
inference in the loop that must keep the frame Endpoint drained.

## Relay never becomes ready

Confirm that the control-plane and Relay URLs refer to services you operate or
to the rate-limited demo deployment. Verify the declared `required_buses`, then
wait for publisher readiness before creating an invitation.

If a receiver does not connect, keep publisher readiness and receiver readiness
as separate results. Neither result proves loudspeaker playout.

## Generated speech continues after interruption

Check each component separately:

1. provider response cancellation;
2. Core pending-output cancellation;
3. Connector queue clearing, when supported;
4. receiver playout clearing and acknowledgement, when supported.

Cancelling a Python task cannot recall audio already accepted by a transport or
receiver. Report receiver and acoustic state as unavailable when the receiver
does not expose it.

## Shutdown does not complete

Use finite provider and network deadlines. Close application-owned inputs when
no more frames will arrive. Request normal stop to drain accepted work, or
cancel when active asynchronous work must abort. Then inspect the `StopResult`,
provider outcome, and recording outcome for the component that did not stop.

When reporting an issue, include the PocketStation versions, operating system,
source selector, Session events, route metrics, and structured terminal error.
