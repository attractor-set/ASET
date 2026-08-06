# PDCA-15 — Extension extraction closure

## Plan

Remove noncontrolling system/component material from the active ASET tree while preserving exact
provenance and keeping the Seed resolution semantics unchanged.

## Do

- externalized the legacy component corpus into a deterministic release asset;
- removed component canons, component audits, component-only tools, tests and generated views;
- added non-normative extension and implementation registries;
- aligned the declared repository assurance gates with the Seed-only repository boundary;
- recorded exact source revisions and archive digests.

## Check

The cleanup is acceptable only when Seed validation, canon-package parity, portable conformance,
model checking, traceability, repository tests, documentation audit and manifest parity pass.

## Act

Set `extension_separation` to `COMPLETE`. Future component semantics enter ASET only through an
explicit, separately versioned extension repository and never by restoring the former tree.
