#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FORMAL_ENV = (
    "TLA2TOOLS_JAR",
    "TLAPM_BIN",
)
BASE_COMMANDS = [
    ["tools/generate_repository_views.py", "--check"],
    ["tools/check_language.py"],
    ["tools/validate_seed_canon.py"],
    ["tools/build_canon_package.py", "--check"],
    ["tools/validate_canon_package.py"],
    ["tools/verify_frozen_release.py"],
    ["tools/materialize_rc11.py", "--check"],
    ["tools/model_check_seed.py", "--output", "dist/seed-model-check.json"],
    ["tools/run_invariant_mutations.py", "--output", "dist/invariant-mutations.json"],
    [
        "tools/check_assurance_traceability.py",
        "--model-report",
        "dist/seed-model-check.json",
    ],
    [
        "tools/check_proof_traceability.py",
        "--output",
        "dist/proof-traceability-check.json",
    ],
    [
        "tools/check_canon_tla_refinement.py",
        "--output",
        "dist/canon-tla-refinement-check.json",
    ],
    [
        "tools/check_invariant_coverage.py",
        "--mutation-report",
        "dist/invariant-mutations.json",
    ],
    ["tools/validate_background_ip.py"],
    ["tools/validate_background_ip_supplement.py"],
    ["tools/validate_reference_boundary.py"],
    ["-m", "pytest", "-q"],
    ["-m", "ruff", "check", "tools", "tests"],
    ["tools/static_python_sanity.py"],
    ["tools/build_release.py"],
    ["tools/blackbox_documentation_audit.py"],
    ["tools/rebuild_manifest.py", "--check"],
]


def commands() -> list[list[str]]:
    result: list[list[str]] = []
    approved_ref = os.environ.get("ASET_APPROVED_REF")
    if approved_ref:
        result.append(
            [
                "tools/check_canon_compatibility.py",
                "--approved-ref",
                approved_ref,
                "--output",
                "dist/canon-compatibility.json",
            ]
        )
    result.extend(BASE_COMMANDS)
    tlc_jar = os.environ.get("TLA2TOOLS_JAR")
    if tlc_jar:
        result.append(
            [
                "tools/run_tlc.py",
                "--jar",
                tlc_jar,
                "--output",
                "dist/tlc-model-check.json",
            ]
        )

    tlapm_bin = os.environ.get("TLAPM_BIN")
    if tlapm_bin:
        result.append(
            [
                "tools/run_tlaps.py",
                "--tlapm",
                tlapm_bin,
                "--output",
                "dist/tlaps-proof.json",
            ]
        )
        result.append(
            [
                "tools/run_canon_tla_refinement.py",
                "--tlapm",
                tlapm_bin,
                "--output",
                "dist/canon-tla-refinement-proof.json",
            ]
        )

    return result


def write_report(rows: list[dict[str, object]], verdict: str) -> None:
    output = ROOT / "dist/repository-release-gate.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "document_type": "aset-repository-release-gate",
                "commands": rows,
                "approved_ref_checked": os.environ.get("ASET_APPROVED_REF"),
                "tlc_executed": bool(os.environ.get("TLA2TOOLS_JAR")),
                "tlaps_executed": bool(os.environ.get("TLAPM_BIN")),
                "canon_tla_refinement_executed": bool(os.environ.get("TLAPM_BIN")),
                "verdict": verdict,
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows: list[dict[str, object]] = []

    missing_formal_env = [
        name for name in REQUIRED_FORMAL_ENV if not os.environ.get(name)
    ]

    if missing_formal_env:
        for name in missing_formal_env:
            rows.append(
                {
                    "command": [
                        "required-environment",
                        name,
                    ],
                    "returncode": 1,
                    "seconds": 0.0,
                }
            )

        write_report(rows, "FAIL")

        print(
            "REPOSITORY_RELEASE_GATE_ERROR="
            "missing required formal tool environment: " + ",".join(missing_formal_env)
        )
        print("REPOSITORY_RELEASE_GATE=FAIL")
        return 1
    for args in commands():
        started = time.time()
        result = subprocess.run(
            [sys.executable, *args], cwd=ROOT, text=True, check=False
        )
        rows.append(
            {
                "command": [sys.executable, *args],
                "returncode": result.returncode,
                "seconds": round(time.time() - started, 3),
            }
        )
        if result.returncode:
            write_report(rows, "FAIL")
            print("REPOSITORY_RELEASE_GATE=FAIL")
            return result.returncode or 1
    write_report(rows, "PASS")
    print("REPOSITORY_RELEASE_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
