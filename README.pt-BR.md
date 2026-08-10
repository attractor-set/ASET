[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET é uma especificação aberta e neutra de implementação para um núcleo mínimo de reconhecimento de resolução no escopo da Authority local. Aqui, *seeded* significa que a admissibilidade se origina de um vínculo de Authority explicitamente reconhecido; o Seed não exige um mecanismo específico de assinatura criptográfica.

```text
UNKNOWN | ALLOW | BLOCK
```

Somente um registro `ALLOW` único, válido, exatamente vinculado e reconhecido pela Authority local permite o efeito vinculado. A ausência ou o conflito de material terminal válido resulta em `UNKNOWN`; proibição explícita é `BLOCK`. Material externo não cria Authority local por si só.

## Projetos downstream diretos

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — extensão normativa e neutra de implementação do ASET Seed para reconhecimento entre Contexts.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — implementação de referência não normativa do Seed.

Somente relações downstream diretas são listadas aqui. Descendentes transitivos são descobertos por meio de seus projetos-pai imediatos.

Fonte normativa: [cânone Seed](seed/canonical/README.md).

## Padrão de compatibilidade

Releases publicados do Seed podem funcionar como padrões de compatibilidade imutáveis e versionados para implementações independentes. O primeiro baseline declarado é `seed-0.3.0-alpha.2`. A conformidade é avaliada pelo runner externo do ASET contra a identidade exata do release, o canonical package e todos os casos obrigatórios.

Veja [ASET Seed Compatibility Standard](standards/seed-compatibility/README.md).
