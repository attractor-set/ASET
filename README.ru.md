
# ASET

ASET — проект, в котором спецификация предшествует реализации и определяет её допустимую семантику.

## Стабильная спецификация

Текущая стабильная документация ASET Seed — **0.1-rc11**. Релиз сохранён как неизменяемый пакет и как побайтно точное развёрнутое дерево для чтения непосредственно на GitHub.

- Релиз: [`seed/releases/0.1-rc11/`](seed/releases/0.1-rc11/)
- Спецификация: [`seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md`](seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md)
- Аудит: [`seed/releases/0.1-rc11/expanded/audit/`](seed/releases/0.1-rc11/expanded/audit/)
- Корпус соответствия: [`seed/releases/0.1-rc11/expanded/conformance/`](seed/releases/0.1-rc11/expanded/conformance/)
- Машиночитаемый профиль: [`seed/releases/0.1-rc11/expanded/machine/`](seed/releases/0.1-rc11/expanded/machine/)

## Готовность репозитория

Процесс публикации, проверки, аудита и выпуска документации является эксплуатационно готовым. Каждое изменение `main` должно пройти детерминированную генерацию, проверку схем и семантики, контроль неизменяемого rc11, тесты, статический анализ, сборку воспроизводимого снимка и независимый блэк-бокс аудит документации.

Это утверждение относится к **репозиторию документации**, а не к production-реализации Seed. Статус runtime остаётся `HOLD`, внешний аудит третьей стороной — `PENDING`, а канон rc12 — незамороженный каркас разработки.

См. [`docs/repository/PRODUCTION_READINESS.md`](docs/repository/PRODUCTION_READINESS.md).
