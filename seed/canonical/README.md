# ASET Seed 0.3 minimal resolution core

ASET Seed is a local resolution-recognition kernel.

    Resolution = UNKNOWN | ALLOW | BLOCK
    EffectPermitted(r) iff ResolutionOf(r) = ALLOW

An accepted terminal `ALLOW` or `BLOCK` is immutable and exact-binding.
`UNKNOWN` is derived when no authoritative accepted terminal record is
established or when additional distinct valid terminal material conflicts with
an accepted terminal resolution. Invalid or non-authoritative material cannot
create Authority, create `ALLOW`, create a valid conflict, or replace an
accepted authoritative terminal record.

Seed normatively defines:

- exact `ResolutionBinding`;
- fresh request identity and reconsideration commitment;
- exact-binding local Authority recognition as an admission boundary;
- immutable content-addressed terminal records;
- accepted-terminal uniqueness, conflict soundness and fail-closed evaluation;
- implementation-neutral observable semantics.

Concrete policy evaluation, evidence acquisition, signatures, delegation-chain
construction, workflow, federation, persistence, retention/compaction,
cryptographic accumulators and enforcement are outside Seed.

## State boundary

The formal model deliberately distinguishes ownership:

- Seed-owned mutable state: `requestMeta`, `terminalMeta`;
- environment state: `conflicts`;
- pure observer: `EvaluateResolution(r)`.

`Requests` and `TerminalRequests` are derived from partial-function domains.
Terminal binding is derived from immutable request metadata. Environment
conflict observation cannot mutate Seed-owned state.

## Assurance closure

The active assurance surface contains:

- 12 canonical requirements and 12 canonical invariants;
- 3 canonical operations (`SEED-OP-001..003`): two state transitions and one observer;
- 25 portable conformance cases;
- 13 semantic mutations;
- 14 TLA/TLC properties: 10 state invariants and 4 temporal properties;
- finite Python state exploration to saturation for the published fixture;
- independent TLC checking;
- unbounded TLAPS safety proof for the abstract TLA model;
- a standalone generated canonical TLA projection with TLAPS-proved behavioral
  equivalence to `SeedResolution.tla`.

The TLA proof boundary intentionally abstracts exact Binding construction,
Authority-recognition establishment and recognized terminal-commitment
establishment. External invalid/non-authoritative material processing is checked
at executable/conformance boundaries rather than represented as Seed state.

The normative source remains `seed/canonical/source/seed-model.json`. Generated
projections, TLA modules and reference implementations have no normative
precedence.
