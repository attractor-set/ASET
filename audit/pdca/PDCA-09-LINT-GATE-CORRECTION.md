# PDCA-09 — rc12 lint-gate correction

## Plan / black-box input

The target application reached the mandatory Ruff gate and failed before commit. The external observation contained nine findings: four import-order findings, two quoted-annotation findings, two unused imports, and one unused loop variable. The repository stayed on the exact base commit with the complete candidate payload uncommitted.

Success criteria:

1. change only the reported Python files and the audit records created by this correction;
2. keep frozen rc11 byte-identical and outside the staged diff;
3. pass Ruff with the pinned CI version;
4. rebuild the repository manifest after source changes;
5. pass the entire production gate, whose final stages are documentation, runtime, and adversarial black-box audits;
6. commit only after every mandatory gate passes.

## Do

- Applied Ruff safe fixes only to the seven files named by the failed gate.
- Renamed the unused model-check loop variable from `action` to `_action`.
- Rebuilt `MANIFEST.json` after the source correction.
- Added this corrective cycle and `RC12-AUD-013` to the audit trail.

No semantic rule, protocol schema, frozen rc11 artifact, runtime state transition, database format, or production-profile boundary was changed.

## Check

The corrective script requires:

- exact branch and base commit;
- exact pre-fix payload bytes from package v1;
- pinned Ruff `0.15.22`;
- frozen rc11 mutation check before and after the gate;
- full `tools/production_gate.py` success;
- staged-diff validation and a clean post-commit worktree.

## Act / final black-box audit

The production gate ends with independent snapshot-based documentation, runtime, and controlled-adversarial black-box audits. Their PASS result is the final step of this cycle and the input to any later cycle. A failing black-box result blocks commit and publication.

Residual boundary: this correction closes packaging/lint assurance only. It does not broaden `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1` or alter the pending external third-party audit.
