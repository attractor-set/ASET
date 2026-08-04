# Repository finding closure matrix

| ID | Severity | Finding | Status | Closure |
|---|---|---|---|---|
| REPO-AUD-001 | P0 | Stable rc11 not fully browseable | CLOSED | Byte-exact expanded tree and identity verifier added. |
| REPO-AUD-002 | P0 | No independent snapshot documentation audit | CLOSED | Snapshot-only black-box audit is mandatory in CI and the production gate. |
| REPO-AUD-003 | P0 | Repository and runtime readiness claims conflated | CLOSED | The bounded runtime profile and all excluded claims are explicit. |
| REPO-AUD-004 | P1 | No rc11-to-rc12 disposition register | CLOSED | All 83 requirement, transition, and schema assets are explicitly migrated. |
| REPO-AUD-005 | P1 | No machine-readable operational release gates | CLOSED | Nineteen fail-closed mandatory gates and one orchestrator are defined. |
| REPO-AUD-006 | P1 | Missing operations runbook | CLOSED | Release, audit, incident, deployment, and threat-model procedures are present. |
| REPO-AUD-007 | P0 | Git normalization changed frozen rc11 bytes | CLOSED | Frozen trees are `-text`; committed-byte and fresh-checkout checks are mandatory. |
| RC12-AUD-001 | P0 | rc12 canon represented only a bootstrap subset | CLOSED | Canon expanded to 27 concepts, 40 requirements, 37 invariants, 18 transitions, 39 schemas, and 55 bindings. |
| RC12-AUD-002 | P0 | rc11 semantic assets were deferred | CLOSED | Migration is 83/83, with zero deferred and zero unclassified entries. |
| RC12-AUD-003 | P0 | No durable executable runtime | CLOSED | Bounded SQLite runtime provides serialized durable state-and-audit commits. |
| RC12-AUD-004 | P0 | No runtime black-box assurance | CLOSED | Independent snapshot-only CLI/runtime black-box audit added. |
| RC12-AUD-005 | P1 | Formal directory was a wiring scaffold | CLOSED | TLA+ safety projection and executable bounded checker added. |
| RC12-AUD-006 | P1 | Semantic-core rewrite risk | CLOSED | Audited rc11 core and exact schemas were reused and regression-bound. |
| RC12-AUD-007 | P1 | Nested idempotent initialization read | CLOSED | Refactored to one serialized transaction and one canonical state read. |
| RC12-AUD-008 | P0 | Weak secret-file and backup guards | CLOSED | Private file modes, integrity verification, and no-overwrite backup policy added. |
| RC12-AUD-009 | P1 | Build artifacts could contaminate release scope | CLOSED | Deterministic file exclusions centralized and regression-tested. |
| RC12-AUD-010 | P0 | Audit columns and current state were not cross-bound | CLOSED | Audit verification now checks redundant columns, revision count, and final state root. |
| RC12-AUD-011 | P0 | CI pins referenced unpublished tool versions | CLOSED | Dependency pins now reference published versions and the build backend uses one pinned setuptools requirement. |
| RC12-AUD-012 | P1 | Engineering behavior rules were not persistent | CLOSED | Repository-wide agent instructions now enforce assumptions, simplicity, surgical diffs, verification, PDCA, and black-box closure. |

Open blocking findings: **0**.

Residual assurance boundaries are tracked in `seed/canonical/assurance/limitations.json`. They limit the claim to the single-host SQLite profile and do not invalidate that bounded profile.
