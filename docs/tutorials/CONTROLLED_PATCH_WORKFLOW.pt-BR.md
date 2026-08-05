[English](CONTROLLED_PATCH_WORKFLOW.md) · [Русский](CONTROLLED_PATCH_WORKFLOW.ru.md) · [Português do Brasil](CONTROLLED_PATCH_WORKFLOW.pt-BR.md)

# Exemplo completo: patch controlado por um agente de IA

Este exemplo não é normativo. Ele explica um uso completo das distinções existentes do ASET e aponta para o cânone legível por máquina; ele não cria novos campos de documentos nem novas regras de transição.

## Cenário

Uma organização deseja permitir que um agente de IA proponha um patch de repositório. A alteração do repositório externo somente pode ocorrer após uma decisão específica de autoridade, um Permit de uso único e uma travessia atômica de gate. A conclusão bem-sucedida de um comando ainda não constitui um Outcome aceito.

## Sequência

1. **Proposal.** O agente produz uma proposta com o patch pretendido e o contexto-alvo exato. A Proposal expressa uma mudança solicitada e não possui autoridade.
2. **Resolution.** A autoridade relevante avalia a Proposal exata no contexto atual e retorna uma Resolution permitida ou proibida. A Resolution não é uma credencial reutilizável.
3. **Permit.** Uma Resolution permitida pode fundamentar um Permit vinculado ao digest exato do documento, ao contexto, ao gate, à travessia e à identidade do ator ou da execução. O Permit autoriza somente uma travessia imediata.
4. **Travessia e Receipt.** O gate valida o Permit e o contexto, aplica atomicamente o patch canônico, consome o Permit e emite um Receipt. A repetição da mesma travessia retorna o mesmo resultado; o Permit não autoriza outra travessia.
5. **Execution Intent.** A autorização para incluir uma mudança esperada no contexto é distinta da autorização para produzir um efeito externo. Uma decisão de execução e um Permit separados são necessários antes do despacho da operação do repositório.
6. **Observation.** O worker informa o que foi observado após a tentativa. Uma Observation não é Evidence e não prova que o resultado pretendido ocorreu.
7. **Evidence e Verification.** A Evidence admitida é avaliada segundo critérios explícitos de aceitação. A Verification classifica o resultado; falha do verificador ou incerteza não pode fundamentar um Outcome bem-sucedido.
8. **Outcome.** O Context relevante reconhece localmente um Outcome somente a partir de uma Verification válida. Outros Contexts preservam suas próprias autoridades e regras de reconhecimento.

## Por que as distinções importam

```text
Proposal != Resolution != Permit != Receipt
Intent != efeito externo
Observation != Evidence != Verification != Outcome
```

Essas separações impedem que uma sugestão do modelo, uma autorização expirada, um código de saída ou um relatório não verificado se transforme silenciosamente em estado autoritativo.

## Fontes legíveis por máquina

- Seed model: [`../../seed/canonical/source/seed-model.json`](../../seed/canonical/source/seed-model.json)
- Conformance cases: [`../../seed/canonical/conformance/`](../../seed/canonical/conformance/)
- Formal projection: [`../../seed/canonical/formal/`](../../seed/canonical/formal/)
- Component system model: [`../../aset/system/canonical/source/system-composition-model.json`](../../aset/system/canonical/source/system-composition-model.json)
- External implementation protocol: [`../../seed/canonical/conformance/implementation-conformance-protocol.json`](../../seed/canonical/conformance/implementation-conformance-protocol.json)

Para comportamento executável, use o corpus de conformance em vez de transformar este exemplo em um contrato de implementação independente.
