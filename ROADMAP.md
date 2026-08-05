# Roadmap

## Specification and conformance

- keep the machine canon implementation-neutral;
- maintain exact traceability between requirements, invariants, formal actions and conformance cases;
- publish immutable canon packages with digests;
- distinguish candidate self-consistency from compatibility with the approved canon;
- support independent black-box implementation adapters;
- preserve frozen historical releases and evidence.

## Independent implementation profiles

- maintain the non-normative [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite) reference implementation and educational profile in its separate repository;
- add independent implementations in other languages and storage technologies;
- execute the acceptance plan in [`docs/implementation/CROSS_IMPLEMENTATION_CONFORMANCE_PLAN.md`](docs/implementation/CROSS_IMPLEMENTATION_CONFORMANCE_PLAN.md) with an independently engineered Rust/PostgreSQL profile;
- keep durability, consensus, confidential computation and deployment guarantees profile-specific.

## Full ASET component specification line

See [`aset/README.md`](aset/README.md). Future work includes independent implementations, external audit, component-specific runtime evidence and separately governed version evolution.

## Authorship and Background IP

The public pre-existing-IP boundary remains recorded in [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md). Repository separation does not assign or extinguish those rights.
