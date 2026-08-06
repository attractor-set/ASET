# Role of ASET Seed

ASET Seed is the minimal local resolution-recognition kernel of the ecosystem.

It defines:

- exact `ResolutionBinding`;
- fresh `ResolutionRequest`;
- locally rooted Authority and attenuating Authority proof;
- immutable terminal `ResolutionRecord`;
- derived `UNKNOWN`, terminal `ALLOW` and terminal `BLOCK`;
- fail-closed effect permission;
- fresh linked reconsideration.

It does not define policy evaluation, evidence acquisition, workflow, federation, storage or enforcement. Extensions may produce and transport inputs and proof material, but only Seed semantics determine whether a terminal record is valid.

Evidence, AI output, consensus and remote outcomes remain non-authoritative until a locally authorized exact-binding terminal record is recognized.
