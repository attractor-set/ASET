[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET — открытая технологически нейтральная спецификация Authority-Signed Evidence Trails. Её Seed является минимальным локальным ядром признания разрешения.

```text
UNKNOWN | ALLOW | BLOCK
```

Точно связанный эффект разрешает только одна уникальная действительная, локально авторизованная запись `ALLOW`. Отсутствие действительной терминальной записи или конфликт между действительными терминальными записями даёт `UNKNOWN`; явный запрет — `BLOCK`. Недействительный или неавторитетный материал не может переопределить иначе уникальную действительную терминальную запись. Evidence, выход AI и удалённый outcome сами по себе не создают локальную Authority.

Repository boundary records: [EXTRACTION.md](EXTRACTION.md), [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md), [EXTENSIONS.md](EXTENSIONS.md).

Background IP: [BACKGROUND_IP_SCHEDULE.md](BACKGROUND_IP_SCHEDULE.md).
