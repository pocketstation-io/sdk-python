# Qualify and publish the Python package

A release uses the exact seven distributions selected by a successful
`qualify-python-distribution` run: six ABI3 wheels and one source archive.
The run records 22 installed CPython consumers and one source rebuild. Every
report identifies the source commit, platform, interpreter and artifact hash.

The AEC candidate adds a mandatory installed native processor exercise. Each
consumer must deliver 400 processed frames, preserve the application stem,
reduce synthetic echo, retain near-end signal energy and stop successfully.
The aggregate verifier rejects missing results and mute-only success. These
generated PCM checks do not establish physical echo reduction or double-talk
speech quality. Existing 0.1.5 qualification results predate this requirement.

Build the new native dependency on every declared target. Meson, Ninja,
libclang, pkg-config, compiler tools and Rust `llvm-tools` must be available.
The bundled source invokes POSIX tools and searches Unix archive names;
installing prerequisites alone does not qualify Windows/MSVC. Keep the
Windows cells and resolve failures before publication. Add the exact wrapper,
WebRTC and bundled dependency license texts to the reviewed notices before
finalizing and qualifying release wheels.

## Prepare

Keep SDK version values consistent. Preserve the exact Core and Relay pins,
lockfiles, typing files, SDK license and third-party notices. The source build
uses Maturin 1.13.0. Its small Python build adapter describes the compiled
dependencies in each wheel's license metadata. The hosted workflow applies the
same operation after Linux wheel repair. Run this before any installed tests or
artifact hashing. Never change qualified distributions before publication.

`THIRD_PARTY_NOTICES.md` retains the reviewed Rust and Linux-library notices,
source links and hashes. `tools/dependency-notices.json` is its machine-readable
index. Regenerate both with `tools/collect_dependency_notices.py` from the
retained source inventories. Unknown package versions and altered notice texts
fail package validation. Update notices when changing dependencies or the
repair environment, then rebuild and qualify the resulting distributions.

Review current advisories and record applicability against the exact code.
[Security policy](../../SECURITY.md) lists the current PyO3 findings and the
reviewed usage limits. Keep device and hosted-runtime claims separate.

## Verify

Download the successful run's `qualified-distributions` artifact. From a clean
checkout of the same commit, run:

```bash
python tools/validate_wheel_matrix.py verify \
  --directory qualified \
  --source-commit "$(git rev-parse HEAD)" \
  --output independent-manifest.json
cmp qualified/release-manifest.json independent-manifest.json
```

The manifest must reproduce exactly. Preserve the artifact, job logs and GitHub
run metadata. Review every failed earlier run; a retry does not replace it.
The selected source commit must be contained in `main` before publication.

## Publish

Create `pocketstation-v<VERSION>` at the qualified source commit, then dispatch
`release-python` from `main` with that existing tag and `qualification_run_id`.
Only do this after release approval. Creating a GitHub release does not trigger
publication; the workflow has no release-event trigger.

The validation job checks the version, tag, source ancestry, originating
repository, workflow, successful run and complete consumer manifest. It copies
only the seven verified distributions into the publication input. The separate
`pypi` environment job rechecks their hashes and uploads them with Trusted
Publishing and PyPI attestations. It has no compiler or checkout and does not
rebuild the packages. No long-lived PyPI token is used.

After upload, compare PyPI's filenames and hashes with the accepted manifest.
Download the public wheel into a clean environment, check compatibility and
run the installed Session, typing and uninstall consumer. Retain the registry
receipt and attestation references with the GitHub release.

## Stop or recover

If any pre-publication check fails, keep the tag and evidence intact, diagnose
the cause and qualify a corrected candidate. Never replace published version
bytes, move a release tag, or silently substitute a newly built artifact.

If an upload is partial, inspect the public index before retrying. Existing
filenames must match the accepted hashes; handle a missing-file retry as a
separate reviewed action. The publisher does not enable `skip-existing`.

If a published version is defective, stop recommending it, document the issue
and issue a new patch version. Yanking is a separate maintainer action with a
recorded reason; it does not erase historical downloads. Applications can pin
a known-good version while evaluating the replacement. Preserve all receipts,
qualified bytes, attestations and failed-run diagnostics.
