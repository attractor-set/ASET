# ASET Seed release process

## Protected lines

- `seed/releases/0.1-rc11/` is immutable historical release material.
- `seed/canonical/` is the rc12 normative candidate source and generated semantic projections.
- `src/aset_seed/` is the bounded reference runtime bound to the canonical protocol profile.
- Generated language editions, ontology/terminology views, `codemeta.json` and `.github/repository-metadata.json` must not be edited manually.

## Pull-request path

1. branch from the exact protected `main`;
2. state assumptions, scope, and measurable acceptance criteria;
3. make only changes traceable to those criteria;
4. regenerate derived views with `python tools/generate_repository_views.py`;
5. run `python tools/production_gate.py`;
6. inspect the final documentation and runtime black-box reports as the last PDCA check;
7. record and close every blocking finding;
8. merge only after mandatory CI succeeds.

## rc12 release-candidate path

1. require 83/83 migration coverage with zero deferred or unclassified item;
2. bind exact canon, schema, conformance, formal, implementation, suite, and wheel identities;
3. run the full gate in a clean checkout;
4. perform deployment-profile review and backup/restore rehearsal;
5. require `RC12_FREEZE_ENTRY.json` to report technical readiness while keeping owner approval and exact-byte freeze pending;
6. retain external third-party audit status explicitly;
7. perform the clean-room exact-byte freeze cycle;
8. create a protected annotated tag only after owner approval;
9. publish immutable source snapshot, wheel, evidence, release envelope, and checksums;
10. rerun mandatory workflows against the exact tag target.

## Prohibited operations

- rewriting rc11 release bytes or protected tags;
- weakening a gate to make a candidate pass;
- editing generated artifacts instead of the canonical source;
- using repository readiness as evidence of distributed or universal runtime safety;
- enabling automatic external effects inside Seed;
- storing deployment secrets in the repository.
