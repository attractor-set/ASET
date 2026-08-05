# Component canon refactoring log

## RF-001 — shared toolchain

Seven duplicated validators/generators were rejected. One shared component schema vocabulary, validator, view generator, conformance runner and bounded checker serve all independently versioned canons.

## RF-002 — exact source registry

The rc11 monolith is retained once as read-only source evidence. Component canons store identifiers and mappings rather than copied requirement prose or duplicated protocol schemas.

## RF-003 — mutation descriptors

Conformance negative cases use small deterministic mutation descriptors instead of full copied invalid fixtures. This reduces drift while preserving reproducible rejection evidence.

## RF-004 — distinct formal projections

An initial generic formal skeleton was replaced before acceptance with component-specific TLA+ projections and independent bounded state models.

## RF-005 — self-contained slices without toolchain duplication

Each canon now carries its own requirements, verification, traceability, invariants, limitations, threat model, protocol profile and conformance binding. Validation logic and schema vocabulary remain shared, preventing eight divergent assurance frameworks.

## RF-006 — root navigation without duplicate specification prose

The root READMEs expose one concise component-line summary and link to `aset/README.md`. Detailed ownership, protocol and assurance content remains in generated component views, avoiding a second hand-maintained specification.

## RF-007 — canonical multilingual normalization

Foreign-term normalization is applied by the shared generator only to prose outside code spans. Generated files are never repaired by hand, and the existing repository language policy remains the single vocabulary source.
