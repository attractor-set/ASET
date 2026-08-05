# ASET audit evidence

The audit tree contains two explicitly separated classes of records:

- **active controlling records** for the current implementation-neutral specification and component-conformance line;
- **historical non-controlling records**, including the superseded embedded-runtime pre-freeze line.

The exact classification is normative for repository interpretation and is recorded in:

- [`ACTIVE_AUDIT_INDEX.json`](ACTIVE_AUDIT_INDEX.json);
- [`ACTIVE_AUDIT_INDEX.md`](ACTIVE_AUDIT_INDEX.md).

Historical files are preserved as evidence and are not rewritten. They must not be cited as current runtime, implementation or production-readiness claims.

Executable evidence is produced under `dist/` by the repository release gate and is uploaded by CI. The independent documentation auditor imports no repository validation module and reads the curated active documentation boundary. Component black-box and adversarial checks consume the deterministic snapshot.

```bash
python tools/repository_release_gate.py
```

A release candidate is blocked unless every mandatory stage returns `PASS`. Generated evidence controls only the exact snapshot bytes from which it was produced.
