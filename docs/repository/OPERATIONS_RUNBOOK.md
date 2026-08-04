# ASET Seed repository and bounded-runtime runbook

## CI failure

Reproduce the first failed command from `dist/production-gate.json`. Correct the source defect; do not edit evidence or relax the gate. Regenerate views and manifest, then repeat the entire gate so the final step is a fresh black-box audit.

## Frozen rc11 mismatch

Treat any digest mismatch as a release-integrity incident. Do not regenerate or repair frozen files in place. Restore exact bytes from an independently verified release asset and confirm both archive and Git-stored expanded identities.

## Canon or generated-view mismatch

Change only the machine source, generator, or explicit binding responsible for the defect. Regenerate all RU, EN, and pt-BR editions plus ontology, SKOS, TBX and SHACL views. Never patch a generated edition manually.

## Runtime health failure

Stop new writes when database integrity or audit-chain integrity is not `PASS`. Preserve the database and WAL files, collect version and filesystem evidence, and restore only from a validated backup. Never repair accepted history by direct SQL.

## Proof or key uncertainty

The default response is fail closed. Rotate or replace deployment secrets outside the repository, update the explicit proof profile, and re-run an isolated acceptance transition. Uncertain key provenance does not authorize bypassing proof verification.

## Failed black-box audit

The candidate is not releasable. Open a blocking finding, identify the smallest causal change, apply it, run regression, and use the new black-box report to plan the next PDCA cycle.
