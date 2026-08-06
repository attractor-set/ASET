[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET — открытая технологически нейтральная спецификация. Её Seed определяет проверяемое и
ограниченное полномочиями разрешение точного нормативного вопроса из `UNKNOWN` в `ACCEPT` или
`DENY`.

```text
UNKNOWN --уполномоченное разрешение--> ACCEPT
UNKNOWN --уполномоченное разрешение--> DENY
UNKNOWN --явная эскалация-----------> UNKNOWN
```

`UNKNOWN` не разрешает эффект и не подменяется `DENY`. Полномочие не возникает автоматически
из вложенности Context, членства в федерации, выбора реализации или результата AI.

## Активный Seed

- Канон: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Пакет: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Проверка соответствия: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Формальная проекция: [`seed/canonical/formal/`](seed/canonical/formal/)
- Состояние выпуска: [`REPOSITORY_STATUS.json`](REPOSITORY_STATUS.json)

Активный кандидат — `0.2.0-alpha.2`. Alpha 2 изменяет границу репозитория и assurance, но не
алгебру разрешения, введённую в alpha 1.

## Внешняя экосистема

Расширения и реализации версионируются вне этого репозитория и не имеют семантического
приоритета.

- Реестр расширений: [`EXTENSIONS.md`](EXTENSIONS.md)
- Реестр реализаций: [`IMPLEMENTATIONS.md`](IMPLEMENTATIONS.md)
- Запись об извлечении: [`EXTRACTION.md`](EXTRACTION.md)

Опубликованные репозитории:

- [`aset-network-extension`](https://github.com/attractor-set/aset-network-extension)
- [`aset-ai-extension-template`](https://github.com/attractor-set/aset-ai-extension-template)
- [`aset-ai-local-stack`](https://github.com/attractor-set/aset-ai-local-stack)
- [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite)

## Проверка

```text
python tools/repository_release_gate.py
```

## Авторство и лицензия

ASET независимо создан **Dzmitry Prychyna**, публично известным как **Attractor Set**, и
распространяется по Apache License 2.0. См. [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) и
[`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
