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
    [
        sys.executable,
        "tools/alpha4_proof_witness_materializer.py",
        "--output",
        "dist/proof-derived-recognition-witnesses.json",
    ],
    [
        sys.executable,
        "tools/build_alpha4_release.py",
        "--verify-determinism",
        "--proof-witnesses",
        "dist/proof-derived-recognition-witnesses.json",
    ],
    [
        sys.executable,
        "tools/alpha4_expression_airgap_verifier.py",
        "--witnesses",
        "dist/proof-derived-recognition-witnesses.json",
        "--expression",
        "dist/ASET-Seed-0.4alpha-profiles/python/aset_seed_alpha4.py",
        "--output",
        "dist/airgap-expression-evidence.json",
    ],
    [
        sys.executable,
        "tools/alpha4_python_sqlite_persistence_gate.py",
        "--profiles-root",
        "dist/ASET-Seed-0.4alpha-profiles",
        "--output",
        "dist/python-sqlite-persistence-evidence.json",
    ],
    [
        sys.executable,
        "tools/alpha4_release_admission_certificate.py",
        "--witnesses",
        "dist/proof-derived-recognition-witnesses.json",
        "--expression-evidence",
        "dist/airgap-expression-evidence.json",
        "--persistence-evidence",
        "dist/python-sqlite-persistence-evidence.json",
        "--release-root",
        "dist/ASET-Seed-0.4alpha",
        "--profiles-root",
        "dist/ASET-Seed-0.4alpha-profiles",
        "--release-archive",
        "dist/ASET-Seed-0.4alpha.zip",
        "--profiles-archive",
        "dist/ASET-Seed-0.4alpha-profiles.zip",
        "--output",
        "dist/release-admission-certificate.json",
    ],
    [
        sys.executable,
        "tools/alpha4_public_release_audit.py",
        "--output",
        "dist/public-release-audit.json",
    ],
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
