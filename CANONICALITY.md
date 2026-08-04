
# Canonicality policy

## Stable release

ASET Seed 0.1-rc11 is an immutable historical release governed by its release envelope and audit evidence. The archive under `delivery/`, the materialized publication files, and the byte-exact `expanded/` tree are representations of the same frozen release. A mismatch is a release-integrity failure.

## Development canon

Files under `seed/canonical/` are the authoring and validation architecture for a future release. They do not redefine rc11 and are not a frozen replacement specification.

## Future normative order

After complete semantic migration and independent audit:

1. canonical semantic source;
2. normative schemas, constraints, requirements and transition model;
3. generated Russian, English and Brazilian Portuguese editions;
4. explanatory documentation.

## Conflict rule

A generated edition that differs from the canonical model is invalid. A release containing a divergence must fail closed.

## Generated files

Files under `docs/generated/` must not be edited manually.

## Claim separation

The repository may be production-ready as a publication and assurance system while the Seed runtime remains `HOLD`. These claims are distinct and must not be conflated.
