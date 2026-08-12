# ASET — Authority-Seeded Evidence Trail

ASET Seed 0.4alpha is the current public representation of **ASET Alpha**, the
Local Recognition Algebra, together with an executable abstract Seed machine.

## ASET Alpha

**ASET Alpha** is the public name of the Local Recognition Algebra used by
ASET Seed 0.4alpha. The name *Alpha* refers to α, the first letter of the Greek
alphabet, as a concise metaphor for a minimal foundation and first principle.
In ASET naming, `0.4alpha` is the current representation identifier for this
algebra.

Active structure:

- `theory/local-recognition/` — ASET Alpha and its cardinality-minimality proof.
- `seed/alpha4/operational/` — restricted-Forth abstract machine.
- `seed/alpha4/formal/` — formal reflection, relational correctness model, composition and pairing proofs.
- `seed/alpha4/SEED.aset` — non-semantic bindings between the active subjects.
- `tools/alpha4_seed_gate.py` — complete verification and deterministic release gate.
- `history/REFERENCES.aset` — immutable references to superseded public states; they are not active semantics.

The 0.4alpha line claims no compatibility with the 0.3 canon.

Verify locally:

```text
python tools/alpha4_seed_gate.py
```

The release pipeline materializes controlled English and Python as external
companion profiles with semantic precedence `NONE`. The Python+SQLite artifact
is not a second Seed expression: it is a persistence extension of the exact
generated Python base expression, with `semantic_delta=NONE` and an exact base
expression byte binding.

Generated Python is admitted against independently materialized proof-derived
witnesses through the air-gap verifier. The SQLite persistence extension is
then checked against its exact Python base expression for observational
preservation, transaction rollback, and restart round-trip behavior.

SHA-256 identifies exact release bytes; semantic integrity is established by
declared congruence and proof obligations.

Copyright and attribution are in `NOTICE`. Licensing terms are in `LICENSE`.
