[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET é uma especificação aberta e neutra quanto à implementação. Seu Seed define a resolução
verificável e limitada por autoridade de uma pergunta normativa exata, de `UNKNOWN` para
`ACCEPT` ou `DENY`.

```text
UNKNOWN --resolução autorizada--> ACCEPT
UNKNOWN --resolução autorizada--> DENY
UNKNOWN --escalonamento explícito--> UNKNOWN
```

`UNKNOWN` nunca autoriza um efeito e não é convertido silenciosamente em `DENY`. A autoridade
não decorre automaticamente da ancestralidade de Context, da participação federativa, da escolha
de implementação ou de uma saída de AI.

## Seed ativo

- Cânone: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Pacote: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Conformidade: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Projeção formal: [`seed/canonical/formal/`](seed/canonical/formal/)
- Estado da versão: [`REPOSITORY_STATUS.json`](REPOSITORY_STATUS.json)

O candidato ativo é `0.2.0-alpha.2`. Alpha 2 altera a fronteira do repositório e de assurance,
mas não a álgebra de resolução introduzida em alpha 1.

## Ecossistema externo

Extensões e implementações são versionadas fora deste repositório e não possuem precedência
semântica.

- Registro de extensões: [`EXTENSIONS.md`](EXTENSIONS.md)
- Registro de implementações: [`IMPLEMENTATIONS.md`](IMPLEMENTATIONS.md)
- Registro de extração: [`EXTRACTION.md`](EXTRACTION.md)

Repositórios publicados:

- [`aset-network-extension`](https://github.com/attractor-set/aset-network-extension)
- [`aset-ai-extension-template`](https://github.com/attractor-set/aset-ai-extension-template)
- [`aset-ai-local-stack`](https://github.com/attractor-set/aset-ai-local-stack)
- [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite)

## Validação

```text
python tools/repository_release_gate.py
```

## Autoria e licença

ASET foi criado de forma independente por **Dzmitry Prychyna**, conhecido publicamente como
**Attractor Set**, e é licenciado sob Apache License 2.0. Consulte [`LICENSE`](LICENSE),
[`NOTICE`](NOTICE) e [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).
