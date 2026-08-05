# ASET Seed 0.1-rc12 — машиночитаемый нормативный канон

**Версия:** `0.1-rc12`

**Статус:** `RC12_RELEASE_CANDIDATE_READY`

**SHA-256 канонической модели:** `sha256:4e633a5cfe17872d8edadd51780c01924647a5c80e6a693f1af5d768e36e5faa`

> Документ создан автоматически из машинного канона. Ручное редактирование запрещено.

## Границы гарантий

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Понятия

### пространство доверия (`TrustSpace`)

Состояние одной линии Genesis с изолированной нормативной историей.

Идентификатор: `seed.trust_space`

### генезис (`Genesis`)

Неизменяемый исходный материал, закрепляющий идентичность пространства доверия.

Идентификатор: `seed.genesis`

### конституция доверия (`Constitution`)

Каноническая политика допустимых полномочий, процедур и переходов.

Идентификатор: `seed.constitution`

### контекст (`Context`)

Нормативное пространство имён с неизменяемым ContextID и локальным состоянием.

Идентификатор: `seed.context`

### описатель контекста (`ContextDescriptor`)

Протокольная запись идентичности, родителя, адреса, участника и жизненного цикла контекста.

Идентификатор: `seed.context_descriptor`

### институциональное полномочие (`Authority`)

Действующее институциональное полномочие в точном контексте, области и состоянии.

Идентификатор: `seed.authority`

### связка полномочия (`AuthorityBinding`)

Протокольная запись носителя, вида, области, эпохи и происхождения полномочия.

Идентификатор: `seed.authority_binding`

### решение (`Decision`)

Зафиксированный нормативный выбор или заявление о готовности.

Идентификатор: `seed.decision`

### разрешение (`Permit`)

Ограниченное разрешение на предъявление результата конкретного действия.

Идентификатор: `seed.permit`

### намерение исполнения (`ExecutionIntent`)

Материализованное использование разрешения для конкретной попытки.

Идентификатор: `seed.execution_intent`

### квитанция использования разрешения (`PermitUseReceipt`)

Неизменяемое свидетельство расходования конкретной попытки разрешения.

Идентификатор: `seed.permit_use_receipt`

### наблюдение (`Observation`)

Утверждение о результате действия или внешнем факте, связанное с доказательствами.

Идентификатор: `seed.observation`

### проверка (`Verification`)

Признание прохождения утверждением предписанной процедуры проверки.

Идентификатор: `seed.verification`

### итоговое признание (`Outcome`)

Окончательное институциональное признание результата действия.

Идентификатор: `seed.outcome`

### переход состояния (`Transition`)

Атомарный кандидат изменения канонического состояния одного контекста.

Идентификатор: `seed.transition`

### запись перехода (`TransitionRecord`)

Неизменяемая запись принятого перехода, причин и созданных артефактов.

Идентификатор: `seed.transition_record`

### квитанция экспорта (`ExportReceipt`)

Локальное обязательство источника, переносимое в другой контекст как доказательство.

Идентификатор: `seed.export_receipt`

### запись импорта (`ImportRecord`)

Локальная запись принятия внешнего доказательства без автоматического переноса итогового признания.

Идентификатор: `seed.import_record`

### локальный коммит (`LocalCommit`)

Предварительно классифицированный переход, допустимый во время разделения связи.

Идентификатор: `seed.local_commit`

### квитанция согласования (`ReconciliationReceipt`)

Запись проверки локальных коммитов, подтверждённого префикса и обнаруженных развилок.

Идентификатор: `seed.reconciliation_receipt`

### ребро зависимости (`DependencyEdge`)

Типизированная направленная связь нормативной или ненормативной зависимости контекстов.

Идентификатор: `seed.dependency_edge`

### запись выхода участника (`MembershipWithdrawalRecord`)

Неизменяемая запись добровольного выхода или замещения контекста.

Идентификатор: `seed.membership_withdrawal_record`

### запись переопределения контекста (`ContextRedefinitionRecord`)

Полная запись атомарной замены точного множества взаимозависимых контекстов.

Идентификатор: `seed.context_redefinition_record`

### запись исправления (`CorrectionRecord`)

Добавочная запись отзыва или замены проверки до финального итогового признания.

Идентификатор: `seed.correction_record`

### корень состояния (`StateRoot`)

Домен-разделённый хеш канонического полного состояния пространства доверия.

Идентификатор: `seed.state_root`

### доказательство аутентификации (`Proof`)

Внешне проверяемое доказательство, привязанное к субъекту и точному переходу.

Идентификатор: `seed.proof`

### устойчивое хранилище исполнения (`RuntimeStore`)

Транзакционное хранилище состояния и неизменяемого журнала попыток переходов.

Идентификатор: `seed.runtime_store`

## Требования

### `ASET-SEED-REQ-001`

Публичный интерфейс ДОЛЖЕН применять строгие схемы и закрываться при любой неопределённости.

Каноническая модальность: `MUST`

Предикат: `enforce_strict_schemas_fail_closed`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-002`

TrustSpaceID и ContextID ДОЛЖНЫ выводиться из канонического материала Genesis.

Каноническая модальность: `MUST`

Предикат: `derive_identity_from_genesis`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-003`

Каждый принятый переход ДОЛЖЕН быть атомарным и завершаться проверкой всего состояния.

Каноническая модальность: `MUST`

Предикат: `commit_atomically_and_validate_state`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-004`

Действующие области полномочий для одной пары контекст/вид полномочия НЕ ДОЛЖНЫ пересекаться.

Каноническая модальность: `MUST_NOT`

Предикат: `prevent_active_scope_overlap`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-005`

Условия разрешения ДОЛЖНЫ связывать заявление о готовности и решение о выдаче разрешения.

Каноническая модальность: `MUST`

Предикат: `bind_permit_terms`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-006`

Предикат успеха разрешения ДОЛЖЕН разрешаться в действующее правило конституции.

Каноническая модальность: `MUST`

Предикат: `resolve_success_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-007`

Политика проверки ДОЛЖНА совпадать с предикатом успеха разрешения.

Каноническая модальность: `MUST`

Предикат: `match_verification_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-008`

Итоговое признание ДОЛЖНО агрегировать полный действительный набор успешных проверок.

Каноническая модальность: `MUST`

Предикат: `aggregate_complete_effective_verifications`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-009`

Исправление ДОЛЖНО относиться только к проверке, ещё не закреплённой итоговым признанием.

Каноническая модальность: `MUST`

Предикат: `limit_correction_to_nonfinal_verification`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-010`

Причинные родители ДОЛЖНЫ вычисляться из типизированных ссылок на артефакты.

Каноническая модальность: `MUST`

Предикат: `derive_causal_parents`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-011`

Обычные переходы НЕ ДОЛЖНЫ приниматься в приостановленном контексте.

Каноническая модальность: `MUST_NOT`

Предикат: `block_ordinary_transition_in_suspended_context`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-012`

Согласование ДОЛЖНО включать все известные локальные коммиты и сохранять доказательства развилок.

Каноническая модальность: `MUST`

Предикат: `reconcile_complete_known_commits`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-013`

Обе вершины нормативной зависимости ДОЛЖНЫ быть действующими контекстами.

Каноническая модальность: `MUST`

Предикат: `require_active_normative_endpoints`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-014`

Самостоятельный выход ДОЛЖЕН быть подписан участником и НЕ ДОЛЖЕН оставлять действующего нормативного зависимого.

Каноническая модальность: `MUST`

Предикат: `protect_normative_dependants_on_withdrawal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-015`

AffectedSiblingSet ДОЛЖЕН вычисляться транзитивно из состояния до перехода.

Каноническая модальность: `MUST`

Предикат: `compute_affected_sibling_closure`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-016`

Хеш предложения ДОЛЖЕН связывать полное встроенное предложение.

Каноническая модальность: `MUST`

Предикат: `bind_full_redefinition_proposal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-017`

Каждый затронутый участник ДОЛЖЕН разрешить точное предложение.

Каноническая модальность: `MUST`

Предикат: `require_all_member_authorizations`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-018`

Родитель ДОЛЖЕН обладать полномочием REDEFINE_CONTEXT.

Каноническая модальность: `MUST`

Предикат: `require_parent_redefinition_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-019`

Переопределение ДОЛЖНО завершаться атомарно либо оставлять состояние неизменным.

Каноническая модальность: `MUST`

Предикат: `commit_redefinition_atomically`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-020`

Преемники ДОЛЖНЫ сохранять родителя, псевдоним, участника и вид, получая новый ContextID.

Каноническая модальность: `MUST`

Предикат: `preserve_successor_identity_fields`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-021`

Зависимости между затронутыми соседями ДОЛЖНЫ переназначаться на преемников.

Каноническая модальность: `MUST`

Предикат: `remap_affected_dependencies`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-022`

Записи управления ДОЛЖНЫ сохранять полное предложение и хеши доказательств.

Каноническая модальность: `MUST`

Предикат: `retain_governance_evidence`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-023`

Передача полномочия ДОЛЖНА использовать положительную цепочку действия в том же контексте и готовность нового носителя.

Каноническая модальность: `MUST`

Предикат: `bind_same_context_authority_transfer`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-024`

Покрытие ветвей эталонного ядра ДОЛЖНО быть не ниже 90 процентов для фиксации релиза.

Каноническая модальность: `MUST`

Предикат: `meet_branch_coverage_threshold`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-025`

Доказательства покрытия и проверки публикации ДОЛЖНЫ быть связаны с точными байтами исходников и документов.

Каноническая модальность: `MUST`

Предикат: `bind_assurance_to_exact_bytes`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-026`

Фиксация релиза ДОЛЖНА включать чистую проверку детерминированного архива.

Каноническая модальность: `MUST`

Предикат: `perform_clean_room_release_validation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-DOC-001`

Официальные языковые редакции ДОЛЖНЫ детерминированно строиться из машиночитаемого канона.

Каноническая модальность: `MUST`

Предикат: `derive_editions_from_canon`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

### `ASET-SEED-DOC-002`

Все представления ДОЛЖНЫ сохранять стабильные семантические идентификаторы требований, инвариантов и переходов.

Каноническая модальность: `MUST`

Предикат: `preserve_semantic_identifiers`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

## Инварианты

- `SEED-INV-001` — TrustSpaceID, Root Genesis и конституция эпохи 0 неизменяемы.
- `SEED-INV-002` — Существует ровно один корневой контекст без родителя, а дерево контекстов не содержит циклов.
- `SEED-INV-003` — Каждый ContextID вычисляется из идентификатора родителя и хеша Genesis контекста.
- `SEED-INV-004` — Индекс действующих псевдонимов точно соответствует действующим контекстам.
- `SEED-INV-005` — Все действующие контексты используют текущую эпоху конституции.
- `SEED-INV-006` — Для одного ключа полномочия существует не более одного действующего носителя, а области одного вида полномочия не пересекаются.
- `SEED-INV-007` — Отозванный, замещённый или прекращённый контекст не содержит действующих полномочий и разрешений.
- `SEED-INV-008` — Ключ каждой карты артефактов совпадает с внутренним идентификатором артефакта и указывает на существующий контекст.
- `SEED-INV-009` — Условия разрешения точно связаны с решением, готовностью и признанной политикой успеха.
- `SEED-INV-010` — Политика проверки совпадает с предикатом успеха разрешения и правилом действующей конституции.
- `SEED-INV-011` — Ослабление разрешения линейно и не создаёт двойного бюджета попыток.
- `SEED-INV-012` — Индексы попыток непрерывны, квитанции устойчивы, а индекс submission_id точен.
- `SEED-INV-013` — Каждое наблюдение связано с точными квитанцией, разрешением и контекстом.
- `SEED-INV-014` — Каждая проверка связана с точными наблюдением, квитанцией, разрешением и контекстом.
- `SEED-INV-015` — Итоговое признание использует полный действительный набор проверок данного разрешения.
- `SEED-INV-016` — Экспорт, импорт и локальное признание сохраняют точную межконтекстную линию происхождения.
- `SEED-INV-017` — Исправление относится только к проверке до финального итогового признания.
- `SEED-INV-018` — Счётчики переходов, локальные порядковые номера, владельцы артефактов и вычисленные причинные родители точны.
- `SEED-INV-019` — Приостановленный контекст допускает локальное продолжение только через специальный переход разделения.
- `SEED-INV-020` — Согласование включает все известные локальные коммиты и сохраняет доказательства конкурирующих ветвей.
- `SEED-INV-021` — Рёбра зависимостей уникальны, не ссылаются на себя и имеют существующие вершины.
- `SEED-INV-022` — Обе вершины каждого нормативного ребра являются действующими контекстами.
- `SEED-INV-023` — Самостоятельный выход не оставляет действующего нормативного зависимого.
- `SEED-INV-024` — AffectedSiblingSet является точным транзитивным замыканием прямых соседей.
- `SEED-INV-025` — Переопределение использует канонический хеш полного предложения и точный набор разрешений участников.
- `SEED-INV-026` — Замена контекстов атомарна, сохраняет поля идентичности и точно переназначает зависимости.
- `SEED-INV-027` — Записи управления содержат полное предложение и доказательства аутентификации.
- `SEED-INV-028` — Передача полномочия имеет полную цепочку действия в том же контексте.
- `SEED-INV-029` — Внутренние корни контекстов и глобальный корень состояния точно соответствуют каноническому состоянию.

## Переходы

### `SEED-TX-001` — `MEMBER_CONTEXT_GENESIS`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-member-context-genesis.schema.json`
- `authorization_rule`: bootstrap predicate or CREATE_MEMBER_CONTEXT
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`

### `SEED-TX-002` — `DECISION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-decision.schema.json`
- `authorization_rule`: self-signed readiness or capability selected by decision kind
- `created_artifacts`: `Decision`

### `SEED-TX-003` — `PERMIT_ISSUE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-issue.schema.json`
- `authorization_rule`: ISSUE_PERMIT
- `created_artifacts`: `Permit`

### `SEED-TX-004` — `PERMIT_ATTENUATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-attenuate.schema.json`
- `authorization_rule`: active parent permit and new-delegate readiness
- `created_artifacts`: `Permit`

### `SEED-TX-005` — `PERMIT_USE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-use.schema.json`
- `authorization_rule`: permit delegate and available attempt
- `created_artifacts`: `ExecutionIntent`, `PermitUseReceipt`

### `SEED-TX-006` — `OBSERVATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-observation.schema.json`
- `authorization_rule`: presenter bound to permit-use receipt
- `created_artifacts`: `Observation`

### `SEED-TX-007` — `VERIFICATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-verification.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `Verification`

### `SEED-TX-008` — `OUTCOME`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-outcome.schema.json`
- `authorization_rule`: CONFIRM_OUTCOME
- `created_artifacts`: `Outcome`

### `SEED-TX-009` — `EXPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-export.schema.json`
- `authorization_rule`: EXPORT
- `created_artifacts`: `ExportReceipt`

### `SEED-TX-010` — `IMPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-import.schema.json`
- `authorization_rule`: IMPORT and local permit-use receipt
- `created_artifacts`: `ImportRecord`, `Observation`

### `SEED-TX-011` — `GUARANTEE_SUSPEND`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-guarantee-suspend.schema.json`
- `authorization_rule`: SUSPEND_GUARANTEE in parent context
- `created_artifacts`: `context guarantee status`

### `SEED-TX-012` — `PARTITION_LOCAL_TRANSITION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-partition-local-transition.schema.json`
- `authorization_rule`: constitution-classified local operation and accepted proof
- `created_artifacts`: `LocalCommit`

### `SEED-TX-013` — `RECONCILE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-reconcile.schema.json`
- `authorization_rule`: RECONCILE
- `created_artifacts`: `ReconciliationReceipt`

### `SEED-TX-014` — `MEMBERSHIP_WITHDRAW`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-membership-withdraw.schema.json`
- `authorization_rule`: member signature and no active normative dependant
- `created_artifacts`: `MembershipWithdrawalRecord`

### `SEED-TX-015` — `CONTEXT_REDEFINE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-redefine.schema.json`
- `authorization_rule`: parent REDEFINE_CONTEXT plus exact member authorizations
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`, `MembershipWithdrawalRecord`, `ContextRedefinitionRecord`

### `SEED-TX-016` — `CONTEXT_TERMINATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-terminate.schema.json`
- `authorization_rule`: TERMINATE_CONTEXT plus PASS TRUST_LINEAGE_LOST verification
- `created_artifacts`: `context lifecycle changes`

### `SEED-TX-017` — `CORRECTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-correction.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `CorrectionRecord`

### `SEED-TX-018` — `AUTHORITY_TRANSFER`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-authority-transfer.schema.json`
- `authorization_rule`: TRANSFER_AUTHORITY plus same-context positive action trail
- `created_artifacts`: `AuthorityBinding`

## Граница реализации

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `programming language`, `storage backend`, `deployment topology`, `consensus protocol`, `network transport`, `cryptographic provider`, `operational user interface`
