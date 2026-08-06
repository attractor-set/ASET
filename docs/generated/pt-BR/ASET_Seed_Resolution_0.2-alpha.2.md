# ASET Seed 0.2 alpha — Núcleo de Resolução

**Versão:** `0.2.0-alpha.2`

**Status:** `RESOLUTION_CORE_ALPHA`

**SHA-256 do modelo canônico:** `sha256:b7831e61ea2b58b0f4e8ef2e33a44b42224358f5efefb1c38bb9768cb9469611`

> Esta edição é derivada do cânone legível por máquina.

## Garantias

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Conceitos

### ciclo de resolução (`ResolutionCycle`)

Um ciclo imutavelmente vinculado para resolver uma questão normativa exata.

Identificador: `seed.resolution_cycle`

### vinculação de contexto (`ContextBinding`)

A vinculação exata de contexto, raiz de estado e época de política dentro da qual uma questão é resolvida.

Identificador: `seed.context_binding`

### questão de resolução (`ResolutionQuestion`)

Uma questão resumida canonicamente e seu escopo limitado de resolução.

Identificador: `seed.resolution_question`

### estado de resolução (`ResolutionStatus`)

O estado normativo UNKNOWN, ACCEPT ou DENY dentro de um ciclo.

Identificador: `seed.resolution_status`

### disposição de execução (`EnforcementDisposition`)

A consequência operacional de uma decisão: BLOCKED para UNKNOWN e DENY, ALLOW somente para ACCEPT.

Identificador: `seed.enforcement_disposition`

### autoridade de resolução (`ResolutionAuthority`)

Um sujeito explicitamente autorizado capaz de restringir UNKNOWN em um escopo e época exatos.

Identificador: `seed.resolution_authority`

### autorização de escalonamento (`EscalationGrant`)

Uma autorização explícita para encaminhar uma questão não resolvida à próxima Resolution Authority sem herança automática de autoridade.

Identificador: `seed.escalation_grant`

### referência de evidência (`EvidenceReference`)

Uma referência endereçada por conteúdo ao material usado ao restringir UNKNOWN.

Identificador: `seed.evidence_reference`

### registro de resolução (`ResolutionRecord`)

Um registro imutável de abertura, escalonamento ou resolução terminal e sua proveniência.

Identificador: `seed.resolution_record`

### cadeia de resolução (`ResolutionChain`)

Uma sequência acíclica de Resolution Authorities explicitamente autorizadas para uma questão.

Identificador: `seed.resolution_chain`

## Requisitos

### `ASET-SEED-REQ-001`

Um novo ciclo de resolução DEVE ser aberto como UNKNOWN com execução BLOCKED.

Modalidade: `MUST`

Predicado: `open_as_unknown_blocked`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-002`

O estado de um ciclo DEVE ser UNKNOWN, ACCEPT ou DENY; somente ACCEPT e DENY são terminais.

Modalidade: `MUST`

Predicado: `use_three_status_lattice`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-003`

UNKNOWN NÃO DEVE autorizar um efeito externo nem ser convertido silenciosamente em DENY.

Modalidade: `MUST_NOT`

Predicado: `authorize_from_unknown`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-004`

BLOCKED DEVE corresponder a UNKNOWN e DENY; ALLOW PODE corresponder somente a ACCEPT.

Modalidade: `MUST`

Predicado: `bind_enforcement_to_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-005`

Cada ciclo DEVE vincular valores exatos de context_id, state_root, question_digest, policy_epoch e scope.

Modalidade: `MUST`

Predicado: `bind_exact_question_state_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-006`

A restrição de UNKNOWN DEVE ser realizada por uma Resolution Authority ativa no escopo e época exatos.

Modalidade: `MUST`

Predicado: `require_exact_resolution_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-007`

Uma resolução ou escalonamento NÃO DEVE ampliar o escopo original da questão.

Modalidade: `MUST_NOT`

Predicado: `expand_resolution_scope`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-008`

O encaminhamento de UNKNOWN à próxima autoridade DEVE ter um EscalationGrant explícito; ancestralidade de contexto ou participação federativa, por si só, não cria autoridade.

Modalidade: `MUST`

Predicado: `require_explicit_escalation_grant`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-009`

O escalonamento DEVE preservar resolution_id, context_id, state_root, question_digest e policy_epoch.

Modalidade: `MUST`

Predicado: `preserve_question_during_escalation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-010`

A cadeia de Resolution Authority DEVE permanecer acíclica.

Modalidade: `MUST`

Predicado: `keep_resolution_chain_acyclic`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-011`

Dentro de um ciclo, ACCEPT ou DENY NÃO DEVEM mudar para outro estado; uma repetição exata PODE ser idempotente.

Modalidade: `MUST_NOT`

Predicado: `mutate_terminal_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-012`

A reconsideração de uma decisão terminal DEVE criar um novo resolution_id e ciclo vinculado ao registro anterior.

Modalidade: `MUST`

Predicado: `use_new_cycle_for_reconsideration`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-013`

A abertura, o escalonamento e a resolução terminal DEVEM adicionar um ResolutionRecord imutável com Authority e proveniência.

Modalidade: `MUST`

Predicado: `append_resolution_records`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-014`

As implementações DEVEM ser verificadas pela semântica observável e não têm precedência normativa entre si.

Modalidade: `MUST`

Predicado: `preserve_implementation_neutrality`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-EXTERNAL-CONFORMANCE`

## Invariantes

- `SEED-INV-001` — Todo estado válido é UNKNOWN, ACCEPT ou DENY.
- `SEED-INV-002` — UNKNOWN está sempre associado a BLOCKED.
- `SEED-INV-003` — DENY está sempre associado a BLOCKED.
- `SEED-INV-004` — ALLOW é possível somente com ACCEPT.
- `SEED-INV-005` — Uma decisão terminal é imutável dentro de um resolution_id.
- `SEED-INV-006` — A Resolution Authority deve corresponder ao contexto, escopo e época de política.
- `SEED-INV-007` — O escalonamento é possível somente a partir de UNKNOWN por meio de um EscalationGrant explícito.
- `SEED-INV-008` — O escalonamento preserva a identidade da questão e não amplia o escopo.
- `SEED-INV-009` — A cadeia de Resolution Authority não contém autoridade repetida.
- `SEED-INV-010` — Os registros ResolutionRecord são acrescentados monotonicamente e nunca reescritos.
- `SEED-INV-011` — Um comando rejeitado preserva o estado e a raiz de estado.
- `SEED-INV-012` — Uma nova reconsideração de uma decisão terminal usa um novo resolution_id.

## Transições

### `SEED-TX-001` — `OPEN_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-open-resolution.schema.json`
- `authority_rule`: The opening authority must be explicit and exactly bound to context, scope and policy epoch.
- `scope_rule`: The opened scope becomes the maximum scope of this cycle.
- `created_artifacts`: `ResolutionCycle`, `ResolutionRecord`

### `SEED-TX-002` — `RESOLVE_ACCEPT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-resolve.schema.json`
- `authority_rule`: The current Resolution Authority must match exact binding and scope.
- `scope_rule`: Decision scope must be equal to or narrower than the opened scope.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `RESOLVE_DENY`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-resolve.schema.json`
- `authority_rule`: The current Resolution Authority must match exact binding and scope.
- `scope_rule`: Decision scope must be equal to or narrower than the opened scope.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-004` — `ESCALATE_UNKNOWN`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-escalate-unknown.schema.json`
- `authority_rule`: An exact EscalationGrant must authorize the current and next Resolution Authorities.
- `scope_rule`: Escalated scope must not expand and exact question binding must remain unchanged.
- `created_artifacts`: `ResolutionRecord`

## Limite da implementação

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `execution engine`, `planning`, `memory`, `federation topology`, `artifact retention`
