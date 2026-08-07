#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / 'seed/canonical/conformance/conformance-profile.json'
CASES_ROOT = ROOT / 'seed/canonical/conformance/cases'


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'expected object: {path}')
    return value


def sha256(path: Path) -> str:
    return 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()


def expected() -> dict[str, Any]:
    current = load(PROFILE_PATH)
    model = load(ROOT / 'seed/canonical/source/seed-model.json')
    cases: list[dict[str, Any]] = []
    for polarity in ('negative', 'positive'):
        for path in sorted((CASES_ROOT / polarity).glob('*.json')):
            case = load(path)
            relative = path.relative_to(ROOT).as_posix()
            cases.append({
                'case_id': case['case_id'],
                'expected': case['expected'],
                'path': relative,
                'polarity': polarity,
                'sha256': sha256(path),
            })
    return {
        'case_count': len(cases),
        'cases': cases,
        'document_type': current['document_type'],
        'negative_count': sum(item['polarity'] == 'negative' for item in cases),
        'positive_count': sum(item['polarity'] == 'positive' for item in cases),
        'profile_id': current['profile_id'],
        'protocol': current['protocol'],
        'schema_version': current['schema_version'],
        'seed_version': model['version'],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = json.dumps(expected(), ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    if args.check:
        ok = PROFILE_PATH.is_file() and PROFILE_PATH.read_text(encoding='utf-8') == content
        print('CONFORMANCE_PROFILE_PARITY=' + ('PASS' if ok else 'DIFFERENT'))
        return 0 if ok else 1
    PROFILE_PATH.write_text(content, encoding='utf-8', newline='\n')
    print('CONFORMANCE_PROFILE_BUILT=PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
