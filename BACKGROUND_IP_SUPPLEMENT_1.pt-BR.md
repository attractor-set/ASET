# Suplemento 1 ao Inventário de Background IP do ASET

**Status do documento:** suplemento probatório público
**Identificador:** `ASET-BACKGROUND-IP-SUPPLEMENT-1`
**Versão do suplemento:** `1.0`
**Data de vigência:** `2026-08-05`
**Perfil jurisdicional:** Brasil (`BR`)
**Documento principal:** ASET Background IP Schedule 1.0

Idiomas: [English](BACKGROUND_IP_SUPPLEMENT_1.md) · [Русский](BACKGROUND_IP_SUPPLEMENT_1.ru.md) · Português do Brasil

## 1. Finalidade e relação com o Schedule 1.0

Este Suplemento registra ativos do ASET criados, separados ou materialmente reorganizados após
o baseline do ASET Background IP Schedule 1.0 imutável e até os cortes exatos dos repositórios
indicados abaixo. Ele complementa o Schedule 1.0, sem substituí-lo, reescrevê-lo ou reduzi-lo.

O Schedule principal permanece preservado pelo GitHub Release imutável
`aset-background-ip-schedule-v1-2026-08-05` e pelo pacote de evidências
`aset-background-ip-schedule-v1-evidence-r3-2026-08-05.tar.gz`, SHA-256
`3153921cf9546c83113497289b49e4e03e2a5745f073e6dd4bdac1ad1bc81f84`.

Este Suplemento é um inventário probatório. Não é cessão, registro de programa de computador,
registro de marca, parecer jurídico nem decisão sobre titularidade.

## 2. Criador e continuidade da titularidade

- **Criador e atual titular declarado dos direitos patrimoniais:** Dzmitry Prychyna.
- **Pseudônimo público e identidade do projeto:** Attractor Set.
- **Limite jurídico:** Attractor Set é um pseudônimo, não uma pessoa jurídica separada.
- **Continuidade:** até a data de vigência, os ativos suplementados não haviam sido cedidos a
  empresa, laboratório, universidade, investidor ou outra pessoa jurídica.

Dzmitry Prychyna reafirma para os ativos adicionados a declaração de criação independente do
Schedule 1.0: foram desenvolvidos fora de suas atribuições profissionais, sem encomenda,
direção, supervisão, financiamento, equipamentos, informações confidenciais, segredos
industriais ou comerciais de seu empregador atual, e com equipamentos, contas, armazenamento,
ferramentas e tempo próprios.

Os documentos comprobatórios confidenciais permanecem fora do repositório público.

## 3. Cortes técnicos exatos

### 3.1 Repositório da especificação ASET

- Repositório: `https://github.com/attractor-set/ASET`
- Commit de corte: `a122e2f828256501abb645b89046cc866f4466ed`
- Tree de corte: `265640e8e842f6a1f384713cfab5c2acacf040b6`
- SHA-256 de `MANIFEST.json`: `1496fa5ba43b2490af8b3d18b649ae6dadf42f025213773be6be0eb93d5f82c5`
- Quantidade de arquivos no manifest: `654`
- Arquivo-fonte preservado: `ASET-a122e2f-source.zip`
- SHA-256 do arquivo: `fa0c7096bfbca5463911b9566e3e011fd8e150b79cce212c3baa97eeadf41876`
- Digest do canon package: `sha256:026494e546a0504fddd81a16df3c4f4bcc35f308cff6f5d58371b79c91d94562`

### 3.2 Perfil de referência separado Python + SQLite

- Repositório: `https://github.com/attractor-set/aset-python-sqlite`
- Commit de corte: `2038f84b6b5f6a0aed3636c1685d2c1fb79a1ed1`
- Arquivo-fonte preservado: `aset-python-sqlite-2038f84-source.zip`
- SHA-256 do arquivo: `8adb6f9bfdf7c40715b914e1c061d5c23dad83b0dde4e500ef22dfc7441dba39`
- Perfil: `ASET-PYTHON-SQLITE-LEARNING-V1`
- Origem do canon lock: `a122e2f828256501abb645b89046cc866f4466ed`
- Digest no canon lock: `sha256:026494e546a0504fddd81a16df3c4f4bcc35f308cff6f5d58371b79c91d94562`

Para este Suplemento, o commit Git e o arquivo-fonte preservado constituem a identidade técnica
controladora do perfil de referência. O `MANIFEST.json` local desse repositório não é utilizado
como limite probatório controlador.

## 4. Ativos de Background IP adicionados

### BI-S1-001 — Linha ASET Seed 0.1-rc12 neutra quanto à implementação

Canon legível por máquina, schemas, projeções formais, corpus de conformance e canon package
após a separação da semântica normativa de linguagens, mecanismos de armazenamento e perfis de
distribuição específicos.

### BI-S1-002 — Limite externo de conformance de implementação

Protocolo, schemas, corpus model-based e runner externo pelos quais a implementação devolve um
resultado observável e o canon ASET fixado determina o verdict.

### BI-S1-003 — System Composition e assurance de componentes neutros

Canons ativos de sistema e componentes, assurance cases e views geradas após a remoção de
vínculos normativos específicos de Python, SQLite e runtime. Evidências históricas permanecem
preservadas como históricas.

### BI-S1-004 — Implementação separada `aset-python-sqlite`

Perfil educacional/de referência não normativo Python + SQLite, incluindo código-fonte, adapter,
declaração de perfil, canon lock, testes, ferramentas e documentação. No corte, é expressamente
não production-ready e não possui precedência semântica.

### BI-S1-005 — Integração de atualização do canon entre repositórios

Workflow e mecanismo de canon lock que comunicam identidades exatas do canon aos perfis de
implementação. A automação não transfere titularidade nem concede autoridade normativa.

### BI-S1-006 — Documentação e know-how técnico

Documentação autoral, expressão de governança, justificativa da neutralidade tecnológica,
separação dos repositórios, desenho de conformance e seleção e organização originais dos
materiais suplementados. Ideias abstratas, métodos genéricos e materiais de terceiros não são
reivindicados como expressão protegida apenas por constarem do inventário.

Os caminhos exatos constam em
[`governance/ip/background-ip-supplement-1.json`](governance/ip/background-ip-supplement-1.json).

## 5. Exclusões

Este Suplemento não duplica ativos já classificados no Schedule 1.0. Também exclui:

- software, normas, publicações e marcas de terceiros;
- contribuições independentes não cedidas ou licenciadas a Dzmitry Prychyna;
- ideias, métodos e procedimentos genéricos como tais;
- trabalho criado após cada corte de repositório;
- futuras implementações Rust, PostgreSQL ou outras ausentes nos cortes;
- patches de remediação de assurance não integrados e criados após os cortes;
- documentos pessoais, contratuais e trabalhistas confidenciais.

## 6. Limites da licença, das implementações e da futura empresa

As permissões da Apache License 2.0 permanecem inalteradas. O licenciamento público não transfere
por si só autoria ou titularidade.

A especificação ASET e `aset-python-sqlite` são ativos e repositórios distintos. O perfil de
referência não define o ASET. Uma futura implementação Rust/PostgreSQL também será um perfil de
implementação separado, salvo classificação ou cessão expressa em instrumento escrito.

A criação de empresa ou laboratório, o financiamento, a hospedagem de repositório ou o uso do
ASET não transferem direitos automaticamente. Cessão ou licença exclusiva exigem instrumento
escrito separado.

## 7. Perfil contratual brasileiro

Em operações brasileiras, o Schedule 1.0 e este Suplemento devem ser anexados em conjunto como
`Propriedade Intelectual Preexistente`. PI resultante do projeto, melhorias, publicações,
confidencialidade, licenciamento, comercialização e término devem ser tratados separadamente no
instrumento específico ou no `Acordo de Parceria para PD&I`, quando aplicável.

A proteção de programa de computador pela Lei nº 9.609/1998 independe de registro. O registro no
INPI pode, porém, reforçar a segurança probatória de uma versão suficientemente estável. É
necessária revisão jurídica especializada antes de cessão, investimento, parceria universitária,
participação em edital ou comercialização.

## 8. Preservação e suplementos futuros

O Schedule 1.0 e este Suplemento não devem ser silenciosamente reescritos após a publicação.
Qualquer classificação posterior deve usar nova versão ou novo suplemento, identificar novos
cortes exatos, preservar os registros anteriores e passar pelos assurance gates aplicáveis.
