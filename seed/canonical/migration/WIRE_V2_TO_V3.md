# Seed resolution wire V2 → V3

Wire/profile V3 is a breaking cleanup of the active Seed 0.3 candidate.

## Removed from the active store

- `authority_grants`;
- concrete delegation/grant-chain interpretation.

## Authority recognition

`ResolutionAuthorityBinding` now represents the exact-binding recognition fact
consumed by Seed. Concrete signatures, certificates, delegation chains and
other evidence mechanisms are external to the Seed wire semantics.

`ResolutionRecord.authority_proof_digests` is replaced by
`authority_evidence_digests`. These references are opaque and non-authoritative;
they do not create Authority by themselves.

## Operation roles

`REGISTER_REQUEST` and `SUBMIT_RESOLUTION` are state transitions.
`EVALUATE_RESOLUTION` is a pure observer.

## Invalid material

Malformed or non-authoritative material does not override an otherwise unique
valid terminal record. Conflict means conflict among valid terminal material.

## Active schema surface

Wire V3 contains only the schemas declared by the active protocol profile.
Historical RC11/RC12 schema copies remain in frozen release bundles rather than
being duplicated in the active protocol directory.
