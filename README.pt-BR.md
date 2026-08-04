# ASET

O ASET é um projeto no qual a especificação precede a implementação
e define o comportamento admissível.

## Estado do repositório

- O ASET Seed 0.1-rc11 é preservado como versão histórica imutável.
- O cânone legível por máquina da próxima versão do Seed está
  em desenvolvimento.
- As edições em russo, inglês e português do Brasil são geradas
  diretamente a partir do mesmo modelo canônico.
- A implementação de referência permanece candidata.
- O estado de produção permanece `HOLD`.

## Ordem normativa

Para versões posteriores à migração canônica:

1. modelo semântico legível por máquina;
2. restrições e invariantes legíveis por máquina;
3. edições oficiais geradas em língua natural;
4. materiais explicativos.

Uma versão congelada não pode ser alterada retroativamente.

## Línguas

- [Русский](README.ru.md)
- [English](README.md)
- Português do Brasil

## Diretórios principais

- `seed/releases/` — versões imutáveis do Seed;
- `seed/canonical/` — trabalho canônico da próxima versão;
- `docs/generated/` — edições geradas;
- `tools/` — ferramentas de validação e publicação;
- `.github/workflows/` — verificações de integração contínua.

## Limite das garantias

O congelamento da documentação não implica prontidão para produção,
verificação criptográfica implantada, armazenamento concorrente
durável, consenso distribuído ou certificação por terceira parte.
