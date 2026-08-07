# Минимальное ядро разрешения ASET Seed 0.3 alpha 1

**Версия:** `0.3.0-alpha.1`

**Статус:** `MINIMAL_STRONG_CORE_ALPHA`

**SHA-256 канонической модели:** `sha256:d8fde8f21b6524b2442151505f8bf4aec29e17be4a17d2409021ad594597b203`

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

### признание Authority (`AuthorityRecognition`)

Локальный результат точного признания, устанавливающий полномочие одной Authority для одной ResolutionBinding; конкретные цепочки делегирования, подписи и построение доказательства находятся вне Seed.

Идентификатор: `seed.authority_recognition`

### ссылка на основание (`EvidenceReference`)

Непрозрачная контентно-адресуемая ссылка на неавторитетное основание или доказательный материал. Она не имеет нормативного эффекта, пока граница допуска Seed не признает подтверждаемый ею факт.

Идентификатор: `seed.evidence_reference`

### запись разрешения (`ResolutionRecord`)

Одна неизменяемая контентно-адресуемая терминальная запись ALLOW или BLOCK с точной связкой, признанной Authority и необязательными непрозрачными ссылками на основания.

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

Точно связанный эффект ДОЛЖЕН быть разрешён тогда и только тогда, когда принятая авторитетная терминальная ResolutionRecord имеет значение ALLOW и не наблюдается действительный терминальный конфликт.

Модальность: `MUST`

Предикат: `allow_only`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-005`

UNKNOWN и BLOCK ДОЛЖНЫ запрещать эффект. Отсутствие принятого терминального состояния, невозможность установить авторитетную терминальную запись либо наблюдение дополнительного конфликтующего действительного терминального материала ДОЛЖНЫ давать UNKNOWN. Недействительный или неавторитетный материал НЕ ДОЛЖЕН переопределять уже принятую авторитетную терминальную запись.

Модальность: `MUST`

Предикат: `fail_closed`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-006`

Терминальная запись ДОЛЖНА быть укоренена в Authority, явно признанной локальным Context для точной связки и эпохи политики.

Модальность: `MUST`

Предикат: `local_authority`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-007`

Доказательный или делегационный материал Authority НЕ ДОЛЖЕН сам по себе создавать или расширять полномочие; Authority терминальной записи ДОЛЖНА быть явно признана для точной связки до того, как запись может стать действительной.

Модальность: `MUST`

Предикат: `authority_recognition_boundary`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-008`

Evidence, результаты проверки, выводы ИИ, результаты консенсуса, удалённые outcomes и иные внешние утверждения НЕ ДОЛЖНЫ сами по себе изменять принадлежащее Seed каноническое состояние либо создавать ALLOW или локальную Authority.

Модальность: `MUST`

Предикат: `inputs_non_authoritative`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-009`

Принадлежащее Seed состояние ДОЛЖНО принимать не более одной терминальной записи для одного resolution_id. Наблюдение дополнительного отличающегося действительного терминального материала для уже принятого терминального разрешения ДОЛЖНО давать fail-closed UNKNOWN без замены принятой записи.

Модальность: `MUST`

Предикат: `accepted_terminal_unique`

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
- `SEED-INV-002` — Разрешение эффекта истинно тогда и только тогда, когда принятая авторитетная терминальная запись имеет значение ALLOW и не наблюдается действительный терминальный конфликт.
- `SEED-INV-003` — UNKNOWN и BLOCK никогда не разрешают эффект.
- `SEED-INV-004` — Каждый запрос и терминальная запись сохраняют один точный digest связки.
- `SEED-INV-005` — Каждая действительная терминальная запись использует Authority, явно признанную для точной локальной связки.
- `SEED-INV-006` — Доказательный материал Authority неавторитетен до успешного точного признания Authority; непрозрачный proof material не может сам по себе создать или расширить полномочие.
- `SEED-INV-007` — Внешние утверждения и Evidence находятся вне принадлежащего Seed канонического состояния, пока не приняты признанным переходом Seed.
- `SEED-INV-008` — Принадлежащее Seed состояние принимает не более одной терминальной записи для одного resolution_id.
- `SEED-INV-009` — Наблюдение конфликта допустимо только для resolution_id, у которого уже есть принятая терминальная запись. Дополнительный конфликтующий действительный терминальный материал даёт UNKNOWN; недействительный или неавторитетный материал не может создать ALLOW, создать конфликт или заменить принятую запись.
- `SEED-INV-010` — Записи разрешения являются append-only, неизменяемыми и контентно-адресуемыми.
- `SEED-INV-011` — Только признанные переходы состояния Seed могут изменять принадлежащее Seed каноническое состояние; наблюдения среды и observer-операции его не изменяют.
- `SEED-INV-012` — Пересмотр использует свежий resolution_id, связанный неизменяемым контентно-адресуемым коммитментом с ранее признанной терминальной ResolutionRecord; хранение объекта-предшественника не требуется.

## Операции

### `SEED-OP-001` — `REGISTER_REQUEST`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-register-request.schema.json`
- `authority_rule`: The Authority must be explicitly recognized for the exact request binding.
- `binding_rule`: The request contains one canonical exact binding and a fresh resolution_id. For reconsideration, previous_terminal_record_digest must be a recognized immutable terminal-record commitment; predecessor object presence in retained storage is not required.
- `created_artifacts`: `ResolutionRequest`

### `SEED-OP-002` — `SUBMIT_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-submit-resolution.schema.json`
- `authority_rule`: The Authority must be explicitly recognized for the exact request binding. Concrete signatures, credentials, delegation mechanisms and proof construction are external validation mechanisms.
- `binding_rule`: The record request_digest and binding_digest must exactly match the registered request.
- `created_artifacts`: `ResolutionRecord`

### `SEED-OP-003` — `EVALUATE_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/operation.schema.json`
- `authority_rule`: Evaluation creates no Authority and accepts no external statement as a resolution.
- `binding_rule`: Evaluation observes one resolution_id without mutating Seed-owned state. It derives UNKNOWN when no authoritative accepted terminal result is established or when additional conflicting valid terminal material is observed; invalid or non-authoritative material cannot override an otherwise authoritative accepted terminal result.
- `created_artifacts`: `ResolutionEvaluation`

## Граница реализации

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `policy evaluation language`, `evidence acquisition`, `orchestration semantics`, `enforcement mechanism`, `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `concrete Authority grant-chain construction and validation`, `key custody`, `federation topology`, `AI model`, `artifact retention`, `retention, pruning, archiving and compaction of superseded request/record material`, `terminal-commitment accumulator construction`, `accumulator membership/update witness retention`
