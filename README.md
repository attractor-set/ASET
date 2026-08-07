[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET is an open, implementation-neutral specification for Authority-Signed Evidence Trails. Its Seed is a minimal local resolution-recognition kernel.

```text
UNKNOWN | ALLOW | BLOCK
```

Only one unique valid, locally authorized and exact-binding `ALLOW` record permits the bound effect. Missing or conflicting valid terminal state is `UNKNOWN`; explicit prohibition is `BLOCK`. Invalid or non-authoritative material cannot override an otherwise unique valid terminal record. Evidence, AI output and remote outcomes never create local Authority by themselves.

Repository boundary records: [EXTRACTION.md](EXTRACTION.md), [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md), [EXTENSIONS.md](EXTENSIONS.md).

Background IP: [BACKGROUND_IP_SCHEDULE.md](BACKGROUND_IP_SCHEDULE.md).
