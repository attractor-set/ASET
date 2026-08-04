# ASET Seed 0.1-rc12 canonical area

Status: `RC12_RELEASE_CANDIDATE_READY`

This directory is the complete machine-readable canonical candidate for ASET Seed 0.1-rc12. It preserves the audited rc11 wire semantics and identity domains while making the full requirements, invariants, transition catalogue, protocol schemas, conformance bindings, terminology, formal safety projection, and bounded production runtime profile explicit and machine-checkable.

The bounded production claim covers the single-node SQLite profile only. External proof-key management, distributed consensus, physical-world truth, deployment hardening, and independent third-party certification remain outside this claim.

## Canon hierarchy

1. `source/seed-model.json`;
2. protocol schemas and profiles;
3. requirements, invariants, transition and conformance bindings in the model;
4. generated RU, EN, and pt-BR editions;
5. diagrams and examples.

Frozen rc11 bytes under `seed/releases/0.1-rc11/` remain immutable.
