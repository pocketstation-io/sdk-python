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
- The final result reports the local Core runtime `session_id` and the remote
  control-plane/Relay `relay_session_id` separately. Browser invitation
  redemption matches the latter; neither identity is relabeled as the other.
- Result construction and human/JSON Lines serialization are isolated in the
  focused `pocketstation_demo.result` module with direct schema and
  secret-boundary tests; `pocketstation_demo.demo` remains the small runnable
  workflow. Numeric application selectors are parsed as positive process IDs,
  while display names and bundle IDs remain strings.
- The allocated Relay Session enters cleanup ownership before capture, model,
  publication, or receiver setup. Relay and model routes are declared before
  entering Capture freezes the Session draft. Capture, publisher, and model
  declaration failures close the Relay without starting Capture; focused
  regression tests cover all three paths and the draft-freeze ordering.
- Focused synchronous/asyncio Relay and demo tests pass 47 cases. The complete
  source-tree suite passes 534 cases with 34 platform-dependent skips. Ruff and
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

## W21 Python performance and resource qualification

Candidate 105 replaces Candidate 104's invalid measurement design without
changing its budgets or overwriting its evidence. It qualifies the exact
Candidate 103 wheel in seven fresh measured processes after two discarded
warmups.

- One-source serialized round-trip cells retain all 300 raw latency samples and
  recompute p50, p95, p99, and maximum values.
- Separate two-source capacity cells deliver 1,000 frames per source with exact
  source, stream, route, count, and sequence checks. Every repetition exceeds
  the 500 aggregate frames/second gate.
- Separate two-source product-load cells pace 400 frames per source over at
  least four seconds. Every repetition exceeds 180 aggregate frames/second
  with zero drops or scheduling-deadline misses.
- Cancellation uses the public read default of 100 ms and remains below the
  unchanged 250 ms gate.
- Twenty synchronous and twenty asyncio lifecycle cycles per process return
  Python threads, operating-system threads, file descriptors, and unfinished
  asyncio tasks to their starting counts.
- The private interpreter, installed package, native module, dependency freeze,
  wheel payload, retained runner, and retained probe are hash-bound. Candidate
  104's report, failure diagnosis, reference review, and checksum file are also
  byte-pinned.
- The rejection-tested independent verifier passes the retained Candidate 105
  report. Focused qualification gates pass 41 tests with one platform skip;
  Ruff, formatting, and strict MyPy pass for the task-owned SDK files.

Classification is `SAFE-TO-TEST`. This is installed-wheel local component
evidence, not a new physical-device, browser, WAN, cross-platform, competitor,
or public-release claim. Candidate 103 remains the physical product-path
authority. No scaffold, mock runtime, or loopback transport was added.

## W21 Python wheel and source-distribution qualification

Candidate 106 adds one fail-closed packaging path for a fresh wheel and source
distribution from the exact committed SDK tree.

- The archive validator requires one native extension, installed typing files,
  the demo command, complete and non-duplicated `RECORD` hashes, MIT license and
  notice, the CycloneDX SBOM, and exact SDK/Core/Relay version agreement.
- The source distribution must contain both lockfiles, use only registry
  dependencies, reject checkout, path, Git, URL and absolute-manifest inputs,
  contain no compiled/build output, and rebuild without sibling repositories.
- Separate isolated consumers install the frozen wheel and the extracted
  source distribution, run `pip check`, execute the canonical Session and
  runtime-resource vector, type-check against the installed package with exact
  MyPy 2.3.1, rehash every installed `RECORD` file, inspect the command, and
  prove all owned files and entry points disappear after uninstall.
- The freezer requires at least 8 GiB of free disk, a clean committed source
  tree before and after the run, an external atomic output directory, exact
  retained membership, and frozen-byte revalidation after both consumers.
- Forty focused rejection and behavior tests pass. The final wheel/sdist build,
  independent verifier, and hash-backed acceptance run occur from the clean
  Candidate 106 commit; these source-tree tests alone do not accept the task.

Classification remains `SAFE-TO-TEST`. Resumed on 2026-09-26 for the authorized
new Python 0.1.5 release against Core 1.1.11 and Relay Connector 0.1.5. Own
package versions, lock entries and runtime compatibility values now agree.
The actual wheel/sdist and installed-consumer gates remain pending; no public
release or new platform/device claim follows from the metadata edit.
The unrelated native-extension fixture modification remains outside this task.

Resumption checks: all 9 native tests and strict Clippy pass; Ruff and strict
MyPy pass; Python reports 610 passed and 34 platform/fixture skips. The first
Python run exposed duplicate filenames in a packaging rejection fixture after
the version bump; distinct 0.1.5/0.1.6 inputs restore the intended ambiguity.
The two new freezer tests prove failed diagnostics survive and successful
scratch output is removed. Package NOTICE is installed only under dist-info
licenses, avoiding a shared top-level site-packages NOTICE file. The existing
consumer CLI retains both --artifact-format and --artifact-kind spellings.

The first real archive build failed before freezing: Maturin omitted uv.lock
from the sdist. Explicit sdist inclusion fixes the missing build input. Failed
artifacts and diagnostics remain retained. The consumer also verifies pip's
local installation origin against the supplied artifact before recording the
SDK's exact version, avoiding temporary artifact URLs in the dependency list;
a wrong-origin negative test rejects sibling input. Forty-four packaging tests
pass after these corrections. Actual corrected-artifact acceptance is pending.

## W21 Python native distribution qualification

Candidate 106 is now hash-accepted at fcf6422962f6b27ec7c5e11903e293152ba71fc2.
Both the actual macOS arm64 wheel and rebuilt source archive pass isolated
Session, typing, RECORD and uninstall checks. The independent verifier accepts
the exact frozen artifacts and rejects nine tampered proofs. Canonical unrelated
fixture dirt remains preserved; the qualified build checkout was clean.

Candidate 107 declares six native targets and 22 Python runtime cells. Its
qualification workflow builds each ABI3 wheel once, then runs those same bytes
on every declared interpreter. A separate Linux source rebuild and aggregate
artifact verifier are mandatory. Reports bind real host/runtime identity,
source commit, wheel hash, logs, installed Session execution, strict typing,
bounded saturation and uninstall. Twelve rejection/matrix tests pass locally.
No remote run or target completion is claimed before its retained result.
This workflow cannot publish; it uploads qualified artifacts for a later release.
