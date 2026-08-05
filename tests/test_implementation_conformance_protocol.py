import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_canon_package_and_protocol_validate():
    for tool in ("tools/build_canon_package.py --check","tools/validate_canon_package.py"):
        r=subprocess.run([sys.executable,*tool.split()],cwd=ROOT,text=True,capture_output=True); assert r.returncode==0,r.stdout+r.stderr
def test_protocol_has_no_implementation_precedence():
    p=json.loads((ROOT/"seed/canonical/conformance/implementation-conformance-protocol.json").read_text()); assert p["implementation_precedence"]=="NONE"
