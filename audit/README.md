# ASET audit evidence

This directory contains the finding closure matrix, refactoring log, PDCA history, and final rc12 black-box audit declarations. Executable evidence is produced under `dist/` by the production gate and is uploaded by CI.

The independent documentation auditor imports no repository validation module and reads only the deterministic snapshot:

```bash
python tools/blackbox_documentation_audit.py \
  dist/ASET-Repository-Snapshot.zip \
  --output-json dist/blackbox-documentation-audit.json \
  --output-md dist/blackbox-documentation-audit.md
```

The runtime auditor installs and invokes the packaged project from the snapshot, and the adversarial runner mutates independent copies of that snapshot. A release candidate is blocked unless all three verdicts are `PASS`.
