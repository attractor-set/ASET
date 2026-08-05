# ASET Python full semantic critical-path reference 0.2.0

`src/aset_reference` is a **NON_NORMATIVE** clean executable interpretation of the
full deterministic semantic critical path defined by the ASET component canons and
bound to ASET Seed 0.1-rc12.

```text
REFERENCE_IMPLEMENTATION=true
NORMATIVE_SOURCE=false
PRODUCTION_READY=false
REFERENCE_VERSION=0.2.0
```

The normative sources remain `seed/canonical/`, `aset/components/`, and
`aset/system/`. A disagreement is a defect in this implementation or an ambiguity
to be resolved in the specification; Python code does not silently become canon.

## Implemented path

The reference executes eight separately governed crossings:

1. `GATE-CONTEXT-PROJECT` — `ContextProjection` admission;
2. `GATE-EXPECT-ADMIT` — `PlanProposal` and `ExpectedChangePatch` admission;
3. `GATE-EXEC-BIND` — `OperationalBinding` admission;
4. `GATE-DISPATCH` — `ExecutionIntent` admission before the effect boundary;
5. `GATE-OBSERVE` — `Observation` admission;
6. `GATE-EVIDENCE` — `EvidenceBundle` admission;
7. `GATE-ACCEPT` — `Verification` and `AcceptanceDecision` admission;
8. `GATE-TASK-CLOSE` — task closure and conditional `Outcome` recognition.

Every crossing has its own `CoreResolution`, exact one-shot `Permit`,
`PermitUseReceipt`, source Context root, patch digest, write-set, and immediate
predecessor receipt. `Outcome` is created only from a `PASS` Verification. The
`UNKNOWN` effect class closes the task as rejected without an Outcome.

## Deliberate boundaries

The reference is deterministic and storage-free. It excludes:

- production signatures, PKI, HSM and key lifecycle;
- persistent transactional storage and distributed consensus;
- network, subprocess, clock and random sources;
- real model inference and real external connectors;
- operational SLO, deployment and certification claims.

The deterministic connector implements four semantic classes: `SUCCESS`,
`FAILURE`, `NO_EFFECT`, and `UNKNOWN`. It is an assurance instrument, not an
external-effect adapter.

## Verification

```text
python tools/run_reference_conformance.py --check
python tools/model_check_reference.py --check
python -m pytest -q tests/reference
python tools/build_release.py
python tools/blackbox_reference_audit.py dist/ASET-Repository-Snapshot.zip
python tools/run_reference_blackbox_adversarial.py dist/ASET-Repository-Snapshot.zip
```

A portable vector in `test-vectors/reference/full-critical-path-success.json`
contains exact canonical bytes, final Context root, Outcome ID, and all eight
receipt IDs for an independent implementation.
