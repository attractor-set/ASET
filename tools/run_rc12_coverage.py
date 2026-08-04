from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
COVERAGE_JSON = DIST / "rc12-coverage.json"
MIN_CORE_BRANCH_PERCENT = 90.0


def run(command: list[str]) -> int:
    print(f"COVERAGE_COMMAND={' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, text=True, check=False)
    return result.returncode


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    commands = [
        [sys.executable, "-m", "coverage", "erase"],
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--branch",
            "--source=src/aset_seed",
            "tools/run_rc12_branch_suite.py",
        ],
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--append",
            "--branch",
            "--source=src/aset_seed",
            "tools/run_rc12_conformance.py",
            "--output",
            "dist/rc12-conformance-results.json",
        ],
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--append",
            "--branch",
            "--source=src/aset_seed",
            "-m",
            "pytest",
            "-q",
            "tests/test_runtime.py",
        ],
        [
            sys.executable,
            "-m",
            "coverage",
            "json",
            "-o",
            str(COVERAGE_JSON),
        ],
    ]
    for command in commands:
        status = run(command)
        if status != 0:
            print("RC12_COVERAGE=FAIL")
            return status

    report = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    core = report["files"].get("src/aset_seed/core.py")
    if core is None:
        print("RC12_COVERAGE_ERROR=core.py absent from report")
        return 1
    summary = core["summary"]
    covered = int(summary["covered_branches"])
    missing = int(summary["missing_branches"])
    total = covered + missing
    percent = 100.0 if total == 0 else covered * 100.0 / total
    print(f"RC12_CORE_BRANCHES={covered}/{total}")
    print(f"RC12_CORE_BRANCH_PERCENT={percent:.6f}")
    coverage_data = ROOT / ".coverage"
    if coverage_data.exists():
        coverage_data.unlink()
    if percent < MIN_CORE_BRANCH_PERCENT:
        print(f"RC12_COVERAGE_ERROR=below {MIN_CORE_BRANCH_PERCENT:.1f}%")
        return 1
    print("RC12_COVERAGE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
