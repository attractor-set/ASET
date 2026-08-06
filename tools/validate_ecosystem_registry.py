#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = "ASET-SEED-RESOLUTION-CANON-0.3-ALPHA1"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative} must contain an object")
    return value


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com"


def main() -> int:
    errors: list[str] = []
    extensions = load("EXTENSIONS.json")
    implementations = load("IMPLEMENTATIONS.json")
    extraction = load("EXTRACTION.json")

    for name, registry, key in (
        ("extensions", extensions, "extensions"),
        ("implementations", implementations, "implementations"),
    ):
        if registry.get("normative") is not False:
            errors.append(f"{name}:normative")
        if registry.get("active_seed_canon") != ACTIVE:
            errors.append(f"{name}:active_seed")
        rows = registry.get(key)
        if not isinstance(rows, list) or not rows:
            errors.append(f"{name}:rows")
            continue
        identifiers: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                errors.append(f"{name}:row_type")
                continue
            identifier = row.get("extension_id") or row.get("implementation_id")
            if not isinstance(identifier, str) or identifier in identifiers:
                errors.append(f"{name}:identifier")
            else:
                identifiers.add(identifier)
            if row.get("implementation_precedence") != "NONE":
                errors.append(f"{name}:{identifier}:precedence")
            if not valid_url(row.get("repository")):
                errors.append(f"{name}:{identifier}:repository")
            revision = row.get("repository_revision")
            if not isinstance(revision, str) or len(revision) != 40:
                errors.append(f"{name}:{identifier}:revision")

    legacy = extraction.get("legacy_release_asset")
    if extraction.get("status") != "EXTRACTION_COMPLETE":
        errors.append("extraction:status")
    if extraction.get("normative_effect") != "NONE_ON_RESOLUTION_SEMANTICS":
        errors.append("extraction:normative_effect")
    if not isinstance(legacy, dict):
        errors.append("extraction:asset")
    else:
        digest = legacy.get("sha256")
        if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
            errors.append("extraction:digest")

    for forbidden in ("aset", "audit/components"):
        if (ROOT / forbidden).exists():
            errors.append(f"legacy_path_present:{forbidden}")

    if errors:
        for error in errors:
            print("ECOSYSTEM_REGISTRY_ERROR=" + error)
        return 1
    print(f"EXTENSIONS_REGISTERED={len(extensions['extensions'])}")
    print(f"IMPLEMENTATIONS_REGISTERED={len(implementations['implementations'])}")
    print("ECOSYSTEM_REGISTRY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
