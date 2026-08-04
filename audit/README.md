
# Repository audit evidence

This directory contains repository-level PDCA history, finding closure, and the latest independently generated black-box documentation audit report.

The black-box report is reproducible from the deterministic snapshot with:

```bash
python tools/blackbox_documentation_audit.py \
  dist/ASET-Repository-Snapshot.zip \
  --output-json dist/blackbox-documentation-audit.json \
  --output-md dist/blackbox-documentation-audit.md
```
