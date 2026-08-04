# Canonical Seed development area

Status: `BOOTSTRAP_SCAFFOLD_NOT_RELEASED`

This area provides the authoring and validation architecture for a future ASET Seed release. It is not yet a complete extraction of rc11 and must not be cited as the current stable specification.

The current stable documentation remains the frozen rc11 release under `seed/releases/0.1-rc11/`.

## Components

- `source/seed-model.json` — structured canonical source candidate;
- `schemas/` — structural and repository-assurance validation;
- `ontology/` — RDF/OWL semantic vocabulary;
- `shapes/` — SHACL constraints;
- `terminology/` — SKOS and TBX terminology;
- `formal/` — formal transition-model work;
- `migration/` — explicit rc11-to-rc12 dispositions;
- `assurance/` — release gates and known limitations;
- `decisions/` — canonicality and architecture decisions.

A future semantic freeze requires complete requirement and transition traceability, executable conformance coverage, formal evidence, deterministic publications, independent black-box audit, and a clean-room release audit.
