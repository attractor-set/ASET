[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET is an open, implementation-neutral specification whose Seed defines verifiable, authority-scoped resolution of an exact normative question from `UNKNOWN` to `ACCEPT` or `DENY`.

## Active Seed

```text
UNKNOWN --authorized resolution--> ACCEPT
UNKNOWN --authorized resolution--> DENY
UNKNOWN --explicit escalation----> UNKNOWN
```

`UNKNOWN` never authorizes an effect and is not silently converted to `DENY`. Authority does not follow context ancestry or federation membership automatically.

- Machine canon: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Canon package: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Portable conformance: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Formal projection: [`seed/canonical/formal/`](seed/canonical/formal/)
- Breaking migration: [`seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md`](seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md)

## Extensions and implementations

Execution, Permit consumption, negative attempts, planning, memory, federation topology, consensus, persistence and cryptographic providers are outside Seed. They belong to separately versioned extension templates and implementation profiles. No extension or implementation has semantic precedence.

[`aset-network-extension`](https://github.com/attractor-set/aset-network-extension) is the first separately versioned federation extension. Its non-normative registry entry is recorded in [`EXTENSIONS.md`](EXTENSIONS.md).

[`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite) remains non-normative. It must implement the active resolution conformance protocol before claiming compatibility with this Seed line; otherwise it remains pinned to its historical canon.

## Validation

```text
python tools/repository_release_gate.py
```

## Authorship and licence

ASET was independently created by **Dzmitry Prychyna**, publicly known as **Attractor Set**, and is licensed under Apache License 2.0. See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) and [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).

## Historical extension material and walkthrough

The current in-repository component canons are historical migration inputs pending extraction: [`aset/README.md`](aset/README.md). The non-normative controlled-patch walkthrough remains available at [`docs/tutorials/CONTROLLED_PATCH_WORKFLOW.md`](docs/tutorials/CONTROLLED_PATCH_WORKFLOW.md).

The reference implementation is [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite); it has no semantic precedence. Background-IP provenance is recorded in [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
