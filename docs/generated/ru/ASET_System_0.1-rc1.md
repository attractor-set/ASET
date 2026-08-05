# ASET System Composition 0.1-rc1

- `status`: `COMPONENT_COMPOSITION_CANDIDATE`
- `canonical_digest`: `sha256:d7a0120c924adef6b6839339ed85db82e153b8fd3e132425f3d236023b8a0dc4`
- `seed_version`: `0.1-rc12`

## Роль ASET Seed

- `classification`: `MINIMAL_SEMANTIC_NUCLEUS`
- `implementation_neutral`: `True`
- `normative_function`: `Определяет связанные с полномочиями понятия, условия действительности, инварианты и семантику переходов, необходимые для совместимых с ASET систем.`
- `composition_rule`: `Полные системы ASET и совместимые профили реализации могут использовать независимые внутренние или внешние компоненты. Любой переход, претендующий на авторитетное значение в ASET, включая авторизацию значимого изменения состояния, авторитетную фиксацию его исполнения, его верификацию или признание как Outcome, должен соответствовать семантике Seed.`
- `extension_rule`: `Компонентные каноны и профили реализации могут уточнять понятия Seed и вводить дополнительные меры контроля, но не должны ослаблять, объединять или обходить различия и инварианты Seed.`
- `claim_boundary`: `Seed устанавливает нормативную действительность и прослеживаемость авторитетных переходов. Сам по себе он не устанавливает фактическую истинность, полноту или внешнюю корректность наблюдений, evidence или исходных данных.`

### Возможности, не предоставляемые Seed

- `планирование`
- `долговременная память`
- `оркестрация агентов и рабочих процессов`
- `инфраструктура выполнения внешних эффектов`
- `инфраструктура получения evidence`
- `аналитика процессов`

## Компоненты

- `aset.context` `0.1-rc1` — `sha256:450cac15f64c2b3ed3f7c6399c1a456da0c84faf2dcdb911075bd03219e1cd36`
- `aset.core` `0.1-rc1` — `sha256:10a14bd8f18a51c48b56d0b8cbfc90fa862239eae5d47dbc68b8b39e890c289b`
- `aset.model-gateway` `0.1-rc1` — `sha256:f527277f95a3be9197eb92c9d441bf412ee6bd7caf16cfdd7880ccc7602f5e05`
- `aset.master` `0.1-rc1` — `sha256:c36f06a1a60fbb4f85244674a875e599a222302de449c77198bb71454d2ed4db`
- `aset.memory` `0.1-rc1` — `sha256:fe4c5a7e6ad4dfe7dc43ee988fc82b1214f034b2a9e81c5fe07b3abfab3d9d67`
- `aset.monade` `0.1-rc1` — `sha256:e4dac2a626959053d22f7f3941af369595ef2c7a5d81b7ab1df816366860836c`
- `aset.protocol` `0.1-rc1` — `sha256:ec4ec84b6aa045946f9383b0601ad919718d2253454f36b3e0a8f59afa192662`

## Gates

- `GATE-CONTEXT-PROJECT` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-EXPECT-ADMIT` — producer `aset.master`, authority `aset.core`, schema `aset.protocol`
- `GATE-EXEC-BIND` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-DISPATCH` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-OBSERVE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-EVIDENCE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-ACCEPT` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-RETRY` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-COMPENSATE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-TASK-CLOSE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-MEM-MUTATE` — producer `aset.memory`, authority `aset.core`, schema `aset.protocol`

## Рабочий процесс

1. Memory projection
1. Master PlanProposal + ExpectedChangePatch
1. Expectation resolution/permit/gate
1. Execution OperationalBinding
1. Execution resolution/permit/dispatch gate
1. Worker observation
1. Acceptance evidence/verdict/gate
1. Memory/Master feedback
