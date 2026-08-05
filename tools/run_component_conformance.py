from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from component_common import (
    ASET_ROOT,
    COMPONENT_KEYS,
    ROOT,
    canonical_digest,
    file_digest,
    load,
    schema_errors,
)
from jsonschema import Draft202012Validator

PROFILE = ASET_ROOT / "shared/conformance/component-conformance-profile.json"
POSITIVE_INDEX = ASET_ROOT / "shared/conformance/positive/index.json"
NEGATIVE_INDEX = ASET_ROOT / "shared/conformance/negative/index.json"
RESULTS = ASET_ROOT / "shared/conformance/results.json"
CASE_SCHEMA = ASET_ROOT / "shared/schemas/component-conformance-case.schema.json"
PROFILE_SCHEMA = ASET_ROOT / "shared/schemas/component-conformance-profile.schema.json"
INDEX_SCHEMA = ASET_ROOT / "shared/schemas/component-conformance-index.schema.json"
RESULTS_SCHEMA = ASET_ROOT / "shared/schemas/component-conformance-results.schema.json"
COMPONENT_SCHEMA = ASET_ROOT / "shared/schemas/component-canon.schema.json"
SYSTEM_SCHEMA = ASET_ROOT / "shared/schemas/system-composition-canon.schema.json"
BRIDGE_SCHEMA = ASET_ROOT / "shared/schemas/seed-compatibility-profile.schema.json"
MIGRATION_SCHEMA = ASET_ROOT / "shared/schemas/rc11-component-migration.schema.json"
SOURCE_MODEL = ASET_ROOT / "source/rc11/aset-system-model-1.5-rc11.json"
SOURCE_REQUIREMENTS = ASET_ROOT / "source/rc11/requirements-register.json"
BRIDGE = ASET_ROOT / "shared/seed-bridge/seed-compatibility-profile.json"

EXPECTED_COUNTS = {
    "requirements": 177,
    "invariants": 57,
    "artifacts": 52,
    "gates": 11,
    "schemas": 57,
}

ALLOWED_CLASSIFICATIONS = {
    "aset.context": {
        "LOCAL_NON_GOVERNED_COMPUTATION",
        "GOVERNED_CONTEXT_MUTATION",
    },
    "aset.core": {
        "NORMATIVE_DECISION",
        "AUTHORIZATION_ISSUANCE",
        "GOVERNED_CONTEXT_MUTATION",
    },
    "aset.model-gateway": {"LOCAL_NON_GOVERNED_COMPUTATION"},
    "aset.master": {"LOCAL_NON_GOVERNED_COMPUTATION"},
    "aset.memory": {
        "LOCAL_NON_GOVERNED_COMPUTATION",
        "GOVERNED_CONTEXT_MUTATION",
    },
    "aset.monade": {
        "GOVERNED_CONTEXT_MUTATION",
        "EXTERNAL_EFFECT",
        "OBSERVATION_ADMISSION",
        "VERIFICATION_PROCESSING",
        "OUTCOME_RECOGNITION",
    },
    "aset.protocol": {"LOCAL_NON_GOVERNED_COMPUTATION"},
}


def canonical_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def pointer_target(document: object, pointer: str) -> tuple[object, str]:
    if not pointer.startswith("/"):
        raise ValueError("mutation path must be a JSON Pointer")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
    current = document
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise ValueError(f"cannot traverse mutation path:{pointer}")
    return current, parts[-1]


def apply_mutation(document: dict[str, object], mutation: dict[str, object]) -> None:
    target, final = pointer_target(document, str(mutation["path"]))
    operation = str(mutation["operation"])
    if operation == "SET":
        if isinstance(target, list):
            target[int(final)] = copy.deepcopy(mutation.get("value"))
        elif isinstance(target, dict):
            target[final] = copy.deepcopy(mutation.get("value"))
        else:
            raise ValueError("SET target is not a collection")
    elif operation == "REMOVE":
        if isinstance(target, list):
            del target[int(final)]
        elif isinstance(target, dict):
            del target[final]
        else:
            raise ValueError("REMOVE target is not a collection")
    elif operation == "APPEND":
        if isinstance(target, list):
            target.append(copy.deepcopy(mutation.get("value")))
        elif isinstance(target, dict):
            collection = target[final]
            if not isinstance(collection, list):
                raise ValueError("APPEND target is not an array")
            collection.append(copy.deepcopy(mutation.get("value")))
        else:
            raise ValueError("APPEND target is not a collection")
    else:
        raise ValueError(f"unknown mutation operation:{operation}")
    if mutation.get("refresh_canonical_digest") and "canonical_digest" in document:
        document["canonical_digest"] = canonical_digest(document)


def validate_schema(value: object, schema_path: Path) -> list[str]:
    schema = load(schema_path)
    return ["schema:" + error for error in schema_errors(schema, value)]


def bridge_rules() -> dict[str, dict[str, object]]:
    bridge = load(BRIDGE)
    return {
        str(item["classification"]): item
        for item in bridge["classification_rules"]
    }


def validate_component(value: dict[str, object]) -> list[str]:
    errors = validate_schema(value, COMPONENT_SCHEMA)
    if value.get("canonical_digest") != canonical_digest(value):
        errors.append("canonical digest mismatch")
    component_id = str(value.get("component_id"))
    allowed = ALLOWED_CLASSIFICATIONS.get(component_id, set())
    rules = bridge_rules()
    operation_ids: list[str] = []
    for operation in value.get("operations", []):
        if not isinstance(operation, dict):
            continue
        operation_ids.append(str(operation.get("id")))
        classification = str(operation.get("classification"))
        if classification not in allowed:
            errors.append(f"component boundary forbids classification:{classification}")
        rule = rules.get(classification)
        mapping = operation.get("seed_mapping")
        if not isinstance(mapping, dict) or rule is None:
            errors.append("seed mapping unavailable")
            continue
        for field in (
            "seed_transition_required",
            "sequence",
            "outcome_recognition_required",
        ):
            if mapping.get(field) != rule.get(field):
                errors.append(f"seed mapping mismatch:{operation.get('id')}:{field}")
        if component_id == "aset.master":
            forbidden = {"Permit", "Outcome", "GateCrossingReceipt", "CoreResolution"}
            outputs = {str(item) for item in operation.get("output_artifacts", [])}
            if outputs & forbidden:
                errors.append(f"Master output authority forbidden:{sorted(outputs & forbidden)}")
    if len(operation_ids) != len(set(operation_ids)):
        errors.append("duplicate operation ID")
    return errors


def validate_bridge(value: dict[str, object]) -> list[str]:
    errors = validate_schema(value, BRIDGE_SCHEMA)
    if value.get("canonical_digest") != canonical_digest(value):
        errors.append("canonical digest mismatch")
    rules = {
        str(item["classification"]): item
        for item in value.get("classification_rules", [])
        if isinstance(item, dict)
    }
    external = rules.get("EXTERNAL_EFFECT", {})
    external_sequence = [
        "Decision",
        "Permit",
        "PermitUseReceipt",
        "ExecutionIntent",
        "Observation",
        "Verification",
        "Outcome",
    ]
    if external.get("sequence") != external_sequence:
        errors.append("external effect sequence differs")
    outcome = rules.get("OUTCOME_RECOGNITION", {})
    sequence = outcome.get("sequence", [])
    if (
        not isinstance(sequence, list)
        or "Verification" not in sequence
        or sequence[-1:] != ["Outcome"]
    ):
        errors.append("outcome sequence lacks Verification before Outcome")
    return errors


def validate_migration(value: dict[str, object]) -> list[str]:
    errors = validate_schema(value, MIGRATION_SCHEMA)
    if value.get("canonical_digest") != canonical_digest(value):
        errors.append("canonical digest mismatch")
    source_model = load(SOURCE_MODEL)
    source_requirements = load(SOURCE_REQUIREMENTS)["requirements"]
    source_sets = {
        "requirements": {str(item["ID"]) for item in source_requirements},
        "invariants": {str(item["id"]) for item in source_model["invariants"]},
        "artifacts": {str(item["id"]) for item in source_model["artifacts"]},
        "gates": {str(item["id"]) for item in source_model["gate_types"]},
    }
    for kind, expected_count in EXPECTED_COUNTS.items():
        assignments = value.get("assignments", {}).get(kind, [])
        ids = [str(item.get("id")) for item in assignments if isinstance(item, dict)]
        if len(ids) != expected_count or len(ids) != len(set(ids)):
            errors.append(f"duplicate assignment or count mismatch:{kind}")
        if kind in source_sets and set(ids) != source_sets[kind]:
            errors.append(f"source partition mismatch:{kind}")
    return errors


def validate_system(value: dict[str, object]) -> list[str]:
    errors = validate_schema(value, SYSTEM_SCHEMA)
    if value.get("canonical_digest") != canonical_digest(value):
        errors.append("canonical digest mismatch")
    components = value.get("components", [])
    if len(components) != len(COMPONENT_KEYS):
        errors.append("component inventory differs")
    for item in components:
        if not isinstance(item, dict):
            continue
        path = ROOT / str(item.get("path"))
        if not path.is_file():
            errors.append(f"component path missing:{path}")
            continue
        actual = load(path)
        if item.get("canonical_digest") != actual.get("canonical_digest"):
            errors.append(f"component digest mismatch:{item.get('component_id')}")
    gates = value.get("gates", [])
    if len(gates) != 11 or len({str(item.get("id")) for item in gates}) != 11:
        errors.append("gate inventory differs")
    return errors


def validate_seed_baseline(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    files = value.get("files", [])
    if value.get("files_count") != 303 or len(files) != 303:
        errors.append("Seed byte baseline count differs")
    for item in files:
        if not isinstance(item, dict):
            errors.append("Seed byte baseline entry invalid")
            continue
        path = ROOT / str(item["path"])
        if not path.is_file():
            errors.append(f"Seed byte baseline missing:{item['path']}")
            continue
        if path.stat().st_size != item["size_bytes"] or file_digest(path) != item["sha256"]:
            errors.append(f"Seed byte baseline drift:{item['path']}")
    return errors



def validate_canon_package(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    files = value.get("files", [])
    if not isinstance(files, list) or not files:
        return ["Canon package file inventory missing"]
    material: list[dict[str, str]] = []
    for item in files:
        if not isinstance(item, dict):
            errors.append("Canon package entry invalid")
            continue
        relative = str(item.get("path", ""))
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"Canon package missing:{relative}")
            continue
        observed = file_digest(path)
        if observed != item.get("sha256"):
            errors.append(f"Canon package digest differs:{relative}")
        material.append({"path": relative, "sha256": observed})
    expected = "sha256:" + __import__("hashlib").sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if value.get("package_digest") != expected:
        errors.append("Canon package digest differs")
    if value.get("implementation_precedence") != "NONE":
        errors.append("Canon package implementation precedence differs")
    return errors

def validate_protocol_registry(value: dict[str, object]) -> list[str]:
    errors = validate_migration(value)
    assignments = value.get("assignments", {}).get("schemas", [])
    base = ASET_ROOT / "components/protocol/canonical/protocol/schemas"
    for item in assignments:
        path = base / str(item["id"])
        if not path.is_file() or file_digest(path) != item.get("sha256"):
            errors.append(f"protocol schema byte mismatch:{item.get('id')}")
    return errors


def validate_subject(subject: str, value: dict[str, object]) -> list[str]:
    if subject == "COMPONENT":
        return validate_component(value)
    if subject == "SYSTEM":
        return validate_system(value)
    if subject == "BRIDGE":
        return validate_bridge(value)
    if subject == "MIGRATION":
        return validate_migration(value)
    if subject == "SEED_BASELINE":
        return validate_seed_baseline(value)
    if subject == "CANON_PACKAGE":
        return validate_canon_package(value)
    if subject == "PROTOCOL_REGISTRY":
        return validate_protocol_registry(value)
    return [f"unknown subject:{subject}"]


def load_cases(index_path: Path) -> list[dict[str, object]]:
    index = load(index_path)
    cases: list[dict[str, object]] = []
    for item in index["cases"]:
        cases.append(load(ROOT / str(item["path"])))
    return cases


def validate_control_documents() -> list[str]:
    errors: list[str] = []
    profile = load(PROFILE)
    for error in validate_schema(profile, PROFILE_SCHEMA):
        errors.append(f"profile:{error}")
    if profile.get("canonical_digest") != canonical_digest(profile):
        errors.append("profile canonical digest mismatch")
    for label, path in (("positive", POSITIVE_INDEX), ("negative", NEGATIVE_INDEX)):
        value = load(path)
        for error in validate_schema(value, INDEX_SCHEMA):
            errors.append(f"{label} index:{error}")
        if value.get("canonical_digest") != canonical_digest(value):
            errors.append(f"{label} index canonical digest mismatch")
    case_schema = load(CASE_SCHEMA)
    cases = load_cases(POSITIVE_INDEX) + load_cases(NEGATIVE_INDEX)
    identifiers = [str(case["id"]) for case in cases]
    if len(identifiers) != len(set(identifiers)):
        errors.append("duplicate conformance case ID")
    if set(identifiers) != set(profile["required_case_ids"]):
        errors.append("profile case inventory differs")
    for case in cases:
        for error in Draft202012Validator(case_schema).iter_errors(case):
            errors.append(f"case:{case.get('id')}:{error.message}")
    return errors


def build_results() -> dict[str, object]:
    control_errors = validate_control_documents()
    results: list[dict[str, object]] = []
    if control_errors:
        results.append(
            {
                "id": "CONTROL-DOCUMENTS",
                "expected": "ACCEPT",
                "observed": "REJECT",
                "status": "FAIL",
                "details": "; ".join(control_errors),
            }
        )
    for case in load_cases(POSITIVE_INDEX) + load_cases(NEGATIVE_INDEX):
        fixture = load(ROOT / str(case["fixture"]))
        candidate = copy.deepcopy(fixture)
        mutation = case.get("mutation")
        if isinstance(mutation, dict):
            apply_mutation(candidate, mutation)
        errors = validate_subject(str(case["subject"]), candidate)
        observed = "REJECT" if errors else "ACCEPT"
        expected = str(case["expected"])
        expected_error = str(case.get("expected_error", ""))
        expected_error_found = not expected_error or any(
            expected_error in error for error in errors
        )
        passed = observed == expected and expected_error_found
        results.append(
            {
                "id": str(case["id"]),
                "expected": expected,
                "observed": observed,
                "status": "PASS" if passed else "FAIL",
                "details": "accepted" if not errors else "; ".join(errors),
            }
        )
    failures = [item for item in results if item["status"] == "FAIL"]
    return {
        "document_type": "aset-component-conformance-results",
        "schema_version": 1,
        "profile": "0.1-rc1",
        "cases_total": len(results),
        "cases_passed": len(results) - len(failures),
        "cases_failed": len(failures),
        "verdict": "PASS" if not failures else "FAIL",
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(RESULTS.relative_to(ROOT)))
    args = parser.parse_args()
    result = build_results()
    for error in validate_schema(result, RESULTS_SCHEMA):
        print(f"COMPONENT_CONFORMANCE_ERROR={error}")
        return 1
    text = canonical_text(result)
    output = ROOT / args.output
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != text:
            print("COMPONENT_CONFORMANCE_RESULTS=DIFFERENT")
            return 1
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8", newline="\n")
    print(f"COMPONENT_CONFORMANCE={result['cases_passed']}/{result['cases_total']}")
    print(f"COMPONENT_CONFORMANCE_VERDICT={result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
