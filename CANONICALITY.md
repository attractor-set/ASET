# Canonicality policy

## Stable release

ASET Seed 0.1-rc11 remains the immutable current stable release. Its delivery archive, materialized publications, byte-exact expanded tree, release envelope and audit evidence are representations of one frozen identity. Any mismatch is a release-integrity failure.

## rc12 release-candidate canon

`seed/canonical/` is the complete normative machine canon for the ASET Seed 0.1-rc12 release candidate. It does not mutate rc11. The candidate becomes the current stable release only after every mandatory gate passes on exact release bytes, the protected-branch change is merged, and a separately identified rc12 release is frozen.

The earlier rc12 embedded-runtime candidate is retained as pre-freeze historical evidence and is explicitly superseded by `seed/canonical/release/RC12_RUNTIME_CANDIDATE_SUPERSESSION.json`.

## Normative order for rc12

1. `seed/canonical/source/seed-model.json` and its stable semantic identifiers;
2. normative schemas, constraints, requirements, invariants, transition semantics and conformance bindings;
3. `seed/canonical/CANON_PACKAGE.json`, canonical cases and the implementation-conformance protocol;
4. formal safety projections and bounded model-check evidence;
5. deterministic Russian, English and Brazilian Portuguese editions;
6. explanatory and operational documentation.

No executable implementation, checker or storage profile is a second source of semantics. If an implementation conflicts with the canon, the implementation is non-conforming. If a checker conflicts with frozen canonical cases or formal properties, the checker is defective.

## Full ASET composition canon

`aset/system/canonical/source/system-composition-model.json` is the normative machine-readable source for the architectural role of Seed within complete ASET systems. Its `seed_role` object defines Seed as the minimal, implementation-neutral semantic nucleus and states the composition, extension and claim boundaries for compatible component canons and implementation profiles.

This composition canon does not modify or supersede `seed/canonical/`. Component integration acquires authoritative ASET significance only through conformance to Seed semantics. Generated System Composition editions are deterministic projections of the composition canon.

## Conflict rule

A generated edition, protocol copy, formal projection, conformance binding, checker verdict or executable behavior that conflicts with the canonical model is invalid. The repository release gate must fail closed.

## Project identity metadata

`metadata/project.json` is the canonical repository-discovery source for the project name, the Authority-Signed Evidence Trail expansion, the GitHub About description, repository topics and CodeMeta projection. `codemeta.json`, `.github/repository-metadata.json` and `docs/generated/README.md` are deterministic generated views of that source.

The explanatory introductions in `README.md`, `README.ru.md` and `README.pt-BR.md` remain curated static documentation. Their claims must remain consistent with canonical project metadata, but they are not generated because translation and explanatory context require review.

## Generated files

Files under `docs/generated/`, generated semantic views, CodeMeta and repository-discovery projections, manifests and machine audit reports must be reproduced by their generators and must not be edited manually.

Regenerate all derived repository views with `python tools/generate_repository_views.py`. Verify committed parity with `python tools/generate_repository_views.py --check`.

## Claim boundary

The specification repository claims a machine-readable canon, language-neutral conformance contract, formal projections, deterministic generated views and repository-level assurance. It does not claim that any particular implementation is production-ready, nor does it prescribe Python, SQLite, PostgreSQL, a distributed consensus mechanism, deployment key management or physical-world truth. Such guarantees belong to separately identified implementation profiles and their own evidence.
