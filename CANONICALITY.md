# Canonicality policy

## Stable release

ASET Seed 0.1-rc11 remains the immutable current stable release. Its delivery archive, materialized publications, byte-exact expanded tree, release envelope, and audit evidence are representations of one frozen identity. Any mismatch is a release-integrity failure.

## rc12 release candidate canon

`seed/canonical/` is the complete normative machine canon for the ASET Seed 0.1-rc12 release candidate. It does not mutate rc11. The candidate becomes the current stable release only after every mandatory gate passes on exact release bytes, the protected-branch change is merged, and a separately identified rc12 release is frozen.

## Normative order for rc12

1. `seed/canonical/source/seed-model.json` and its stable semantic identifiers;
2. normative protocol schemas, constraints, requirements, invariants, transition catalogue, and conformance bindings;
3. the bounded formal safety projection and executable model-check evidence;
4. deterministic Russian, English, and Brazilian Portuguese editions;
5. explanatory and operational documentation.

The executable runtime is a conforming implementation of the bounded profile. It is not a second source of semantics.

## Full ASET composition canon

`aset/system/canonical/source/system-composition-model.json` is the normative machine-readable source for the architectural role of Seed within complete ASET systems. Its `seed_role` object defines Seed as the minimal, implementation-neutral semantic nucleus and states the composition, extension and claim boundaries for compatible component canons and implementation profiles.

This composition canon does not modify or supersede `seed/canonical/`. Component integration acquires authoritative ASET significance only through conformance to Seed semantics. Generated System Composition editions are deterministic projections of the composition canon.

## Conflict rule

A generated edition, protocol copy, runtime schema, formal projection, conformance binding, or executable behavior that conflicts with the canonical model is invalid. The release gate must fail closed.

## Project identity metadata

`metadata/project.json` is the canonical repository-discovery source for the project name, the Authority-Signed Evidence Trail expansion, the GitHub About description, repository topics and CodeMeta projection. `codemeta.json`, `.github/repository-metadata.json` and `docs/generated/README.md` are deterministic generated views of that source.

The explanatory introductions in `README.md`, `README.ru.md` and `README.pt-BR.md` remain curated static documentation. Their claims must remain consistent with the canonical project metadata, but they are not generated because translation and explanatory context require review.

## Generated files

Files under `docs/generated/`, generated semantic views, CodeMeta and repository-discovery projections, release envelopes, manifests, and machine audit reports must be reproduced by their generators and must not be edited manually.

Regenerate all derived repository views with `python tools/generate_repository_views.py`. Verify committed parity with `python tools/generate_repository_views.py --check`.

## Claim boundary

The rc12 candidate includes a production-ready single-host SQLite runtime profile with serialized writers, durable local commits, explicit proof verification, and no implicit external effects. It does not claim distributed consensus, multi-primary safety, physical-world truth, universal formal proof, deployment key management, or external certification. These exclusions are normative assurance boundaries rather than hidden implementation gaps.
