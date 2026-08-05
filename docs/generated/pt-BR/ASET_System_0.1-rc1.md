# ASET System Composition 0.1-rc1

- `status`: `COMPONENT_COMPOSITION_CANDIDATE`
- `canonical_digest`: `sha256:d7a0120c924adef6b6839339ed85db82e153b8fd3e132425f3d236023b8a0dc4`
- `seed_version`: `0.1-rc12`

## Papel do ASET Seed

- `classification`: `MINIMAL_SEMANTIC_NUCLEUS`
- `implementation_neutral`: `True`
- `normative_function`: `Define os conceitos vinculados à autoridade, as condições de validade, os invariantes e a semântica de transições necessários para sistemas compatíveis com o ASET.`
- `composition_rule`: `Sistemas ASET completos e perfis de implementação compatíveis podem usar componentes internos ou externos independentes. Toda transição que reivindique significado autoritativo no ASET, incluindo a autorização de uma mudança significativa de estado, o registro autoritativo de sua execução, sua verificação ou seu reconhecimento como Outcome, deve estar em conformidade com a semântica do Seed.`
- `extension_rule`: `Cânones de componentes e perfis de implementação podem refinar conceitos do Seed e introduzir controles adicionais, mas não devem enfraquecer, fundir ou contornar as distinções e os invariantes do Seed.`
- `claim_boundary`: `O Seed estabelece a validade normativa e a rastreabilidade de transições autoritativas. Por si só, ele não estabelece a verdade factual, a completude ou a correção externa de observações, evidências ou dados de origem.`

### Capacidades não fornecidas pelo Seed

- `planejamento`
- `memória de longo prazo`
- `orquestração de agentes e fluxos de trabalho`
- `infraestrutura de execução de efeitos externos`
- `infraestrutura de aquisição de evidências`
- `análise de processos`

## Componentes

- `aset.context` `0.1-rc1` — `sha256:450cac15f64c2b3ed3f7c6399c1a456da0c84faf2dcdb911075bd03219e1cd36`
- `aset.core` `0.1-rc1` — `sha256:10a14bd8f18a51c48b56d0b8cbfc90fa862239eae5d47dbc68b8b39e890c289b`
- `aset.model-gateway` `0.1-rc1` — `sha256:f527277f95a3be9197eb92c9d441bf412ee6bd7caf16cfdd7880ccc7602f5e05`
- `aset.master` `0.1-rc1` — `sha256:c36f06a1a60fbb4f85244674a875e599a222302de449c77198bb71454d2ed4db`
- `aset.memory` `0.1-rc1` — `sha256:fe4c5a7e6ad4dfe7dc43ee988fc82b1214f034b2a9e81c5fe07b3abfab3d9d67`
- `aset.monade` `0.1-rc1` — `sha256:e4dac2a626959053d22f7f3941af369595ef2c7a5d81b7ab1df816366860836c`
- `aset.protocol` `0.1-rc1` — `sha256:ec4ec84b6aa045946f9383b0601ad919718d2253454f36b3e0a8f59afa192662`

## Gates

- `GATE-CONTEXT-PROJECT` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-EXPECT-ADMIT` — producer `aset.master`, authority `aset.core`, schema `aset.protocol`
- `GATE-EXEC-BIND` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-DISPATCH` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-OBSERVE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-EVIDENCE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-ACCEPT` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-RETRY` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-COMPENSATE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-TASK-CLOSE` — producer `aset.monade`, authority `aset.core`, schema `aset.protocol`
- `GATE-MEM-MUTATE` — producer `aset.memory`, authority `aset.core`, schema `aset.protocol`

## Fluxo de trabalho

1. Memory projection
1. Master PlanProposal + ExpectedChangePatch
1. Expectation resolution/permit/gate
1. Execution OperationalBinding
1. Execution resolution/permit/dispatch gate
1. Worker observation
1. Acceptance evidence/verdict/gate
1. Memory/Master feedback
