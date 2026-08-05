# ASET Seed 0.1-rc12 — cânone normativo legível por máquina

**Versão:** `0.1-rc12`

**Estado:** `RC12_RELEASE_CANDIDATE_READY`

**SHA-256 do modelo canônico:** `sha256:4e633a5cfe17872d8edadd51780c01924647a5c80e6a693f1af5d768e36e5faa`

> Este documento é gerado automaticamente a partir do cânone de máquina. A edição manual é proibida.

## Limites de garantia

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Conceitos

### espaço de confiança (`TrustSpace`)

O estado de uma linhagem Genesis com histórico normativo isolado.

Identificador: `seed.trust_space`

### gênese (`Genesis`)

Material inicial imutável que ancora a identidade de um espaço de confiança.

Identificador: `seed.genesis`

### constituição de confiança (`Constitution`)

A política canônica de autoridade, procedimentos e transições admissíveis.

Identificador: `seed.constitution`

### contexto (`Context`)

Um espaço de nomes normativo com ContextID imutável e estado local.

Identificador: `seed.context`

### descritor de contexto (`ContextDescriptor`)

Um registro de protocolo da identidade, pai, endereço, membro e ciclo de vida do contexto.

Identificador: `seed.context_descriptor`

### autoridade institucional (`Authority`)

Um poder institucional vigente em contexto, escopo e estado exatos.

Identificador: `seed.authority`

### vínculo de autoridade (`AuthorityBinding`)

Um registro de protocolo que vincula titular, tipo, escopo, época e proveniência da autoridade.

Identificador: `seed.authority_binding`

### decisão (`Decision`)

Uma escolha normativa registrada ou declaração de prontidão.

Identificador: `seed.decision`

### permissão (`Permit`)

Uma autorização limitada para apresentar o resultado de uma ação específica.

Identificador: `seed.permit`

### intenção de execução (`ExecutionIntent`)

Um uso materializado de uma permissão para uma tentativa específica.

Identificador: `seed.execution_intent`

### comprovante de uso da permissão (`PermitUseReceipt`)

Evidência imutável de que uma tentativa específica da permissão foi consumida.

Identificador: `seed.permit_use_receipt`

### observação (`Observation`)

Uma afirmação sobre resultado de ação ou fato externo vinculada a evidências.

Identificador: `seed.observation`

### verificação (`Verification`)

Reconhecimento de que uma afirmação passou pelo procedimento de verificação previsto.

Identificador: `seed.verification`

### reconhecimento final (`Outcome`)

O reconhecimento institucional final do resultado de uma ação.

Identificador: `seed.outcome`

### transição de estado (`Transition`)

Uma alteração candidata atômica do estado canônico de um contexto.

Identificador: `seed.transition`

### registro de transição (`TransitionRecord`)

Um registro imutável de uma transição aceita, suas causas e artefatos criados.

Identificador: `seed.transition_record`

### comprovante de exportação (`ExportReceipt`)

Um compromisso local da origem transferível a outro contexto como evidência.

Identificador: `seed.export_receipt`

### registro de importação (`ImportRecord`)

Um registro local que aceita evidência externa sem importar automaticamente seu reconhecimento final.

Identificador: `seed.import_record`

### commit local (`LocalCommit`)

Uma transição pré-classificada admissível durante uma partição de rede.

Identificador: `seed.local_commit`

### comprovante de reconciliação (`ReconciliationReceipt`)

Um registro da validação de commits locais, prefixo confirmado e bifurcações detectadas.

Identificador: `seed.reconciliation_receipt`

### aresta de dependência (`DependencyEdge`)

Uma relação direcionada tipada de dependência normativa ou não normativa entre contextos.

Identificador: `seed.dependency_edge`

### registro de retirada de membro (`MembershipWithdrawalRecord`)

Um registro imutável de saída voluntária ou substituição de contexto.

Identificador: `seed.membership_withdrawal_record`

### registro de redefinição de contexto (`ContextRedefinitionRecord`)

Um registro completo da substituição atômica de um conjunto exato de contextos interdependentes.

Identificador: `seed.context_redefinition_record`

### registro de correção (`CorrectionRecord`)

Um registro somente de acréscimo que revoga ou substitui uma verificação antes do resultado final.

Identificador: `seed.correction_record`

### raiz de estado (`StateRoot`)

Um hash com separação de domínio do estado canônico completo do espaço de confiança.

Identificador: `seed.state_root`

### prova de autenticação (`Proof`)

Evidência verificável externamente vinculada a um principal e à transição exata.

Identificador: `seed.proof`

### armazenamento durável de execução (`RuntimeStore`)

Um armazenamento transacional para o estado e o log imutável de tentativas de transição.

Identificador: `seed.runtime_store`

## Requisitos

### `ASET-SEED-REQ-001`

A API pública DEVE aplicar esquemas estritos e falhar de modo fechado.

Modalidade canônica: `MUST`

Predicado: `enforce_strict_schemas_fail_closed`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-002`

TrustSpaceID e ContextID DEVEM ser derivados do material canônico de Genesis.

Modalidade canônica: `MUST`

Predicado: `derive_identity_from_genesis`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-003`

Cada transição aceita DEVE ser atômica e seguida pela validação do estado completo.

Modalidade canônica: `MUST`

Predicado: `commit_atomically_and_validate_state`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-004`

Os escopos de autoridade vigentes para um mesmo contexto/capacidade NÃO DEVEM se sobrepor.

Modalidade canônica: `MUST_NOT`

Predicado: `prevent_active_scope_overlap`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-005`

Os termos da permissão DEVEM vincular a prontidão e a decisão de emissão da permissão.

Modalidade canônica: `MUST`

Predicado: `bind_permit_terms`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-006`

O predicado de sucesso da permissão DEVE corresponder a uma regra vigente da constituição.

Modalidade canônica: `MUST`

Predicado: `resolve_success_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-007`

A política de verificação DEVE ser igual ao predicado de sucesso da permissão.

Modalidade canônica: `MUST`

Predicado: `match_verification_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-008`

O reconhecimento final DEVE agregar o conjunto efetivo completo de verificações PASS.

Modalidade canônica: `MUST`

Predicado: `aggregate_complete_effective_verifications`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-009`

Uma correção DEVE ter como alvo somente uma verificação ainda não finalizada por um resultado.

Modalidade canônica: `MUST`

Predicado: `limit_correction_to_nonfinal_verification`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-010`

Os pais causais DEVEM ser derivados de referências tipadas a artefatos.

Modalidade canônica: `MUST`

Predicado: `derive_causal_parents`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-011`

Transições comuns NÃO DEVEM ser aceitas em um contexto suspenso.

Modalidade canônica: `MUST_NOT`

Predicado: `block_ordinary_transition_in_suspended_context`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-012`

A reconciliação DEVE incluir todos os commits locais conhecidos e preservar evidências de bifurcação.

Modalidade canônica: `MUST`

Predicado: `reconcile_complete_known_commits`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-013`

As duas extremidades de uma dependência normativa DEVEM ser contextos ativos.

Modalidade canônica: `MUST`

Predicado: `require_active_normative_endpoints`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-014`

A retirada autônoma DEVE ser assinada pelo membro e NÃO DEVE deixar um dependente normativo ativo.

Modalidade canônica: `MUST`

Predicado: `protect_normative_dependants_on_withdrawal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-015`

AffectedSiblingSet DEVE ser calculado transitivamente a partir do estado anterior.

Modalidade canônica: `MUST`

Predicado: `compute_affected_sibling_closure`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-016`

O resumo da proposta DEVE vincular a proposta completa incorporada.

Modalidade canônica: `MUST`

Predicado: `bind_full_redefinition_proposal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-017`

Cada membro afetado DEVE autorizar a proposta exata.

Modalidade canônica: `MUST`

Predicado: `require_all_member_authorizations`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-018`

O contexto pai DEVE possuir a autoridade REDEFINE_CONTEXT.

Modalidade canônica: `MUST`

Predicado: `require_parent_redefinition_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-019`

A redefinição DEVE confirmar atomicamente ou deixar o estado inalterado.

Modalidade canônica: `MUST`

Predicado: `commit_redefinition_atomically`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-020`

Os sucessores DEVEM preservar pai, alias, membro e tipo, recebendo um novo ContextID.

Modalidade canônica: `MUST`

Predicado: `preserve_successor_identity_fields`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-021`

As dependências entre irmãos afetados DEVEM ser remapeadas para os sucessores.

Modalidade canônica: `MUST`

Predicado: `remap_affected_dependencies`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-022`

Os registros de governança DEVEM reter a proposta completa e os resumos das provas.

Modalidade canônica: `MUST`

Predicado: `retain_governance_evidence`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-023`

A transferência de autoridade DEVE usar uma cadeia positiva no mesmo contexto e a prontidão do novo titular.

Modalidade canônica: `MUST`

Predicado: `bind_same_context_authority_transfer`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-024`

A cobertura de ramos do núcleo de referência DEVE ser de pelo menos 90 por cento para o congelamento da versão.

Modalidade canônica: `MUST`

Predicado: `meet_branch_coverage_threshold`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-025`

As evidências de cobertura e qualidade da publicação DEVEM estar vinculadas aos bytes exatos de código e documentos.

Modalidade canônica: `MUST`

Predicado: `bind_assurance_to_exact_bytes`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-026`

O congelamento da versão DEVE incluir validação em sala limpa do arquivo determinístico.

Modalidade canônica: `MUST`

Predicado: `perform_clean_room_release_validation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-DOC-001`

As edições oficiais DEVEM ser derivadas deterministicamente do cânone legível por máquina.

Modalidade canônica: `MUST`

Predicado: `derive_editions_from_canon`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

### `ASET-SEED-DOC-002`

Todas as representações DEVEM preservar identificadores semânticos estáveis de requisitos, invariantes e transições.

Modalidade canônica: `MUST`

Predicado: `preserve_semantic_identifiers`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

## Invariantes

- `SEED-INV-001` — TrustSpaceID, Root Genesis e a época zero da constituição são imutáveis.
- `SEED-INV-002` — Existe exatamente um contexto raiz sem pai e a árvore de contextos é acíclica.
- `SEED-INV-003` — Cada ContextID é derivado do identificador do pai e do resumo de Genesis do contexto.
- `SEED-INV-004` — O índice de aliases vigentes corresponde exatamente aos contextos ativos.
- `SEED-INV-005` — Todos os contextos ativos usam a época atual da constituição.
- `SEED-INV-006` — Uma chave de autoridade tem no máximo um titular ativo e os escopos ativos de uma capacidade não se sobrepõem.
- `SEED-INV-007` — Um contexto retirado, substituído ou encerrado não possui autoridade nem permissões ativas.
- `SEED-INV-008` — Cada chave de mapa de artefatos é igual ao identificador interno e refere-se a um contexto existente.
- `SEED-INV-009` — Os termos da permissão estão vinculados exatamente à decisão de emissão, prontidão e política de sucesso reconhecida.
- `SEED-INV-010` — A política de verificação é igual ao predicado de sucesso da permissão e a uma regra ativa da constituição.
- `SEED-INV-011` — A atenuação da permissão é linear e não cria orçamento duplicado de tentativas.
- `SEED-INV-012` — Os índices de tentativas são contíguos, os comprovantes são duráveis e o índice de submission_id é exato.
- `SEED-INV-013` — Cada observação está vinculada ao comprovante, permissão e contexto exatos.
- `SEED-INV-014` — Cada verificação está vinculada à observação, comprovante, permissão e contexto exatos.
- `SEED-INV-015` — Um resultado usa o conjunto efetivo completo de verificações de sua permissão.
- `SEED-INV-016` — Exportação, importação e reconhecimento local preservam proveniência exata entre contextos.
- `SEED-INV-017` — Uma correção tem como alvo somente uma verificação antes do resultado final.
- `SEED-INV-018` — Contagens de transições, ordinais locais, propriedade de artefatos e pais causais derivados são exatos.
- `SEED-INV-019` — Um contexto suspenso permite continuação local somente pela transição dedicada de partição.
- `SEED-INV-020` — A reconciliação inclui todos os commits locais conhecidos e preserva evidências de ramos concorrentes.
- `SEED-INV-021` — As arestas de dependência são únicas, não autorreferentes e possuem extremidades existentes.
- `SEED-INV-022` — As duas extremidades de cada aresta normativa são contextos ativos.
- `SEED-INV-023` — A retirada autônoma não deixa dependente normativo ativo.
- `SEED-INV-024` — AffectedSiblingSet é o fechamento transitivo exato dos irmãos diretos.
- `SEED-INV-025` — A redefinição usa o resumo canônico da proposta completa e o conjunto exato de autorizações dos membros.
- `SEED-INV-026` — A substituição de contextos é atômica, preserva campos de identidade e remapeia dependências exatamente.
- `SEED-INV-027` — Os registros de governança contêm a proposta completa e as evidências de autenticação.
- `SEED-INV-028` — A transferência de autoridade possui uma cadeia de ação completa no mesmo contexto.
- `SEED-INV-029` — As raízes internas dos contextos e a raiz global correspondem exatamente ao estado canônico.

## Transições

### `SEED-TX-001` — `MEMBER_CONTEXT_GENESIS`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-member-context-genesis.schema.json`
- `authorization_rule`: bootstrap predicate or CREATE_MEMBER_CONTEXT
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`

### `SEED-TX-002` — `DECISION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-decision.schema.json`
- `authorization_rule`: self-signed readiness or capability selected by decision kind
- `created_artifacts`: `Decision`

### `SEED-TX-003` — `PERMIT_ISSUE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-issue.schema.json`
- `authorization_rule`: ISSUE_PERMIT
- `created_artifacts`: `Permit`

### `SEED-TX-004` — `PERMIT_ATTENUATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-attenuate.schema.json`
- `authorization_rule`: active parent permit and new-delegate readiness
- `created_artifacts`: `Permit`

### `SEED-TX-005` — `PERMIT_USE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-use.schema.json`
- `authorization_rule`: permit delegate and available attempt
- `created_artifacts`: `ExecutionIntent`, `PermitUseReceipt`

### `SEED-TX-006` — `OBSERVATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-observation.schema.json`
- `authorization_rule`: presenter bound to permit-use receipt
- `created_artifacts`: `Observation`

### `SEED-TX-007` — `VERIFICATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-verification.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `Verification`

### `SEED-TX-008` — `OUTCOME`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-outcome.schema.json`
- `authorization_rule`: CONFIRM_OUTCOME
- `created_artifacts`: `Outcome`

### `SEED-TX-009` — `EXPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-export.schema.json`
- `authorization_rule`: EXPORT
- `created_artifacts`: `ExportReceipt`

### `SEED-TX-010` — `IMPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-import.schema.json`
- `authorization_rule`: IMPORT and local permit-use receipt
- `created_artifacts`: `ImportRecord`, `Observation`

### `SEED-TX-011` — `GUARANTEE_SUSPEND`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-guarantee-suspend.schema.json`
- `authorization_rule`: SUSPEND_GUARANTEE in parent context
- `created_artifacts`: `context guarantee status`

### `SEED-TX-012` — `PARTITION_LOCAL_TRANSITION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-partition-local-transition.schema.json`
- `authorization_rule`: constitution-classified local operation and accepted proof
- `created_artifacts`: `LocalCommit`

### `SEED-TX-013` — `RECONCILE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-reconcile.schema.json`
- `authorization_rule`: RECONCILE
- `created_artifacts`: `ReconciliationReceipt`

### `SEED-TX-014` — `MEMBERSHIP_WITHDRAW`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-membership-withdraw.schema.json`
- `authorization_rule`: member signature and no active normative dependant
- `created_artifacts`: `MembershipWithdrawalRecord`

### `SEED-TX-015` — `CONTEXT_REDEFINE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-redefine.schema.json`
- `authorization_rule`: parent REDEFINE_CONTEXT plus exact member authorizations
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`, `MembershipWithdrawalRecord`, `ContextRedefinitionRecord`

### `SEED-TX-016` — `CONTEXT_TERMINATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-terminate.schema.json`
- `authorization_rule`: TERMINATE_CONTEXT plus PASS TRUST_LINEAGE_LOST verification
- `created_artifacts`: `context lifecycle changes`

### `SEED-TX-017` — `CORRECTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-correction.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `CorrectionRecord`

### `SEED-TX-018` — `AUTHORITY_TRANSFER`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-authority-transfer.schema.json`
- `authorization_rule`: TRANSFER_AUTHORITY plus same-context positive action trail
- `created_artifacts`: `AuthorityBinding`

## Limite de implementação

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `programming language`, `storage backend`, `deployment topology`, `consensus protocol`, `network transport`, `cryptographic provider`, `operational user interface`
