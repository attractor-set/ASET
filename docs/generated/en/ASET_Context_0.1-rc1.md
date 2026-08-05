# ASET Context 0.1-rc1

Defines context as a versioned namespace, its immutable components, projections, composition, and atomic patch transitions.

- `component_id`: `aset.context`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:450cac15f64c2b3ed3f7c6399c1a456da0c84faf2dcdb911075bd03219e1cd36`

## Source boundary

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Ownership

- `CompositeContextManifest`
- `ContextNamespace`
- `ContextPatchSet`
- `SignedContextComponent`

## Forbidden responsibilities

- issue Permit
- mutate an existing context in place
- promote epistemic status

## Operations and Seed mapping

### `CTX-COMPOSE` — ComposeContext

Compute a deterministic composite root from immutable signed components.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

### `CTX-APPLY-PATCH` — ApplyAuthorizedPatch

Create a new context version from an authorized atomic patch set.

- `classification`: `GOVERNED_CONTEXT_MUTATION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt`
- `outcome_recognition_required`: `False`

## Requirements

Count: `15`

`CTX-001`, `CTX-002`, `CTX-003`, `CTX-004`, `CTX-005`, `CTX-006`, `CTX-007`, `CTX-008`, `CTX-009`, `CTX-010`, `CTX-011`, `CTX-012`, `CTX-013`, `CTX-014`, `CTX-015`

## Invariants

- `INV-CTX-001` — Существующие Context и SignedContextComponent неизменяемы.
- `INV-CTX-002` — Любое каноническое изменение создаёт новый Context через atomic gate patch set.
- `INV-CTX-003` — Gate является linearization point: patch set, new components/root, scoped HEAD updates, Permit consumption и receipt фиксируются атомарно.
- `INV-CTX-004` — Composite root однозначно зависит от канонически упорядоченных подписанных компонентов.
- `INV-CTX-005` — Изменение dependency component инвалидирует Permit; изменение независимого компонента не обязано его инвалидировать.
- `INV-CTX-006` — Один crossing_id создаёт не более одного target context и receipt; повтор возвращает тот же результат.
- `INV-EPI-001` — EXPECTED не является OBSERVED; OBSERVED не является VERIFIED; verified transition не равен Task goal completion.
- `INV-EPI-002` — Worker self-report не является достаточным evidence по умолчанию.
- `CTX-BND-001` — Context composition and patch application never issue authority.
- `CTX-BND-002` — Retrieved or expected content does not become VERIFIED by context inclusion.

## Assurance boundaries

- `CONTEXT-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `CONTEXT-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Machine-readable canon assets

- `conformance_binding`: `aset/components/context/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/context/canonical/formal/context.tla`
- `invariants`: `aset/components/context/canonical/assurance/invariants.json`
- `limitations`: `aset/components/context/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/context/canonical/protocol/profile.json`
- `requirements`: `aset/components/context/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/context/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/context/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/context/canonical/assurance/verification-cases.json`
