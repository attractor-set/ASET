# Quadro de Propriedade Intelectual Preexistente do ASET

**Status do documento:** inventário probatório público
**Versão do quadro:** 1.0
**Data de vigência:** 2026-08-05
**Perfil jurisdicional:** Brasil (`BR`)
**Repositório:** `https://github.com/attractor-set/ASET`
**Commit de referência:** `f22c67569374550418818bbbdf1a59e96264113d`
**Manifesto de referência:** `MANIFEST.json`
**SHA-256 do manifesto de referência:** `sha256:e127ae646d5bc7368ac1e42d6a657b5d2bbf6e2f99590d9345dfb00f704c585a`

Idiomas: [English](BACKGROUND_IP_SCHEDULE.md) · [Русский](BACKGROUND_IP_SCHEDULE.ru.md) · Português do Brasil

## 1. Finalidade e natureza jurídica

Este Quadro identifica os ativos intelectuais do ASET existentes antes de futuros vínculos de
emprego, investimento, universidade, fomento, prestação de serviços ou desenvolvimento
comercial. Ele estabelece uma fronteira pública e reproduzível entre a propriedade intelectual
preexistente do ASET e eventual propriedade intelectual resultante de instrumento posterior.

Este documento é um inventário probatório. Não constitui cessão, registro de programa de
computador, registro de marca, parecer jurídico ou decisão definitiva sobre titularidade. O
instrumento específico de uma transação prevalece quando aplicável.

## 2. Criador, pseudônimo público e titular atual

- **Criador e atual titular reivindicado dos direitos patrimoniais:** Dzmitry Prychyna.
- **Pseudônimo público e identidade do projeto:** Attractor Set.
- **Limite de personalidade jurídica:** Attractor Set é pseudônimo utilizado por Dzmitry
  Prychyna. Não é identificado por este Quadro como pessoa jurídica distinta nem como titular
  autônomo.
- **Futura sociedade:** nenhuma empresa, laboratório, universidade ou investidor recebe direitos
  sobre a PI preexistente apenas por participar, financiar ou utilizar o ASET. Qualquer cessão
  exige instrumento escrito expresso.

## 3. Declaração de criação independente

Dzmitry Prychyna declara, segundo seu melhor conhecimento, que os ativos relacionados neste
Quadro foram:

- concebidos e desenvolvidos por iniciativa própria;
- desenvolvidos fora do escopo de suas atribuições profissionais, sem encomenda, direção,
  financiamento, supervisão ou participação do empregador atual;
- desenvolvidos com computador, contas, armazenamento, ferramentas, tempo e demais recursos
  próprios;
- desenvolvidos sem uso não autorizado de código-fonte, dados, credenciais, infraestrutura,
  informações tecnológicas confidenciais, segredos industriais ou segredos de negócio de
  terceiros;
- não produzidos como entrega de cliente, projeto de pesquisa encomendado, bolsa, estágio ou
  obrigação estatutária.

A documentação comprobatória confidencial deve ser mantida fora do repositório público.

## 4. Referência técnica reproduzível

A fronteira técnica exata é definida pelo commit Git e pelo `MANIFEST.json` indicados acima. O
commit é a identidade principal. O manifesto nesse commit registra os arquivos e os SHA-256
existentes antes da inclusão deste Quadro.

Arquivos criados depois do commit de referência não integram automaticamente a PI preexistente
desta versão. Exigem alteração versionada do Quadro ou classificação contratual separada.

## 5. Inventário da propriedade intelectual preexistente

### BI-001 — ASET Seed

Especificações, cânone de máquina, terminologia, schemas, modelos formais, casos de conformidade,
releases fixadas, edições geradas, runtime limitado e materiais de assurance.

Caminhos principais: `seed/`, `src/aset_seed/`, `docs/generated/`, `docs/runtime/`.

### BI-002 — Sistema ASET completo e cânones de componentes

Modelos-fonte preservados, System Composition, Context, Core, Monade, Memory, Master, Model
Gateway, Protocol, pontes compartilhadas e pacotes de assurance.

Caminhos principais: `aset/source/`, `aset/system/`, `aset/components/`, `aset/shared/`.

### BI-003 — Implementações de referência e ferramentas executáveis

Referência Python do caminho crítico semântico, runtime limitado, interfaces de linha de comando
e ferramentas executáveis existentes no commit de referência.

Caminhos principais: `src/aset_reference/`, `src/aset_seed/`, `tools/`.

### BI-004 — Assurance, conformidade e verificação formal

Vetores de teste, testes, projeções formais, validadores, gates de release, construção
determinística, auditorias black-box, suítes adversariais e mecanismos de rastreabilidade.

Caminhos principais: `tests/`, `test-vectors/`, `audit/`, `tools/` e diretórios de assurance.

### BI-005 — Documentação e expressão autoral

Descrições de arquitetura, especificações, diagramas, exemplos, documentos de governança,
terminologia e seleção e organização originais dos materiais.

Caminhos principais: `docs/` e documentação Markdown ativa na raiz.

### BI-006 — Identidade do projeto e metadados de release

Identidade do repositório, convenções de release, metadados, manifestos, citação e registros de
status existentes no commit de referência.

### BI-007 — Nomes do ASET e goodwill associado

Nome ASET, nomes dos componentes, identificadores de release e identidade pública Attractor Set,
sujeitos ao direito marcário e a eventual registro futuro. Não se reivindica exclusividade sobre
termos genéricos, descritivos ou de terceiros.

### BI-008 — Know-how técnico específico do ASET

Know-how preexistente relativo à semântica canônica de accountability, transições vinculadas à
autoridade, conformidade, recovery, replay, perfis de composição e estratégia PostgreSQL/Rust.
Ideias abstratas não são tratadas como expressão autoral protegida apenas por constarem neste
Quadro; know-how confidencial exige controles e contratos.

## 6. Exclusões e licença aberta

Este Quadro não reivindica titularidade sobre software, padrões, publicações, marcas ou projetos
de terceiros; contribuições independentes não cedidas ou licenciadas; ideias e métodos genéricos
como tais; PI resultante de instrumento posterior; documentos pessoais confidenciais; nem ativos
criados depois do commit de referência sem classificação posterior.

A Apache License 2.0 permanece inalterada. A licença pública concede permissões de uso; ela não
transfere, por si só, autoria ou titularidade da PI preexistente.

## 7. Perfil jurídico-operacional brasileiro

Para fins brasileiros, este Quadro separa:

- `autor`: a pessoa natural criadora;
- `titular dos direitos patrimoniais`: a pessoa natural ou jurídica que detém os direitos
  econômicos;
- `pseudônimo`: identidade pública que não cria pessoa jurídica distinta.

Na data de vigência, Dzmitry Prychyna é declarado autor e titular atual; Attractor Set é seu
pseudônimo.

A proteção do programa de computador independe de registro, mas versões suficientemente estáveis
podem ser registradas no INPI para reforço probatório. A futura transferência a uma sociedade
brasileira exige instrumento de cessão. Em parceria com ICT, este Quadro deve integrar o acordo
como anexo de `Propriedade Intelectual Preexistente`, enquanto a titularidade e exploração das
criações resultantes devem ser definidas separadamente no instrumento de parceria.

Referências jurídicas principais:

- Lei nº 9.609/1998, especialmente arts. 2º a 4º;
- Lei nº 9.610/1998, especialmente arts. 18 e 22;
- Lei nº 10.973/2004, especialmente art. 9º;
- Decreto nº 9.283/2018, especialmente art. 37;
- procedimentos vigentes do INPI para registro de programa de computador.

Este Quadro deve ser revisto por advogado brasileiro antes de investimento, cessão, registro,
APPD&I ou contrato de comercialização específico.

## 8. Uso em empresa, laboratório e parceria universitária

Todo instrumento posterior deve:

1. incorporar este Quadro e o commit exato de referência;
2. reconhecer a PI preexistente de Dzmitry Prychyna até cessão expressa;
3. definir separadamente a PI resultante do projeto;
4. disciplinar publicações, confidencialidade, licenciamento e comercialização;
5. identificar contribuições e respectivos autores ou titulares;
6. excluir cessão implícita da PI preexistente;
7. exigir nova versão do Quadro para reclassificação intencional de ativos.

## 9. Alterações e preservação

Cada alteração deve receber nova versão, preservar as anteriores, identificar novo commit de
corte, descrever inclusões ou reclassificações e passar pelo production gate. Versões anteriores
não podem ser reescritas silenciosamente.

Consulte [`governance/ip/README.md`](governance/ip/README.md) para o inventário legível por
máquina e os procedimentos de verificação.
