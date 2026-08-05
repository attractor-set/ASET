#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=[
 'seed/canonical/source/seed-model.json','seed/canonical/schemas/seed-model.schema.json',
 'seed/canonical/protocol/protocol-profile.json','seed/canonical/conformance/conformance-profile.json',
 'seed/canonical/conformance/implementation-conformance-protocol.json',
 'seed/canonical/conformance/model-based-conformance.json',
 'seed/canonical/schemas/implementation-conformance-protocol.schema.json',
 'seed/canonical/schemas/implementation-conformance-envelope.schema.json',
 'seed/canonical/assurance/verification-registry.json',
 'seed/canonical/formal/SeedRC12.tla','seed/canonical/formal/SeedRC12.cfg',
]
def sha(p): return 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
def expected():
 rows=[{'path':p,'sha256':sha(ROOT/p)} for p in FILES]
 package_digest='sha256:'+hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return {'document_type':'aset-canon-package','schema_version':1,'canon_id':'ASET-SEED-CANON-RC12','canon_version':'0.1-rc12','normative_source':'seed/canonical/source/seed-model.json','implementation_precedence':'NONE','conformance_protocol':'ASET-IMPLEMENTATION-CONFORMANCE-V1','files':rows,'package_digest':package_digest}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); p=ROOT/'seed/canonical/CANON_PACKAGE.json'; content=json.dumps(expected(),sort_keys=True,indent=2)+'\n'
 if a.check:
  ok=p.is_file() and p.read_text(encoding='utf-8')==content
  print('CANON_PACKAGE_PARITY='+('PASS' if ok else 'DIFFERENT')); return 0 if ok else 1
 p.write_text(content,encoding='utf-8'); print('CANON_PACKAGE_BUILT=PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
