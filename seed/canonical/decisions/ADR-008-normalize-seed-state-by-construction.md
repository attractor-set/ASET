# ADR-008 — Normalize Seed state by construction

## Status

Superseded in part by ADR-009 for state/environment and Authority-boundary semantics. The representation-normalization decision remains historical context for the abstract Seed 0.3 safety projection. This ADR does not change
the normative wire/protocol contract in `seed-model.json`; it reduces the
formal representation while preserving its observable resolution semantics.

## Context

The previous TLA+ projection used twelve mutable variables, including parallel
request/terminal binding and Authority maps plus bookkeeping for invalid and
non-authoritative observations. Several invariants existed primarily to prove
that duplicated fields stayed equal or that stored observations had no effect.

## Decision

Use three mutable formal variables: `requestMeta`, `terminalMeta`, and
`conflicts`.

Make local/validated Authority-binding relations immutable context constants.
Represent `requestMeta` and `terminalMeta` as partial functions and derive
request/terminal membership directly from their domains. No `NoRequest` or
`NoTerminal` sentinel is retained. Do not store an independent
terminal binding; derive it from the immutable request binding. Do not retain invalid or non-authoritative material in Seed state. ADR-009 later clarified that these are admission/external-material boundaries rather than artificial TLA stutter actions.

## Consequences

- metadata absence is represented structurally by function-domain absence, so
  sentinel/record type disagreement is unrepresentable;
- exact-binding disagreement is unrepresentable after admission;
- initial local Authority need not be duplicated in mutable state after the
  local-root check;
- terminal uniqueness follows from one keyed terminal metadata cell;
- invalid/non-authoritative material is not retained in Seed state;
- conflict remains explicit because it changes `ResolutionOf` to `UNKNOWN`;
- the formal state space and proof surface are reduced without adding crypto or
  accumulator assumptions.

The executable protocol oracle remains responsible for concrete digest,
record-binding and Authority-proof validation before a candidate becomes an
accepted abstract transition.
