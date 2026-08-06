[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET é uma especificação aberta e neutra quanto à implementação. Seu Seed define a resolução verificável e limitada por autoridade de uma questão normativa exata de `UNKNOWN` para `ACCEPT` ou `DENY`.

`UNKNOWN` não autoriza efeito e não é convertido em `DENY`. Uma questão não resolvida pode permanecer `UNKNOWN` e seguir para a próxima Resolution Authority explicitamente autorizada. A ancestralidade de contexto ou a participação federativa, por si só, não cria autoridade.

O cânone ativo legível por máquina está em [`seed/canonical/`](seed/canonical/). Execução, registros de tentativas, Monade, Master, memória, topologia federativa, consenso e persistência pertencem a extensões e implementações independentes.

A migração a partir de rc12 é intencionalmente incompatível: [`seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md`](seed/canonical/migration/RC12_TO_RESOLUTION_CORE.md).

## Extensões históricas e exemplo

Os component canons atuais são fontes históricas de migração até sua extração: [`aset/README.md`](aset/README.md). O exemplo não normativo de patch controlado está em [`docs/tutorials/CONTROLLED_PATCH_WORKFLOW.pt-BR.md`](docs/tutorials/CONTROLLED_PATCH_WORKFLOW.pt-BR.md).

A implementação de referência não normativa não possui precedência semântica e é [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite). A proveniência de background IP está em [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md).

A primeira extensão federativa publicada separadamente é [`aset-network-extension`](https://github.com/attractor-set/aset-network-extension). O registro não normativo está em [`EXTENSIONS.md`](EXTENSIONS.md).
