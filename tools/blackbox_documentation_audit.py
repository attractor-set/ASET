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
]
ACTIVE_GLOBS = [
    "docs/generated/*/ASET_Seed_0.1-rc12.md",
    "docs/generated/*/ASET_Seed_Next.md",
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
