# Production readiness of ASET Seed 0.1-rc12 candidate

## Claim

This repository is production-ready for specification publication and for the bounded executable profile `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`.

| Scope | Status |
|---|---|
| Repository publication and deterministic release assurance | `PRODUCTION_READY` |
| Frozen rc11 preservation and regression | `PASS_WITH_LIMITATIONS` |
| Complete rc12 machine canon | `RC12_RELEASE_CANDIDATE_READY` |
| Single-node SQLite runtime | `PRODUCTION_READY_BOUNDED_PROFILE` |
| Distributed consensus and multi-primary operation | `OUT_OF_SCOPE` |
| Physical-world truth and automatic external effects | `OUT_OF_SCOPE` |
| Deployment key management and infrastructure | `DEPLOYMENT_RESPONSIBILITY` |
| External third-party audit or certification | `PENDING` |

The runtime claim requires one operating-system host, a local durable filesystem, SQLite WAL, `synchronous=FULL`, serialized write transactions, explicit proof verification, controlled backup and restore, and operational acceptance of the deployment checklist.

## Mandatory release gates

The fail-closed registry contains 19 mandatory gates covering machine-canon completeness, generated views, rc11 integrity, exact 83/83 migration, semantic regression, branch coverage, bounded model checking, tests, static checks, wheel installation, deterministic snapshot construction, documentation and runtime black-box audits, adversarial rejection, and zero blocking findings.

A missing, skipped, indeterminate, or failed gate blocks promotion. Internal reports cannot override a failed snapshot-only audit.

## Residual assurance boundary

The bounded model check is not an unbounded proof. HMAC verification is a concrete local profile, not a public-key federation PKI. Deployment operators remain responsible for secrets, filesystem durability, monitoring, restore rehearsal, and process isolation. External audit remains pending and must not be inferred from internal independent harnesses.
