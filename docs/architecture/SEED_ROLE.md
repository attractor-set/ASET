# Role of ASET Seed

ASET Seed is the minimal local resolution-recognition core.

It owns only the state necessary to remember admitted requests and accepted
terminal resolutions. It does not own the world that supplies evidence,
conflict observations, policy results or cryptographic proofs.

## Seed-owned state

- immutable request metadata for registered `resolution_id` values;
- immutable terminal metadata for accepted terminal `ALLOW`/`BLOCK` values.

## Environment and observers

Conflict is environment state because additional distinct valid terminal material for an already accepted terminal resolution changes the derived resolution to `UNKNOWN`. Conflict observation is not admissible before an accepted terminal record exists.
`EVALUATE_RESOLUTION` is a pure observer and never mutates Seed-owned state.

Invalid, malformed or non-authoritative material has no Seed state slot. It may
fail admission or be ignored by the resolution algebra, but it cannot create
Authority, `ALLOW` or a conflict by mere presence.

## Authority boundary

Seed consumes one exact-binding Authority-recognition relation for both request registration and terminal submission. How recognition is established—signature, certificate, delegation mechanism, hardware root, external verifier or another mechanism—is a profile concern. Opaque evidence references are not Authority by themselves.

## Outside Seed

Policy evaluation, evidence acquisition, workflow, federation, storage,
retention/compaction, cryptographic accumulators, signature schemes and effect
enforcement are extension or implementation concerns.

Reconsideration refers to a recognized immutable terminal commitment. The
predecessor object need not remain physically retained.
