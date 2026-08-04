
# Governance

ASET uses owner-led, specification-first governance with protected `main` and protected release tags.

A normative change requires:

1. a machine-readable proposal;
2. semantic-difference classification;
3. schema and constraint updates;
4. executable conformance cases where semantics change;
5. regenerated official editions;
6. deterministic snapshot construction;
7. black-box documentation audit;
8. independent review for a release candidate;
9. a new immutable release.

Every mandatory release gate is fail-closed. Missing evidence is failure, not waiver.

Frozen release bytes are never rewritten. Experimental work belongs outside frozen release directories.
