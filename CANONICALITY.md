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

## Conflict rule

A generated edition, protocol copy, runtime schema, formal projection, conformance binding, or executable behavior that conflicts with the canonical model is invalid. The release gate must fail closed.

## Generated files

Files under `docs/generated/`, generated semantic views, release envelopes, manifests, and machine audit reports must be reproduced by their generators and must not be edited manually.

## Claim boundary

The rc12 candidate includes a production-ready single-host SQLite runtime profile with serialized writers, durable local commits, explicit proof verification, and no implicit external effects. It does not claim distributed consensus, multi-primary safety, physical-world truth, universal formal proof, deployment key management, or external certification. These exclusions are normative assurance boundaries rather than hidden implementation gaps.
