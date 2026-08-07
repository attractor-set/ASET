# ASET audit evidence

The audit tree contains:

- active controlling records for the current implementation-neutral Seed candidate;
- historical non-controlling records from predecessor Seed and embedded-runtime work.

The exact classification is recorded in:

- [`ACTIVE_AUDIT_INDEX.json`](ACTIVE_AUDIT_INDEX.json);
- [`ACTIVE_AUDIT_INDEX.md`](ACTIVE_AUDIT_INDEX.md).

Legacy component audits were externalized with the component corpus. The extraction closure and
release-asset digest remain recorded in [`PDCA-15-EXTENSION-EXTRACTION-CLOSURE.json`](PDCA-15-EXTENSION-EXTRACTION-CLOSURE.json).
Removal from the active tree does not rewrite their historical content or make them current Seed evidence.

Executable evidence is produced under `dist/` by:

```bash
python tools/repository_release_gate.py
```

Generated evidence controls only the exact snapshot bytes from which it was produced.
