# ASET Seed formal safety projection

`SeedResolution.tla` is the abstract formal projection of the Seed 0.3
minimal resolution-recognition kernel.

The model covers:

- the closed resolution domain `UNKNOWN | ALLOW | BLOCK`;
- sound and fail-closed effect permission;
- exact request/record binding;
- local Authority roots;
- an abstract validated delegated-Authority predicate;
- non-authoritative external inputs;
- conflict and invalid-material handling;
- fresh reconsideration through recognized immutable terminal commitments without predecessor-object retention;
- append-only requests and inputs;
- immutable terminal records;
- exclusion of invalid or unrecognized candidates from the Seed transition relation;
- canonical-state changes only through recognized Seed transitions.

`SeedResolution.cfg` drives bounded TLC checking of eleven state invariants
and four temporal safety properties. The Python bounded explorer checks the
same registered property names and validates bounded transition preservation.

`SeedResolutionProofs.tla` provides the unbounded deductive safety layer.
Its final theorems establish:

- `Spec => []SeedStateSafety`;
- `Spec => RequestsAppendOnly`;
- `Spec => TerminalRecordsImmutable`;
- `Spec => CanonicalStateChangesOnlyByRecognizedTransition`;
- `Spec => ObservedInputsAppendOnly`.

The proof uses a strengthened inductive invariant containing the auxiliary
reachability property that a terminal record can exist only for a registered
request. This auxiliary predicate supports induction and does not introduce
a new normative Seed requirement.

Detailed grant-chain construction, canonical digest computation and static
implementation neutrality are checked by the executable oracle and canon
validators. The formal model abstracts validated Authority evidence through
`authorityProofBindings` and validated historical terminal-commitment recognition
through `RecognizedTerminalCommitments`. Concrete accumulator construction,
membership/update witnesses and retention are profile-level concerns.

`SeedCanonProjection.tla` is a deterministic generated interpretation of the
exact machine-readable Seed identity under
`ASET-SEED-CANON-TLA-PROJECTION-V2`. `SeedCanonRefinementProofs.tla` proves
behavioral equivalence between that generated projection and
`SeedResolution.tla`. Projection parity and source/target digests are mandatory
release checks.

This canon-to-TLA relation preserves the declared abstractions. It does not
establish:

- equivalence of every natural-language sentence;
- concrete Binding or digest construction;
- refinement from the TLA+ model to an implementation;
- correctness of any implementation;
- concrete Authority grant-chain construction;
- cryptographic primitive security;
- concrete terminal-commitment accumulator or witness correctness;
- liveness.

`UNKNOWN` may remain unresolved indefinitely. This is intentional fail-closed
behaviour for a recognition kernel rather than a workflow engine.

The CI proof gate pins TLAPM commit
`4600b24c6d95a25ff081ad37b63b2a01c29d43a5`. It verifies process exit status,
the TLAPM success summary and the presence of every final theorem.

The number of generated proof obligations is recorded as evidence and is not
a fixed semantic contract.
