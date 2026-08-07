# ASET specification release process

## Protected lines

- `seed/releases/0.1-rc11/` is immutable historical Seed release material.
- `seed/canonical/` is the active normative Seed source and canon package.
- Extensions and implementations are maintained outside this repository and have no semantic
  precedence.
- Generated language editions, ontology/terminology views, `codemeta.json` and
  `.github/repository-metadata.json` must not be edited manually.
- Extracted legacy component material remains historical evidence in Git history and the
  extraction-closure audit record; it must not be silently reintroduced into Seed.

## Pull-request path

1. branch from the exact protected `main`;
2. state assumptions, scope and measurable acceptance criteria;
3. classify semantic changes independently from repository-only changes;
4. make only changes traceable to those criteria;
5. regenerate derived views with `python tools/generate_repository_views.py`;
6. rebuild the canon package with `python tools/build_canon_package.py`;
7. rebuild the repository manifest with `python tools/rebuild_manifest.py`;
8. run `python tools/repository_release_gate.py`;
9. inspect compatibility, model-check, traceability and documentation evidence;
10. merge only after every mandatory CI contour succeeds.

## Seed candidate path

1. preserve exact historical Seed release bytes;
2. bind exact canon, schemas, conformance cases, protocol, formal projections and repository
   manifest;
3. verify candidate self-consistency and compatibility with the approved canon;
4. run the full gate in a clean checkout;
5. retain external third-party audit status explicitly;
6. create a protected annotated tag only after owner approval;
7. publish immutable source snapshot, canon package, evidence and checksums;
8. rerun mandatory workflows against the exact tag target.

## Extension and implementation releases

External repositories release independently. Each must identify the exact supported Seed package
and publish its own conformance and assurance evidence. A passing external profile does not modify
or define ASET semantics.

## Prohibited operations

- rewriting immutable historical release bytes or protected tags;
- weakening a gate to make a candidate pass;
- editing generated artifacts instead of their canonical source;
- treating an extension, implementation, checker or programming language as normatively
  privileged;
- using repository readiness as evidence of deployment or physical-world safety;
- restoring extracted component semantics into Seed without an explicit canon change;
- storing deployment secrets in the repository.
