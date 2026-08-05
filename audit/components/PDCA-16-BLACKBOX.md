# ASET component canons — independent black-box audit

- Verdict: **PASS**
- Checks: `25/25` passed
- Snapshot: `dist/ASET-Repository-Snapshot.zip`
- SHA-256: `sha256:8cb8309e4d7e43e8d0d3f7e0317b9ee07cd2179de46770c503e6490c27ab397a`

| ID | Check | Status | Details |
|---|---|---|---|
| CB-001 | safe deterministic snapshot | PASS | ok |
| CB-002 | exact repository manifest | PASS | entries=670; mismatches=[] |
| CB-003 | strict component JSON corpus | PASS | documents=190; errors=[] |
| CB-004 | exact rc11 source provenance | PASS | model=sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94; spec=sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6 |
| CB-005 | component schemas and canonical digests | PASS | components=7; errors=[] |
| CB-006 | lossless rc11 partition | PASS | requirements=177/177; invariants=57/57; artifacts=52/52; gates=11/11; schemas=57/57; targets={'context': 24, 'core': 50, 'gateway': 11, 'master': 16, 'memory': 24, 'monade': 79, 'protocol': 102, 'system': 48} |
| CB-007 | Seed RC12 exact-byte non-regression | PASS | baseline_files=303; drift=[] |
| CB-008 | Seed RC12 semantic bridge | PASS | errors=[] |
| CB-009 | generated multilingual and semantic views | PASS | docs=24/24; semantic_errors=[] |
| CB-010 | component conformance suite | PASS | complete |
| CB-011 | bounded component formal models | PASS | complete |
| CB-012 | repository gate integration | PASS | markers=(True, True, True, True, True) |
| CB-013 | module ownership and negative boundaries | PASS | errors=[] |
| CB-014 | independent version compatibility | PASS | components={'aset.context': '0.1-rc1', 'aset.core': '0.1-rc1', 'aset.model-gateway': '0.1-rc1', 'aset.master': '0.1-rc1', 'aset.memory': '0.1-rc1', 'aset.monade': '0.1-rc1', 'aset.protocol': '0.1-rc1'}; seed=0.1-rc12 |
| CB-015 | assurance claims remain bounded | PASS | errors=[] |
| CB-016 | closed component meta-schemas | PASS | errors=[] |
| CB-017 | component conformance results | PASS | verdict=PASS; cases=26/26 |
| CB-018 | independent bounded formal evidence | PASS | errors=[] |
| CB-019 | expectation and execution separation | PASS | errors=[] |
| CB-020 | exact source registry and schema evidence | PASS | errors=[] |
| CB-021 | exclusive primitive ownership | PASS | duplicates={} |
| CB-022 | distinct multilingual operation semantics | PASS | non-distinct=[] |
| CB-023 | self-contained component assurance packages | PASS | complete |
| CB-024 | local requirement-verification-traceability identity | PASS | totals=177/177/177; errors=[] |
| CB-025 | canonical asset closure | PASS | errors=[] |

## Findings

No open findings.
