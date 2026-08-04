from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

COMMANDS = [
    [sys.executable, "tools/generate_editions.py", "--check"],
    [sys.executable, "tools/check_language.py"],
    [sys.executable, "tools/verify_frozen_release.py"],
    [sys.executable, "tools/materialize_rc11.py", "--check"],
    [sys.executable, "tools/rebuild_manifest.py", "--check"],
    [sys.executable, "tools/validate_repository.py"],
    [sys.executable, "-m", "pytest", "-q"],
    [sys.executable, "-m", "ruff", "check", "tools", "tests"],
    [sys.executable, "tools/build_release.py"],
    [
        sys.executable,
        "tools/blackbox_documentation_audit.py",
        "dist/ASET-Repository-Snapshot.zip",
        "--output-json",
        "dist/blackbox-documentation-audit.json",
        "--output-md",
        "dist/blackbox-documentation-audit.md",
    ],
    [
        sys.executable,
        "tools/run_blackbox_adversarial.py",
        "dist/ASET-Repository-Snapshot.zip",
        "--output",
        "dist/blackbox-adversarial-results.json",
    ],
]


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    status = 0

    for command in COMMANDS:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        record = {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "PASS" if result.returncode == 0 else "FAIL",
        }
        results.append(record)
        print(f"GATE_COMMAND={' '.join(command)}")
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            status = result.returncode or 1
            break

    report = {
        "document_type": "aset-production-repository-gate",
        "version": 1,
        "verdict": "PASS" if status == 0 else "FAIL",
        "commands": results,
    }
    (DIST / "production-gate.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"PRODUCTION_REPOSITORY_GATE={report['verdict']}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
