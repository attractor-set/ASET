#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.seed_recognition_assurance_cases import case_manifest, generate_cases, validate_cases
except ModuleNotFoundError:
    from seed_recognition_assurance_cases import case_manifest, generate_cases, validate_cases

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assurance/seed-implementation-assurance/GENERATED_CASES_MANIFEST.json"


def expected_text() -> str:
    cases = generate_cases()
    errors = validate_cases(cases)
    if errors:
        raise RuntimeError("generated assurance cases invalid: " + "; ".join(errors))
    return json.dumps(case_manifest(cases), sort_keys=True, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = expected_text()
    if args.check:
        ok = MANIFEST.is_file() and MANIFEST.read_text(encoding="utf-8") == content
        print("SEED_RECOGNITION_ASSURANCE_CASE_MANIFEST=" + ("PASS" if ok else "DIFFERENT"))
        return 0 if ok else 1
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(content, encoding="utf-8", newline="\n")
    manifest = json.loads(content)
    print(f"SEED_RECOGNITION_ASSURANCE_CASES_BUILT={manifest['cases_total']}")
    print(f"SEED_RECOGNITION_ASSURANCE_CASE_SET_DIGEST={manifest['case_set_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
