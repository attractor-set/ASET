[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET — открытая технологически нейтральная спецификация минимального ядра локального распознавания разрешений в границах Authority. Здесь *seeded* означает, что допустимость берёт начало от явно признанной привязки Authority; Seed не требует конкретного механизма криптографической подписи.

```text
UNKNOWN | ALLOW | BLOCK
```

Только одна уникальная действительная и точно связанная запись `ALLOW`, признанная локальной Authority, разрешает связанный эффект. Отсутствие или конфликт действительного терминального материала даёт `UNKNOWN`; явный запрет — `BLOCK`. Внешний материал сам по себе не создаёт локальную Authority.

## Эталонные артефакты

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — ненормативное эталонное расширение.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — ненормативная эталонная реализация.

Нормативный источник: [канон Seed](seed/canonical/README.md).
