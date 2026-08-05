[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET é uma especificação aberta e neutra em relação à implementação para Authority-Signed Evidence Trails, com conformidade baseada em modelo e responsabilização verificável em sistemas sociotécnicos heterogêneos.

## O que define ASET

ASET é definido pelo cânone legível por máquina, esquemas normativos, condições de validade, invariantes, semântica de transições e corpus de conformidade. Nenhuma implementação, linguagem, base de dados, verificador ou perfil de implantação possui precedência semântica.

- Cânone de máquina: [`seed/canonical/source/seed-model.json`](seed/canonical/source/seed-model.json)
- Identidade do pacote canônico: [`seed/canonical/CANON_PACKAGE.json`](seed/canonical/CANON_PACKAGE.json)
- Projeção formal: [`seed/canonical/formal/`](seed/canonical/formal/)
- Corpus de conformidade: [`seed/canonical/conformance/`](seed/canonical/conformance/)
- Cânones dos componentes: [`aset/README.md`](aset/README.md)

## Conformidade de implementações baseada em modelo

Implementações independentes são testadas como caixas-pretas por `ASET-IMPLEMENTATION-CONFORMANCE-V1`. A implementação devolve resultados observáveis; um runner externo consome um pacote canônico fixado e determina o veredito.

Armazenamento, durabilidade, concorrência, recuperação, consenso, rede e custódia de chaves pertencem aos perfis de implementação e não definem o Seed.

## Implementações

As implementações são mantidas separadamente da especificação. [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite) é a implementação de referência não normativa e o perfil educacional em Python + SQLite. Ela não possui precedência semântica, e Python e SQLite não passam a fazer parte da definição do ASET.

## Licença e direitos

ASET foi criado de forma independente por **Dzmitry Prychyna**, publicamente conhecido como **Attractor Set**. O projeto é licenciado sob Apache License 2.0. A licença não transfere autoria nem titularidade. Consulte [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) e [`BACKGROUND_IP_SCHEDULE.pt-BR.md`](BACKGROUND_IP_SCHEDULE.pt-BR.md).
