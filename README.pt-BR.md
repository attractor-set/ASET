
# ASET

ASET é um projeto orientado pela especificação: a especificação pública antecede e governa as implementações.

## Especificação estável

A documentação estável atual do ASET Seed é a versão **0.1-rc11**. O release é preservado como pacote imutável e como árvore expandida byte a byte para leitura direta no GitHub.

- Release: [`seed/releases/0.1-rc11/`](seed/releases/0.1-rc11/)
- Especificação: [`seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md`](seed/releases/0.1-rc11/expanded/docs/ASET_SEED_SPECIFICATION.md)
- Auditoria: [`seed/releases/0.1-rc11/expanded/audit/`](seed/releases/0.1-rc11/expanded/audit/)
- Conjunto de conformidade: [`seed/releases/0.1-rc11/expanded/conformance/`](seed/releases/0.1-rc11/expanded/conformance/)
- Perfil legível por máquina: [`seed/releases/0.1-rc11/expanded/machine/`](seed/releases/0.1-rc11/expanded/machine/)

## Prontidão do repositório

O processo de publicação, validação, garantia de release e auditoria da documentação está pronto para operação. Toda alteração em `main` deve passar por geração determinística, validação semântica e de esquemas, verificação do release congelado, testes, análise estática, construção de snapshot determinístico e auditoria black-box independente da documentação.

Essa afirmação se aplica ao **repositório de documentação**, não a uma implementação de produção do Seed. O runtime permanece em `HOLD`, a auditoria externa de terceira parte permanece `PENDING` e o cânone rc12 continua sendo um esqueleto de desenvolvimento não publicado.

Consulte [`docs/repository/PRODUCTION_READINESS.md`](docs/repository/PRODUCTION_READINESS.md).
