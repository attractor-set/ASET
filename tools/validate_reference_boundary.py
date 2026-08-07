#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_FILES = ("README.md", "README.ru.md", "README.pt-BR.md")
REMOVED_REGISTRY_FILES = (
    "EXTENSIONS.json",
    "EXTENSIONS.md",
    "IMPLEMENTATIONS.json",
    "IMPLEMENTATIONS.md",
    "EXTRACTION.json",
    "EXTRACTION.md",
)
REFERENCE_URLS = (
    "https://github.com/attractor-set/aset-network-extension",
    "https://github.com/attractor-set/aset-python-sqlite",
)
FORBIDDEN_PUBLIC_REFERENCES = (
    "attractor-set/aset-ai-extension-template",
    "attractor-set/aset-ai-local-stack",
)


def main() -> int:
    errors: list[str] = []

    for relative in REMOVED_REGISTRY_FILES:
        if (ROOT / relative).exists():
            errors.append(f"legacy registry file remains: {relative}")

    if (ROOT / ".github/workflows/notify-implementation-profiles.yml").exists():
        errors.append("implementation-specific notification workflow remains")

    for relative in README_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing README: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for url in REFERENCE_URLS:
            if text.count(url) != 1:
                errors.append(f"{relative} must contain exactly one reference to {url}")
        for token in FORBIDDEN_PUBLIC_REFERENCES:
            if token in text:
                errors.append(f"{relative} contains removed public artifact reference: {token}")

    if errors:
        for error in errors:
            print("REFERENCE_BOUNDARY_ERROR=" + error)
        print("REFERENCE_BOUNDARY_VALIDATION=FAIL")
        return 1

    print("REFERENCE_ARTIFACTS=2")
    print("REFERENCE_BOUNDARY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
