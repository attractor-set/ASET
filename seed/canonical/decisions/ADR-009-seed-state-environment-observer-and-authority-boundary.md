# ADR-009 — Separate Seed state, environment observations, observers and Authority recognition

## Status

Accepted. Supersedes the state-boundary and Authority-proof wording of ADR-008
for the active Seed 0.3 model. Historical release bundles are not rewritten.

## Context

The minimized formal model had already removed duplicated binding and Authority
maps, but several older descriptions still conflated four different things:

1. Seed-owned canonical state;
2. environment observations that can change a derived resolution;
3. read-only evaluation operations;
4. concrete evidence/signature/delegation mechanisms used to establish Authority.

The same legacy also caused the active canon to describe invalid material as if
its mere presence necessarily overrode a unique valid terminal record. That
would permit trivial denial-of-service by injecting malformed material.

## Decision

The active Seed boundary is:

- **Seed-owned mutable state:** `requestMeta` and `terminalMeta`;
- **environment state:** conflict observation only;
- **observer:** `EVALUATE_RESOLUTION` derives `Resolution` and effect permission
  and never mutates Seed-owned state;
- **Authority boundary:** Seed consumes an exact-binding local Authority
  recognition result. Concrete signatures, delegation chains, credentials and
  proof construction are outside Seed semantics;
- **invalid/non-authoritative material:** cannot create Authority, ALLOW or a
  valid conflict, and cannot override an otherwise unique valid terminal record;
- **conflict:** means conflict between valid terminal material and therefore
  derives `UNKNOWN`.

The canonical TLA projection is standalone. It does not import the handwritten
`SeedResolution` model. Behavioral equivalence is proved by explicit
instantiation in `SeedCanonRefinementProofs.tla`.

## Consequences

- `SeedStateChangesOnlyByRecognizedTransition` applies specifically to
  Seed-owned state, not environment state.
- `ConflictObservationPreservesSeedState` makes the environment boundary
  explicit.
- invalid and non-authoritative material have no TLA state slot or artificial
  stutter transition; their treatment is an admission/executable boundary.
- `EVALUATE_RESOLUTION` is an observer, not a transition in `Next`.
- concrete Authority grant-chain schemas are not part of the active 0.3
  protocol profile.
- finite Python model checking runs to saturation rather than relying on an
  arbitrary depth bound.
- assurance metadata distinguishes TLA-proved properties from partial external
  boundaries instead of claiming full formal coverage of concrete mechanisms.
