# ADR-010 — Unify Authority recognition, conflict admissibility and operation semantics

## Status

Accepted. Refines ADR-009 for the active Seed 0.3 alpha model. Historical
artifacts are not rewritten.

## Context

After the deep semantic cleanup, three residual mismatches remained between the
machine canon, wire semantics and formal abstraction:

1. the formal model exposed separate request and terminal Authority-recognition
   relations although the wire model has one exact-binding AuthorityBinding
   type and one recognition store;
2. environment conflict observation was allowed before any terminal record had
   been accepted, although concrete conflict requires additional distinct valid
   terminal material for an existing terminal resolution;
3. `EVALUATE_RESOLUTION` was correctly modeled as an observer but remained
   stored under a machine-canon collection named `transitions` with a
   `SEED-TX-*` identifier.

The phrase “at most one valid terminal record exists” also conflated globally
observed valid material with the single terminal record accepted into Seed-owned
state.

## Decision

The active Seed model uses:

- one immutable `RecognizedAuthorityBindings` relation for exact-binding
  Authority recognition in both request registration and terminal submission;
- conflict observation only for a `resolution_id` already present in
  `TerminalRequests` and not already conflicted;
- `AcceptedTerminalUnique` for the structural single terminal cell in
  Seed-owned state;
- `ConflictSound` for the rule that conflict state is a subset of accepted
  terminal requests and always derives `UNKNOWN`;
- a machine-canon `operations` catalogue with identifiers `SEED-OP-001` through
  `SEED-OP-003`, containing two `STATE_TRANSITION` operations and one
  `OBSERVER` operation;
- standalone canon-to-TLA projection profile
  `ASET-SEED-CANON-TLA-PROJECTION-V5`.

## Consequences

- formal Authority admission now matches the single wire AuthorityBinding
  semantics instead of introducing an unexpressed terminal-only privilege;
- impossible pre-request/pre-terminal conflict states are no longer reachable;
- the finite model reports only states reachable under the concrete conflict
  boundary;
- accepted terminal uniqueness no longer claims that additional valid external
  terminal material cannot exist; such material is represented by conflict;
- generated documentation describes three operations rather than three
  transitions;
- this is a breaking machine-canon shape change inside the 0.3 alpha line and
  is explicitly declared as such by the canon change declaration.
