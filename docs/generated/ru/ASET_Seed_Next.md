# Минимальное ядро разрешения ASET Seed 0.3 alpha 1

**Версия:** `0.3.0-alpha.1`

**Статус:** `MINIMAL_STRONG_CORE_ALPHA`

**SHA-256 канонической модели:** `sha256:5bbdfefe35a0adf83fd5e5dd86475a4f57ae92d4f9b9c06a7d530faf2e484396`

> Эта редакция выводится из машинного канона.

## Гарантии

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Понятия

### связка разрешения (`ResolutionBinding`)

Точная связка контекста, корня состояния, вопроса, эпохи политики и области, к которой относится одно разрешение.

Идентификатор: `seed.resolution_binding`

### запрос разрешения (`ResolutionRequest`)

Свежий идентификатор, связанный с одной точной связкой разрешения и начальной локально признанной Authority.

Идентификатор: `seed.resolution_request`

### разрешение (`Resolution`)

Производное значение UNKNOWN либо терминальное значение ALLOW или BLOCK.

Идентификатор: `seed.resolution_value`

### локальная Authority (`LocalAuthority`)

Authority, явно признанная одним Context для одной точной связки и эпохи политики.

Идентификатор: `seed.local_authority`

### доказательство Authority (`AuthorityProof`)

Локально укоренённая, точно связанная, ациклическая и нерасширяющая цепочка явных разрешений Authority.

Идентификатор: `seed.authority_proof`

### ссылка на основание (`EvidenceReference`)

Контентно-адресуемый неавторитетный вход, указанный как основание терминальной записи.

Идентификатор: `seed.evidence_reference`

### запись разрешения (`ResolutionRecord`)

Одна неизменяемая контентно-адресуемая терминальная запись ALLOW или BLOCK с точной связкой и доказательством Authority.

Идентификатор: `seed.resolution_record`

### коммитмент пересмотра (`ReconsiderationCommitment`)

Неизменяемый контентно-адресуемый коммитмент нового запроса на ранее признанную терминальную ResolutionRecord; запрос или запись-предшественник не обязаны физически сохраняться реализацией. Признание может устанавливаться текущим сохранённым материалом либо внешним проверенным доказательством принадлежности аутентифицированному множеству/аккумулятору.

Идентификатор: `seed.reconsideration_commitment`

## Требования

### `ASET-SEED-REQ-001`

ResolutionBinding ДОЛЖЕН содержать точные context_id, state_root, question_digest, policy_epoch и scope, а также канонический digest связки.

Модальность: `MUST`

Предикат: `binding_exact`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-002`

Каждый ResolutionRequest ДОЛЖЕН использовать свежий resolution_id и связывать одну точную ResolutionBinding.

Модальность: `MUST`

Предикат: `request_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-003`

Производное Resolution ДОЛЖНО быть UNKNOWN, ALLOW или BLOCK; хранимыми терминальными значениями являются только ALLOW и BLOCK.

Модальность: `MUST`

Предикат: `resolution_domain`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-004`

Точно связанный эффект ДОЛЖЕН быть разрешён тогда и только тогда, когда единственная действительная терминальная ResolutionRecord имеет значение ALLOW.

Модальность: `MUST`

Предикат: `allow_only`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-005`

UNKNOWN и BLOCK ДОЛЖНЫ запрещать эффект; отсутствие, недействительность, неоднозначность или ошибка проверки ДОЛЖНЫ давать UNKNOWN, а не ALLOW.

Модальность: `MUST`

Предикат: `fail_closed`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-006`

Терминальная запись ДОЛЖНА быть укоренена в Authority, явно признанной локальным Context для точной связки и эпохи политики.

Модальность: `MUST`

Предикат: `local_authority`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-007`

Каждое делегированное доказательство Authority ДОЛЖНО быть явным, ациклическим, точно связанным и нерасширяющим.

Модальность: `MUST`

Предикат: `proof_attenuating`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-008`

Evidence, результаты проверки, выходы AI, результаты консенсуса и удалённые outcomes НЕ ДОЛЖНЫ сами по себе создавать ALLOW или локальную Authority.

Модальность: `MUST`

Предикат: `inputs_non_authoritative`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-009`

Для одного resolution_id МОЖЕТ существовать не более одной действительной терминальной записи; конфликтующие терминальные записи ДОЛЖНЫ давать fail-closed UNKNOWN.

Модальность: `MAY`

Предикат: `terminal_unique`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-010`

Терминальная ResolutionRecord ДОЛЖНА быть неизменяемой и контентно-адресуемой; точный повтор МОЖЕТ быть идемпотентным, но замена запрещена.

Модальность: `MAY`

Предикат: `record_immutable`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-011`

Пересмотр ДОЛЖЕН создавать свежий resolution_id и нести неизменяемый контентно-адресуемый коммитмент на ранее признанную терминальную ResolutionRecord; запрос или запись-предшественник не обязаны физически сохраняться.

Модальность: `MUST`

Предикат: `reconsider_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-012`

Реализации и расширения ДОЛЖНЫ проверяться по наблюдаемой семантике и НЕ ДОЛЖНЫ иметь нормативного приоритета.

Модальность: `MUST`

Предикат: `implementation_neutral`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

## Инварианты

- `SEED-INV-001` — Каждое допустимое производное разрешение принадлежит UNKNOWN, ALLOW или BLOCK.
- `SEED-INV-002` — Разрешение эффекта истинно тогда и только тогда, когда единственная действительная терминальная запись равна ALLOW.
- `SEED-INV-003` — UNKNOWN и BLOCK никогда не разрешают эффект.
- `SEED-INV-004` — Каждый запрос и терминальная запись сохраняют один точный digest связки.
- `SEED-INV-005` — Каждая действительная терминальная запись укоренена в локальной связке Authority.
- `SEED-INV-006` — Каждое делегированное доказательство Authority точно связано, ациклично и не расширяет полномочие.
- `SEED-INV-007` — Evidence и внешние утверждения являются неавторитетными входами.
- `SEED-INV-008` — Для одного resolution_id существует не более одной действительной терминальной записи.
- `SEED-INV-009` — Конфликтующий или недействительный терминальный материал даёт UNKNOWN и никогда не ALLOW.
- `SEED-INV-010` — Записи разрешения являются append-only, неизменяемыми и контентно-адресуемыми.
- `SEED-INV-011` — Только признанные переходы Seed могут изменять каноническое хранилище; недействительный или непризнанный кандидат не является переходом Seed.
- `SEED-INV-012` — Пересмотр использует свежий resolution_id, связанный неизменяемым контентно-адресуемым коммитментом с ранее признанной терминальной ResolutionRecord; хранение объекта-предшественника не требуется.

## Переходы

### `SEED-TX-001` — `REGISTER_REQUEST`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-register-request.schema.json`
- `authority_rule`: The initial Authority binding must be locally rooted and exactly match the request binding.
- `binding_rule`: The request contains one canonical exact binding and a fresh resolution_id. For reconsideration, previous_terminal_record_digest must be a recognized immutable terminal-record commitment; predecessor object presence in retained storage is not required.
- `created_artifacts`: `ResolutionRequest`

### `SEED-TX-002` — `SUBMIT_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-submit-resolution.schema.json`
- `authority_rule`: The record Authority must be the local root Authority or be justified by a valid exact-binding Authority proof.
- `binding_rule`: The record request_digest and binding_digest must exactly match the registered request.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `EVALUATE_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/operation.schema.json`
- `authority_rule`: Evaluation creates no Authority and accepts no external statement as a resolution.
- `binding_rule`: Evaluation is performed for one registered resolution_id and fails closed on missing, invalid or conflicting terminal material.
- `created_artifacts`: `ResolutionEvaluation`

## Граница реализации

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `policy evaluation language`, `evidence acquisition`, `orchestration semantics`, `enforcement mechanism`, `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `federation topology`, `AI model`, `artifact retention`, `retention, pruning, archiving and compaction of superseded request/record material`, `terminal-commitment accumulator construction`, `accumulator membership/update witness retention`
