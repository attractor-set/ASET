
# ADR-001 — Semantic canon authority and language editions

Status: accepted for repository architecture; not a semantic freeze of rc12.

## Decision

For a future release after complete migration, the machine-readable semantic source is the primary canonical source. Normative schemas, constraints, requirement records and transition semantics are bound to stable semantic identifiers. Russian, English and Brazilian Portuguese editions are deterministic generated representations of the same source.

## rc11 boundary

ASET Seed 0.1-rc11 remains governed by its own release package, in which the Russian normative prose and executable machine profile are jointly subject to the internal-consistency rule. This ADR does not retroactively alter rc11.

## Conflict handling

A generated edition that does not match the source is invalid. No language edition may be used as an independent editing source. A semantic change requires an update to the canonical source and all bound verification artifacts.

## Hashing

Release identity binds exact files through the release manifest and SHA-256. JSON-LD or RDF semantic datasets, when introduced, require a separately specified canonicalization profile before their digest can be normative.
