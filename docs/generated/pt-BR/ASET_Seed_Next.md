# ASET Seed — cânone normativo legível por máquina

**Versão:** `0.1-rc12-development`

**Estado:** `BOOTSTRAP_SCAFFOLD_NOT_RELEASED`

**SHA-256 do modelo canônico:** `sha256:1ebe6babe03edce9595a921e059e3e65bd55112c22ae79dd60e4fdd4a9335c5d`

> Este documento é gerado automaticamente. A edição manual é proibida.

## Estado

`BOOTSTRAP_SCAFFOLD_NOT_RELEASED`

## Conceitos

### contexto (`Context`)

Um espaço de nomes normativo com identidade imutável e endereço resolvível.

Identificador: `seed.context`

### autoridade institucional (`Authority`)

Um poder institucional vigente em um contexto e estado exatos.

Identificador: `seed.authority`

### decisão (`Decision`)

Uma escolha normativa registrada ou uma declaração de prontidão.

Identificador: `seed.decision`

### permissão (`Permit`)

Uma autorização limitada para apresentar o resultado de uma ação específica.

Identificador: `seed.permit`

### intenção de execução (`ExecutionIntent`)

Um uso materializado de uma permissão para uma tentativa específica.

Identificador: `seed.execution_intent`

### observação (`Observation`)

Uma afirmação sobre o resultado de uma ação ou sobre um fato externo.

Identificador: `seed.observation`

### verificação (`Verification`)

Reconhecimento de que uma afirmação passou pelo procedimento de verificação previsto.

Identificador: `seed.verification`

### reconhecimento final (`Outcome`)

O reconhecimento institucional final do resultado de uma ação.

Identificador: `seed.outcome`

## Requisitos

### `SEED-REQ-001`

Cada transição DEVE pertencer a exatamente um contexto.

Modalidade canônica: `MUST`

Predicado: `belong_to_exactly_one_context`

### `SEED-REQ-002`

A verificação DEVE usar uma regra reconhecida pela constituição vigente do espaço de confiança.

Modalidade canônica: `MUST`

Predicado: `use_recognized_policy`

### `SEED-REQ-003`

O reconhecimento final NÃO DEVE ser aceito sem uma cadeia válida desde a decisão até a verificação.

Modalidade canônica: `MUST_NOT`

Predicado: `exist_without_valid_trail`

### `SEED-REQ-004`

Uma transferência de autoridade entre contextos NÃO DEVE ser aceita sem novo reconhecimento local.

Modalidade canônica: `MUST_NOT`

Predicado: `cross_context_without_local_recognition`

### `SEED-DOC-REQ-001`

Cada edição oficial em língua natural DEVE ser gerada de forma determinística a partir do cânone legível por máquina.

Modalidade canônica: `MUST`

Predicado: `derive_from_machine_readable_canon`

### `SEED-DOC-REQ-002`

Um termo estrangeiro desnecessário NÃO DEVE ser usado quando houver termo nativo exato e consolidado; identificadores de protocolo são exceções.

Modalidade canônica: `MUST_NOT`

Predicado: `use_unnecessary_foreign_term`

## Invariantes

- `SEED-INV-001` — Cada transição aceita pertence a exatamente um contexto.
- `SEED-INV-002` — Uma chave de autoridade possui no máximo um titular vigente.
- `SEED-INV-003` — Uma tentativa vinculada a uma permissão nunca é consumida mais de uma vez.
- `SEED-INV-004` — A ancestralidade histórica não constitui vínculo de participação vigente.
- `SEED-INV-005` — Nenhum reconhecimento final existe sem um conjunto efetivo de verificações.
