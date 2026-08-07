# CI assurance architecture

ASET CI is divided into independent assurance contours. Multiple workflow
names do not count as independent evidence when they execute the same
aggregate command.

## Candidate canon consistency

`.github/workflows/seed-ci.yml` checks the candidate checkout against itself:

- deterministic generated views;
- language policy;
- machine-canon and canon-package validity;
- bounded model output;
- assurance, proof traceability and canon-to-TLA refinement integrity;
- specification tests;
- critical Ruff rules;
- active-documentation claims.

This contour proves internal candidate consistency. It does not authorize a
normative change.

## Formal and adversarial assurance

`.github/workflows/production-assurance.yml` independently executes:

- the bounded Python state-space model;
- the checked formal-property registry;
- TLC over the committed TLA+ model;
- TLAPS over the committed safety proof module;
- TLAPS over the source-locked canon-to-TLA behavioral-equivalence proof.

TLC is downloaded from the pinned upstream TLA+ v1.7.4 release and its
configured identity is verified before execution.

TLAPM is downloaded from the pinned `1.6.0-pre` Linux x86-64 asset. CI verifies
archive SHA-256:

    bfa5e5350ac1ec7202feecad0a4a71a5bb58c16a49660448b35b6f371ba9e2f5

CI also requires TLAPM version output:

    4600b24

This corresponds to commit:

    4600b24c6d95a25ff081ad37b63b2a01c29d43a5

Downloaded formal tools are assurance instruments. They are not normative
ASET artifacts and have no semantic or implementation precedence.

## Approved-to-candidate compatibility

`.github/workflows/release-candidate.yml` compares the candidate machine canon
with the approved base ref before running the repository release gate.

Detected change classes are:

- `NONE`;
- `MONOTONIC_EXTENSION`;
- `BREAKING`.

Every non-empty normative change requires an exact candidate-model digest and
an explicit change declaration. A declaration records and exposes a breaking
change; it does not make the change non-breaking.

## Implementation conformance boundary

Implementation repositories consume the published canon package and are
tested as external processes. The runner verifies mandatory operations,
response schemas, exact case identity, timeout behaviour and deterministic
replay.

An implementation adapter cannot issue its own PASS verdict.

## Claim boundary

The formal contour establishes:

- bounded model assurance for the committed finite configuration;
- unbounded deductive safety for the committed abstract TLA+ projection;
- byte-for-byte parity of the deterministic canonical projection generated from the exact machine-readable Seed identity;
- TLAPS-proved behavioral equivalence between that declared projection and `SeedResolution.tla`.

The canon-to-TLA theorem is scoped to the declared abstraction profile. It does not establish:

- equivalence of every natural-language sentence;
- concrete Binding/digest construction;
- concrete Authority grant-chain construction;
- implementation refinement or production readiness;
- liveness;
- cryptographic primitive security;
- factual truth of external evidence;
- external certification.
