# Active ASET audit index

This index separates the current implementation-neutral Seed candidate from historical evidence.

## Current controlling line

The current candidate is Seed `0.3.0-alpha.1`. Its machine identity is [`seed/canonical/CANON_PACKAGE.json`](../seed/canonical/CANON_PACKAGE.json), and its repository claim boundary is [`REPOSITORY_STATUS.json`](../REPOSITORY_STATUS.json).

Static controlling records are listed in [`ACTIVE_AUDIT_INDEX.json`](ACTIVE_AUDIT_INDEX.json). Candidate-specific executable evidence is generated under `dist/` by [`tools/repository_release_gate.py`](../tools/repository_release_gate.py). The active assurance line additionally requires complete invariant coverage and zero surviving semantic mutations as defined by [`PDCA-17-INVARIANT-CLOSURE.md`](PDCA-17-INVARIANT-CLOSURE.md).

## Historical records

The rc12 and Seed 0.2 records are preserved historical development evidence. They do not control the 0.3 minimal resolution-recognition semantics and grant no implementation precedence.

## Interpretation rule

When historical evidence conflicts with the active canon package, repository status or current controlling records, the active exact package and a passing release gate control the claim.
