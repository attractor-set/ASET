# ASET specification release process

## Protected lines

- `seed/releases/0.1-rc11/` is immutable historical release material.
- `seed/canonical/` is the rc12 normative candidate source, canonical conformance package and generated semantic projections.
- `aset/` contains component and system-composition canons governed by their own traceable sources.
- Implementations are maintained outside the specification repository and have no semantic precedence.
- Generated language editions, ontology/terminology views, `codemeta.json` and `.github/repository-metadata.json` must not be edited manually.

## Pull-request path

1. branch from the exact protected `main`;
2. state assumptions, scope and measurable acceptance criteria;
3. classify canon changes as none, monotonic extension or breaking normative change;
4. make only changes traceable to those criteria;
5. regenerate derived views with `python tools/generate_repository_views.py`;
6. rebuild the canon package with `python tools/build_canon_package.py`;
7. rebuild the repository manifest with `python tools/rebuild_manifest.py`;
8. run `python tools/repository_release_gate.py`;
9. inspect model-check, conformance and black-box component evidence;
10. merge only after mandatory CI succeeds.

## rc12 specification-candidate path

1. preserve exact rc11 release bytes and compatibility evidence;
2. bind exact canon, schemas, conformance cases, protocol, formal projections and repository manifest;
3. verify candidate self-consistency and compatibility with the independently identified approved canon;
4. run the full gate in a clean checkout;
5. retain external third-party audit status explicitly;
6. perform the clean-room exact-byte freeze cycle;
7. create a protected annotated tag only after owner approval;
8. publish immutable source snapshot, canonical package, evidence, release envelope and checksums;
9. rerun mandatory workflows against the exact tag target.

## Implementation releases

Implementation repositories release independently. Each implementation must identify the exact supported canon version, commit and package digest, expose the language-neutral conformance adapter, and publish its own profile-specific assurance. A passing implementation profile does not modify or define ASET semantics.

## Prohibited operations

- rewriting rc11 release bytes, historical evidence or protected tags;
- weakening a gate to make a candidate pass;
- editing generated artifacts instead of the canonical source;
- treating an implementation, checker or programming language as normatively privileged;
- using repository readiness as evidence of deployment, distributed or universal runtime safety;
- storing deployment secrets in the repository.

## CI assurance contours

The candidate-consistency, formal/adversarial, and approved-to-candidate compatibility contours are intentionally separate. See [`CI_ASSURANCE.md`](CI_ASSURANCE.md) for their responsibilities and claim boundaries.
