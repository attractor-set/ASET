# ASET

ASET é um projeto orientado pela especificação: a especificação antecede e governa a semântica permitida das implementações.

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
