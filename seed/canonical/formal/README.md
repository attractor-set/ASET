# ASET Seed formal safety model

`SeedResolution.tla` models the active Seed 0.3 resolution core.

## State ownership

Seed-owned mutable state:

- `requestMeta`;
- `terminalMeta`.

Environment state:

- `conflicts`.

The model therefore has three TLA variables but only two Seed-owned mutable
state dimensions. `Requests` and `TerminalRequests` are partial-map domains.
`EvaluateResolution(r)` is a pure observer and is not included in `Next`.

## Authority and external-material boundary

`RecognizedAuthorityBindings` is the single immutable abstract recognition relation. It means that Authority recognition has already succeeded for an exact binding and is used consistently by both request registration and terminal submission; the formal model does not interpret signatures, credentials or delegation mechanisms.

Invalid or non-authoritative material has no state variable and no artificial
transition. It cannot enter accepted state by construction of the admission
boundary. The TLA model covers additional distinct valid terminal material as an environment observation only after a terminal record has already been accepted.

## Checked properties

`SeedResolution.cfg` registers ten state invariants and four temporal safety
properties. The Python finite model checker explores its published finite
fixture to saturation; TLC independently checks the TLA model.

The final TLAPS theorem surface is:

- `SpecImpliesAlwaysSeedStateSafety`;
- `SpecImpliesRequestsAppendOnly`;
- `SpecImpliesTerminalRecordsImmutable`;
- `SpecImpliesSeedStateChangesOnlyByRecognizedTransition`;
- `SpecImpliesConflictObservationPreservesSeedState`.

## Canon-to-TLA relation

`SeedCanonProjection.tla` is generated under
`ASET-SEED-CANON-TLA-PROJECTION-V5` as a **standalone module**. It does not
`EXTEND` or instantiate `SeedResolution`. `SeedCanonRefinementProofs.tla`
explicitly instantiates the standalone projection onto the handwritten model
and proves evaluator and behavioral equivalence.

The relation still abstracts concrete Binding/digest construction,
Authority-recognition establishment, terminal-commitment recognition,
cryptographic security, implementation refinement and liveness.

The normative source remains the machine-readable canon; formal artifacts are
assurance projections, not normative implementations.

Historical bootstrap/RC12 formal models are not duplicated in the active formal
directory. Their immutable copies remain available in frozen historical release
bundles.
