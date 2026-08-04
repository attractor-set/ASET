from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
MODEL_SCHEMA_PATH = ROOT / "seed/canonical/schemas/seed-model.schema.json"
PROTOCOL_PATH = ROOT / "seed/canonical/protocol/protocol-profile.json"
CONFORMANCE_PATH = ROOT / "seed/canonical/conformance/conformance-profile.json"
MIGRATION_PATH = ROOT / "seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json"


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def unique(items) -> bool:
    materialized = list(items)
    return len(materialized) == len(set(materialized))


def main() -> int:
    errors = []
    model = load(MODEL_PATH)
    schema = load(MODEL_SCHEMA_PATH)
    for error in Draft202012Validator(schema).iter_errors(model):
        errors.append("schema:" + "/".join(map(str, error.absolute_path)) + ":" + error.message)

    protocol = load(PROTOCOL_PATH)
    conformance = load(CONFORMANCE_PATH)
    migration = load(MIGRATION_PATH)

    if not unique(item["id"] for item in model["concepts"]):
        errors.append("duplicate concept id")
    if not unique(item["id"] for item in model["requirements"]):
        errors.append("duplicate requirement id")
    if not unique(item["id"] for item in model["invariants"]):
        errors.append("duplicate invariant id")
    if not unique(item["kind"] for item in model["transitions"]):
        errors.append("duplicate transition kind")

    if len(model["transitions"]) != 18:
        errors.append("transition catalogue must contain 18 entries")
    if protocol["schema_count"] != 39 or len(protocol["schemas"]) != 39:
        errors.append("protocol profile must contain 39 schemas")
    for item in protocol["schemas"]:
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item["sha256"]:
            errors.append(f"schema digest mismatch:{item['name']}")
        runtime_copy = ROOT / "src/aset_seed/schemas" / item["name"]
        if not runtime_copy.is_file() or runtime_copy.read_bytes() != path.read_bytes():
            errors.append(f"runtime schema copy mismatch:{item['name']}")

    if conformance["case_count"] != 55 or len(conformance["cases"]) != 55:
        errors.append("conformance profile must contain 55 cases")
    for item in conformance["cases"]:
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item["sha256"]:
            errors.append(f"conformance digest mismatch:{item['case_id']}")

    expected_summary = {
        "rc11_requirements": 26,
        "rc11_transition_kinds": 18,
        "rc11_schemas": 39,
        "fully_migrated_to_rc12": 83,
        "deferred_with_explicit_disposition": 0,
        "unclassified": 0,
    }
    if migration.get("summary") != expected_summary:
        errors.append("migration summary is not complete")
    if model["status"] != "RC12_RELEASE_CANDIDATE_READY":
        errors.append("unexpected rc12 status")
    if model["runtime_profile"]["status"] != "PRODUCTION_READY_BOUNDED_PROFILE":
        errors.append("unexpected runtime profile status")
    if model["canonicality"]["external_third_party_audit"] != "PENDING":
        errors.append("external audit boundary must remain explicit")

    if errors:
        for error in errors:
            print(f"RC12_CANON_ERROR={error}")
        return 1
    print(f"RC12_CONCEPTS={len(model['concepts'])}")
    print(f"RC12_REQUIREMENTS={len(model['requirements'])}")
    print(f"RC12_INVARIANTS={len(model['invariants'])}")
    print("RC12_TRANSITIONS=18")
    print("RC12_SCHEMAS=39")
    print("RC12_CONFORMANCE_BINDINGS=55")
    print("RC12_MIGRATION=83/83")
    print("RC12_CANON_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
