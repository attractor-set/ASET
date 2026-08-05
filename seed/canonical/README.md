# ASET Seed 0.1-rc12 canonical area

Status: `RC12_IMPLEMENTATION_NEUTRAL_RELEASE_CANDIDATE`

This directory contains the machine-readable canonical candidate for ASET Seed 0.1-rc12. It preserves the audited rc11 wire semantics and identity domains while making requirements, invariants, transition semantics, protocol schemas, conformance bindings, terminology and formal safety projections explicit and machine-checkable.

The canon is implementation-neutral. It does not prescribe a programming language, storage backend, network topology, consensus protocol, cryptographic provider or deployment model. Implementations are evaluated as black boxes through the canonical conformance protocol and have no semantic precedence over one another.

## Canon hierarchy

1. `source/seed-model.json` and its stable semantic identifiers;
2. normative schemas, constraints, requirements, invariants and transition semantics;
3. `CANON_PACKAGE.json`, the implementation-conformance protocol and canonical cases;
4. formal projections and bounded model-check evidence;
5. generated Russian, English and Brazilian Portuguese editions;
6. explanatory diagrams and examples.

`release/RC12_RELEASE_CANDIDATE.json` and `release/RC12_FREEZE_ENTRY.json` describe the earlier embedded-runtime candidate. They are retained as pre-freeze historical evidence and are superseded by `release/RC12_RUNTIME_CANDIDATE_SUPERSESSION.json`; they do not define the active rc12 candidate.

Frozen rc11 bytes under `seed/releases/0.1-rc11/` remain immutable.
