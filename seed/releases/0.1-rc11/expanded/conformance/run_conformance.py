from __future__ import annotations
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
NO_WRITE='--no-write' in sys.argv
sys.path.insert(0,str(ROOT/'machine/reference'))
from seed_reference import validate_case, initialize_state, apply_transition, SeedError


def no_duplicates(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError(f'duplicate JSON member: {k}')
        out[k]=v
    return out

def load(p):
    return json.loads(p.read_text(encoding='utf-8'),object_pairs_hook=no_duplicates)

schemas={}; resources=[]
for p in sorted((ROOT/'machine/schemas').glob('*.json')):
    s=load(p); schemas[s['$id']]=s; resources.append((s['$id'],Resource.from_contents(s)))
registry=Registry().with_resources(resources)
case_schema=schemas['https://spec.aset.example/seed/0.1-rc11/schemas/conformance-case.schema.json']
state_schema=schemas['https://spec.aset.example/seed/0.1-rc11/schemas/trust-space-state.schema.json']
case_validator=Draft202012Validator(case_schema,registry=registry)
state_validator=Draft202012Validator(state_schema,registry=registry)

rows=[]
for index_name in ['positive-index.json','negative-index.json']:
    index=load(ROOT/'conformance'/index_name)
    for rel in index['cases']:
        case=load(ROOT/rel)
        schema_errors=sorted(case_validator.iter_errors(case),key=lambda e:list(e.path))
        state_schema_errors=[]
        if not schema_errors:
            try:
                state=initialize_state(case['initial_genesis'])
                state_schema_errors.extend(state_validator.iter_errors(state))
                for setup in case.get('setup',[]):
                    result=apply_transition(state,setup)
                    if not result['accepted'] or not result['state_changed']:
                        break
                    state=result['state']
                    state_schema_errors.extend(state_validator.iter_errors(state))
            except SeedError as exc:
                # Negative genesis vectors may intentionally fail before a state exists.
                if case['expected']['accepted'] or case['expected']['code'] != exc.code:
                    state_schema_errors.append(exc)
        ok,actual,expected=validate_case(case)
        row={
          'case_id':case['case_id'],'pass':bool(ok and not schema_errors and not state_schema_errors),
          'schema_errors':[e.message for e in schema_errors],
          'state_schema_errors':[getattr(e,'message',str(e)) for e in state_schema_errors],
          'actual':actual,'expected':expected,'path':rel,
        }
        rows.append(row)
report={
 'version':'0.1-rc11','cases_total':len(rows),'cases_passed':sum(r['pass'] for r in rows),
 'case_schema_passed':sum(not r['schema_errors'] for r in rows),
 'reachable_state_schema_passed':sum(not r['state_schema_errors'] for r in rows),
 'pass':all(r['pass'] for r in rows),'results':rows,
}
if not NO_WRITE:
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/conformance_results.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print(f"Conformance: {report['cases_passed']}/{report['cases_total']}")
print(f"Case schema: {report['case_schema_passed']}/{report['cases_total']}")
print(f"Reachable state schema: {report['reachable_state_schema_passed']}/{report['cases_total']}")
for r in rows:
    if not r['pass']:
        print(json.dumps(r,ensure_ascii=False,indent=2))
sys.exit(0 if report['pass'] else 1)
