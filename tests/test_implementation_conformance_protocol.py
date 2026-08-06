import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_canon_package_and_protocol_validate():
 for tool in ('tools/build_canon_package.py --check','tools/validate_canon_package.py','tools/validate_seed_canon.py'):
  result=subprocess.run([sys.executable,*tool.split()],cwd=ROOT,text=True,capture_output=True); assert result.returncode==0,result.stdout+result.stderr
def test_protocol_has_no_implementation_precedence():
 protocol=json.loads((ROOT/'seed/canonical/conformance/implementation-conformance-protocol.json').read_text()); assert protocol['implementation_precedence']=='NONE'; assert protocol['protocol_id']=='ASET-SEED-RESOLUTION-CONFORMANCE-V2'
