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
