# ASET Seed 0.3 minimal strong core

ASET Seed is a local resolution-recognition kernel.

    Resolution = UNKNOWN | ALLOW | BLOCK
    EffectPermitted(binding) iff one unique valid exact-binding
    terminal record is ALLOW

`UNKNOWN` is derived when no unique valid terminal record exists. `BLOCK` is
an explicit terminal prohibition. Both are fail-closed.

Seed normatively defines exact binding, local Authority roots, attenuating
Authority proof, terminal uniqueness, immutable content-addressed records and
fresh reconsideration identifiers.

Policy evaluation, evidence acquisition, workflow, federation, persistence
and enforcement are extension or implementation concerns.

## Assurance closure

The published safety contract has complete machine traceability:

- 12/12 canonical requirements covered;
- 12/12 canonical invariants covered;
- 3/3 transitions covered positively and negatively;
- 15 bounded TLA+/TLC properties;
- 15/15 registered TLA+/TLC safety properties covered by unbounded TLAPS proof;
- 4 exact executable-or-static properties;
- 24 portable conformance cases;
- 13 semantic mutations, all required to be killed.

The unbounded proof applies to the committed abstract TLA+ safety projection.
It establishes all eleven registered state invariants and all four registered
temporal safety properties for every behaviour of `Spec`.

It does not establish:

- refinement from the normative machine-readable canon;
- correctness or refinement of implementations;
- concrete grant-chain construction;
- liveness;
- cryptographic primitive security;
- external certification.

The normative source remains
`seed/canonical/source/seed-model.json`.

Neither the TLA+ model, the proof module nor TLAPM receives normative,
semantic or implementation precedence.
