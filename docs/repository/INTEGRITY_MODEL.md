# ASET integrity model

ASET keeps four identity domains separate. No repository-wide file manifest is part of the active integrity model.

## 1. Normative canon identity

The normative Seed is identified by `seed/canonical/CANON_PACKAGE.json`. Its `package_digest` is computed only from the files in the canonical package and therefore identifies the normative machine-readable canon independently from unrelated repository files.

Changing canonical package material changes the canonical package digest. Published Seed compatibility targets additionally bind the exact release tag and release commit.

## 2. Repository source identity

The source repository is identified by the exact Git commit and tree. `tools/check_repository_source_identity.py` requires the tracked worktree and index to equal `HEAD` before a release gate may pass.

Git is the source-of-truth inventory for repository bytes. A second repository-wide hash inventory would duplicate Git identity and would incorrectly couple normative integrity to documentation, CI, audit notes and other non-canonical files.

## 3. Distribution identity

Repository snapshots and other release artifacts are deterministic outputs from an exact committed source tree. Each published artifact is independently SHA-256 bound. `tools/build_release.py --verify-determinism` rebuilds the repository snapshot twice from committed Git bytes and requires identical archive digests.

Artifact checksums identify distributed bytes; they do not define Seed semantics.

## 4. External assurance-perimeter identity

`assurance/seed-recognition-boundary/ASSURANCE_PACKAGE.json` identifies a
public non-normative v60 proof perimeter around the frozen Seed. Its digest covers only the
perimeter documentation, publication provenance and all 34 active v60 TLA+ modules, while its subject binding points
inward to the exact canonical package digest, machine-readable Seed model,
`SeedResolution.tla` and existing canon-to-TLA relation.

The direction is intentionally asymmetric: the assurance package depends on the
canonical identity, but the canonical package does not contain or hash the
assurance package. This prevents proof/tooling maintenance from redefining Seed
semantics while making any change to the frozen subject fail the perimeter
closed until deliberate re-baselining.

## Historical manifests

Historical releases and Background IP records may reference earlier `MANIFEST.json` files and their SHA-256 values. Those references identify immutable historical commits and remain valid evidence. They are not an active repository-integrity mechanism and must not be rewritten merely because the current repository no longer maintains a repository-wide manifest.

The external Seed recognition-boundary perimeter also pins the TLAPM toolchain-notice multiset. This is an assurance/output-integrity control only; it neither changes nor enters the canonical Seed identity.
