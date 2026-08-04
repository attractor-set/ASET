
# Production readiness of the ASET specification repository

## Claim

This repository is production-ready for the controlled publication, preservation, review, validation, and release assurance of ASET Seed documentation.

The claim is intentionally narrower than Seed runtime production readiness.

| Scope | Status |
|---|---|
| Public specification repository operations | `PRODUCTION_READY` |
| Deterministic documentation publication | `PRODUCTION_READY` |
| Frozen rc11 preservation and verification | `PRODUCTION_READY` |
| Black-box documentation audit | `REQUIRED` |
| rc11 semantic documentation | `PASS_WITH_LIMITATIONS` |
| rc12 canonical migration | `IN_DEVELOPMENT` |
| Seed runtime implementation | `HOLD` |
| Deployment, durability, concurrency and consensus | `NOT_CLAIMED` |
| External third-party certification | `PENDING` |

## Release gates

A change is eligible for merge to `main` only when all repository gates pass:

1. strict JSON and machine-readable model validation;
2. RDF, SHACL and TBX validation;
3. deterministic language-edition parity;
4. terminology policy;
5. frozen rc11 bundle integrity;
6. expanded rc11 byte identity against the frozen documentation archive;
7. unit tests and static Python checks;
8. deterministic repository snapshot construction;
9. independent black-box documentation audit of the snapshot;
10. adversarial mutation rejection by the black-box auditor;
11. exact manifest coverage and digest verification;
12. zero unresolved blocking findings.

## Fail-closed rule

A missing, skipped, indeterminate, or failed mandatory check blocks promotion. The gate may report only `PASS` or `FAIL`; absence of evidence is not a pass.

## Separation of claims

Repository readiness must never be used as evidence that the reference state machine is a production datastore or that cryptographic proof verification, concurrent serialization, distributed consensus, operational recovery, or external certification has been completed.

## Evidence

- `audit/PDCA_HISTORY.md`
- `audit/FINDING_CLOSURE_MATRIX.json`
- `audit/BLACKBOX_DOCUMENTATION_AUDIT.json`
- `seed/canonical/assurance/repository-release-gates.json`
- deterministic snapshot and checksum in `dist/` during CI
