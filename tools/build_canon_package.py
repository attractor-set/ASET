#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = [
    "seed/canonical/source/seed-model.json",
    "seed/canonical/schemas/seed-model.schema.json",
    "seed/canonical/protocol/protocol-profile.json",
    "seed/canonical/protocol/digest-profile.json",
    "seed/canonical/schemas/protocol-profile.schema.json",
    "seed/canonical/conformance/conformance-profile.json",
    "seed/canonical/schemas/conformance-profile.schema.json",
    "seed/canonical/conformance/implementation-conformance-protocol.json",
    "seed/canonical/schemas/implementation-conformance-protocol.schema.json",
    "seed/canonical/schemas/implementation-conformance-envelope.schema.json",
    "seed/canonical/conformance/model-based-conformance.json",
    "seed/canonical/assurance/verification-registry.json",
    "seed/canonical/assurance/invariant-coverage.json",
    "seed/canonical/schemas/invariant-coverage.schema.json",
    "seed/canonical/assurance/proof-traceability.json",
    "seed/canonical/schemas/proof-traceability.schema.json",
    "seed/canonical/assurance/canon-tla-refinement.json",
    "seed/canonical/schemas/canon-tla-refinement.schema.json",
    "seed/canonical/assurance/limitations.json",
    "seed/canonical/schemas/assurance-limitations.schema.json",
    "seed/canonical/assurance/repository-release-gates.json",
    "seed/canonical/schemas/repository-release-gates.schema.json",
    "seed/canonical/shapes/seed.shacl.ttl",
    "seed/canonical/formal/SeedResolution.tla",
    "seed/canonical/formal/SeedResolutionProofs.tla",
    "seed/canonical/formal/SeedCanonProjection.tla",
    "seed/canonical/formal/SeedCanonRefinementProofs.tla",
    "seed/canonical/formal/SeedResolution.cfg",
    "seed/canonical/migration/ALPHA2_TO_0.3_ALPHA1_CHANGE_DECLARATION.json",
    "seed/canonical/decisions/ADR-005-minimal-resolution-recognition-kernel.md",
    "seed/canonical/decisions/ADR-006-complete-invariant-closure.md",
    "seed/canonical/decisions/ADR-007-reconsideration-commitments-and-bounded-retention.md",
]


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def files() -> list[str]:
    protocol = load("seed/canonical/protocol/protocol-profile.json")
    conformance = load("seed/canonical/conformance/conformance-profile.json")
    result = list(BASE)
    result.extend(item["path"] for item in protocol["schemas"])
    result.extend(item["path"] for item in conformance["cases"])
    return list(dict.fromkeys(result))


def expected() -> dict[str, Any]:
    rows = [{"path": path, "sha256": sha(path)} for path in files()]
    package_digest = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    return {
        "document_type": "aset-canon-package",
        "schema_version": 2,
        "canon_id": "ASET-SEED-RESOLUTION-CANON-0.3-ALPHA1",
        "canon_version": "0.3.0-alpha.1",
        "normative_source": "seed/canonical/source/seed-model.json",
        "implementation_precedence": "NONE",
        "conformance_protocol": "ASET-SEED-RESOLUTION-CONFORMANCE-V2",
        "files": rows,
        "package_digest": package_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "seed/canonical/CANON_PACKAGE.json"
    content = json.dumps(expected(), sort_keys=True, indent=2) + "\n"
    if args.check:
        ok = path.is_file() and path.read_text(encoding="utf-8") == content
        print("CANON_PACKAGE_PARITY=" + ("PASS" if ok else "DIFFERENT"))
        return 0 if ok else 1
    path.write_text(content, encoding="utf-8")
    print("CANON_PACKAGE_BUILT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
