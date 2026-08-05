# ASET

ASET is an open specification and reference implementation for Authority-Signed Evidence Trails, enabling verifiable accountability within heterogeneous sociotechnical systems.

The specification defines a shared accountability semantics for governed contextual transformation and verifiable execution. It is authoritative over implementations.

## ASET Seed as the semantic nucleus

ASET Seed is the minimal, implementation-neutral semantic nucleus of ASET. It defines the authority-bound concepts, validity conditions, invariants and transition semantics from which complete ASET systems and compatible implementation profiles can grow.

Components may provide planning, memory, orchestration, external-effect execution, evidence acquisition and analytics. Seed determines when their work acquires authoritative ASET significance. See [`docs/architecture/SEED_ROLE.md`](docs/architecture/SEED_ROLE.md).

## Release lines

**ASET Seed 0.1-rc11** remains the immutable audited stable release. **ASET Seed 0.1-rc12** is the complete machine-canon release candidate and includes an installable bounded production runtime.

- Frozen rc11 release: [`seed/releases/0.1-rc11/`](seed/releases/0.1-rc11/)
- rc12 machine canon: [`seed/canonical/`](seed/canonical/)
- Generated rc12 specification: [`docs/generated/en/ASET_Seed_0.1-rc12.md`](docs/generated/en/ASET_Seed_0.1-rc12.md)
- Bounded runtime: [`src/aset_seed/`](src/aset_seed/)
- Deployment profile: [`docs/runtime/PRODUCTION_PROFILE.md`](docs/runtime/PRODUCTION_PROFILE.md)
- Deployment checklist: [`docs/runtime/DEPLOYMENT_CHECKLIST.md`](docs/runtime/DEPLOYMENT_CHECKLIST.md)

## rc12 candidate scope

The rc12 canon contains 27 concepts, 40 requirements, 37 invariants, 18 transition kinds, 39 strict JSON Schemas, and 55 bound conformance cases. The rc11 semantic surface is explicitly migrated 83/83 with no deferred or unclassified item. Russian, English, and Brazilian Portuguese editions are generated from one machine source.

The executable profile is production-ready only within `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`: one host, serialized SQLite writers, WAL with `synchronous=FULL`, local CLI or embedded API, explicit proof verification, durable state and append-only hash-chained audit records. The default proof verifier rejects every transition.

This claim excludes distributed consensus, multi-primary operation, automatic network or physical effects, physical-world truth, deployment key management, and external certification. External third-party audit remains `PENDING`.

## Required assurance

Every candidate change is required to pass generated-view parity, schema and SHACL validation, exact frozen rc11 preservation, 55-case semantic regression, 252 branch guards, at least 90% core branch coverage, bounded model checking, unit and concurrency tests, Ruff, wheel installation, deterministic snapshot construction, documentation black-box audit, runtime black-box audit, adversarial mutation rejection, and zero blocking findings.

Run:

```text
python tools/production_gate.py
```

## Languages

- [Русский](README.ru.md)
- English
- [Português do Brasil](README.pt-BR.md)

## Project metadata

- Canonical project identity: [`metadata/project.json`](metadata/project.json)
- CodeMeta projection: [`codemeta.json`](codemeta.json)
- GitHub About projection: [`.github/repository-metadata.json`](.github/repository-metadata.json)

Regenerate all derived documentation and repository metadata with:

```text
python tools/generate_repository_views.py
```

## Full ASET component canons

The full ASET 1.5-rc11 machine specification is preserved as exact source evidence and decomposed into independently versioned candidate canons for System Composition, Context, Core, Monade, Memory, Master, Model Gateway and Protocol. The component line is `0.1-rc1` and is explicitly bound to ASET Seed `0.1-rc12`.

- Component canon index: [`aset/README.md`](aset/README.md)
- System composition: [`aset/system/`](aset/system/)
- Seed compatibility bridge: [`aset/shared/seed-bridge/`](aset/shared/seed-bridge/)

The decomposition preserves the rc11 inventory exactly: 177 requirements, 57 invariants, 52 artifacts, 11 gates and 57 schemas. It has 26 component conformance cases and eight bounded formal projections. These are specification-candidate claims only; independent implementation and production conformance are not claimed.

## Python semantic critical-path reference

A non-normative, storage-free Python reference now executes the complete deterministic
semantic path from Context projection through governed dispatch, Observation, Evidence,
Verification and conditional Outcome recognition. See
[`docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md`](docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md).
It is an interoperability and assurance artifact, not a production deployment claim.
