# ASET Seed 0.3 minimal strong core

ASET Seed is a local resolution-recognition kernel.

    Resolution = UNKNOWN | ALLOW | BLOCK
    EffectPermitted(binding) iff one unique valid exact-binding
    terminal record is ALLOW

`UNKNOWN` is derived when no unique valid terminal record exists. `BLOCK` is
an explicit terminal prohibition. Both are fail-closed.

Seed normatively defines exact binding, local Authority roots, attenuating
Authority proof, terminal uniqueness, immutable content-addressed records and
fresh reconsideration identifiers and recognized immutable predecessor commitments.

Policy evaluation, evidence acquisition, workflow, federation, persistence,
retention/compaction and concrete terminal-commitment accumulation are extension
or implementation concerns. Seed does not require predecessor requests or records
to remain physically retained after recognition evidence has been preserved.

## Assurance closure

The published safety contract has complete machine traceability:

- 12/12 canonical requirements covered;
- 12/12 canonical invariants covered;
- 3/3 transitions covered positively and negatively;
- 16 bounded TLA+/TLC properties;
- 16/16 registered TLA+/TLC safety properties covered by unbounded TLAPS proof;
- 4 exact executable-or-static properties;
- 24 portable conformance cases;
- 13 semantic mutations, all required to be killed.

The unbounded safety proof applies to the committed abstract TLA+ safety
projection. It establishes all eleven registered state invariants and all five
registered temporal safety properties for every behaviour of `Spec`.

The abstract formal projection is normalized to three state variables
(`requestMeta`, `terminalMeta`, `conflicts`). Authority relations are immutable
context constants; exact terminal binding is derived from request metadata;
invalid material and non-authoritative inputs have no retained state slot and
are proved to be semantic stutters.

The canon-to-TLA assurance adds a second proof layer.
`SeedCanonProjection.tla` is generated deterministically from the exact
`seed-model.json` identity under a versioned projection profile, and TLAPS
proves behavioral equivalence between that generated projection and
`SeedResolution.tla`.

That relation is explicitly scoped. It does not establish:

- equivalence of every natural-language sentence;
- concrete Binding or digest construction;
- correctness or refinement of implementations;
- concrete Authority grant-chain construction;
- liveness;
- cryptographic primitive security;
- concrete terminal-commitment accumulator or witness correctness;
- external certification.

The normative source remains
`seed/canonical/source/seed-model.json`.

Neither the TLA+ model, the proof module nor TLAPM receives normative,
semantic or implementation precedence.
