from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "seed/canonical/release/RC12_RELEASE_CANDIDATE.json"

KEY_FILES = [
    "seed/canonical/source/seed-model.json",
    "seed/canonical/protocol/protocol-profile.json",
    "seed/canonical/conformance/conformance-profile.json",
    "seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json",
    "seed/canonical/formal/SeedRC12.tla",
    "seed/canonical/formal/SeedRC12.cfg",
    "REPOSITORY_STATUS.json",
    "seed/canonical/assurance/repository-release-gates.json",
    "seed/canonical/assurance/limitations.json",
    "seed/canonical/release/RC12_FREEZE_ENTRY.json",
    "audit/RC12_FINAL_BLACKBOX_AUDIT.json",
    "pyproject.toml",
]


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def records(pattern: str) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
        }
        for path in sorted(ROOT.glob(pattern))
        if path.is_file()
    ]


def build() -> dict[str, object]:
    key_records = [
        {
            "path": relative,
            "size_bytes": (ROOT / relative).stat().st_size,
            "sha256": digest(ROOT / relative),
        }
        for relative in KEY_FILES
    ]
    schema_records = records("seed/canonical/protocol/schemas/*.json")
    runtime_records = records("src/aset_seed/*.py") + records("src/aset_seed/schemas/*.json")
    return {
        "document_type": "aset-seed-rc12-release-candidate-envelope",
        "schema_version": 1,
        "version": "0.1-rc12",
        "status": "RC12_RELEASE_CANDIDATE_READY",
        "stable_predecessor": "0.1-rc11",
        "wire_profile": "ASET-SEED-WIRE-0.1-RC11-COMPAT",
        "runtime_profile": "ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1",
        "external_third_party_audit": "PENDING",
        "counts": {
            "concepts": 27,
            "requirements": 40,
            "invariants": 37,
            "transition_kinds": 18,
            "protocol_schemas": len(schema_records),
            "conformance_cases": 55,
            "migrated_rc11_assets": 83,
        },
        "key_artifacts": key_records,
        "protocol_schemas": schema_records,
        "runtime_artifacts": runtime_records,
        "mandatory_gate_registry": "seed/canonical/assurance/repository-release-gates.json",
        "limitations_registry": "seed/canonical/assurance/limitations.json",
    }


def text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = text(build())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("RC12_RELEASE_ENVELOPE=DIFFERENT")
            return 1
        print("RC12_RELEASE_ENVELOPE=PASS")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
    print("RC12_RELEASE_ENVELOPE=BUILT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
