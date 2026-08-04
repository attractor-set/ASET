# ASET Seed 0.1-rc11 — Architecture

## Scope

Seed is a deterministic reference monitor over one Trust Space. It accepts a Root Genesis and typed transitions, derives predicates, atomically updates canonical State, validates whole-state invariants, and emits a new state root.

## Layers

1. **Normative prose** — the Russian specification.
2. **Machine contract** — 39 strict JSON Schemas.
3. **Reference semantics** — `machine/reference/seed_reference.py`.
4. **Evidence** — 55 traces, independent audit, black-box attacks, branch guards, coverage bindings.

## Main flow

`RootGenesis -> State0 -> validate envelope -> derive authority/causality/policy predicates -> handler -> validate_state -> state root`. Any failure returns the original State unchanged.

## Governance simplification

There is no plebiscite or pending consent state. A standalone exit is `MEMBERSHIP_WITHDRAW`. A coordinated change is one atomic `CONTEXT_REDEFINE` carrying the canonical proposal and every affected member authorization.
