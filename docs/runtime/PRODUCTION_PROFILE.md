# ASET Seed rc12 bounded production runtime

## Supported claim

`PRODUCTION_READY_BOUNDED_PROFILE` means a single host, one SQLite database, serialized writers, strict JSON input, an explicitly configured proof verifier, atomic state-and-audit commits, hash-chained audit attempts, integrity checks, consistent backup, and deterministic rc11 semantic compatibility.

It does not mean distributed consensus, automatic external effects, universal cryptographic trust, physical truth, or external certification.

## Proof profiles

The default verifier rejects every transition. The bundled production verifier is `HMAC_SHA256_V1`; deployments may provide a separately reviewed verifier through the embedded interface. HMAC keys are deployment secrets and must never be stored in the repository. A proof decision must bind the exact canonical transition content.

## Durability

The SQLite profile uses WAL, `synchronous=FULL`, `BEGIN IMMEDIATE`, an exact schema/profile binding, and the SQLite backup API. State mutation and its audit entry commit in the same transaction. Backup is refused unless database integrity, semantic state validation, and audit-chain verification all pass.

## Input and audit boundary

Every JSON transition document targeting an existing trust space is recorded in that trust space's hash-chained audit log. Oversized documents are recorded by exact SHA-256 digest and byte size. A Python value that cannot be represented as JSON is rejected before transition admission with `INPUT_NOT_JSON_VALUE`; an unknown trust-space identifier is rejected with `TRUST_SPACE_UNKNOWN` because no trust-space-local chain exists for it.

## Interface

```text
aset-seed --db seed.db init genesis.json
aset-seed --db seed.db --proof-secrets secrets.json apply <trust_space_id> transition.json
aset-seed --db seed.db state <trust_space_id>
aset-seed --db seed.db validate <trust_space_id>
aset-seed --db seed.db health
aset-seed --db seed.db backup backup.db
```
