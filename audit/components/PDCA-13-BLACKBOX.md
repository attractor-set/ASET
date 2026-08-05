# ASET component canons — independent black-box audit

- Verdict: **FAIL**
- Checks: `12/15` passed
- Snapshot: `dist/ASET-Repository-Snapshot.zip`
- SHA-256: `sha256:1d4332f8f4e2191b813d721fa681d8246682e9c7f36ad0a8c7284d27af72d2d1`

| ID | Check | Status | Details |
|---|---|---|---|
| CB-001 | safe deterministic snapshot | PASS | ok |
| CB-002 | exact repository manifest | PASS | entries=530; mismatches=[] |
| CB-003 | strict component JSON corpus | PASS | documents=80; errors=[] |
| CB-004 | exact rc11 source provenance | PASS | model=sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94; spec=sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6 |
| CB-005 | component schemas and canonical digests | PASS | components=7; errors=[] |
| CB-006 | lossless rc11 partition | PASS | requirements=177/177; invariants=57/57; artifacts=52/52; gates=11/11; schemas=57/57; targets={'context': 24, 'core': 50, 'gateway': 11, 'master': 16, 'memory': 24, 'monade': 79, 'protocol': 102, 'system': 48} |
| CB-007 | Seed RC12 exact-byte non-regression | PASS | baseline_files=303; drift=[] |
| CB-008 | Seed RC12 semantic bridge | PASS | errors=[] |
| CB-009 | generated multilingual and semantic views | PASS | docs=24/24; semantic_errors=[] |
| CB-010 | component conformance suite | FAIL | missing=['aset/shared/conformance/component-conformance-profile.json', 'aset/shared/conformance/positive/index.json', 'aset/shared/conformance/negative/index.json', 'aset/shared/conformance/results.json', 'tools/run_component_conformance.py'] |
| CB-011 | bounded component formal models | FAIL | missing=['aset/components/context/canonical/formal/context.tla', 'aset/components/core/canonical/formal/core.tla', 'aset/components/gateway/canonical/formal/gateway.tla', 'aset/components/master/canonical/formal/master.tla', 'aset/components/memory/canonical/formal/memory.tla', 'aset/components/monade/canonical/formal/monade.tla', 'aset/components/protocol/canonical/formal/protocol.tla', 'aset/system/canonical/formal/system-composition.tla', 'aset/shared/formal/results.json', 'tools/model_check_components.py'] |
| CB-012 | repository gate integration | FAIL | markers=(False, False, False, False, False) |
| CB-013 | module ownership and negative boundaries | PASS | errors=[] |
| CB-014 | independent version compatibility | PASS | components={'aset.context': '0.1-rc1', 'aset.core': '0.1-rc1', 'aset.model-gateway': '0.1-rc1', 'aset.master': '0.1-rc1', 'aset.memory': '0.1-rc1', 'aset.monade': '0.1-rc1', 'aset.protocol': '0.1-rc1'}; seed=0.1-rc12 |
| CB-015 | assurance claims remain bounded | PASS | errors=[] |

## Findings

- `FINDING-CB-010` (HIGH): missing=['aset/shared/conformance/component-conformance-profile.json', 'aset/shared/conformance/positive/index.json', 'aset/shared/conformance/negative/index.json', 'aset/shared/conformance/results.json', 'tools/run_component_conformance.py']
- `FINDING-CB-011` (HIGH): missing=['aset/components/context/canonical/formal/context.tla', 'aset/components/core/canonical/formal/core.tla', 'aset/components/gateway/canonical/formal/gateway.tla', 'aset/components/master/canonical/formal/master.tla', 'aset/components/memory/canonical/formal/memory.tla', 'aset/components/monade/canonical/formal/monade.tla', 'aset/components/protocol/canonical/formal/protocol.tla', 'aset/system/canonical/formal/system-composition.tla', 'aset/shared/formal/results.json', 'tools/model_check_components.py']
- `FINDING-CB-012` (HIGH): markers=(False, False, False, False, False)
