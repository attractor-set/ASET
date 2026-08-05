# CI assurance architecture

ASET CI is divided into independent assurance contours. Multiple workflow names do not count as independent evidence when they execute the same aggregate command.

## Candidate canon consistency

`.github/workflows/seed-ci.yml` checks the candidate checkout against itself:

- deterministic generated views;
- language policy;
- machine-canon and canon-package validity;
- bounded model output;
- assurance traceability;
- specification tests;
- critical Ruff rules;
- active-documentation claims.

This contour proves internal candidate consistency. It does not authorize a normative change.

## Formal and adversarial assurance

`.github/workflows/production-assurance.yml` independently executes:

- the bounded Python state-space model;
- the checked formal-property registry;
- component model checks;
- TLC over the committed TLA+ model;
- black-box and adversarial component audits from a built snapshot.

TLC is downloaded from the pinned upstream TLA+ v1.7.4 release and its published SHA-1 identity is verified before execution. The downloaded tool is not part of the ASET canon and has no semantic precedence.

## Approved-to-candidate compatibility

`.github/workflows/release-candidate.yml` compares the candidate machine canon with the approved base ref before running the complete repository release gate.

Detected change classes are:

- `NONE`;
- `MONOTONIC_EXTENSION`;
- `BREAKING`.

Every non-empty normative change requires an exact candidate-model digest and an explicit change declaration. A declaration records and exposes a breaking change; it does not make the change non-breaking.

## Implementation conformance boundary

Implementation repositories consume the published canon package and are tested as external processes. The runner verifies all mandatory operations, response schemas, exact case identity, timeout behaviour and deterministic replay. An implementation adapter cannot issue its own PASS verdict.

## Claim boundary

These checks provide bounded, reproducible assurance. They do not establish complete mathematical proof, production readiness of an implementation, factual truth of external evidence or external certification.
