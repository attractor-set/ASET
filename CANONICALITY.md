# Canonicality

`seed/canonical/` is the active normative ASET Seed resolution core. Its machine-readable model,
referenced schemas, requirements, invariants, conformance corpus and package identity define the
active canon.

The decision lattice is `UNKNOWN -> ACCEPT | DENY`. `UNKNOWN` is distinct from `DENY`, remains
operationally blocked and may move to another Resolution Authority only through an explicit
escalation grant.

No extension, implementation, programming language, storage engine, AI model or checker has
semantic precedence. `EXTENSIONS.json` and `IMPLEMENTATIONS.json` are discovery registries only.

Legacy system and component material is not part of the active tree or Seed conformance. Its
provenance and immutable extraction identity are recorded in [`EXTRACTION.json`](EXTRACTION.json)
and preserved in Git history and the legacy release asset.
