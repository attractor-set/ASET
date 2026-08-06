[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET — открытая технологически нейтральная спецификация. Её Seed определяет проверяемое и ограниченное полномочиями разрешение точного нормативного вопроса из `UNKNOWN` в `ACCEPT` или `DENY`.

`UNKNOWN` не разрешает эффект и не подменяется `DENY`. Неразрешённый вопрос может остаться `UNKNOWN` и перейти следующей явно уполномоченной Resolution Authority. Вложенность контекстов или членство в федерации сами по себе полномочие не создают.

Активный машинный канон находится в [`seed/canonical/`](seed/canonical/). Исполнение, журналы попыток, Monade, Master, память, топология федерации, consensus и хранение принадлежат независимым расширениям и реализациям.

Миграция с rc12 намеренно несовместима: [`seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md`](seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md).

## Исторические расширения и пример

Текущие component canons являются историческими источниками миграции до их выделения: [`aset/README.md`](aset/README.md). Ненормативный пример управляемого patch: [`docs/tutorials/CONTROLLED_PATCH_WORKFLOW.ru.md`](docs/tutorials/CONTROLLED_PATCH_WORKFLOW.ru.md).

Ненормативная reference-реализация не имеет семантического приоритета: [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite). Происхождение background IP: [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
