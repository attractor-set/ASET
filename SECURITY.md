
# Security policy

## Supported scope

The repository supports secure publication and integrity verification of ASET Seed documentation. The current stable documentation release is rc11 and remains `PASS_WITH_LIMITATIONS`.

## Reporting

Report suspected vulnerabilities privately to the repository owner through GitHub Security Advisories when available. Do not publish exploit details before coordinated review.

## Repository controls

- protected `main` and protected published tags;
- least-privilege GitHub Actions permissions;
- dependency monitoring;
- deterministic release artifacts;
- SHA-256-bound manifests;
- black-box audit of release snapshots;
- common secret-pattern scanning.

## Explicit runtime limitations

The repository does not establish production cryptographic identity verification, key custody, durable concurrent transactions, distributed consensus, implementation-refinement proof, operational disaster recovery, or external certification.
