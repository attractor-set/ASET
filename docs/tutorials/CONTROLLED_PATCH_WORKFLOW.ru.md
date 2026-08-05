[English](CONTROLLED_PATCH_WORKFLOW.md) · [Русский](CONTROLLED_PATCH_WORKFLOW.ru.md) · [Português do Brasil](CONTROLLED_PATCH_WORKFLOW.pt-BR.md)

# Сквозной пример: контролируемый patch от AI-агента

Этот пример ненормативен. Он объясняет одно сквозное применение существующих различий ASET и ссылается на машинный канон; он не вводит новых полей документов или правил переходов.

## Сценарий

Организация хочет позволить AI-агенту предложить patch репозитория. Изменение внешнего репозитория допускается только после конкретного решения authority, однократного Permit и атомарного пересечения гейта. Успешное завершение команды ещё не является принятым Outcome.

## Последовательность

1. **Proposal.** Агент формирует предложение с предполагаемым patch и точным целевым контекстом. Proposal выражает запрошенное изменение и не несёт authority.
2. **Resolution.** Соответствующий authority оценивает точный Proposal в текущем контексте и возвращает разрешающее или запрещающее Resolution. Resolution не является многократно используемым credential.
3. **Permit.** Разрешающее Resolution может обосновать один Permit, связанный с точными digest документа, контекстом, гейтом, crossing и actor/execution identity. Permit допускает только одно немедленное пересечение.
4. **Пересечение гейта и Receipt.** Гейт проверяет Permit и контекст, атомарно применяет канонический patch, потребляет Permit и выпускает Receipt. Повтор того же crossing возвращает тот же результат; Permit не может разрешить другое пересечение.
5. **Execution Intent.** Разрешение включить ожидаемое изменение в контекст отличается от разрешения выполнить внешний эффект. До отправки операции репозиторию требуются отдельные execution decision и Permit.
6. **Observation.** Worker сообщает, что наблюдалось после попытки. Observation не является Evidence и не доказывает достижение требуемого результата.
7. **Evidence и Verification.** Допущенное Evidence проверяется по явным критериям приёмки. Verification классифицирует результат; ошибка verifier или неопределённость не могут обосновать успешный Outcome.
8. **Outcome.** Соответствующий Context локально признаёт Outcome только на основании действительного Verification. Другие Context сохраняют собственные authority и правила признания.

## Зачем нужны различия

```text
Proposal != Resolution != Permit != Receipt
Intent != внешний эффект
Observation != Evidence != Verification != Outcome
```

Эти границы не позволяют предложению модели, истёкшему разрешению, exit code команды или непроверенному отчёту незаметно стать авторитетным состоянием.

## Машинные источники

- Seed model: [`../../seed/canonical/source/seed-model.json`](../../seed/canonical/source/seed-model.json)
- Conformance cases: [`../../seed/canonical/conformance/`](../../seed/canonical/conformance/)
- Formal projection: [`../../seed/canonical/formal/`](../../seed/canonical/formal/)
- Component system model: [`../../aset/system/canonical/source/system-composition-model.json`](../../aset/system/canonical/source/system-composition-model.json)
- External implementation protocol: [`../../seed/canonical/conformance/implementation-conformance-protocol.json`](../../seed/canonical/conformance/implementation-conformance-protocol.json)

Для исполняемого поведения используйте conformance corpus, а не превращайте этот пример в самостоятельный implementation contract.
