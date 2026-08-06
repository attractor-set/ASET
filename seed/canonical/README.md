# ASET Seed 0.3 minimal strong core

ASET Seed is a local resolution-recognition kernel.

```text
Resolution = UNKNOWN | ALLOW | BLOCK
EffectPermitted(binding) iff one unique valid exact-binding terminal record is ALLOW
```

`UNKNOWN` is derived when no unique valid terminal record exists. `BLOCK` is an explicit terminal prohibition. Both are fail-closed.

Seed normatively defines exact binding, local Authority roots, attenuating Authority proof, terminal uniqueness, immutable content-addressed records and fresh reconsideration identifiers. Policy evaluation, evidence acquisition, workflow, federation, persistence and enforcement are extensions or implementation concerns.
