# ASET Seed minimal formal projection

`SeedResolution.tla` models the record-recognition kernel of Seed 0.3. Requests are append-only, terminal records are unique, `UNKNOWN` is derived from the absence of a terminal record, and only `ALLOW` permits the exact bound effect.

Authority proof construction, evidence acquisition, policy evaluation, storage, transport and enforcement are intentionally outside this bounded assurance projection. `AuthorityBindings` represents authority material that has already passed the normative exact-binding and local-root checks defined by the wire schemas and conformance corpus.
