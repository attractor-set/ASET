from __future__ import annotations
import json
from pathlib import Path
from tools.seed_resolution_oracle import execute_case
ROOT=Path(__file__).resolve().parents[1]
def test_all_canonical_cases_match_the_pure_oracle():
 profile=json.loads((ROOT/'seed/canonical/conformance/conformance-profile.json').read_text())
 for entry in profile['cases']:
  case=json.loads((ROOT/entry['path']).read_text())
  actual,_=execute_case(case)
  assert actual==case['expected'], entry['case_id']
def test_unknown_is_derived_not_stored():
 schema=json.loads((ROOT/'seed/canonical/protocol/schemas/resolution-record.schema.json').read_text())
 assert schema['properties']['resolution']['$ref'].endswith('/terminal_resolution')

def test_reconsideration_commitment_does_not_require_predecessor_retention():
 case=json.loads((ROOT/'seed/canonical/conformance/cases/positive/RES-POS-008.json').read_text())
 assert case['initial_store']['requests']==[]
 assert case['initial_store']['records']==[]
 previous=case['candidate']['payload']['request']['previous_terminal_record_digest']
 assert previous in case['recognized_terminal_record_digests']
 actual,final_store=execute_case(case)
 assert actual['accepted'] is True
 assert final_store['requests'][0]['previous_terminal_record_digest']==previous


def test_historical_recognition_context_is_not_canonical_store_state():
 store_schema=json.loads((ROOT/'seed/canonical/protocol/schemas/resolution-store.schema.json').read_text())
 case_schema=json.loads((ROOT/'seed/canonical/protocol/schemas/conformance-case.schema.json').read_text())
 assert 'recognized_terminal_record_digests' not in store_schema['properties']
 assert 'recognized_terminal_record_digests' in case_schema['properties']
