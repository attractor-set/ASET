import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def model(): return json.loads((ROOT/'seed/canonical/source/seed-model.json').read_text(encoding='utf-8'))
def test_seed_is_implementation_neutral():
 value=model(); assert value['implementation_boundary']['implementation_precedence']=='NONE'; assert value['model_id']=='ASET-SEED-RESOLUTION-CANON-0.3-ALPHA1'
def test_resolution_algebra_is_exact():
 value=model()['resolution_algebra']; assert value['values']==['UNKNOWN','ALLOW','BLOCK']; assert value['fail_closed_values']==['UNKNOWN','BLOCK']; assert value['conflict_result']=='UNKNOWN'
def test_seed_does_not_embed_extension_components():
 symbols={item['symbol'] for item in model()['concepts']}; assert not {'Permit','ExecutionIntent','Observation','Verification','RuntimeStore'} & symbols
