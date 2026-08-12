#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "tools/validate_alpha4_seed.py"],
    [sys.executable, "tools/alpha4_binding_graph.py"],
    [sys.executable, "tools/alpha4_congruence.py"],
    [sys.executable, "tools/alpha4_paired_expression.py"],
    [sys.executable, "-m", "pytest", "-q", "tests/test_alpha4_seed.py"],
    [sys.executable, "tools/run_alpha4_tlaps.py"],
    [sys.executable, "tools/build_alpha4_release.py", "--verify-determinism"],
    [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "tools/validate_alpha4_seed.py",
        "tools/alpha4_binding_graph.py",
        "tools/alpha4_congruence.py",
        "tools/alpha4_operational_expression.py",
        "tools/alpha4_relational_expression.py",
        "tools/alpha4_paired_expression.py",
        "tools/alpha4_release_profiles.py",
        "tools/alpha4_release_profile_congruence.py",
        "tools/build_alpha4_release.py",
        "tools/alpha4_seed_gate.py",
        "tools/run_alpha4_tlaps.py",
        "tests/test_alpha4_seed.py",
    ],
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
