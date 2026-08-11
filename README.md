[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET is an open, implementation-neutral specification for a **minimal machine-interpretable semantic Seed**: a machine-readable, independently implementable and verifiable semantic vessel whose operational nucleus is authority-scoped resolution recognition. Here, *seeded* means both that admissibility originates from an explicitly recognized Authority binding and that the same public form can carry independently produced semantics forward without giving any producer recognition authority.

```text
UNKNOWN | ALLOW | BLOCK
```

Only one unique valid, locally recognized and exact-binding `ALLOW` record permits the bound effect. Missing or conflicting valid terminal material is `UNKNOWN`; explicit prohibition is `BLOCK`. External material does not create local Authority by itself.

## Why Seed

Seed is not a prescribed application architecture or evolution algorithm. It is the minimal public form that keeps normative meaning machine-readable, explicit enough for independent interpretation, independently implementable and externally verifiable. New candidate forms may be discovered by any external mechanism; producing, selecting or verifying a candidate never grants that mechanism Authority or recognition precedence.

ASET therefore standardizes the **public boundary of evolution**, not a privileged search substrate. See [Role of ASET Seed](docs/architecture/SEED_ROLE.md) and [Evolution boundary](docs/architecture/EVOLUTION_BOUNDARY.md).

## Direct downstream projects

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — implementation-neutral normative extension of ASET Seed for cross-context recognition.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — non-normative Seed reference implementation.

Only direct downstream relationships are listed here. Transitive descendants are discoverable through their immediate parent projects.

Normative source: [Seed canon](seed/canonical/README.md).

## Compatibility standard

Published Seed releases can serve as immutable, versioned compatibility standards for independent implementations. The first declared baseline is `seed-0.3.0-alpha.2`. Conformance is evaluated against the exact release identity, canonical package and mandatory cases by the external ASET conformance runner.

See [ASET Seed Compatibility Standard](standards/seed-compatibility/README.md).
