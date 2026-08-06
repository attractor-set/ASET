import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def model(): return json.loads((ROOT/'seed/canonical/source/seed-model.json').read_text(encoding='utf-8'))
def test_seed_is_implementation_neutral():
 value=model(); assert value['implementation_boundary']['implementation_precedence']=='NONE'; assert value['model_id']=='ASET-SEED-RESOLUTION-CANON-0.2-ALPHA2'
def test_resolution_lattice_is_exact():
 value=model()['decision_lattice']; assert value['initial']=='UNKNOWN'; assert value['terminal']==['ACCEPT','DENY']; assert value['unknown_enforcement']=='BLOCKED'
def test_seed_does_not_embed_extension_components():
 symbols={item['symbol'] for item in model()['concepts']}; assert not {'Permit','ExecutionIntent','Observation','Verification','RuntimeStore'} & symbols
