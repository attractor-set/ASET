# ASET

ASET is a specification-first project for governed contextual
transformation and verifiable execution.

## Repository status

- ASET Seed 0.1-rc11 is preserved as an immutable historical release.
- The machine-readable canon for the next Seed release is under
  development.
- Russian, English and Brazilian Portuguese editions are generated
  directly from the same canonical model.
- The reference implementation is a candidate.
- Production status remains HOLD.

## Canonicality

For releases created after the canonical migration:

1. machine-readable semantic model;
2. machine-readable constraints and invariants;
3. generated official language editions;
4. explanatory material.

A frozen release cannot be changed retroactively.

## Languages

- [Русский](README.ru.md)
- English
- [Português do Brasil](README.pt-BR.md)

## Main directories

- `seed/releases/` — immutable Seed releases;
- `seed/canonical/` — next-release canonical work;
- `docs/generated/` — generated language editions;
- `tools/` — validation and publication tools;
- `.github/workflows/` — continuous-integration checks.

## Assurance boundary

Documentation freeze does not imply production readiness,
cryptographic deployment assurance, durable concurrent storage,
distributed consensus or third-party certification.
