# PDCA history — ASET Seed 0.1-rc12 production candidate

The project uses evidence-driven Deming cycles. Each cycle ends with a full black-box view of the built project; its findings become the next cycle input.

| Cycle | Objective | Verified result | Next input |
|---|---|---|---|
| 01–04 | Public documentation repository, frozen rc11 visibility, and committed-byte correction | repository assurance v1.1; rc11 174/174 byte identity | complete rc12 semantics |
| [05](pdca/PDCA-05-RC12-CANON.md) | complete machine canon | 27 concepts, 40 requirements, 37 invariants, 18 transitions, migration 83/83 | bounded executable profile |
| [06](pdca/PDCA-06-BOUNDED-RUNTIME.md) | durable single-host runtime | atomic SQLite state/audit, explicit proof boundary, local CLI/API | hardening and simplification |
| [07](pdca/PDCA-07-REGRESSION-REFACTOR.md) | semantic regression and surgical refactor | 55/55, 252/252, 30 tests, 90.570720% core branches | deterministic candidate packaging |
| [08](pdca/PDCA-08-RELEASE-CANDIDATE.md) | release candidate and fail-closed production gates | exact envelope, wheel, snapshot, documentation/runtime/adversarial audits | protected PR and external audit |
| [09](pdca/PDCA-09-LINT-GATE-CORRECTION.md) | close the target Ruff gate without semantic expansion | nine lint findings corrected; full production and final black-box gates required | protected PR and external audit |
| [10](pdca/PDCA-10-ENVELOPE-REBUILD-ORDERING.md) | restore release metadata after runtime-byte correction | release envelope rebuilt before manifest; complete production and black-box gates required | protected PR and external audit |

Current classification: `RC12_RELEASE_CANDIDATE_READY` for `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`. External third-party audit remains `PENDING`.
