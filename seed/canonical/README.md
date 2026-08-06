# ASET Seed 0.3 minimal strong core

ASET Seed is a local resolution-recognition kernel.

```text
Resolution = UNKNOWN | ALLOW | BLOCK
EffectPermitted(binding) iff one unique valid exact-binding terminal record is ALLOW
```

`UNKNOWN` is derived when no unique valid terminal record exists. `BLOCK` is an
explicit terminal prohibition. Both are fail-closed.

Seed normatively defines exact binding, local Authority roots, attenuating
Authority proof, terminal uniqueness, immutable content-addressed records and
fresh reconsideration identifiers. Policy evaluation, evidence acquisition,
workflow, federation, persistence and enforcement are extensions or
implementation concerns.

## Assurance closure

The published safety contract has complete machine traceability:

- 12/12 canonical requirements covered;
- 12/12 canonical invariants covered;
- 3/3 transitions covered positively and negatively;
- 15 bounded TLA+/model-check properties;
- 4 exact executable-or-static properties;
- 24 portable conformance cases;
- 13 semantic mutations, all required to be killed.

The normative coverage matrix is
`seed/canonical/assurance/invariant-coverage.json`. Complete bounded coverage
must not be represented as unbounded TLAPS proof, liveness proof, cryptographic
proof or implementation certification.
