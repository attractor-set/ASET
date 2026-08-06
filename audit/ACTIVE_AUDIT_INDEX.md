# Active ASET audit index

This index separates the current implementation-neutral Seed candidate from historical evidence.

## Current controlling line

The current candidate is Seed `0.2.0-alpha.2`. Its machine identity is
[`seed/canonical/CANON_PACKAGE.json`](../seed/canonical/CANON_PACKAGE.json), and its repository
claim boundary is [`REPOSITORY_STATUS.json`](../REPOSITORY_STATUS.json).

Static controlling records are listed in [`ACTIVE_AUDIT_INDEX.json`](ACTIVE_AUDIT_INDEX.json).
Candidate-specific executable evidence is generated under `dist/` by
[`tools/repository_release_gate.py`](../tools/repository_release_gate.py).

## Historical records

The root rc12 pre-freeze audit, finding matrix and `audit/pdca/` records are preserved historical
development evidence. Component-specific audit records were externalized with the exact legacy
corpus identified in [`../EXTRACTION.json`](../EXTRACTION.json).

Historical records do not describe the current repository role, do not grant semantic precedence
to any implementation and must not be used as current production-readiness evidence.

## Interpretation rule

When historical evidence conflicts with the active canon package, repository status or current
controlling records, the active exact package and a passing release gate control the claim.
