# Phase 2 progress

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
