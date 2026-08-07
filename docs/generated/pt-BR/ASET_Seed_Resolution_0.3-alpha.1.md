# Núcleo Mínimo de Resolução ASET Seed 0.3 alpha 1

**Versão:** `0.3.0-alpha.1`

**Status:** `MINIMAL_STRONG_CORE_ALPHA`

**SHA-256 do modelo canônico:** `sha256:5bbdfefe35a0adf83fd5e5dd86475a4f57ae92d4f9b9c06a7d530faf2e484396`

> Esta edição é derivada do cânone legível por máquina.

## Garantias

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Conceitos

### vinculação de resolução (`ResolutionBinding`)

A vinculação exata de contexto, raiz de estado, questão, época de política e escopo à qual uma resolução se aplica.

Identificador: `seed.resolution_binding`

### solicitação de resolução (`ResolutionRequest`)

Um identificador novo vinculado a uma vinculação exata de resolução e a uma Authority inicial reconhecida localmente.

Identificador: `seed.resolution_request`

### resolução (`Resolution`)

O valor derivado UNKNOWN ou o valor terminal ALLOW ou BLOCK.

Identificador: `seed.resolution_value`

### Authority local (`LocalAuthority`)

Uma Authority explicitamente reconhecida por um Context para uma vinculação exata e uma época de política.

Identificador: `seed.local_authority`

### prova de Authority (`AuthorityProof`)

Uma cadeia localmente enraizada, exatamente vinculada, acíclica e não expansiva de concessões explícitas de Authority.

Identificador: `seed.authority_proof`

### referência de evidência (`EvidenceReference`)

Uma entrada não autoritativa endereçada por conteúdo, citada como base de um registro terminal.

Identificador: `seed.evidence_reference`

### registro de resolução (`ResolutionRecord`)

Um registro terminal imutável e endereçado por conteúdo, ALLOW ou BLOCK, com vinculação exata e prova de Authority.

Identificador: `seed.resolution_record`

### compromisso de reconsideração (`ReconsiderationCommitment`)

Um compromisso imutável e endereçado por conteúdo de uma nova solicitação com um ResolutionRecord terminal previamente reconhecido; a solicitação ou o registro predecessor não precisa permanecer fisicamente retido pela implementação. O reconhecimento pode ser estabelecido por material atualmente retido ou por prova externa validada de conjunto autenticado/acumulador.

Identificador: `seed.reconsideration_commitment`

## Requisitos

### `ASET-SEED-REQ-001`

ResolutionBinding DEVE conter valores exatos de context_id, state_root, question_digest, policy_epoch e scope, além de um digest canônico da vinculação.

Modalidade: `MUST`

Predicado: `binding_exact`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-002`

Toda ResolutionRequest DEVE usar um resolution_id novo e vincular uma ResolutionBinding exata.

Modalidade: `MUST`

Predicado: `request_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-003`

A Resolution derivada DEVE ser UNKNOWN, ALLOW ou BLOCK; somente ALLOW e BLOCK são valores terminais armazenados.

Modalidade: `MUST`

Predicado: `resolution_domain`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-004`

Um efeito exatamente vinculado DEVE ser permitido se, e somente se, o único ResolutionRecord terminal válido for ALLOW.

Modalidade: `MUST`

Predicado: `allow_only`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-005`

UNKNOWN e BLOCK DEVEM proibir o efeito; ausência, invalidade, ambiguidade ou erro de verificação DEVEM resultar em UNKNOWN, nunca ALLOW.

Modalidade: `MUST`

Predicado: `fail_closed`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-006`

Um registro terminal DEVE estar enraizado em uma Authority explicitamente reconhecida pelo Context local para a vinculação exata e a época de política.

Modalidade: `MUST`

Predicado: `local_authority`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-007`

Toda prova de Authority delegada DEVE ser explícita, acíclica, exatamente vinculada e não expansiva.

Modalidade: `MUST`

Predicado: `proof_attenuating`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-008`

Evidence, resultados de verificação, saídas de AI, resultados de consenso e outcomes remotos NÃO DEVEM, por si só, criar ALLOW ou Authority local.

Modalidade: `MUST`

Predicado: `inputs_non_authoritative`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-009`

No máximo um registro terminal válido PODE existir para um resolution_id; registros terminais conflitantes DEVEM falhar de modo fechado como UNKNOWN.

Modalidade: `MAY`

Predicado: `terminal_unique`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-010`

Um ResolutionRecord terminal DEVE ser imutável e endereçado por conteúdo; uma repetição exata PODE ser idempotente, mas a substituição é proibida.

Modalidade: `MAY`

Predicado: `record_immutable`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-011`

A reconsideração DEVE criar um resolution_id novo e portar um compromisso imutável e endereçado por conteúdo com um ResolutionRecord terminal previamente reconhecido; a solicitação ou o registro predecessor não precisa permanecer fisicamente retido.

Modalidade: `MUST`

Predicado: `reconsider_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-012`

Implementações e extensões DEVEM ser verificadas por semântica observável e NÃO DEVEM ter precedência normativa.

Modalidade: `MUST`

Predicado: `implementation_neutral`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

## Invariantes

- `SEED-INV-001` — Toda resolução derivada válida é UNKNOWN, ALLOW ou BLOCK.
- `SEED-INV-002` — A permissão do efeito é verdadeira se, e somente se, o único registro terminal válido for ALLOW.
- `SEED-INV-003` — UNKNOWN e BLOCK nunca permitem um efeito.
- `SEED-INV-004` — Toda solicitação e registro terminal preservam um único digest exato de vinculação.
- `SEED-INV-005` — Todo registro terminal válido está enraizado em uma vinculação de Authority local.
- `SEED-INV-006` — Toda prova de Authority delegada é exatamente vinculada, acíclica e não expansiva.
- `SEED-INV-007` — Evidence e declarações externas são entradas não autoritativas.
- `SEED-INV-008` — Existe no máximo um registro terminal válido para um resolution_id.
- `SEED-INV-009` — Material terminal conflitante ou inválido resulta em UNKNOWN e nunca ALLOW.
- `SEED-INV-010` — Registros de resolução são append-only, imutáveis e endereçados por conteúdo.
- `SEED-INV-011` — Somente transições reconhecidas do Seed podem alterar o armazenamento canônico; um candidato inválido ou não reconhecido não é uma transição do Seed.
- `SEED-INV-012` — A reconsideração usa um resolution_id novo vinculado por um compromisso imutável e endereçado por conteúdo a um ResolutionRecord terminal previamente reconhecido; a retenção do objeto predecessor não é obrigatória.

## Transições

### `SEED-TX-001` — `REGISTER_REQUEST`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-register-request.schema.json`
- `authority_rule`: The initial Authority binding must be locally rooted and exactly match the request binding.
- `binding_rule`: The request contains one canonical exact binding and a fresh resolution_id. For reconsideration, previous_terminal_record_digest must be a recognized immutable terminal-record commitment; predecessor object presence in retained storage is not required.
- `created_artifacts`: `ResolutionRequest`

### `SEED-TX-002` — `SUBMIT_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-submit-resolution.schema.json`
- `authority_rule`: The record Authority must be the local root Authority or be justified by a valid exact-binding Authority proof.
- `binding_rule`: The record request_digest and binding_digest must exactly match the registered request.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `EVALUATE_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/operation.schema.json`
- `authority_rule`: Evaluation creates no Authority and accepts no external statement as a resolution.
- `binding_rule`: Evaluation is performed for one registered resolution_id and fails closed on missing, invalid or conflicting terminal material.
- `created_artifacts`: `ResolutionEvaluation`

## Limite da implementação

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `policy evaluation language`, `evidence acquisition`, `orchestration semantics`, `enforcement mechanism`, `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `federation topology`, `AI model`, `artifact retention`, `retention, pruning, archiving and compaction of superseded request/record material`, `terminal-commitment accumulator construction`, `accumulator membership/update witness retention`
