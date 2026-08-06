# ASET Seed complete bounded safety projection

`SeedResolution.tla` is the bounded formal projection of the Seed 0.3 minimal
resolution-recognition kernel.

The model covers:

- the closed resolution domain `UNKNOWN | ALLOW | BLOCK`;
- sound and fail-closed effect permission;
- exact request/record binding;
- local Authority roots;
- an abstract validated delegated-Authority predicate;
- non-authoritative external inputs;
- conflict and invalid-material handling;
- fresh reconsideration lineage;
- append-only requests and inputs;
- immutable terminal records;
- preservation of canonical state by rejected operations.

The TLC configuration checks eleven state invariants and four temporal
properties. The Python bounded explorer checks the identical property names and
also validates transition preservation.

Detailed grant-chain construction, canonical digest computation and static
implementation neutrality are checked by the executable oracle and canon
validators. Their exact mapping is normative in
`seed/canonical/assurance/invariant-coverage.json`.

The formal projection does not claim liveness or unbounded deductive proof.
`UNKNOWN` may remain unresolved indefinitely; this is intentional fail-closed
behaviour for a recognition kernel rather than a workflow engine.
