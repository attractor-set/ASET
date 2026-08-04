# Finding closure matrix — ASET Seed 0.1-rc11

- Closed findings: **28**
- Open blocking findings: **0**

- **RC7-A1 / CRITICAL / CLOSED:** Schemas not enforced by public API — Strict schema validation in initialize/apply/validate.
- **RC7-A2 / CRITICAL / CLOSED:** Malformed State accepted after root recomputation — State schema precedes semantic validation.
- **RC7-A4 / CRITICAL / CLOSED:** Reconciliation could omit known fork — Known commits complete; fork evidence persistent.
- **RC7-A5 / CRITICAL / CLOSED:** Ordinary actions in suspended Context — Universal pre-dispatch partition gate.
- **RC7-A6 / CRITICAL / CLOSED:** Candidate-attested causal DAG — Causal parents derived from artifact ownership.
- **RC7-A7 / HIGH / CLOSED:** Outcome selected convenient Verification subset — Complete effective PASS set required.
- **RC7-A8 / HIGH / CLOSED:** Correction ambiguity — Verification-only, one effective correction before Outcome.
- **RC7-A9 / CRITICAL / CLOSED:** Authority transfer without new-holder acceptance — Responsibility readiness and exact-context trail.
- **RC7-A11 / HIGH / CLOSED:** Recursive plebiscite state explosion — Plebiscite removed.
- **RC8-IA-001 / HIGH / CLOSED:** Unrecognized verification policy — Policy resolves through active Constitution.
- **RC8-IA-002 / CRITICAL / CLOSED:** Corrected Outcome remained usable — Outcome immutable; corrections Verification-only.
- **RC8-IA-003 / HIGH / CLOSED:** Historical Context re-entered governance — Active-only alias/governance/dependency sets.
- **RC8-IA-004 / HIGH / CLOSED:** Cross-context Authority transfer laundering — Exact Context across full transfer lineage.
- **RC9-CTRL-001 / CRITICAL / CLOSED:** Targeted Amendment mutated global Constitution — Root Constitution immutable; new Genesis required.
- **RC9-CTRL-002 / HIGH / CLOSED:** Permit success predicate inert — Recognized predicate and exact Verification match.
- **RC9-CTRL-003 / HIGH / CLOSED:** Stale coverage accepted — Coverage bound to exact runtime/test/schema/case hashes.
- **RC9-CTRL-004 / HIGH / CLOSED:** Publication QA not byte-bound — QA records exact DOCX/PDF hashes.
- **RC9-CTRL-005 / MEDIUM / CLOSED:** VOLUNTARY_CLOSE consent undefined — Removed; final member-signed withdrawal only.
- **RC10-CTRL-001 / CRITICAL / CLOSED:** Executable rc10 package absent — rc11 rebuilt from complete rc9 baseline with runtime, schemas, corpus and harness.
- **RC10-CTRL-002 / HIGH / CLOSED:** Destructive pending withdrawal deadlock — No pending governance state; inline authorizations in atomic redefinition.
- **RC10-CTRL-003 / HIGH / CLOSED:** Exit and redefinition consent conflated — Standalone withdrawal separated from redefinition authorization.
- **RC10-CTRL-004 / HIGH / CLOSED:** Opaque proposal digest — Full canonical proposal embedded and retained.
- **RC10-CTRL-005 / HIGH / CLOSED:** Order-dependent affected closure — Closure computed once from pre-state.
- **RC10-CTRL-006 / HIGH / CLOSED:** Redefinition authority undefined — Parent REDEFINE_CONTEXT Authority required.
- **RC10-CTRL-007 / MEDIUM / CLOSED:** Replacement definition underdefined — Strict schema binds nonce, initial authorities and dependencies; identity fields preserved.
- **RC11-BB-001 / HIGH / CLOSED:** Voluntary exit could break active normative dependant — WITHDRAWAL_REDEFINITION_REQUIRED.
- **RC11-BB-002 / HIGH / CLOSED:** Successor dependency could target withdrawn descendant — REDEFINITION_DEPENDENCY_TARGET_WITHDRAWN.
- **RC11-BB-003 / HIGH / CLOSED:** Governance record did not retain full authorization evidence — Full proposal and proof digests retained and revalidated.

## Residual limitations

- **LIM-001 (HIGH):** `proof_digest` is an abstract authenticated-verifier input; production cryptography is not implemented.
- **LIM-002 (HIGH):** crash durability, transactional storage, multi-process serialization and concurrency refinement are not established.
- **LIM-003 (MEDIUM):** distributed consensus is outside the minimal profile.
- **LIM-004 (MEDIUM):** root semantic change requires a new Genesis and migration procedure.
- **LIM-005 (MEDIUM):** universal breach propagation model checking remains future work.
- **LIM-006 (INFO):** external third-party certification is pending.
