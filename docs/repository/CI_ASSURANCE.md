# CI assurance architecture

ASET CI is divided into independent assurance contours. Multiple workflow
names do not count as independent evidence when they execute the same
aggregate command.

## Candidate canon consistency

`.github/workflows/seed-ci.yml` checks the candidate checkout against itself:

- deterministic generated views;
- language policy;
- machine-canon and canon-package validity;
- finite-state saturation output;
- assurance, proof traceability and canon-to-TLA refinement integrity;
- frozen-Seed recognition-boundary perimeter identity and executable oracle;
- specification tests;
- critical Ruff rules;
- active-documentation claims.

This contour proves internal candidate consistency. It does not authorize a
normative change.

## Formal and adversarial assurance

`.github/workflows/production-assurance.yml` independently executes:

- the Python finite-state model to saturation, reporting unique labelled graph edges separately from generated action instances;
- the checked formal-property registry;
- TLC over the committed TLA+ model;
- TLAPS over the committed safety proof module;
- TLAPS over the source-locked canon-to-TLA behavioral-equivalence proof;
- TLAPS replay of the complete active public v60 Seed recognition-boundary assurance corpus (20 proof modules, 2257 obligations).

The recognition-boundary perimeter is deliberately outside the normative
`seed/canonical/` package. It binds inward to the exact frozen canonical package,
`SeedResolution.tla` and the existing canon-to-TLA relation. The repository
release runner treats it as a mandatory precondition, but it is not assigned an
`ASET-GATE-*` identifier because the canonical gate registry is itself frozen
normative material. See
`assurance/seed-recognition-boundary/README.md`.

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
tested as external processes. The normative runner verifies mandatory operations,
response schemas, exact case identity, timeout behaviour and deterministic
replay.

An implementation adapter cannot issue its own PASS verdict.

A separate non-normative runner, `tools/run_seed_recognition_assurance.py`,
reuses the same frozen external adapter protocol with a deterministic 24-case
witness set derived from the public v60 recognition-boundary analysis. It checks
protocol-observable binding, previous-commitment, terminal-authority, decision,
idempotence, immutability and effective-conflict distinctions without modifying
the canonical 25-case conformance corpus. Its verdict is
`SEED_RECOGNITION_ASSURANCE_VERDICT`, not normative Seed conformance. See
`assurance/seed-implementation-assurance/README.md`.

## Claim boundary

The formal contour establishes:

- exhaustive reachable-state assurance for the committed finite Python configuration, with saturation asserted and graph-edge counts deduplicated from equivalent action instantiations;
- unbounded deductive safety for the committed abstract TLA+ projection;
- byte-for-byte parity of a standalone deterministic canonical projection generated from the exact machine-readable Seed identity;
- TLAPS-proved behavioral equivalence between that standalone projection and `SeedResolution.tla`;
- a public non-normative external v60 assurance corpus covering recognition cardinality/binding, independent and minimal recognition boundaries, bidirectional canonical-phase refinement, payload observability, exact reachable cardinality and the finite faithful-code lower bound.

The recognition-boundary theorem is scoped to exact reachable local recognition
semantics. It does not prove universal system minimality, minimum implementation
variable count, Shannon entropy, global Seed bit size or implementation
refinement without a separate witness.

The canon-to-TLA theorem is scoped to the declared abstraction profile. It does not establish:

- equivalence of every natural-language sentence;
- concrete Binding/digest construction;
- concrete Authority-recognition evidence, signature or delegation-mechanism construction;
- implementation refinement or production readiness;
- liveness;
- cryptographic primitive security;
- factual truth of external evidence;
- external certification.

### TLAPM notice hygiene

The Seed recognition-boundary replay pins the exact TLAPM `4600b24` generated-pattern notice multiset in `assurance/seed-recognition-boundary/TOOLCHAIN_NOTICES.json`. Known raw notice lines are summarized; any missing or additional warning fails the perimeter. The formal v60 source is not rewritten merely to suppress toolchain-generated diagnostics.
