# Role of ASET Seed

ASET Seed is the minimal local resolution-recognition kernel of the ecosystem.

It defines:

- exact `ResolutionBinding`;
- fresh `ResolutionRequest`;
- locally rooted Authority and attenuating Authority proof;
- immutable terminal `ResolutionRecord`;
- derived `UNKNOWN`, terminal `ALLOW` and terminal `BLOCK`;
- fail-closed effect permission;
- fresh reconsideration linked by an immutable recognized terminal-record commitment.

It does not define policy evaluation, evidence acquisition, workflow, federation, storage, retention/compaction, a concrete cryptographic accumulator or enforcement. Extensions may produce and transport inputs and proof material, but only Seed semantics determine whether a terminal record is valid.

Evidence, AI output, consensus and remote outcomes remain non-authoritative until a locally authorized exact-binding terminal record is recognized.


Historical predecessor objects are not part of the reconsideration requirement. An implementation may prune them after preserving profile-specific proof material sufficient to re-establish recognition of the terminal commitment. A bounded hot buffer plus an authenticated accumulator is one scalable profile; Merkle/MMR or any other concrete construction is non-normative.
