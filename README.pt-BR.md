[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

**ASET — Authority-Seeded Evidence Trail.**

ASET é uma especificação aberta e neutra de implementação para um **Seed semântico mínimo e interpretável por máquina**: um recipiente semântico legível por máquina, implementável de forma independente e verificável, cujo núcleo operacional é o reconhecimento de resolução no escopo da Authority local. Aqui, *seeded* significa tanto que a admissibilidade se origina de um vínculo de Authority explicitamente reconhecido quanto que a mesma forma pública pode transportar semântica produzida independentemente sem conceder autoridade de reconhecimento ao produtor.

```text
UNKNOWN | ALLOW | BLOCK
```

Somente um registro `ALLOW` único, válido, exatamente vinculado e reconhecido pela Authority local permite o efeito vinculado. A ausência ou o conflito de material terminal válido resulta em `UNKNOWN`; proibição explícita é `BLOCK`. Material externo não cria Authority local por si só.

## Por que Seed

O Seed não prescreve uma arquitetura de aplicação nem um algoritmo de evolução. Ele é a forma pública mínima na qual o significado normativo permanece legível por máquina, explícito o bastante para interpretação independente, implementável de forma independente e verificável externamente. Novas formas candidatas podem ser descobertas por qualquer mecanismo externo; produzir, selecionar ou verificar um candidato não concede Authority nem precedência de reconhecimento a esse mecanismo.

Assim, o ASET padroniza a **fronteira pública da evolução**, não um substrato de busca privilegiado. Veja [Role of ASET Seed](docs/architecture/SEED_ROLE.md) e [Evolution boundary](docs/architecture/EVOLUTION_BOUNDARY.md).

## Projetos downstream diretos

- [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) — extensão normativa e neutra de implementação do ASET Seed para reconhecimento entre Contexts.
- [ASET Python SQLite](https://github.com/attractor-set/aset-python-sqlite) — implementação de referência não normativa do Seed.

Somente relações downstream diretas são listadas aqui. Descendentes transitivos são descobertos por meio de seus projetos-pai imediatos.

Fonte normativa: [cânone Seed](seed/canonical/README.md).

## Padrão de compatibilidade

Releases publicados do Seed podem funcionar como padrões de compatibilidade imutáveis e versionados para implementações independentes. O primeiro baseline declarado é `seed-0.3.0-alpha.2`. A conformidade é avaliada pelo runner externo do ASET contra a identidade exata do release, o canonical package e todos os casos obrigatórios.

Veja [ASET Seed Compatibility Standard](standards/seed-compatibility/README.md).
