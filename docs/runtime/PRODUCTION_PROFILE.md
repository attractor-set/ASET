# ASET Seed rc12 bounded production runtime

## Supported claim

`PRODUCTION_READY_BOUNDED_PROFILE` means a single host, one SQLite database, serialized writers, strict JSON input, an explicitly configured proof verifier, atomic state-and-audit commits, hash-chained audit attempts, integrity checks, consistent backup, and deterministic rc11 semantic compatibility.

It does not mean distributed consensus, automatic external effects, universal cryptographic trust, physical truth, or external certification.

## Proof profiles

The default verifier rejects every transition. Deployments must configure either an external verifier, `HMAC_SHA256_V1`, or a pinned pre-verified digest set. HMAC keys are deployment secrets and must never be stored in the repository.

## Durability

The SQLite profile uses WAL, `synchronous=FULL`, `BEGIN IMMEDIATE`, an exact schema/profile binding, and the SQLite backup API. State mutation and its audit entry commit in the same transaction.

## Interface

```text
aset-seed --db seed.db init genesis.json
aset-seed --db seed.db --proof-secrets secrets.json apply <trust_space_id> transition.json
aset-seed --db seed.db state <trust_space_id>
aset-seed --db seed.db validate <trust_space_id>
aset-seed --db seed.db health
aset-seed --db seed.db backup backup.db
```
