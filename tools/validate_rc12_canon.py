from __future__ import annotations
import hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def strict(pairs):
 out={}
 for k,v in pairs:
  if k in out: raise ValueError(f'duplicate JSON member: {k}')
  out[k]=v
 return out
def load(p): return json.loads(p.read_text(encoding='utf-8'),object_pairs_hook=strict)
def digest(p): return 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 errors=[]; model=load(ROOT/'seed/canonical/source/seed-model.json'); schema=load(ROOT/'seed/canonical/schemas/seed-model.schema.json')
 errors += ['schema:'+'/'.join(map(str,e.absolute_path))+':'+e.message for e in Draft202012Validator(schema).iter_errors(model)]
 for key in ('concepts','requirements','invariants'):
  ids=[x['id'] for x in model[key]]
  if len(ids)!=len(set(ids)): errors.append('duplicate '+key)
 kinds=[x['kind'] for x in model['transitions']]
 if len(kinds)!=18 or len(set(kinds))!=18: errors.append('transition catalogue')
 if model['implementation_boundary']['implementation_precedence']!='NONE': errors.append('implementation precedence')
 if any(x['id'].startswith('ASET-SEED-PRT-') for x in model['requirements']): errors.append('implementation requirement in Seed')
 protocol=load(ROOT/'seed/canonical/protocol/protocol-profile.json'); conf=load(ROOT/'seed/canonical/conformance/conformance-profile.json')
 if protocol['schema_count']!=39 or len(protocol['schemas'])!=39: errors.append('protocol schema count')
 for item in protocol['schemas']:
  p=ROOT/item['path']
  if not p.is_file() or digest(p)!=item['sha256']: errors.append('schema digest:'+item['name'])
 if conf['case_count']!=55 or len(conf['cases'])!=55: errors.append('conformance case count')
 for item in conf['cases']:
  p=ROOT/item['path']
  if not p.is_file() or digest(p)!=item['sha256']: errors.append('case digest:'+item['case_id'])
 if errors:
  for e in errors: print('RC12_CANON_ERROR='+e)
  return 1
 print(f"RC12_CONCEPTS={len(model['concepts'])}"); print(f"RC12_REQUIREMENTS={len(model['requirements'])}"); print(f"RC12_INVARIANTS={len(model['invariants'])}"); print('RC12_TRANSITIONS=18'); print('RC12_CANON_VALIDATION=PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
