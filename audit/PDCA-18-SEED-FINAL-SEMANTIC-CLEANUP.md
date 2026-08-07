# PDCA-18 — Seed final semantic cleanup

## Plan

Remove the remaining mismatches between the active machine canon, wire
semantics and formal model without adding new Seed capabilities.

## Do

The candidate:

- uses one `RecognizedAuthorityBindings` relation for both request and terminal
  admission;
- admits conflict observation only for an already accepted terminal resolution;
- distinguishes `AcceptedTerminalUnique` from external conflicting valid
  material and expresses the latter through `ConflictSound`;
- publishes three role-classified operations, not three transitions;
- uses `SEED-OP-*` identifiers for two state transitions and one observer;
- advances the standalone canon projection to profile V5;
- replaces the obsolete RC12 runtime black-box methodology with the actual
  active specification-repository audit boundary;
- reports finite-model unique labelled graph edges separately from generated
  action instances so transition counts are graph metrics rather than
  enumeration artifacts.

## Check

The exact candidate is required to close:

```text
requirements = 12/12
invariants = 12/12
operations = 3/3
semantic mutations killed = 13/13
finite model saturated = true
TLC = PASS
TLAPS = PASS
canon-to-TLA refinement = PASS
repository release gate = PASS
```

## Act

Once those gates pass, Seed 0.3 should be treated as semantically stabilized.
Further capability growth belongs in extensions; further Seed changes should
be limited to demonstrated defects or assurance strengthening.
