[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET is an open, implementation-neutral specification for a minimal authority-scoped resolution kernel. Here, *seeded* means that admissibility originates from an explicitly recognized Authority binding; no particular cryptographic signature mechanism is required by the Seed.

```text
UNKNOWN | ALLOW | BLOCK
```

Only one unique valid, locally recognized and exact-binding `ALLOW` record permits the bound effect. Missing or conflicting valid terminal material is `UNKNOWN`; explicit prohibition is `BLOCK`. External material does not create local Authority by itself.

## Reference artifacts

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — non-normative reference extension.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — non-normative reference implementation.

Normative source: [Seed canon](seed/canonical/README.md).

## Compatibility standard

Published Seed releases can serve as immutable, versioned compatibility standards for independent implementations. The first declared baseline is `seed-0.3.0-alpha.2`. Conformance is evaluated against the exact release identity, canonical package and mandatory cases by the external ASET conformance runner.

See [ASET Seed Compatibility Standard](standards/seed-compatibility/README.md).
