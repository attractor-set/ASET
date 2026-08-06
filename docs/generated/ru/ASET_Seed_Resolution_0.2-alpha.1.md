# ASET Seed 0.2 alpha — ядро разрешения

**Версия:** `0.2.0-alpha.1`

**Статус:** `RESOLUTION_CORE_ALPHA`

**SHA-256 канонической модели:** `sha256:af855b45f052ebfef144de856d71230f5b2b9a65d48fe58c24be778ace51d633`

> Эта редакция выводится из машинного канона.

## Гарантии

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Понятия

### цикл разрешения (`ResolutionCycle`)

Один неизменяемо связанный цикл разрешения точного нормативного вопроса.

Идентификатор: `seed.resolution_cycle`

### связка контекста (`ContextBinding`)

Точная связка контекста, корня состояния и эпохи политики, внутри которой разрешается вопрос.

Идентификатор: `seed.context_binding`

### вопрос разрешения (`ResolutionQuestion`)

Канонически хешированный вопрос и его ограниченная область решения.

Идентификатор: `seed.resolution_question`

### статус разрешения (`ResolutionStatus`)

Нормативный статус UNKNOWN, ACCEPT или DENY внутри одного цикла.

Идентификатор: `seed.resolution_status`

### режим исполнения (`EnforcementDisposition`)

Операционное следствие решения: BLOCKED для UNKNOWN и DENY, ALLOW только для ACCEPT.

Идентификатор: `seed.enforcement_disposition`

### власть разрешения (`ResolutionAuthority`)

Явно уполномоченный субъект, способный сузить UNKNOWN в точной области и эпохе.

Идентификатор: `seed.resolution_authority`

### разрешение эскалации (`EscalationGrant`)

Явное разрешение передать неразрешённый вопрос следующей Resolution Authority без автоматического наследования власти.

Идентификатор: `seed.escalation_grant`

### ссылка на доказательство (`EvidenceReference`)

Контентно-адресуемая ссылка на материал, использованный при сужении UNKNOWN.

Идентификатор: `seed.evidence_reference`

### запись разрешения (`ResolutionRecord`)

Неизменяемая запись открытия, эскалации или терминального решения и его provenance.

Идентификатор: `seed.resolution_record`

### цепочка разрешения (`ResolutionChain`)

Ациклическая последовательность явно уполномоченных Resolution Authorities для одного вопроса.

Идентификатор: `seed.resolution_chain`

## Требования

### `ASET-SEED-REQ-001`

Новый цикл разрешения ДОЛЖЕН открываться как UNKNOWN с режимом BLOCKED.

Модальность: `MUST`

Предикат: `open_as_unknown_blocked`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-002`

Статус цикла ДОЛЖЕН принадлежать множеству UNKNOWN, ACCEPT, DENY; терминальными являются только ACCEPT и DENY.

Модальность: `MUST`

Предикат: `use_three_status_lattice`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-003`

UNKNOWN НЕ ДОЛЖЕН разрешать внешний эффект и НЕ ДОЛЖЕН неявно подменяться DENY.

Модальность: `MUST_NOT`

Предикат: `authorize_from_unknown`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-004`

BLOCKED ДОЛЖЕН соответствовать UNKNOWN и DENY; ALLOW МОЖЕТ соответствовать только ACCEPT.

Модальность: `MUST`

Предикат: `bind_enforcement_to_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-005`

Каждый цикл ДОЛЖЕН быть связан с точными context_id, state_root, question_digest, policy_epoch и scope.

Модальность: `MUST`

Предикат: `bind_exact_question_state_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-006`

Сужение UNKNOWN ДОЛЖНО выполняться действующей Resolution Authority в точной области и эпохе.

Модальность: `MUST`

Предикат: `require_exact_resolution_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-007`

Решение или эскалация НЕ ДОЛЖНЫ расширять исходную область вопроса.

Модальность: `MUST_NOT`

Предикат: `expand_resolution_scope`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-008`

Передача UNKNOWN следующей власти ДОЛЖНА иметь явный EscalationGrant; вложенность контекстов или членство в федерации сами по себе власть не создают.

Модальность: `MUST`

Предикат: `require_explicit_escalation_grant`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-009`

Эскалация ДОЛЖНА сохранять resolution_id, context_id, state_root, question_digest и policy_epoch.

Модальность: `MUST`

Предикат: `preserve_question_during_escalation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-010`

Цепочка Resolution Authority ДОЛЖНА оставаться ациклической.

Модальность: `MUST`

Предикат: `keep_resolution_chain_acyclic`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-011`

Внутри одного цикла ACCEPT или DENY НЕ ДОЛЖНЫ изменяться на другой статус; точный повтор МОЖЕТ быть идемпотентным.

Модальность: `MUST_NOT`

Предикат: `mutate_terminal_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-012`

Пересмотр терминального решения ДОЛЖЕН создавать новый resolution_id и новый цикл, связанный с исходной записью.

Модальность: `MUST`

Предикат: `use_new_cycle_for_reconsideration`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-013`

Открытие, эскалация и терминальное решение ДОЛЖНЫ добавлять неизменяемый ResolutionRecord с Authority и provenance.

Модальность: `MUST`

Предикат: `append_resolution_records`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-014`

Реализации ДОЛЖНЫ проверяться по наблюдаемой семантике и НЕ ИМЕЮТ нормативного приоритета друг над другом.

Модальность: `MUST`

Предикат: `preserve_implementation_neutrality`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-EXTERNAL-CONFORMANCE`

## Инварианты

- `SEED-INV-001` — Каждый допустимый статус принадлежит UNKNOWN, ACCEPT или DENY.
- `SEED-INV-002` — UNKNOWN всегда связан с BLOCKED.
- `SEED-INV-003` — DENY всегда связан с BLOCKED.
- `SEED-INV-004` — ALLOW возможен только при ACCEPT.
- `SEED-INV-005` — Терминальное решение неизменяемо внутри одного resolution_id.
- `SEED-INV-006` — Resolution Authority должна совпадать по context, scope и policy epoch.
- `SEED-INV-007` — Эскалация возможна только из UNKNOWN по явному EscalationGrant.
- `SEED-INV-008` — Эскалация сохраняет идентичность вопроса и не расширяет scope.
- `SEED-INV-009` — Цепочка Resolution Authority не содержит повторов.
- `SEED-INV-010` — ResolutionRecord добавляется монотонно и не переписывается.
- `SEED-INV-011` — Отклонённая команда сохраняет состояние и state root.
- `SEED-INV-012` — Новый пересмотр терминального решения использует новый resolution_id.

## Переходы

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

## Граница реализации

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `execution engine`, `planning`, `memory`, `federation topology`, `artifact retention`
