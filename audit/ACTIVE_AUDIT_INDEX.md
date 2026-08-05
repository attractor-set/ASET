# Active ASET audit index

This index separates the current implementation-neutral ASET candidate from preserved historical evidence.

## Current controlling line

The current candidate is the implementation-neutral Seed `0.1-rc12` specification and conformance package. Its machine identity is [`seed/canonical/CANON_PACKAGE.json`](../seed/canonical/CANON_PACKAGE.json), and its repository claim boundary is [`REPOSITORY_STATUS.json`](../REPOSITORY_STATUS.json).

Static controlling records are listed in [`ACTIVE_AUDIT_INDEX.json`](ACTIVE_AUDIT_INDEX.json). Candidate-specific executable evidence is generated under `dist/` by [`tools/repository_release_gate.py`](../tools/repository_release_gate.py). A generated report controls only the exact snapshot from which it was produced.

## Historical records

The root rc12 pre-freeze audit, finding matrix and `audit/pdca/` records are preserved historical development evidence. Some describe the superseded embedded-runtime candidate. They do not describe the current repository role, do not grant semantic precedence to Python or SQLite, and must not be used as current production-readiness evidence.

Historical bytes are retained rather than rewritten. Their status is supplied by this index and by the runtime-candidate supersession record.

## Interpretation rule

When a historical record conflicts with the current canon package, repository status or active controlling records, the historical record is non-controlling. Current claims require a passing repository release gate on the exact candidate bytes.
