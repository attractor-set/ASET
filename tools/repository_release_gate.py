#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMANDS = [
    ["tools/generate_repository_views.py", "--check"],
    ["tools/check_language.py"],
    ["tools/validate_rc12_canon.py"],
    ["tools/build_canon_package.py", "--check"],
    ["tools/validate_canon_package.py"],
    ["tools/verify_frozen_release.py"],
    ["tools/materialize_rc11.py", "--check"],
    ["tools/validate_component_canons.py"],
    ["tools/run_component_conformance.py", "--check"],
    ["tools/build_monade_attempt_profile_package.py", "--check"],
    ["tools/validate_monade_attempt_profile.py"],
    ["tools/run_monade_attempt_conformance.py", "--check"],
    ["tools/model_check_monade_attempt_profile.py", "--check"],
    ["tools/model_check_rc12.py", "--output", "dist/rc12-model-check.json"],
    ["tools/check_assurance_traceability.py", "--model-report", "dist/rc12-model-check.json"],
    ["tools/model_check_components.py", "--check"],
    ["tools/validate_background_ip_supplement.py"],
    ["-m", "pytest", "-q"],
    ["-m", "ruff", "check", "tools", "tests"],
    ["tools/static_python_sanity.py"],
    ["tools/blackbox_documentation_audit.py"],
    ["tools/rebuild_manifest.py", "--check"],
    ["tools/build_release.py"],
    [
        "tools/blackbox_component_audit.py",
        "dist/ASET-Repository-Snapshot.zip",
        "--output-json",
        "dist/blackbox-component-audit.json",
        "--output-md",
        "dist/blackbox-component-audit.md",
    ],
    ["tools/run_component_blackbox_adversarial.py"],
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
    for args in commands():
        started = time.time()
        result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, check=False)
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
