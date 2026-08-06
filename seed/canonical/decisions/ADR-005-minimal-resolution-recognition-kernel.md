# ADR-005 — Establish the minimal resolution-recognition kernel

## Decision

ASET Seed 0.3 replaces the coupled `status` and `enforcement` dimensions and the mutable escalation workflow with a single derived resolution algebra: `UNKNOWN`, `ALLOW`, `BLOCK`.

`UNKNOWN` is not a stored terminal decision. It means that no unique valid terminal `ResolutionRecord` exists for the exact registered request. Only a valid `ALLOW` record permits the exact bound effect. `BLOCK`, invalid material, missing material and conflicts remain fail-closed.

Authority is local to a Context and exact binding. Delegation is supplied as explicit proof material and must be locally rooted, exact-binding, acyclic and non-expanding. Evidence, AI output, consensus and remote outcomes remain non-authoritative inputs.

Workflow orchestration, policy evaluation, federation, storage and enforcement are outside Seed.

## Consequence

This is a breaking semantic simplification relative to `0.2.0-alpha.2`. The smaller kernel is intended to become the stable compatibility foundation of the ASET ecosystem.
