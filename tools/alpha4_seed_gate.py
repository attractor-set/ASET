#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "tools/validate_repository_minimal.py"],
    [sys.executable, "tools/validate_alpha4_seed.py"],
    [sys.executable, "tools/alpha4_binding_graph.py"],
    [sys.executable, "tools/alpha4_congruence.py"],
    [sys.executable, "tools/alpha4_paired_expression.py"],
    [sys.executable, "-m", "pytest", "-q"],
    [sys.executable, "tools/run_alpha4_tlaps.py"],
    [sys.executable, "tools/build_alpha4_release.py", "--verify-determinism"],
    [sys.executable, "-m", "ruff", "format", "--check", "tools", "tests"],
    [sys.executable, "-m", "ruff", "check", "tools", "tests"],
]


def main() -> int:
    for command in COMMANDS:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print("ALPHA4_SEED_GATE=FAIL")
            return result.returncode
    print("ALPHA4_SEED_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
