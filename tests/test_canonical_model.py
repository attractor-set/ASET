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
def test_terminal_transitions_are_explicit():
 transitions={item['kind']:item for item in model()['transitions']}; assert transitions['RESOLVE_ACCEPT']['to_status']=='ACCEPT'; assert transitions['RESOLVE_DENY']['to_status']=='DENY'; assert transitions['ESCALATE_UNKNOWN']['to_status']=='UNKNOWN'
