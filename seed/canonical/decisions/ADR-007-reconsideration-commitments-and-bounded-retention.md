# ADR-007 — Reconsideration commitments and bounded retention

## Decision

ASET Seed does not require a reconsideration request to retain, dereference or replay the predecessor `ResolutionRequest` or `ResolutionRecord` as live canonical state.

A reconsideration carries `previous_terminal_record_digest`, an immutable content-addressed commitment to a previously recognized terminal `ResolutionRecord`. Recognition is a verification-boundary fact: an implementation must establish that the commitment denotes a valid previously recognized terminal record, but Seed does not prescribe how the corresponding historical material is retained.

The canonical Seed state therefore does not contain an ever-growing registry of all recognized terminal commitments. A valid terminal record still present in the current state may establish recognition directly. Historical recognition may instead be established by externally validated proof material.

Implementations MAY realize historical recognition with a cryptographic accumulator. A recommended scalable profile is:

1. retain a bounded hot buffer of at most `N` recent terminal commitments;
2. when the buffer reaches its profile-defined compaction threshold, fold the completed block into an authenticated accumulator;
3. retain only the accumulator state required by that profile plus the current hot buffer;
4. supply an external membership/update witness when a pruned commitment must be recognized later.

Merkle trees, Merkle Mountain Ranges, hash-chain checkpoints, RSA/class-group accumulators, recursive proofs or future authenticated-set constructions are profile choices, not Seed semantics.

## Important boundary

A digest by itself is not proof of authenticity or prior recognition. A profile must bind accumulator membership to a terminal record whose Authority and exact binding were valid under Seed rules. Seed's abstract `RecognizedTerminalCommitments` boundary represents the result of that verification, not an assumption that every syntactically valid digest is recognized.

A generic Merkle root alone is also not sufficient to guarantee both root-only incremental updates and future individual membership proofs. Concrete profiles must specify which frontier, update witness, membership witness or external history is retained. Consequently, `N + 1` digest-sized values is a possible profile bound only for constructions whose update/verification protocol supports that bound; it is not a universal Seed invariant.

## Consequences

- Pruning, archiving and compaction are not Seed transitions and do not mutate a terminal resolution fact.
- Old requests and records may be physically removed after the implementation has preserved whatever proof material its selected recognition profile requires.
- The active Seed semantic state need not grow with the complete historical request chain.
- Reconsideration freshness remains a semantic property of a new `resolution_id` plus a recognized immutable predecessor commitment.
- Concrete accumulator soundness, collision resistance, witness maintenance and storage bounds require separate profile-level assurance.
