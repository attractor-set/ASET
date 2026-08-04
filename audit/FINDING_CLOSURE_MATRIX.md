# Repository finding closure matrix

| ID | Severity | Finding | Status | Closure |
|---|---|---|---|---|
| REPO-AUD-001 | P0 | Stable rc11 not fully browseable | CLOSED | Added byte-exact expanded rc11 tree and independent identity check. |
| REPO-AUD-002 | P0 | No snapshot black-box documentation audit | CLOSED | Added independent black-box auditor and mandatory CI gate. |
| REPO-AUD-003 | P0 | Repository and runtime production claims not separated | CLOSED | Added explicit claim boundary and status schema. |
| REPO-AUD-004 | P1 | No explicit rc11-to-rc12 disposition register | CLOSED | Added complete requirement, transition-kind and schema disposition register. |
| REPO-AUD-005 | P1 | No operational release gate registry | CLOSED | Added machine-readable mandatory release gates and production gate orchestrator. |
| REPO-AUD-006 | P1 | No repository operations runbook | CLOSED | Added release, black-box audit and incident runbooks. |
| REPO-AUD-007 | P0 | Git line-ending normalization changed frozen rc11 CSV bytes | CLOSED | Marked the frozen release tree -text, added Git-filter byte preflight, fresh-checkout regression coverage and an adversarial audit. |
| RC12-AUD-001 | P0 | rc12 canon represented only a bootstrap subset | CLOSED | Expanded the normative canon to 27 concepts, 40 requirements, 37 invariants, 18 transition kinds, 39 schemas, and 55 exact conformance bindings. |
| RC12-AUD-002 | P0 | rc11 semantic assets were deferred rather than migrated | CLOSED | Changed the migration register to 83/83 migrated, zero deferred, and zero unclassified assets. |
| RC12-AUD-003 | P0 | no durable executable runtime | CLOSED | Added the bounded SQLite runtime with serialized writers, atomic state-and-audit transactions, strict JSON, fail-closed proof verification, integrity checks, and backup. |
| RC12-AUD-004 | P0 | no runtime black-box assurance | CLOSED | Added snapshot-only CLI black-box audit covering initialization, proof rejection, accepted transition, persistence, audit chain, health, and backup. |
| RC12-AUD-005 | P1 | formal directory was a wiring scaffold | CLOSED | Added a TLA+ safety projection and an executable bounded model checker retained in CI evidence. |
| RC12-AUD-006 | P1 | semantic core rewrite could invalidate audited behavior | CLOSED | Preserved the audited rc11 core and schemas byte-for-byte except for package path/version metadata, then ran all 55 vectors and 252 branch guards against the packaged core. |
| RC12-AUD-007 | P1 | runtime initialization used a nested read connection on the idempotent path | CLOSED | Refactored initialization to return the stored canonical state from the same BEGIN IMMEDIATE transaction, reducing connection coupling and preserving one serialization boundary. |
| RC12-AUD-008 | P0 | deployment secret files and backup destinations lacked fail-closed local guards | CLOSED | Require POSIX-private HMAC secret files, create databases and backups with mode 0600, validate backup integrity, and refuse backup overwrite. |
| RC12-AUD-009 | P1 | local build and coverage artifacts could enter deterministic repository scope | CLOSED | Centralized repository-file exclusions for dist, build, coverage, caches, virtual environments, Git metadata, and egg-info before manifest and snapshot construction. |
| RC12-AUD-010 | P0 | audit hash chain did not cross-check redundant columns and current state revision | CLOSED | Verify accepted, state_changed, and code against hashed result_json, bind changed-attempt count to the current revision, and bind the final audit root to the persisted state root. |
| RC12-AUD-011 | P0 | CI dependency pins referenced unpublished Ruff and PySHACL versions | CLOSED | Replaced speculative pins with published versions, updated the remaining CI pins, and simplified the build backend to one pinned setuptools dependency. |
| RC12-AUD-012 | P1 | engineering behavior rules were not persisted in the repository | CLOSED | Added repository-wide AGENTS.md with assumption disclosure, simplicity, surgical-change, goal-driven, PDCA, refactoring, frozen-release, and bounded-production rules; made it mandatory in validation and black-box audit. |
| RC12-AUD-013 | P0 | rc12 candidate package failed the mandatory Ruff gate before commit | CLOSED | Applied pinned-Ruff safe fixes to the seven reported files, renamed the unused model-check loop variable, rebuilt the repository manifest, and required the full production gate ending in all black-box audits. |
| RC12-AUD-014 | P0 | lint correction changed envelope-bound runtime bytes after release metadata was generated | CLOSED | Regenerated the rc12 release envelope after all runtime source corrections, rebuilt the repository manifest only after the envelope and audit records, and required the complete production gate ending in documentation, runtime, and adversarial black-box audits. |
| RC12-PF-001 | P0 | Pinned proof could authorize modified transition | CLOSED | Removed the unsafe pinned-digest verifier from the production API and canon; bundled admission now uses reject-all or exact-content HMAC, with black-box proof-profile enforcement. |
| RC12-PF-002 | P0 | Health passed schema-invalid or root-inconsistent state | CLOSED | Added semantic validation of every stored state, trust-space identity, current root, and stored root; CLI health now requires state_validation PASS. |
| RC12-PF-003 | P1 | Oversized transition attempts were not audited | CLOSED | Audit oversized JSON transition documents by exact SHA-256 digest and byte size inside the trust-space transaction; clarified non-JSON and unknown-space boundaries. |
| RC12-PF-004 | P1 | Embedded API leaked TypeError for non-JSON values | CLOSED | Added a stable INPUT_NOT_JSON_VALUE boundary rejection before transition admission and regression coverage. |
| RC12-PF-005 | P1 | Proof-verifier exceptions escaped the runtime boundary | CLOSED | Isolated verifier exceptions as stable PROOF_VERIFIER_ERROR results, preserved state, and recorded them in the audit chain. |
| RC12-PF-006 | P2 | Backup accepted logically invalid persisted state | CLOSED | Refuse backup unless database, semantic-state, and audit-chain health checks all pass. |
| RC12-PF-007 | P2 | Database symlink path was accepted | CLOSED | Reject symbolic-link database paths and require a private regular file using lstat and O_NOFOLLOW where available. |
| RC12-PF-008 | P2 | Runtime dependency set was not exact | CLOSED | Pinned the wheel runtime dependency to jsonschema==4.26.0 and bound the same version in CI and deployment documentation. |
| RC12-PF-009 | P1 | Invalid trust-space identifier escaped into SQLite binding | CLOSED | Validate the identifier type and exact ts:<64 lowercase hex> profile before database access; return stable TRUST_SPACE_ID_INVALID and cover it in unit, black-box, and mutation tests. |
| RC12-PF-010 | P0 | Corrupted stored state remained reachable through read, initialize, or execution paths | CLOSED | Centralized strict stored-state decoding and validation, bound state identity/root to redundant columns, and require the same guard for get_state, idempotent initialize, apply, health, and backup. |
| RC12-PF-011 | P0 | Repository validator retained the obsolete 19-gate count after hostile gates were added | CLOSED | Updated strict repository validation, tests, and snapshot black-box expectations to the complete 23-gate pre-freeze registry. |
| RC12-PF-012 | P1 | Exact-content HMAC binding lacked direct hostile regression and mutation coverage | CLOSED | Added modified-after-proof unit and public CLI black-box cases plus a controlled verifier mutation that must be detected. |

Open blocking findings: **0**.

Residual assurance boundaries are tracked in `seed/canonical/assurance/limitations.json`. They limit the claim to the single-host SQLite profile and do not invalidate that bounded profile.
