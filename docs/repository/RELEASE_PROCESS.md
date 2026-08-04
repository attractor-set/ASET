
# Release process

## Stable and development lines

- `seed/releases/0.1-rc11/` is immutable historical release material.
- `seed/canonical/` is mutable development material for a future release.
- Generated documents are derived artifacts and must not be edited directly.

## Pull-request path

1. branch from current protected `main`;
2. modify canonical sources, policies, tools, or repository documentation;
3. regenerate derived editions where applicable;
4. run `python tools/production_gate.py`;
5. attach black-box evidence to the pull request;
6. resolve all review conversations;
7. merge only after required checks pass.

## Release-candidate path

1. classify the semantic difference;
2. complete migration and traceability records;
3. freeze the candidate source and conformance suite digests;
4. run the full production gate in a clean environment;
5. run independent black-box audit against the built snapshot;
6. complete owner approval and independent audit;
7. create a protected annotated tag;
8. publish immutable release assets and checksums.

## Prohibited operations

- rewriting frozen release bytes;
- bypassing failed or missing checks;
- claiming runtime production readiness from documentation evidence;
- editing generated language editions manually;
- replacing an existing protected release tag.
