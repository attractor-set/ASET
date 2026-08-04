
# ASET

ASET is a specification-first project for governed contextual transformation and verifiable execution.

## Stable specification

The current stable ASET Seed documentation release is **0.1-rc11**. It is preserved as immutable release bytes and as a byte-exact expanded tree for direct review on GitHub.

- Frozen release: [`seed/releases/0.1-rc11/`](seed/releases/0.1-rc11/)
- Expanded specification: [`seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md`](seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md)
- Audit evidence: [`seed/releases/0.1-rc11/expanded/audit/`](seed/releases/0.1-rc11/expanded/audit/)
- Conformance corpus: [`seed/releases/0.1-rc11/expanded/conformance/`](seed/releases/0.1-rc11/expanded/conformance/)
- Machine-readable profile: [`seed/releases/0.1-rc11/expanded/machine/`](seed/releases/0.1-rc11/expanded/machine/)

## Repository readiness

The repository publication, validation, release-assurance, and documentation-audit process is production-ready. Every change to `main` is expected to pass deterministic generation, schema and semantic validation, frozen-release integrity, test and static checks, deterministic snapshot construction, and an independent black-box documentation audit.

This repository-readiness claim does **not** claim that a Seed runtime is production-ready. Runtime production status remains `HOLD`; external third-party audit remains `PENDING`; the rc12 machine-readable canon remains a non-released development scaffold.

See [`docs/repository/PRODUCTION_READINESS.md`](docs/repository/PRODUCTION_READINESS.md).

## Next-release development

The next Seed release is developed under [`seed/canonical/`](seed/canonical/). Generated Russian, English, and Brazilian Portuguese editions are derived from the same candidate canonical model. The migration coverage register explicitly records what is preserved, deferred, or not yet represented.

## Languages

- [Русский](README.ru.md)
- English
- [Português do Brasil](README.pt-BR.md)

## Required checks

```text
canonical validation
frozen rc11 integrity
expanded rc11 byte identity
generated-edition parity
terminology policy
unit tests and static checks
deterministic snapshot
black-box documentation audit
adversarial black-box rejection suite
production repository gate
```

Frozen release bytes are never rewritten.
