# Security

Request a private reporting channel by opening a GitHub issue titled
“Security contact request”, addressed to the maintainer listed in CODEOWNERS.
Include no exploit, credentials, audio, personal data or affected deployment
addresses in that public request. Private vulnerability reporting is currently
disabled for this repository; do not assume the GitHub advisory form is usable.

Security fixes target the latest published version. Older versions receive no
promised backports. This is an early developer package with no response-time
or remediation SLA. Reports should identify the exact package version, Python,
OS, architecture, dependency advisory and a minimal reproduction using
non-sensitive generated input.

Before release, review the exact wheel SBOMs and dependency notices, current
advisories, source changes, installed consumers and package hashes. Reachable
memory-safety issues, credential disclosure and unresolved high-impact findings
block publication. Record the reasoning for any finding assessed as inapplicable;
a scanner result alone does not establish whether an SDK operation reaches it.

## Reviewed dependency findings for 0.1.5

The retained September 26 scan reports PyO3 0.27.2 affected by:

- [RUSTSEC-2026-0176](https://rustsec.org/advisories/RUSTSEC-2026-0176.html):
  unchecked arithmetic in list/tuple iterator `nth` and `nth_back`.
- [RUSTSEC-2026-0177](https://rustsec.org/advisories/RUSTSEC-2026-0177.html):
  a missing `Sync` requirement for `PyCFunction::new_closure`.

The SDK calls none of these APIs, uses no `skip` or `step_by` operation on a
Python list/tuple iterator, and creates no PyCFunction closure. Inspection of
the pinned PyO3 implementation finds these uses in their implementations,
tests and examples, rather than the conversion operations used by the SDK.
These findings are assessed as not reached by the reviewed SDK operations;
this is a source review, not a formal whole-program proof. PyO3 itself remains
an affected version. A future dependency upgrade should use at least 0.29.0,
and any new use of these APIs requires this assessment to be revisited.

This package does not qualify free-threaded CPython. Native extensions and
user-supplied provider code execute with the application's privileges and must
come from trusted sources. Audio capture requires the host's consent and device
permissions. Keep source capabilities and private invitation fragments out of
logs, issue reports and saved diagnostics.
