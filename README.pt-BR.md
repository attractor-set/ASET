# ASET

ASET é uma especificação aberta e uma implementação de referência para Authority-Signed Evidence Trails, permitindo responsabilização verificável em sistemas sociotécnicos heterogêneos.

A especificação define uma semântica comum de responsabilização para transformações governadas de contexto e execução verificável, e tem autoridade sobre as implementações.

## Linhas de release

**ASET Seed 0.1-rc11** continua sendo o release estável, imutável e auditado. **ASET Seed 0.1-rc12** é o candidato completo do cânone legível por máquina e inclui um runtime instalável para um perfil operacional limitado.

- rc11 congelado: [`seed/releases/0.1-rc11/`](seed/releases/0.1-rc11/)
- Cânone rc12: [`seed/canonical/`](seed/canonical/)
- Especificação rc12 gerada: [`docs/generated/pt-BR/ASET_Seed_0.1-rc12.md`](docs/generated/pt-BR/ASET_Seed_0.1-rc12.md)
- Runtime: [`src/aset_seed/`](src/aset_seed/)
- Perfil de produção: [`docs/runtime/PRODUCTION_PROFILE.md`](docs/runtime/PRODUCTION_PROFILE.md)
- Lista de implantação: [`docs/runtime/DEPLOYMENT_CHECKLIST.md`](docs/runtime/DEPLOYMENT_CHECKLIST.md)

## Limite do candidato rc12

O cânone rc12 contém 27 conceitos, 40 requisitos, 37 invariantes, 18 tipos de transição, 39 JSON Schemas estritos e 55 casos de conformidade vinculados. A superfície semântica rc11 foi migrada 83/83, sem item adiado ou não classificado. As edições em russo, inglês e português brasileiro são geradas de uma única fonte de máquina.

O perfil executável está pronto para produção somente no limite `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`: um host, escritores SQLite serializados, WAL com `synchronous=FULL`, CLI local ou API incorporada, verificação explícita de provas, estado durável e auditoria append-only encadeada por hash. O verificador padrão rejeita todas as transições.

A afirmação exclui consenso distribuído, operação multi-primary, efeitos automáticos de rede ou físicos, verdade do mundo físico, gestão de chaves da implantação e certificação externa. A auditoria externa de terceira parte permanece `PENDING`.

Execute a verificação completa com:

```text
python tools/production_gate.py
```

## Metadados do projeto

- Identidade canônica do projeto: [`metadata/project.json`](metadata/project.json)
- Projeção CodeMeta: [`codemeta.json`](codemeta.json)
- Projeção do GitHub About: [`.github/repository-metadata.json`](.github/repository-metadata.json)

Para regenerar toda a documentação derivada e os metadados do repositório, execute:

```text
python tools/generate_repository_views.py
```

## Cânones de componentes do ASET completo

A especificação completa legível por máquina do ASET 1.5-rc11 é preservada como evidência-fonte exata e decomposta em cânones candidatos versionados de forma independente para System Composition, Context, Core, Monade, Memory, Master, Model Gateway e Protocol. A linha de componentes é `0.1-rc1` e está vinculada explicitamente ao ASET Seed `0.1-rc12`.

- Índice dos cânones: [`aset/README.md`](aset/README.md)
- Composição do sistema: [`aset/system/`](aset/system/)
- Ponte de compatibilidade com Seed: [`aset/shared/seed-bridge/`](aset/shared/seed-bridge/)

A decomposição preserva exatamente o inventário rc11: 177 requisitos, 57 invariantes, 52 artefatos, 11 gates e 57 schemas. Ela inclui 26 casos de conformidade de componentes e oito projeções formais limitadas. Essas afirmações se restringem aos candidatos de especificação; não se afirma conformidade de implementação independente nem de produção.

## Referência Python do caminho crítico semântico

Uma implementação Python não normativa e sem armazenamento executa o caminho semântico
determinístico completo, desde a projeção de Context, passando por dispatch governado,
Observation, Evidence e Verification, até o reconhecimento condicional de Outcome. Consulte
[`docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md`](docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md).
Ela é um artefato de interoperabilidade e assurance, não uma afirmação de implantação em produção.
