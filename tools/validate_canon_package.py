#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = load(ROOT / "seed/canonical/CANON_PACKAGE.json")
    errors: list[str] = []
    material: list[dict[str, str]] = []
    for item in package["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append("missing:" + item["path"])
            continue
        actual = sha(path)
        if actual != item["sha256"]:
            errors.append("digest:" + item["path"])
        material.append({"path": item["path"], "sha256": actual})
    actual_package = "sha256:" + hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if actual_package != package["package_digest"]:
        errors.append("package_digest")

    protocol = load(ROOT / "seed/canonical/conformance/implementation-conformance-protocol.json")
    protocol_schema = load(
        ROOT / "seed/canonical/schemas/implementation-conformance-protocol.schema.json"
    )
    envelope_schema = load(
        ROOT / "seed/canonical/schemas/implementation-conformance-envelope.schema.json"
    )
    for name, schema in (("protocol", protocol_schema), ("envelope", envelope_schema)):
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(f"{name}_schema_invalid:{exc}")
    errors.extend(
        "protocol_schema:" + error.message
        for error in Draft202012Validator(protocol_schema).iter_errors(protocol)
    )

    if errors:
        for error in errors:
            print("CANON_PACKAGE_ERROR=" + error)
        return 1
    print(f"CANON_PACKAGE_FILES={len(material)}")
    print("CANON_PACKAGE_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
