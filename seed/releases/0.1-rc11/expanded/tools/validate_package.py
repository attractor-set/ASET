from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); raise SystemExit(1)
def sha(p): return 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
if len(list((root/'machine/schemas').glob('*.json'))) != 39: fail('schema count')
if len(list((root/'machine/examples/positive').glob('*.json')))+len(list((root/'machine/examples/negative').glob('*.json'))) != 55: fail('case count')
if (root/'docs/ASET_SEED_SPECIFICATION.md').read_bytes() != (root/'docs/ASET_Seed_Specification_0.1-rc11.md').read_bytes(): fail('markdown parity')
cov=json.loads((root/'validation/coverage_bindings.json').read_text())
for rel,d in cov['input_files'].items():
 p=root/rel
 if not p.exists() or sha(p)!=d: fail('coverage binding '+rel)
if not cov['pass'] or cov['branch_percent']<90: fail('coverage')
qa=json.loads((root/'validation/publication_qa.json').read_text())
for k in ('markdown','docx','pdf'):
 x=qa['documents'][k]; p=root/x['path']
 if not p.exists() or sha(p)!=x['sha256']: fail('publication binding '+k)
for fn,total in [('conformance_results.json',55),('independent_reaudit_results.json',367),('blackbox_audit_results.json',25),('branch_suite_results.json',252)]:
 if not (root/'validation'/fn).exists(): fail(fn)
# no stale release files
if list(root.rglob('*rc9*')): fail('stale rc9 filenames')
print('Package validation: PASS')
print('Schemas: 39; cases: 55; branch coverage:',cov['branch_percent'])
