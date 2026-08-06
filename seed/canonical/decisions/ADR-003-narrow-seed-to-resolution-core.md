# ADR-003: Narrow the active Seed to a resolution core

## Decision

The active Seed is intentionally narrowed to an exact, authority-scoped resolution cycle with the lattice `UNKNOWN -> ACCEPT | DENY`.

`UNKNOWN` remains operationally blocked and is not silently rewritten as `DENY`. It may move to a next Resolution Authority only through an exact escalation grant. Context ancestry and federation membership do not create authority.

Execution, Permit consumption, evidence acquisition, attempt journals, Context lifecycle, federation topology, reconciliation, memory and planning move to separately versioned extensions or implementations.

## Compatibility

This is a breaking semantic change from 0.1-rc12. Historical bytes and component bridges remain evidence for migration but do not expand the active Seed.
