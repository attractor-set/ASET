[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET é uma especificação aberta e neutra de implementação para um núcleo mínimo de reconhecimento de resolução no escopo da Authority local. Aqui, *seeded* significa que a admissibilidade se origina de um vínculo de Authority explicitamente reconhecido; o Seed não exige um mecanismo específico de assinatura criptográfica.

```text
UNKNOWN | ALLOW | BLOCK
```

Somente um registro `ALLOW` único, válido, exatamente vinculado e reconhecido pela Authority local permite o efeito vinculado. A ausência ou o conflito de material terminal válido resulta em `UNKNOWN`; proibição explícita é `BLOCK`. Material externo não cria Authority local por si só.

## Artefatos de referência

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — extensão de referência não normativa.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — implementação de referência não normativa.

Fonte normativa: [cânone Seed](seed/canonical/README.md).

Background IP: [BACKGROUND_IP_SCHEDULE.md](BACKGROUND_IP_SCHEDULE.md).
