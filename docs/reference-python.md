# ASET Python Reference Critical Path

`aset_reference` is a non-normative, storage-free executable interpretation of the ASET critical context-transition path.

It accepts immutable values for a current context, proposal, permit, and evidence and returns either a complete transition commit result or a stable normative rejection. It performs no persistence, networking, subprocess execution, clock access, randomness, or external effect.

The reference implements the critical path only:

1. bind a proposal to the current context and version;
2. bind a one-use permit to the proposal, gate, context, and version;
3. require the complete exact evidence-type set;
4. derive the next context without mutating inputs;
5. mark the permit consumed in the returned state;
6. return deterministic transition and audit digests.

Persistence, crash recovery, distributed coordination, identity infrastructure, and external effects are responsibilities of independent runtime implementations and are intentionally outside this reference.
