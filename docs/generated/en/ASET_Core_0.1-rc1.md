# ASET Core 0.1-rc1

Defines normative resolution, one-shot Permit, and atomic gate crossing.

- `component_id`: `aset.core`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:10a14bd8f18a51c48b56d0b8cbfc90fa862239eae5d47dbc68b8b39e890c289b`

## Source boundary

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Ownership

- `AuthorityGraph`
- `CoreResolution`
- `GateCrossingReceipt`
- `GateKernel`
- `NormativeLedger`
- `OneShotPermit`
- `PolicySet`

## Forbidden responsibilities

- accept result
- execute external effect
- plan
- rewrite submission

## Operations and Seed mapping

### `CORE-RESOLVE` — ResolveSubmission

Create a CoreResolution without rewriting the submitted document.

- `classification`: `NORMATIVE_DECISION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision`
- `outcome_recognition_required`: `False`

### `CORE-ISSUE-PERMIT` — IssuePermit

Issue one exact one-shot Permit only after a PERMITTED resolution.

- `classification`: `AUTHORIZATION_ISSUANCE`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit`
- `outcome_recognition_required`: `False`

### `CORE-CROSS` — LinearizeCrossing

Atomically apply the patch, compare-and-swap scoped heads, consume the Permit, and emit a receipt.

- `classification`: `GOVERNED_CONTEXT_MUTATION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt`
- `outcome_recognition_required`: `False`

## Requirements

Count: `26`

`COR-001`, `COR-002`, `COR-003`, `COR-004`, `COR-005`, `COR-006`, `COR-007`, `COR-008`, `COR-009`, `COR-010`, `COR-011`, `COR-012`, `COR-013`, `COR-014`, `GAT-001`, `GAT-002`, `GAT-003`, `GAT-004`, `GAT-005`, `GAT-006`, `GAT-007`, `GAT-008`, `GAT-009`, `GAT-010`, `GAT-011`, `GAT-012`

## Invariants

- `INV-AUTH-001` — Только ASET Core создаёт authority-bearing Permit.
- `INV-AUTH-002` — Всё, что не имеет действующего Permit для точного гейта, запрещено.
- `INV-AUTH-003` — CoreResolution имеет только PERMITTED или PROHIBITED; техническая ошибка не является разрешением.
- `INV-CORE-RES-001` — PERMITTED requires exactly one permit reference and digest; PROHIBITED forbids both and requires reason codes.
- `INV-PERMIT-001` — Permit относится ровно к одному document digest, dependency context set, gate instance, crossing ID и actor/execution ID.
- `INV-PERMIT-002` — Permit допускает ровно одно немедленное пересечение и после него безвозвратно CONSUMED.
- `INV-PERMIT-003` — Permit одного гейта неприменим к другому гейту.
- `INV-PERMIT-004` — ExpectationPermit не разрешает внешний эффект; ExecutionPermit является отдельным артефактом.
- `INV-PERMIT-005` — Every Permit has consume_before strictly later than issued_at and within the policy maximum lifetime of 60 seconds.
- `CORE-BND-001` — Core may resolve and issue Permit but may not plan, execute an external effect, or accept a result.

## Assurance boundaries

- `CORE-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `CORE-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Machine-readable canon assets

- `conformance_binding`: `aset/components/core/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/core/canonical/formal/core.tla`
- `invariants`: `aset/components/core/canonical/assurance/invariants.json`
- `limitations`: `aset/components/core/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/core/canonical/protocol/profile.json`
- `requirements`: `aset/components/core/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/core/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/core/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/core/canonical/assurance/verification-cases.json`
