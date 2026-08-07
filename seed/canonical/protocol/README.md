# Active Seed 0.3 protocol surface

This directory contains only schemas declared by
`seed/canonical/protocol/protocol-profile.json`.

Older RC11/RC12 permit, outcome, membership, context-lifecycle and federation
schemas are not part of the active Seed 0.3 protocol. Their immutable historical
copies remain in frozen release bundles and historical generated editions under
`seed/releases/` and `docs/generated/*/ASET_Seed_0.1-rc12.md`.

The active protocol intentionally exposes an exact-binding Authority recognition
record rather than a grant-chain interpreter. `authority_evidence_digests` in a
terminal record are opaque references; they do not create Authority by themselves.
