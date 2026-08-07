#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_FILES = [
    ROOT / "README.md",
    ROOT / "README.ru.md",
    ROOT / "README.pt-BR.md",
    ROOT / "REPOSITORY_STATUS.json",
    ROOT / "ROADMAP.md",
    ROOT / "CANONICALITY.md",
    ROOT / "docs/repository/PRODUCTION_READINESS.md",
    ROOT / "docs/repository/OPERATIONS_RUNBOOK.md",
    ROOT / "docs/repository/RELEASE_PROCESS.md",
    ROOT / "docs/repository/BLACK_BOX_AUDIT_METHOD.md",
    ROOT / "audit/README.md",
    ROOT / "audit/ACTIVE_AUDIT_INDEX.md",
]
ACTIVE_GLOBS = [
    "docs/generated/*/ASET_Seed_Resolution_0.3-alpha.1.md",
]
FORBIDDEN_ACTIVE_CLAIMS = {
    "sqlite_runtime_profile": re.compile(r"ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1"),
    "production_ready_sqlite": re.compile(r"PRODUCTION_READY_(?:SINGLE_NODE_SQLITE_PROFILE|BOUNDED_PROFILE)"),
    "bounded_production_runtime": re.compile(r"bounded production runtime", re.IGNORECASE),
}
LANGUAGE_NAV = "[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)"


def main() -> int:
    files = list(ACTIVE_FILES)
    for pattern in ACTIVE_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))
    findings: list[dict[str, object]] = []
    for path in files:
        if not path.is_file():
            findings.append({"file": str(path.relative_to(ROOT)), "finding": "missing_active_document"})
            continue
        text = path.read_text(encoding="utf-8")
        for claim, pattern in FORBIDDEN_ACTIVE_CLAIMS.items():
            for match in pattern.finditer(text):
                findings.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "finding": claim,
                        "offset": match.start(),
                    }
                )

    audit_index_path = ROOT / "audit/ACTIVE_AUDIT_INDEX.json"
    try:
        audit_index = json.loads(audit_index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append({"file": "audit/ACTIVE_AUDIT_INDEX.json", "finding": f"invalid_audit_index:{type(error).__name__}"})
    else:
        active = set(audit_index.get("active_controlling_records", []))
        historical = set(audit_index.get("historical_noncontrolling_records", []))
        excluded = set(audit_index.get("index_exclusions", []))
        actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / "audit").rglob("*") if path.is_file()}
        if active & historical:
            findings.append({"file": "audit/ACTIVE_AUDIT_INDEX.json", "finding": "audit_classification_overlap"})
        if active | historical | excluded != actual:
            findings.append({"file": "audit/ACTIVE_AUDIT_INDEX.json", "finding": "audit_classification_incomplete"})
        if audit_index.get("active_candidate", {}).get("implementation_precedence") != "NONE":
            findings.append({"file": "audit/ACTIVE_AUDIT_INDEX.json", "finding": "implementation_precedence_not_none"})

    for name in ("README.md", "README.ru.md", "README.pt-BR.md"):
        first = (ROOT / name).read_text(encoding="utf-8").splitlines()[0]
        if first != LANGUAGE_NAV:
            findings.append({"file": name, "finding": "language_navigation_not_first_line"})

    report = {
        "document_type": "aset-documentation-blackbox-audit",
        "active_files_checked": len(files),
        "findings": findings,
        "verdict": "PASS" if not findings else "FAIL",
    }
    out = ROOT / "dist/blackbox-documentation-audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"DOCUMENTATION_BLACKBOX_FILES={len(files)}")
    print(f"DOCUMENTATION_BLACKBOX_FINDINGS={len(findings)}")
    print("DOCUMENTATION_BLACKBOX=" + report["verdict"])
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
