#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$ROOT/validation}"
TARGET="$ROOT/machine/reference/seed_reference.py"
TMP_DIR="$(mktemp -d -t aset-seed-coverage-XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT
mkdir -p "$OUT_DIR"

run_profile() {
  local name="$1"
  local script="$2"
  printf 'COVERAGE_PROFILE=%s\n' "$name"
  (
    cd "$ROOT"
    COVERAGE_FILE="$TMP_DIR/.coverage.$name" COVERAGE_CORE=ctrace \
      coverage run --branch --include="$TARGET" "$script" --no-write
  ) > "$TMP_DIR/$name.log"
}

run_profile conformance conformance/run_conformance.py
run_profile blackbox audit/run_blackbox_audit.py
run_profile branch tests/run_branch_suite.py

COVERAGE_FILE="$TMP_DIR/.coverage.combined" coverage combine --keep \
  "$TMP_DIR/.coverage.conformance" \
  "$TMP_DIR/.coverage.blackbox" \
  "$TMP_DIR/.coverage.branch" >/dev/null
COVERAGE_FILE="$TMP_DIR/.coverage.combined" coverage json -o "$OUT_DIR/coverage.json" >/dev/null
COVERAGE_FILE="$TMP_DIR/.coverage.combined" coverage report -m > "$OUT_DIR/coverage_report.txt"
cp "$TMP_DIR/.coverage.combined" "$OUT_DIR/.coverage.rc11"
{
  printf '=== CONFORMANCE ===\n'; cat "$TMP_DIR/conformance.log"
  printf '=== BLACKBOX ===\n'; cat "$TMP_DIR/blackbox.log"
  printf '=== BRANCH ===\n'; cat "$TMP_DIR/branch.log"
  printf '=== COVERAGE ===\n'; cat "$OUT_DIR/coverage_report.txt"
} > "$OUT_DIR/coverage_run.txt"

python - "$ROOT" "$OUT_DIR" <<'PY'
import hashlib, json, sys
from pathlib import Path
root=Path(sys.argv[1]); out=Path(sys.argv[2])
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024),b''): h.update(chunk)
    return 'sha256:'+h.hexdigest()
paths=[
 root/'machine/reference/seed_reference.py',
 root/'conformance/run_conformance.py', root/'conformance/positive-index.json', root/'conformance/negative-index.json',
 root/'audit/run_blackbox_audit.py', root/'tests/run_branch_suite.py',
 *sorted((root/'machine/schemas').glob('*.json')),
 *sorted((root/'machine/examples/positive').glob('*.json')),
 *sorted((root/'machine/examples/negative').glob('*.json')),
]
inputs={str(p.relative_to(root)):digest(p) for p in paths}
canonical=json.dumps(inputs,sort_keys=True,separators=(',',':')).encode()
totals=json.loads((out/'coverage.json').read_text())['totals']
branch=float(totals['percent_branches_covered'])
record={
 'document_type':'aset-seed-coverage-bindings','version':'0.1-rc11',
 'target':'machine/reference/seed_reference.py','target_sha256':inputs['machine/reference/seed_reference.py'],
 'input_files':inputs,'input_set_sha256':'sha256:'+hashlib.sha256(canonical).hexdigest(),
 'profiles':['conformance','blackbox','branch'],'minimum_branch_percent':90.0,
 'num_statements':totals['num_statements'],'covered_lines':totals['covered_lines'],
 'num_branches':totals['num_branches'],'covered_branches':totals['covered_branches'],
 'branch_percent':branch,'pass':branch>=90.0,
}
(out/'coverage_bindings.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('covered_branches','num_branches','branch_percent','pass')},indent=2))
raise SystemExit(0 if record['pass'] else 1)
PY
