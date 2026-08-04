# ASET Seed rc12 bounded runtime threat model

Profile: `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`.

## Protected assets

Canonical state, state roots, accepted transition history, proof-verifier configuration, audit-chain records, SQLite database and backups, and deployment secrets.

## Trusted boundary

One operating-system host, one local durable filesystem, the reviewed Python wheel, the configured proof verifier, and operators authorized to manage the service account and backups. Input transition authors, JSON files, and callers are untrusted.

## Addressed threats

- malformed or duplicate-member JSON is rejected before semantic use;
- schema-invalid and unknown transitions fail closed without state mutation;
- unauthenticated transitions fail closed because the default verifier rejects all proofs;
- concurrent writers serialize through `BEGIN IMMEDIATE`;
- state and audit entries commit atomically;
- replay does not consume state twice;
- database metadata prevents opening a file under the wrong runtime profile;
- audit records are hash chained and tampering is detected by health checks;
- health checks validate database integrity, semantic state, stored state roots, and audit chains;
- backup uses the SQLite backup API only after all runtime health checks pass;
- oversized transition documents are represented in the audit chain by exact digest and byte size;
- proof-verifier exceptions fail closed with a stable audited result;
- database symbolic links are rejected in the POSIX profile;
- secret files must not be group/world accessible on POSIX;
- the runtime imports no network or automatic external-effect adapter.

## Residual and excluded threats

Compromise of the host or service account, memory disclosure, malicious operators, HMAC-key compromise, filesystem or storage devices that violate durability guarantees, rollback to an older valid database, denial of service, distributed partitions, multi-primary writes, Byzantine consensus, physical-world false evidence, and vulnerabilities in Python, SQLite, or dependencies are not solved by Seed alone.

## Required controls

Use a dedicated service account, private secret files, local storage, monitored disk capacity, protected backups, restore rehearsal, dependency patching, exact wheel provenance, and fail-closed stop procedures. A deployment that violates the bounded assumptions may not claim this production profile.
