# Canonicality policy

## Current boundary

ASET Seed 0.1-rc11 is an immutable historical release governed by
its own release envelope and audit evidence.

The files under `seed/canonical/` are a bootstrap scaffold for
0.1-rc12 development. They do not retroactively redefine rc11 and
are not a frozen replacement specification.

## Future normative order

Once the canonical migration has passed independent audit:

1. canonical semantic source;
2. normative schemas, SHACL constraints and formal transition model;
3. generated Russian, English and Brazilian Portuguese editions;
4. explanatory documentation.

## Conflict rule

A generated edition that differs from the canonical model is invalid.
A release containing such a difference must fail closed and cannot
be promoted.

## Generated files

Files below `docs/generated/` must not be edited manually.
Changes must be made in the canonical source, terminology registry
or language templates.
