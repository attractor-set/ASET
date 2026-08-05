# ASET Model Gateway 0.1-rc1

Renderiza deterministicamente PromptManifest em uma solicitação ao provedor sem alterar o contexto canônico.

- `component_id`: `aset.model-gateway`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:f527277f95a3be9197eb92c9d441bf412ee6bd7caf16cfdd7880ccc7602f5e05`

## Limite de origem

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Propriedade

- `ModelProfile`
- `ProviderAdapter`
- `RenderedModelRequest`
- `UsageReceipt`

## Responsabilidades proibidas

- change PromptManifest
- execute tool call
- own canonical context

## Operações e mapeamento para o Seed

### `GW-RENDER` — RenderProviderRequest

Transforma deterministicamente PromptManifest em uma solicitação ao provedor sem alterar o contexto canônico.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

## Requisitos

Count: `10`

`GW-001`, `GW-002`, `GW-003`, `GW-004`, `GW-005`, `GW-006`, `GW-007`, `GW-008`, `PMC-006`, `PMC-007`

## Invariantes

- `GW-BND-001` — Provider rendering cannot mutate canonical context or execute tool calls.

## Limites de assurance

- `GATEWAY-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `GATEWAY-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Ativos do cânone legíveis por máquina

- `conformance_binding`: `aset/components/gateway/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/gateway/canonical/formal/gateway.tla`
- `invariants`: `aset/components/gateway/canonical/assurance/invariants.json`
- `limitations`: `aset/components/gateway/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/gateway/canonical/protocol/profile.json`
- `requirements`: `aset/components/gateway/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/gateway/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/gateway/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/gateway/canonical/assurance/verification-cases.json`
