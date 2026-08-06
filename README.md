[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET is an open, implementation-neutral specification whose Seed defines verifiable,
authority-scoped resolution of an exact normative question from `UNKNOWN` to `ACCEPT` or
`DENY`.

```text
UNKNOWN --authorized resolution--> ACCEPT
UNKNOWN --authorized resolution--> DENY
UNKNOWN --explicit escalation----> UNKNOWN
```

`UNKNOWN` never authorizes an effect and is not silently converted to `DENY`. Authority does
not follow Context ancestry, federation membership, implementation choice or AI output.

## Active Seed

- Canon: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Package: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Conformance: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Formal projection: [`seed/canonical/formal/`](seed/canonical/formal/)
- Release status: [`REPOSITORY_STATUS.json`](REPOSITORY_STATUS.json)

The active candidate is `0.2.0-alpha.2`. Alpha 2 changes the repository and assurance boundary,
not the resolution algebra introduced by alpha 1.

## External ecosystem

Extensions and implementations are versioned outside this repository and have no semantic
precedence.

- Extension registry: [`EXTENSIONS.md`](EXTENSIONS.md)
- Implementation registry: [`IMPLEMENTATIONS.md`](IMPLEMENTATIONS.md)
- Extraction record: [`EXTRACTION.md`](EXTRACTION.md)

Published repositories currently include:

- [`aset-network-extension`](https://github.com/attractor-set/aset-network-extension)
- [`aset-ai-extension-template`](https://github.com/attractor-set/aset-ai-extension-template)
- [`aset-ai-local-stack`](https://github.com/attractor-set/aset-ai-local-stack)
- [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite)

## Validation

```text
python tools/repository_release_gate.py
```

## Authorship and licence

ASET was independently created by **Dzmitry Prychyna**, publicly known as **Attractor Set**,
and is licensed under Apache License 2.0. See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) and
[`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).

- [External extension conformance](docs/implementation/EXTENSION_CONFORMANCE.md)
