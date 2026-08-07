# Security policy

## Supported scope

This repository supports secure publication and integrity verification of the implementation-neutral ASET Seed specification, its canon package, formal assurance, conformance material, and repository snapshots.

The active Seed source is `0.3.0-alpha.1`; its semantic baseline is frozen by `seed-0.3.0-alpha.1-semantic-freeze`. The historical `0.1-rc11` release remains immutable evidence and is not the active specification surface.

## Reporting

Report suspected vulnerabilities privately to the repository owner through GitHub Security Advisories when available. Do not publish exploit details before coordinated review.

## Repository controls

- protected `main` and protected published tags;
- least-privilege GitHub Actions permissions;
- dependency monitoring;
- deterministic repository snapshots and canon packages;
- SHA-256-bound manifests;
- formal, conformance, mutation, traceability, and black-box assurance gates;
- common secret-pattern scanning.

## Explicit limitations

ASET Seed is a specification, not a deployment security product. The repository does not establish production cryptographic identity verification, key custody, storage durability, concurrent transaction safety, distributed consensus, deployment recovery, physical-world truth, external certification, or correctness of a concrete implementation profile.

The repository proves properties of the declared abstract Seed model and its canonical TLA+ projection. Concrete implementations, cryptographic providers, Authority evidence mechanisms, storage engines, networks, and deployment profiles must establish their own security and conformance claims independently.
