# Seed state boundary and minimization

## Current decomposition

The active formal model has two Seed-owned mutable state dimensions and one
environment dimension:

1. `requestMeta` — partial map of admitted request metadata;
2. `terminalMeta` — partial map of accepted terminal metadata;
3. `conflicts` — environment observation state constrained to accepted terminal requests.

`seedVars == <<requestMeta, terminalMeta>>`; conflict is deliberately excluded
from Seed-owned state.

## Derived, not stored

- `Requests == DOMAIN requestMeta`;
- `TerminalRequests == DOMAIN terminalMeta`;
- terminal binding is the request binding;
- request/terminal absence is domain absence, not a sentinel;
- evaluation is an observer, not stored state.

This makes several disagreement states unrepresentable instead of proving that
duplicated fields remain synchronized.

## Provenance versus decision state

`requestMeta.previous` and `terminalMeta.authority` carry provenance needed for
reconsideration and Authority-soundness claims. They are not independent
resolution-algebra dimensions, but remain in the abstract state until a
separate provenance refinement is specified and proved.

## External material

Invalid/non-authoritative material has no artificial stutter action. It remains
outside the abstract state machine. The executable admission boundary verifies
that it cannot create accepted state. Valid conflict observation is modeled separately as environment state, is admissible only after an accepted terminal record exists, and is proved not to mutate Seed-owned state.

No Merkle tree, MMR, signature algorithm or accumulator is introduced into the
Seed core.
