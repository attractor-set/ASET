[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET is an open, implementation-neutral specification for Authority-Signed Evidence Trails, enabling model-based conformance and verifiable accountability across heterogeneous sociotechnical systems.

## What defines ASET

ASET is defined by the machine-readable canon, normative schemas, validity conditions, invariants, transition semantics and conformance corpus. No implementation, programming language, storage engine, checker or deployment profile has semantic precedence.

- Machine canon: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Canon package identity: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Formal projection: [`seed/canonical/formal/`](seed/canonical/formal/)
- Conformance corpus: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Component canons: [`aset/README.md`](aset/README.md)

## Model-based implementation conformance

Independent implementations are tested as black boxes through `ASET-IMPLEMENTATION-CONFORMANCE-V1`. The implementation returns observable results; an external runner consumes a pinned canon package and determines the verdict. Candidate-canon consistency and compatibility with an approved canon are separate gates.

```text
python tools/run_external_conformance.py   --canon-root /path/to/ASET   --adapter "/path/to/implementation-adapter"
```

Storage, durability, concurrency, recovery, consensus, networking and key custody belong to implementation profiles. Profiles may strengthen operational guarantees but may not weaken Seed semantics.

## Implementations

Implementations are maintained independently from this specification. A minimal non-normative Python + SQLite educational profile is intended for the separate `aset-python-sqlite` repository. Its use does not make Python or SQLite part of ASET.

## Release lines

ASET Seed 0.1-rc11 remains the immutable historical stable release. The rc12 machine-canon line is being prepared as an implementation-neutral specification and conformance package. Historical runtime candidate evidence is retained but is not the current repository role.

## Validation

```text
python tools/repository_release_gate.py
```

## Authorship, licence and rights

ASET was independently created by **Dzmitry Prychyna**, publicly known as **Attractor Set**. The project is licensed under Apache License 2.0. Licensing grants permissions under that licence; it does not transfer authorship or ownership. See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) and [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
