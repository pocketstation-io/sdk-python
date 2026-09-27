# Phase 2 progress

## W21 Python Core dependency refresh — Candidate 121

The binding now pins public Core 1.1.12 in production and conformance builds.
Compatibility facts, archive-validator expectations and synthetic package fixtures
match. Only the Core version/checksum changes in Cargo.lock; the other 290 locked
dependency versions and Relay Connector 0.1.5 remain unchanged. Notices are
regenerated from the complete retained inventory with Core 1.1.12 license texts.

The SDK own version is not changed in this dependency-preparation task; existing
public Python 0.1.5 artifacts remain immutable and use Core 1.1.11. Release notes
distinguish the unpublished source candidate. No capture logic is duplicated in
the wrapper, no new runtime scaffold/mock and no new physical-device claim.

Local acceptance: 55 packaging/notice/release rejection tests pass; Ruff checks
and formatting pass; strict MyPy passes 70 source files; Rust formatting and
public-documentation wording checks pass. Only Core changes in the complete
locked dependency inventory. Exact-source CI and six native wheels with 22
installed CPython consumers remain required. Package publication
requires a separate exact-version release task after successful qualification.


Source CI 36291261583 exposed a synchronization error in the source-truth test:
the first aggregate audio frame can be from the application before the independent
microphone has delivered. The test now waits within the original one-second
budget for both per-source activity and signal observations, then retains every
native-format, microphone-signal and recovery assertion. Missing microphone data
still fails the deadline; no fixed delay, retry of a failed test or runtime change.
The failed log is preserved and fresh exact-source CI/qualification is required.

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

Run 36252864677 built all six wheels and passed the Linux standalone source
rebuild. Installed Linux wheel consumers exposed a harness standards error:
auditwheel adds a second SBOM for repaired native libraries, while the installed
check incorrectly required exactly one JSON SBOM in total. PEP 770 permits
multiple SBOM files. The explicit standards review is retained with Candidate
107 evidence. The check now requires the named PocketStation SBOM, retains
repair SBOMs, and still verifies every RECORD size/hash and complete uninstall.
Regression cases cover accepted additional SBOMs, missing package SBOM, and
changed repair-SBOM bytes. The failed run remains retained; a complete new
matrix must pass before qualification is accepted.

## W21 Python OSS release readiness

Candidate 107 is hash-accepted at fc4673b9a9680912d9131cf107f25af3ee3dc2b1.
Run 36253613676 passes six wheels, 22 installed CPython runtime cells and the
standalone Linux source rebuild. An independent clean-checkout verifier
reproduces the CI manifest byte for byte. The first failed run is retained.
This is hosted installed-package evidence, with no new device or latency claim.

Candidate 108 audits the actual wheel dependency SBOMs before publication.
The union contains 248 Rust package versions, plus ALSA, OpenSSL and PipeWire
RPM packages added during Linux repair. Retained crate/upstream license and
copyright texts and exact source-RPM references now produce one self-contained
THIRD_PARTY_NOTICES.md. All six actual SBOMs have complete notice coverage and
valid SPDX expressions. Notice content hashes and unknown component versions
are checked before a wheel can qualify.

The source package remains MIT. A small PEP 517 wrapper delegates compilation
to pinned Maturin 1.13.0 and finalizes each wheel's License-Expression from its
own SBOM before qualification and hashing. The hosted wheel workflow applies
the same operation after repair. The wrapper and notices ship in the standalone
source archive. Runtime code is unchanged. Forty-nine focused packaging,
notice, metadata-preservation, integrity and uninstall tests pass; Ruff and the
unchanged uv lock check pass. Final archive rebuild and release readiness are
still pending; no tag, public release, upload or deployment has occurred.

Release preparation now independently verifies the complete qualified manifest,
successful same-source GitHub run and seven exact distribution hashes before
copying any files. The publication workflow uses a separate minimal-permission
PyPI OIDC job, rechecks those copies, and never rebuilds or silently skips an
existing release. Tests reject changed files/manifests and wrong run origins.
Support, security, contribution and release instructions describe the actual
matrix and honest support limits. The native dependency review records two
PyO3 0.27.2 advisories affecting APIs unused in the reviewed SDK; it does not
claim the dependency is patched or formal whole-program reachability proof.
Public documentation language is checked before the final hosted run.
Sixty-four focused checks pass. Final same-commit hosted source CI, all native
distributions and independent installed reproduction remain mandatory.
Git attributes preserve exact embedded notice bytes on Windows checkouts;
newline conversion must not invalidate original source-notice hashes.

Final-source run 36256736846 exposed a notice gap in the standalone source
rebuild: its Maturin SBOM includes alternate-target dependencies omitted from
the six explicit-target wheel union. The first absent entry was bumpalo 3.20.3.
The original failing archive and consumer log are retained. Notices now cover
all 291 locked Cargo dependency versions plus three Linux repair packages;
r-efi's license and copyright are retained from its AUTHORS file. A regression
check binds notice coverage to the complete Cargo.lock, so source-only entries
cannot be omitted. Runtime and dependency versions are unchanged. Sixty-five
focused tests pass; a new full hosted qualification remains required.

The full standalone source CI exposed a pre-existing factory dependency in
test collection: Candidate105 report tests imported a verifier and historical
artifacts from two directories above the SDK. Those 23 factory evidence checks
now live in the factory's tools/tests/test_python_performance_evidence.py. All
10 portable runner checks remain in the SDK and share the same synthetic
repetition fixture. The complete 33 checks pass locally with no thresholds or
evidence validation removed. Historical accepted reports are unchanged.
After both corrections the full local SDK suite reports 624 passed and 34
platform/fixture skips; the 23 relocated factory evidence checks also pass.

Run 36257253732 passes the corrected source rebuild; the independent macOS
installed consumer and physical app/microphone/model/recording/browser proof
also pass from da80b19. The full source CI reaches the tests and exposes one
remaining test-only mismatch: conformance_source_replacement_error is correctly
compiled only with conformance-fixtures, but the native stub comparison omitted
it from its explicit test-helper exclusions. The comparison now accounts for
that exact helper while still forbidding it in stubs. Release consumers reject
all three conformance-only exports. The new notice test/generator also declares
its packaging 26.3 development dependency directly. This changes no native
runtime or public API. Final same-commit source and distribution CI must pass.
Both source-CI jobs now have explicit 45-minute upper limits, matching the
finite qualification gates. Focused API/notice/archive checks: 49 passed;
Ruff and the updated uv lock consistency check pass.

The completed Windows jobs additionally exposed a file-URI conversion bug in
the historical benchmark runner: file:///C:/... was treated as a literal
/C:/... filesystem name. Standard-library url2pathname now handles native
Windows paths, with remote hosts, query/fragment additions and sibling wheels
rejected. The existing cross-platform positive test covers the reported case;
four new rejection cases pass. No measurement thresholds or historical frozen
Candidate105 harness/evidence changed. The short-lived c050900 CI runs are
superseded because they still contain this known failing Windows check.

The next full CI passes Linux/macOS Python tests and the source rebuild, and
the final macOS wheel again passes isolated installation and the complete
finite physical workflow. Linux CI's separate inspection-wheel build exposed
a configuration mismatch: automatic repair bundled Ubuntu libasound2t64,
whose version is not in the release's reviewed manylinux library inventory.
Source CI now builds an unbundled linux wheel against its installed development
libraries, as the standalone source consumer already does. The unchanged
qualify-distribution workflow remains the only release-artifact producer and
still requires repaired manylinux wheels, all notices and every installed
runtime check. Unknown bundled libraries still fail closed; no release notice
requirement or declared-platform test is removed.


## 2026-09-26 — Publisher SPDX parser compatibility (Candidate 112)

The exact Python 0.1.5 artifacts at e58b5b1 passed all 31 qualification jobs,
all seven source-CI jobs, isolated installed execution and the finite physical
app/microphone workflow. Release attempt 36261579822 stopped before upload:
the pinned publisher contains packaging 25.0, which rejects nested license
parentheses. The same seven unchanged files fail in that exact container and
pass in the current PyPA v1.14.2 container (packaging 26.2 / Twine 7.0.0).
A minimal parser differential isolates the nested-parenthesis bug fixed by
pypa/packaging#931.

Update only the publisher action pin to dc37677b2e1c63e2034f94d8a5b11f265b73ba33,
and check metadata with that exact container before upload. A verification-only
dispatch runs the full validation path while skipping the publisher job. No
license, distribution byte, release tag, runtime code or product claim changes.
The local old/new container differential passes; protected PR integration and
hosted verification-only execution are the remaining gates before retrying
publication of the already accepted files. No scaffold is introduced.


## 2026-09-27 — Readable navigation preserves existing join authority

Words now navigate into the original opaque join-code capability flow. Two- and
three-word visibility is deprecated formatting only. Both URL formats carry
`#join=…` and always redact credentials. New clients POST opaque codes in the
body to `/v1/join`; readable paths require the matching body `join_code`.
Deprecated secret options alias that same code and reject obsolete separate
secrets. Redirects never forward credentials. Regression cases cover words
alone, conflicting credentials, wire equivalence, redaction and opaque URLs.

Validation: 634 tests passed / 34 existing conditional skips; focused control/Relay 83 passed; strict mypy 63 modules and scoped Ruff passed. Native payload unchanged; installed
archive / real service gates are recorded separately by the integrated Lab.
Staff review: purpose/API boundary is SDK control-client compatibility; enables
existing exact-bus browser joining, no new authorization model or capture path.
Unit HTTP fixtures are MOCKED and make no new real-media claim. No live scaffold
introduced; inventory n/a. CODE_PROTOCOL whitespace/type/test gates passed.
Decision: SAFE-TO-TEST pending exact packaged live integration. No release.

### Follow-up: malformed response diagnostic redaction

Suppress raw JSON decoder causes in both clients so malformed redemption bodies
cannot appear in ordinary chained tracebacks. Two regression cases pass with
85 focused tests, strict mypy and Ruff. No native or wire changes; final wheel
is a separate immutable follow-up artifact. Staff review: PASS, no scaffold.

### Follow-up: detach sensitive exception objects

Raise sanitized transport and decode failures outside exception handlers, so
both `__cause__` and `__context__` are absent instead of merely hidden in normal
tracebacks. Sync/async regression assertions, 85 focused tests, Ruff and strict
mypy pass. No wire/native changes; installed artifact revision remains explicit.

### Qualification fixture correction

Update installed_consumer's retained invitation fixture to the canonical
`#join` URL and `join_code` body; assert words alone cannot authorize and no
join credential enters HTTP URLs. The complete installed consumer passes with
the unchanged final production wheel. This modifies qualification tests only;
package bytes and runtime source remain those of b8fdd14. Ruff passes.
