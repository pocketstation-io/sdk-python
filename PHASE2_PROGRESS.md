# Phase 2 progress

## W21 installed Python real-path entry point

- The installed `pocketstation-demo` command now accepts explicit application,
  microphone, recording, model, download-policy, duration, browser, and output
  settings. The duration is finite and capped at one hour; the deadline ends
  the run even when transcript iteration is idle.
- The command sends only the control-plane origin. The control plane's WHIP and
  WHEP endpoints select the authoritative Relay origin; no default or
  environment-provided Relay URL is forwarded by the demo.
- Application and microphone remain separate stems. The command creates one
  readable single-use invitation for each exact AudioBus and waits for at least
  two active receiver subscriptions before its timed capture interval begins.
- Human output labels both invitations. JSON Lines output is an explicit
  secret-exposure boundary for ephemeral Lab piping: each invitation line
  contains only `event`, `bus_id`, and `share_url`, while the final result line
  contains no capability. The final result carries exact application and
  microphone Source identities from the completed public recording manifest,
  Session termination and failure counters, manifest and per-stem outcomes,
  terminal Relay bus outcomes, and available source/route drop and
  discontinuity observations. Ordinary invitation string and representation
  paths remain redacted.
- The final result names two precise public-observation limits instead of
  inferring them: live capture Stems do not expose their Source IDs before the
  recording manifest finalizes, and Relay subscription readiness does not
  prove browser decode or loudspeaker playout.
- Focused synchronous/asyncio Relay and demo tests pass 33 cases. The complete
  source-tree suite passes 520 cases with 34 platform-dependent skips. Ruff and
  strict MyPy pass.
- This change makes the installed artifact finite and automatable. Physical
  application/microphone capture, real model inference, two Chromium receivers,
  recording lineage, fault isolation, and resource return remain owned by the
  Lab real-path acceptance run; no such claim is made from these component
  tests.

## W21 receiver word-alias SDK projection

Candidate 95 projects the accepted control-plane invitation lifecycle into the
synchronous and asyncio Python clients and the Relay helper.

Implemented behavior:

- private and public invitations scoped to one exact AudioBus;
- separate opaque join codes and readable aliases;
- non-consuming metadata inspection;
- explicit single-use `POST` redemption returning exact-bus receiver access;
- one typed unavailable outcome for invalid, expired, revoked, or replayed
  invitations;
- redacted private URLs and fragment secrets, with explicit exposure methods;
- readable Relay share URLs without exposing Session identity or subscriber
  capabilities.

Acceptance run on 2026-09-26:

```text
ruff: PASS
mypy (four changed public modules): PASS
pytest: 484 passed, 34 skipped
installed wheel consumer: PASS from site-packages
```

The proof uses bounded mock HTTP peers for invitation lifecycle semantics and a
real built wheel for installed-package behavior. It does not claim deployed
service, WAN, browser, or physical-device proof. No scaffold or runtime mock is
added to the package.
