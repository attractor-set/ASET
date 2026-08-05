# ASET Master 0.1-rc1

Produz planos, ExpectedChangePatch e avaliações de trajetória sem criar autoridade.

- `component_id`: `aset.master`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:c36f06a1a60fbb4f85244674a875e599a222302de449c77198bb71454d2ed4db`

## Limite de origem

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Propriedade

- `AttractorDescriptor`
- `ExpectedChangePatch`
- `LearningObservation`
- `PlanAssessment`
- `PlanProposal`
- `TrajectoryAssessment`

## Responsabilidades proibidas

- accept own work
- dispatch effect
- issue Permit
- treat AttractorDescriptor as authority

## Operações e mapeamento para o Seed

### `MASTER-PLAN` — ProposePlan

Produz uma proposta consultiva de plano a partir da projeção atual do contexto.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

### `MASTER-EXPECT` — ProposeExpectedChange

Produz ExpectedChangePatch que, por si só, não concede autoridade.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

### `MASTER-ATTRACTOR` — AssessAttractor

Avalia estados desejáveis estáveis e trajetórias sem autorizar ações.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

## Requisitos

Count: `12`

`MAS-001`, `MAS-002`, `MAS-003`, `MAS-004`, `MAS-005`, `MAS-006`, `MAS-007`, `MAS-008`, `MAS-009`, `MAS-010`, `MAS-011`, `MAS-012`

## Invariantes

- `INV-MASTER-001` — Master формирует ExpectedChangePatch, но не Permit и не внешний эффект.
- `MASTER-BND-001` — ExpectedChangePatch and AttractorDescriptor are advisory and cannot authorize a gate crossing.

## Limites de assurance

- `MASTER-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `MASTER-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Ativos do cânone legíveis por máquina

- `conformance_binding`: `aset/components/master/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/master/canonical/formal/master.tla`
- `invariants`: `aset/components/master/canonical/assurance/invariants.json`
- `limitations`: `aset/components/master/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/master/canonical/protocol/profile.json`
- `requirements`: `aset/components/master/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/master/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/master/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/master/canonical/assurance/verification-cases.json`
