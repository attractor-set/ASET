#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from tools.alpha4_binding_graph import ProofBinding, parse_seed_bindings
except ModuleNotFoundError:
    from alpha4_binding_graph import ProofBinding, parse_seed_bindings

ROOT = Path(__file__).resolve().parents[1]


def default_tlapm() -> str:
    configured = os.environ.get("TLAPM_BIN")
    if configured:
        return configured
    return str(ROOT / ".tooling" / "tlapm" / "bin" / "tlapm")


def parse_obligation_count(text: str) -> int | None:
    match = re.search(r"All\s+(\d+)\s+obligations\s+proved\.", text)
    return int(match.group(1)) if match else None


def run_subject(tlapm: str, subject: ProofBinding) -> tuple[int, int | None]:
    print(f"ALPHA4_TLAPS_SUBJECT={subject.proof_id}:START")
    print(f"ALPHA4_TLAPS_MODULE={subject.module}")
    print(f"ALPHA4_TLAPS_FINAL_THEOREM={subject.final_theorem}")
    print(f"ALPHA4_TLAPS_EXPECTED_OBLIGATIONS={subject.expected_obligations}")
    try:
        result = subprocess.run(
            [
                tlapm,
                "-I",
                "theory/local-recognition/formal",
                "-I",
                "seed/alpha4/formal",
                subject.module,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        print(f"ALPHA4_TLAPS_ERROR={type(error).__name__}: {error}")
        print(f"ALPHA4_TLAPS_SUBJECT={subject.proof_id}:FAIL")
        return 1, None
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    obligations = parse_obligation_count(result.stdout + "\n" + result.stderr)
    if result.returncode != 0 or obligations != subject.expected_obligations:
        print(f"ALPHA4_TLAPS_OBLIGATIONS={obligations}")
        print(f"ALPHA4_TLAPS_SUBJECT={subject.proof_id}:FAIL")
        return result.returncode or 1, obligations
    print(f"ALPHA4_TLAPS_OBLIGATIONS={obligations}")
    print(f"ALPHA4_TLAPS_SUBJECT={subject.proof_id}:PASS")
    return 0, obligations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlapm", default=default_tlapm())
    args = parser.parse_args()
    bindings = parse_seed_bindings(ROOT)
    subjects = bindings.all_proofs
    total_expected = sum(item.expected_obligations for item in subjects)
    total_proved = 0
    print("ALPHA4_TLAPS=START")
    for subject in subjects:
        status, obligations = run_subject(args.tlapm, subject)
        if status:
            print("ALPHA4_TLAPS_VERDICT=FAIL")
            return status
        total_proved += obligations or 0
    print(f"ALPHA4_TLAPS_TOTAL_OBLIGATIONS={total_proved}/{total_expected}")
    print("ALPHA4_TLAPS_VERDICT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
