# ASET Seed 0.1-rc12 bounded production deployment checklist

Status: normative operational checklist for `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`.

This checklist applies only to the bounded single-node SQLite profile. It does not claim distributed consensus, multi-primary operation, physical-world truth, or external certification.

## Before deployment

- [ ] The deployed wheel was built from an exact reviewed rc12 candidate commit.
- [ ] `python tools/production_gate.py` passed on that commit.
- [ ] The deployment uses Python 3.12 and the release-bound dependency `jsonschema==4.26.0`.
- [ ] The SQLite database is on a local durable filesystem; network filesystems are prohibited.
- [ ] Only one operating-system host writes the database.
- [ ] The database and backup paths are restricted to the service account (`0600` on POSIX).
- [ ] HMAC secrets contain at least 32 random bytes and are supplied outside the repository.
- [ ] The default `REJECT_ALL` proof profile is retained until an explicit proof profile is configured.
- [ ] Backup destination, retention, restore ownership, and restore-test cadence are documented.
- [ ] Disk-full, process-crash, corrupted-database, rejected-proof, and audit-chain alerts are configured.

## Start and acceptance

1. Initialize a new database from a reviewed Root Genesis.
2. Record the returned `trust_space_id` and initial state root.
3. Run `aset-seed --db <path> health` and require database integrity `ok`, state validation `PASS`, and audit chain `PASS`.
4. Submit one signed non-effectful acceptance transition in a disposable trust space.
5. Validate the resulting state and create a backup.
6. Restore the backup in an isolated path and repeat health and state validation.

## Routine operation

- Run health checks after startup and after backup/restore activity.
- Treat `PROOF_REJECTED`, schema rejection, or unchanged state as expected fail-closed outcomes, not as permission to bypass the verifier.
- Never edit SQLite rows, canonical state JSON, transition records, or audit hashes manually.
- Stop writes before filesystem-level copying; prefer the runtime backup command.
- Preserve exact application, Python, schema, and proof-profile versions with operational evidence.

## Upgrade and rollback

- Upgrade only through a reviewed release candidate with a passing production gate.
- Back up and validate before upgrade.
- The rc12 runtime preserves the rc11 wire and semantic identity profile; a future wire change requires an explicit migration specification.
- Rollback means restoring a validated pre-upgrade backup and matching executable, never rewriting accepted history.

## Incident boundary

Fail closed and stop new writes when database integrity, audit-chain integrity, filesystem durability, key provenance, or single-writer assumptions are uncertain. Recovery does not authorize changing immutable Seed history.
