import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def model(): return json.loads((ROOT/'seed/canonical/source/seed-model.json').read_text(encoding='utf-8'))
def test_languages_are_exact(): assert model()['languages']==['ru','en','pt-BR']
def test_localization_is_complete():
 expected={'ru','en','pt-BR'}
 for concept in model()['concepts']:
  assert set(concept['labels'])==expected; assert set(concept['definitions'])==expected
 for group in ('requirements','invariants'):
  for item in model()[group]: assert set(item['texts'])==expected
def test_minimal_resolution_algebra_is_exact():
 algebra=model()['resolution_algebra']; assert algebra['values']==['UNKNOWN','ALLOW','BLOCK']; assert algebra['stored_terminal']==['ALLOW','BLOCK']; assert algebra['effect_permitted_if']=='ALLOW'
def test_operations_are_minimal():
 assert [item['kind'] for item in model()['transitions']]==['REGISTER_REQUEST','SUBMIT_RESOLUTION','EVALUATE_RESOLUTION']
