#!/usr/bin/env python3
"""Black-box audit for the storage-free ASET Python reference."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "aset_reference"
FORBIDDEN = {"sqlite3", "sqlalchemy", "psycopg", "asyncpg", "redis", "socket", "subprocess", "requests", "httpx"}


def main() -> int:
    findings: list[str] = []
    for path in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in FORBIDDEN:
                    findings.append(f"forbidden import {name} in {path.relative_to(ROOT)}")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/reference"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        findings.append("reference tests failed\n" + result.stdout + result.stderr)
    if findings:
        print("REFERENCE_BLACKBOX_VERDICT=FAIL")
        for finding in findings:
            print(f"FINDING={finding}")
        return 1
    print("REFERENCE_BLACKBOX_STORAGE_FREE=true")
    print("REFERENCE_BLACKBOX_TESTS=PASS")
    print("REFERENCE_BLACKBOX_VERDICT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
