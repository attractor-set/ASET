#!/usr/bin/env python3
"""Independent black-box audit for the ASET Python critical-path reference."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {
    "asyncpg",
    "httpx",
    "psycopg",
    "redis",
    "requests",
    "socket",
    "sqlalchemy",
    "sqlite3",
    "subprocess",
}


def command(repo: Path, *arguments: str) -> bool:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(repo / "src")
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=repo,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode == 0


def audit(repo: Path) -> tuple[list[dict[str, str]], list[str]]:
    checks: list[dict[str, str]] = []
    findings: list[str] = []

    def record(identifier: str, label: str, passed: bool, finding: str = "") -> None:
        checks.append({"id": identifier, "label": label, "status": "PASS" if passed else "FAIL"})
        print(f"{identifier}={'PASS' if passed else 'FAIL'}:{label}")
        if not passed:
            findings.append(finding or label)

    required = {
        "src/aset_reference/__init__.py",
        "src/aset_reference/canonical.py",
        "src/aset_reference/model.py",
        "src/aset_reference/engine.py",
        "tests/reference/test_critical_path.py",
        "tools/run_reference_conformance.py",
        "tools/model_check_reference.py",
        "tools/reference_adversarial_probe.py",
        "docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md",
        "audit/reference/traceability.json",
    }
    record(
        "REF-BB-001",
        "required reference surface",
        all((repo / item).is_file() for item in required),
    )

    forbidden_findings: list[str] = []
    package = repo / "src/aset_reference"
    for path in sorted(package.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            forbidden_findings.extend(name for name in names if name in FORBIDDEN)
    record(
        "REF-BB-002",
        "storage-free deterministic imports",
        not forbidden_findings,
        ",".join(sorted(set(forbidden_findings))),
    )

    version_ok = command(
        repo,
        "-c",
        "import aset_reference; assert aset_reference.__version__ == '0.2.0'",
    )
    record("REF-BB-003", "independent reference version", version_ok)
    record(
        "REF-BB-004",
        "reference conformance 26 cases",
        command(repo, "tools/run_reference_conformance.py", "--check"),
    )
    record(
        "REF-BB-005",
        "bounded four-class model",
        command(repo, "tools/model_check_reference.py", "--check"),
    )
    record(
        "REF-BB-006",
        "focused reference regression",
        command(repo, "-m", "pytest", "-q", "tests/reference"),
    )
    record(
        "REF-BB-007",
        "portable exact-digest vector",
        command(repo, "-m", "pytest", "-q", "tests/reference/test_vectors.py"),
    )
    semantic_probe = (
        "from aset_reference import run_critical_path; "
        "r={x:run_critical_path(x) for x in ('SUCCESS','FAILURE','NO_EFFECT','UNKNOWN')}; "
        "assert all(len(v.crossings)==8 for v in r.values()); "
        "assert r['UNKNOWN'].outcome is None; "
        "assert all(r[x].outcome is not None for x in ('SUCCESS','FAILURE','NO_EFFECT'))"
    )
    record("REF-BB-008", "complete semantic terminal classes", command(repo, "-c", semantic_probe))
    restore_probe = (
        "from aset_reference import ReferenceMachine; "
        "m=ReferenceMachine(); m.run('SUCCESS'); s=m.snapshot(); "
        "assert ReferenceMachine.restore(s).snapshot()==s"
    )
    record("REF-BB-009", "causal snapshot restore", command(repo, "-c", restore_probe))

    doc = (repo / "docs/reference/PYTHON_CRITICAL_PATH_REFERENCE.md")
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    trace = repo / "audit/reference/traceability.json"
    trace_data = json.loads(trace.read_text(encoding="utf-8")) if trace.is_file() else {}
    claims_ok = (
        "NON_NORMATIVE" in text
        and "PRODUCTION_READY=false" in text
        and trace_data.get("reference_version") == "0.2.0"
        and trace_data.get("normative_status") == "NON_NORMATIVE_EXECUTABLE_INTERPRETATION"
    )
    record("REF-BB-010", "truthful scope and traceability", claims_ok)
    return checks, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", nargs="?")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()

    temporary: tempfile.TemporaryDirectory[str] | None = None
    repo = ROOT
    if args.snapshot:
        snapshot = Path(args.snapshot)
        if not snapshot.is_absolute():
            snapshot = ROOT / snapshot
        if not snapshot.is_file():
            print("REFERENCE_BLACKBOX_ERROR=snapshot missing")
            return 1
        temporary = tempfile.TemporaryDirectory(prefix="aset-ref-blackbox-")
        target = Path(temporary.name)
        with zipfile.ZipFile(snapshot) as archive:
            archive.extractall(target)
        roots = [path for path in target.iterdir() if path.is_dir()]
        repo = roots[0] if len(roots) == 1 else target

    try:
        checks, findings = audit(repo)
    finally:
        if temporary is not None:
            temporary.cleanup()

    verdict = "PASS" if not findings and len(checks) == 10 else "FAIL"
    report = {
        "document_type": "aset-reference-blackbox-audit",
        "version": 1,
        "checks": checks,
        "checks_passed": sum(item["status"] == "PASS" for item in checks),
        "checks_total": 10,
        "findings": findings,
        "verdict": verdict,
    }
    if args.output_json:
        output = ROOT / args.output_json
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output = ROOT / args.output_md
        output.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# ASET Python Reference Black-box Audit", "", f"Verdict: **{verdict}**", ""]
        lines.extend(f"- {item['id']}: {item['status']} — {item['label']}" for item in checks)
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"REFERENCE_BLACKBOX={report['checks_passed']}/10")
    print(f"REFERENCE_BLACKBOX_FINDINGS={len(findings)}")
    print(f"REFERENCE_BLACKBOX_VERDICT={verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
