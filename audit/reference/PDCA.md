# ASET Python reference PDCA record

## Cycle 1 — minimal semantic kernel

### Plan

Create the smallest storage-free critical path: context, proposal, permit, evidence, accepted commit, and stable rejection. Preserve all existing behavior.

### Do

Added `aset_reference`, focused tests, documentation, and an import-based storage/side-effect boundary audit.

### Check

Focused tests passed and full repository regression increased from 55/55 to 59/59.

### Act / black-box analysis

The kernel was storage-free, but nested JSON inputs were only shallowly protected. A caller could mutate nested values after construction. Cycle 2 therefore strengthened immutable value semantics without adding repositories or adapters.

## Cycle 2 — immutable JSON value semantics

### Plan

Make every accepted input a finite strict JSON value and recursively isolate it from caller mutation.

### Do

Added recursive JSON validation/freezing and canonical normalization. Added hostile nested-mutation and non-finite/non-JSON tests.

### Check

Focused tests and the reference black-box audit passed; full regression reached 60/60.

### Act / black-box analysis

The Python API was deterministic and isolated, but the project still lacked language-neutral executable examples and a machine-readable requirement-to-symbol map. Cycle 3 added only those standard-facing artifacts.

## Cycle 3 — portable vectors and repository assurance

### Plan

Add language-neutral acceptance/rejection vectors and traceability, then run the complete available repository assurance chain against a rebuilt deterministic snapshot.

### Do

Added JSON vectors, a vector runner in pytest, and `audit/reference/traceability.json`. Rebuilt `MANIFEST.json` and the repository snapshot.

### Check

- reference tests: 7/7;
- repository tests: 62/62;
- rc12 conformance: 55/55;
- branch guards: 252/252;
- rc12 bounded model: 281 states / 832 transitions;
- component conformance: 26/26;
- component bounded models: 8/8;
- component black-box audit: 27/27;
- documentation black-box audit: 32/32;
- runtime black-box audit: 18/18.

### Act / final black-box analysis

The resulting reference is a small pure value transformer. It has no SQLite, persistence ports, network, subprocess, clock, randomness, external-effect adapter, plugin mechanism, or configuration framework. Existing Seed runtime behavior and frozen rc11 bytes remain unchanged. Remaining production concerns belong to independent runtime implementations, not to this reference kernel.
