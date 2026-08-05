[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET — открытая, технологически нейтральная спецификация Authority-Signed Evidence Trails для модельной проверки соответствия и проверяемой ответственности в гетерогенных социотехнических системах.

## Что определяет ASET

ASET определяется машиночитаемым каноном, нормативными схемами, условиями действительности, инвариантами, семантикой переходов и корпусом conformance. Ни одна реализация, язык, хранилище, checker или deployment profile не имеет семантического приоритета.

- Машинный канон: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Идентичность пакета канона: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Формальная проекция: [`seed/canonical/formal/`](seed/canonical/formal/)
- Корпус соответствия: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Каноны компонентов: [`aset/README.md`](aset/README.md)

## Проверка реализаций моделью

Независимые реализации проверяются как black box через `ASET-IMPLEMENTATION-CONFORMANCE-V1`. Реализация возвращает наблюдаемый результат, а внешний runner потребляет закреплённый пакет канона и формирует verdict.

```text
python tools/run_external_conformance.py   --canon-root /path/to/ASET   --adapter "/path/to/implementation-adapter"
```

Хранилище, долговечность, конкурентность, recovery, consensus, сеть и custody ключей относятся к implementation profiles и не определяют Seed.

## Реализации

Реализации поддерживаются отдельно от спецификации. Минимальный non-normative учебный профиль Python + SQLite предназначен для отдельного репозитория `aset-python-sqlite`. Python и SQLite не становятся частью определения ASET.

## Лицензия и права

ASET независимо создан **Dzmitry Prychyna**, публично известным как **Attractor Set**. Проект распространяется по Apache License 2.0. Лицензирование не передаёт авторство или право собственности. См. [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) и [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
