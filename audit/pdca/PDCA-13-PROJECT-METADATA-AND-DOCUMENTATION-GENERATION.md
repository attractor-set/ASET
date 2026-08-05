# PDCA-13 — project metadata and documentation generation

## Plan

Create one machine-readable repository-discovery source without moving normative semantics out of the existing ASET canons. Generate CodeMeta and the exact GitHub About projection from that source, provide one command for all derived repository views, keep explanatory multilingual README introductions static, and block metadata drift through CI, repository validation, tests and black-box audit.

Acceptance criteria:

- `metadata/project.json` validates against a strict schema;
- the canonical description explicitly binds ASET to Authority-Signed Evidence Trails and heterogeneous sociotechnical systems;
- `codemeta.json`, `.github/repository-metadata.json` and `docs/generated/README.md` are deterministic outputs;
- no more than 20 unique GitHub topics are produced and every topic satisfies GitHub syntax;
- all pre-existing language, component and semantic generators retain parity;
- static README introductions are aligned in English, Russian and Brazilian Portuguese;
- repository tests and snapshot-only documentation audit pass.

## Do

- Added `metadata/project.json` and `metadata/project.schema.json`.
- Added `tools/generate_project_metadata.py` with generate, parity-check and explicit administrator-only GitHub synchronization modes.
- Added `tools/generate_repository_views.py` as the single generation entry point for project metadata, Seed editions, component views and semantic views.
- Generated CodeMeta 3.1 and an exact machine-readable GitHub About projection.
- Integrated generated-view parity into CI, `production_gate.py` and repository validation.
- Updated static multilingual README introductions, canonicality policy, contribution instructions, release process and operations runbook.
- Removed duplicate Python-reference sections and restored the missing pt-BR reference section.
- Added focused regression tests and a snapshot-only metadata parity check.

## Check

- Generated repository-view parity: `PASS` for project metadata, Seed editions, component views and semantic views.
- Language policy: `PASS`.
- Python compilation: `PASS`.
- Regression suite: `87 passed`.
- Deterministic manifest: `698` files, exact parity `PASS`.
- Documentation black-box audit: `33/33 PASS`.
- Component black-box audit: `27/27 PASS`.
- Reference black-box audit: `10/10 PASS`.
- Runtime black-box audit: `18/18 PASS`.
- Reference adversarial suite: `10/10 PASS`.
- Component adversarial suite: `13/13 PASS`.
- Runtime and repository adversarial suites: `PASS`.

The first component black-box run reported `CB-012` because the auditor required a direct component-generator string inside `validate_repository.py`. The new design intentionally routes generation through `generate_repository_views.py`. The auditor was corrected to verify both links — validator to orchestrator and orchestrator to component generator — and the rebuilt snapshot passed `27/27` without weakening the integration requirement.

Exact pinned Ruff 0.15.22 and PySHACL 0.40.0 were unavailable in the local execution environment, so the full `production_gate.py` was not claimed locally. Protected-branch CI remains mandatory and authoritative for those two pinned checks and the complete production gate.

## Act

Keep repository administration as an explicit external effect. Ordinary CI verifies the desired GitHub About state but does not mutate repository settings. After merge, an authorized administrator may apply the exact description and topic set with `python tools/generate_project_metadata.py --apply-github`.

Retain the unified generator as a thin orchestrator. Existing specialized generators remain independently testable, and future derived views should be added only when their source and deterministic projection are explicit.
