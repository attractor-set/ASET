
# Documentation repository operations runbook

## CI failure

1. identify the first failed mandatory gate;
2. reproduce locally with `python tools/production_gate.py`;
3. do not weaken the gate or edit generated evidence;
4. correct the canonical source, tool, policy, or package input;
5. rebuild the manifest and snapshot;
6. rerun the black-box audit;
7. record the finding and closure when the defect affected a published candidate.

## Frozen release mismatch

Treat any rc11 digest mismatch as a release-integrity incident. Do not regenerate or repair files in place. Restore the exact frozen bytes from an independently verified copy and compare the release envelope.

## Generated edition mismatch

Change the canonical model or generator, regenerate all three editions, and rerun parity and terminology checks. Manual editing of generated documents is prohibited.

## Suspected secret exposure

Stop publication, rotate the credential outside the repository, remove it from all reachable Git history using an approved incident procedure, and document the event without reproducing the secret.

## Failed black-box audit

The snapshot is not releasable. The internal validation result cannot override the black-box result. Open or update a finding, correct the source, and repeat the PDCA cycle.
