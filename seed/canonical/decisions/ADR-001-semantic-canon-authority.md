# ADR-001 — Semantic canon authority and language editions

Status: accepted for ASET Seed 0.1-rc12 release candidate; runtime-related wording superseded by ADR-002.

## Decision

`seed/canonical/source/seed-model.json` is the primary semantic source for rc12. Normative JSON Schemas, protocol and conformance profiles, constraints, transition records, formal projection, and generated language editions are bound to stable semantic identifiers. Russian, English, and Brazilian Portuguese documents are deterministic views and are never independent editing sources.

## rc11 compatibility boundary

ASET Seed 0.1-rc11 remains governed by its immutable release package. Rc12 preserves the rc11 wire version, semantic identity domains, exact 39 protocol schemas, 18 transition kinds, and 55-case behavior. The active rc12 normative change is the complete canonical authority, explicit migration binding, multilingual generation, formal projections and implementation-neutral conformance package. The earlier embedded-runtime outcome was superseded before freeze by ADR-002.

## Conflict handling

A mismatch among the canonical source, generated view, protocol profile, conformance binding, canonical package or formal projection invalidates the candidate. The fail-closed repository release gate must reject promotion.

## Hashing

Release identity binds exact files through the manifest and SHA-256. RDF and terminology views are generated projections; they do not define a separate byte-independent identity unless a future release specifies RDF dataset canonicalization.
