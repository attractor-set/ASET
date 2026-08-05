#!/usr/bin/env python3
from __future__ import annotations
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main() -> int:
    errors=[]; count=0
    for base in (ROOT/'tools',ROOT/'tests'):
        for path in sorted(base.rglob('*.py')):
            count+=1
            try: ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
            except Exception as exc: errors.append(f'{path.relative_to(ROOT)}:{exc}')
    if errors:
        for error in errors: print('PYTHON_SANITY_ERROR='+error)
        return 1
    print(f'PYTHON_SANITY_FILES={count}')
    print('PYTHON_SANITY=PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
