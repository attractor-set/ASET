# ASET Monade 0.1-rc1

Coordena Task, execução e aceitação independente do resultado sobre transições autorizadas pelo Seed.

- `component_id`: `aset.monade`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:e4dac2a626959053d22f7f3941af369595ef2c7a5d81b7ab1df816366860836c`

## Limite de origem

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Propriedade

- `AcceptanceContract`
- `AcceptanceDecision`
- `EphemeralExecutionState`
- `EvidenceBundle`
- `ExecutionIntent`
- `ExecutionObservation`
- `OperationalBinding`
- `OutboxCommand`
- `Outcome`
- `PlanRevision`
- `ProjectionProfile`
- `PromptManifest`
- `Task`
- `TaskAcceptance`
- `TokenBudgetPlan`
- `ToolInvocation`
- `TransitionGraph`
- `VerificationReceipt`
- `VerificationVerdict`
- `VerifierAdapter`
- `WorkerEnvelope`
- `WorkerObservation`

## Responsabilidades proibidas

- issue Permit
- merge execution with acceptance
- replace Core
- self-accept execution

## Operações e mapeamento para o Seed

### `MON-PROJECT` — AdmitContextProjection

Admite uma projeção de contexto na Task sem transformar material recuperado em fato verificado.

- `classification`: `GOVERNED_CONTEXT_MUTATION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt`
- `outcome_recognition_required`: `False`

### `MON-BIND` — BindExecution

Vincula a mudança esperada autorizada ao executor, à ferramenta e aos critérios exatos.

- `classification`: `GOVERNED_CONTEXT_MUTATION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt`
- `outcome_recognition_required`: `False`

### `MON-DISPATCH` — DispatchExecution

Materializa ExecutionIntent e despacha o efeito externo somente após um execution Permit separado.

- `classification`: `EXTERNAL_EFFECT`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → ExecutionIntent → Observation → Verification → Outcome`
- `outcome_recognition_required`: `True`

### `MON-OBSERVE` — AdmitObservation

Registra a observação da execução externa sem declará-la resultado verificado.

- `classification`: `OBSERVATION_ADMISSION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → Observation`
- `outcome_recognition_required`: `False`

### `MON-VERIFY` — VerifyEvidence

Verifica a evidence em relação ao AcceptanceContract de forma independente do executor.

- `classification`: `VERIFICATION_PROCESSING`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → Observation → Verification`
- `outcome_recognition_required`: `False`

### `MON-CLOSE` — CloseTask

Reconhece Outcome somente com base em Verification admissível e classificação explícita do resultado.

- `classification`: `OUTCOME_RECOGNITION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → Observation → Verification → Outcome`
- `outcome_recognition_required`: `True`

### `MON-RETRY` — RetryExecution

Cria uma nova tentativa autorizada sem reutilizar um Permit já consumido.

- `classification`: `EXTERNAL_EFFECT`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → ExecutionIntent → Observation → Verification → Outcome`
- `outcome_recognition_required`: `True`

### `MON-COMPENSATE` — CompensateExecution

Executa uma ação compensatória autorizada separadamente com sua própria cadeia de evidence.

- `classification`: `EXTERNAL_EFFECT`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt → ExecutionIntent → Observation → Verification → Outcome`
- `outcome_recognition_required`: `True`

## Requisitos

Count: `42`

`GAT-013`, `GAT-014`, `GAT-015`, `MON-001`, `MON-002`, `MON-003`, `MON-004`, `MON-005`, `MON-006`, `MON-007`, `MON-008`, `MON-009`, `MON-010`, `MON-011`, `MON-012`, `MON-013`, `MON-014`, `MON-015`, `MON-016`, `MON-017`, `MON-018`, `PMC-001`, `PMC-002`, `PMC-003`, `PMC-004`, `PMC-005`, `PMC-008`, `VER-001`, `VER-002`, `VER-003`, `VER-004`, `VER-005`, `VER-006`, `VER-007`, `VER-008`, `WRK-001`, `WRK-002`, `WRK-003`, `WRK-004`, `WRK-005`, `WRK-006`, `WRK-007`

## Invariantes

- `INV-ACC-001` — ACCEPTED requires VERIFIED_SUCCESS, COMPLIANT, evidence and no unresolved claims.
- `INV-ACC-002` — EFFECT_UNKNOWN can only produce EVIDENCE_INSUFFICIENT or MANUAL_REVIEW_REQUIRED with UNDETERMINED normative status.
- `INV-EFFECT-001` — Gate crossing не доказывает dispatch, external effect, verification или acceptance.
- `INV-EFFECT-002` — Retry разрешён только при NO_EFFECT или доказанной идемпотентности.
- `INV-MONADE-001` — Execution не создаёт AcceptanceDecision; Acceptance не выполняет primary effect.
- `INV-MONADE-002` — Retry, verification probe и compensation имеют отдельные documents, gates и Permits.
- `INV-PROMPT-001` — Prompt Compiler детерминирован и не повышает epistemic status.
- `INV-PROMPT-002` — Provider prompt/cache не является источником истины.
- `INV-PROMPT-003` — PromptManifest binds the exact compiler-input projection and canonical messages; Model Gateway separately binds exact provider request bytes.
- `MON-BND-001` — Execution and Acceptance remain separate responsibilities.
- `MON-BND-002` — An execution attempt is not a recognized Outcome.

## Limites de assurance

- `MONADE-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `MONADE-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Ativos do cânone legíveis por máquina

- `conformance_binding`: `aset/components/monade/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/monade/canonical/formal/monade.tla`
- `invariants`: `aset/components/monade/canonical/assurance/invariants.json`
- `limitations`: `aset/components/monade/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/monade/canonical/protocol/profile.json`
- `requirements`: `aset/components/monade/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/monade/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/monade/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/monade/canonical/assurance/verification-cases.json`
