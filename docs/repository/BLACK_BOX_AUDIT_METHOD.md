# Black-box audit method

The final `Check` step of every PDCA cycle evaluates only the deterministic repository snapshot and the public runtime interface. It does not trust internal pass records or import the repository validator.

## Documentation black-box boundary

The snapshot auditor performs 28 independent checks: archive safety and CRC; exact manifest scope and hashes; license and citation; claim boundaries; mandatory gates and findings; frozen and expanded rc11 byte identity; requirements, traceability and conformance inventories; strict JSON; Python syntax; generated multilingual parity; migration completeness; required documents and local links; terminology and secret scanning; workflows; Git byte preservation; rc12 canon counts; canonical/runtime schema identity; installable runtime presence; bounded-profile exclusions; formal projection; absence of implicit effect adapters; residual limitations; and complete production-gate registration.

## Runtime black-box boundary

The runtime auditor extracts the built snapshot and uses only `python -m aset_seed`. It verifies durable initialization, fail-closed invalid proof handling, accepted signed transition commit, replay idempotency, process-reopen validation, database and audit health, consistent backup, and audit-tampering detection.

## Adversarial step

The mutation harness rebuilds a valid manifest after each malicious change. It must still reject removal or drift of required documents, generated editions, frozen rc11 bytes, Git byte policy, migration coverage, runtime files, protocol schemas, formal model, limitation records and release gates; it also rejects a secret marker, readiness overclaim, open blocking finding, and implicit network/effect import.

Any failed mandatory check forms a finding for the next PDCA cycle. A cycle may close only with zero failed black-box checks and zero open blocking findings.
