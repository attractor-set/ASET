# RC12 to Seed Resolution Core

This is an intentional breaking semantic narrowing.

The active Seed no longer defines the RC11/RC12 execution, permit,
verification, federation, membership or context-lifecycle protocol. It defines
only local resolution recognition:

    UNKNOWN | ALLOW | BLOCK

`UNKNOWN` is derived and fail-closed. `ALLOW` and `BLOCK` are immutable terminal
values. A request is admitted under an exact binding and recognized local
Authority. A terminal record is accepted only when its Authority is explicitly
recognized for that exact binding.

There is no active Seed escalation workflow or grant-chain interpreter.
Concrete delegation/signature/evidence mechanisms may establish Authority
recognition externally, but they are not Seed state or Seed transitions.

The former RC11/RC12 concepts remain historical migration evidence and belong
to separately versioned extensions or implementations when reused.
