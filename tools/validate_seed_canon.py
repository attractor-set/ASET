#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from rdflib import Graph
from referencing import Registry, Resource

try:
    from tools.seed_resolution_oracle import execute_case
except ModuleNotFoundError:
    from seed_resolution_oracle import execute_case

ROOT = Path(__file__).resolve().parents[1]


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON member: {key}")
        out[key] = value
    return out


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def registry_for(paths: list[Path]) -> Registry:
    registry = Registry()
    for path in paths:
        schema = load(path)
        identifier = schema.get("$id")
        if isinstance(identifier, str):
            registry = registry.with_resource(
                identifier,
                Resource.from_contents(schema),
            )
    return registry


def validate_document(
    errors: list[str],
    document_path: str,
    schema_path: str,
    label: str,
) -> Any:
    document = load(ROOT / document_path)
    schema = load(ROOT / schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema reports the precise schema defect.
        errors.append(f"{label}_schema_invalid:{exc}")
        return document
    for error in Draft202012Validator(schema).iter_errors(document):
        location = "/" + "/".join(map(str, error.absolute_path))
        errors.append(f"{label}_schema:{location}:{error.message}")
    return document


def json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValueError("invalid JSON pointer")
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                index = int(token)
            except ValueError as exc:
                raise KeyError(pointer) from exc
            if index < 0 or index >= len(current):
                raise KeyError(pointer)
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise KeyError(pointer)
            current = current[token]
        else:
            raise KeyError(pointer)
    return current


def validate_postconditions(
    errors: list[str], case_id: str, case: dict[str, Any], store: dict[str, Any]
) -> None:
    for condition in case.get("postconditions", []):
        pointer = condition["path"]
        try:
            actual = json_pointer(store, pointer)
        except (KeyError, ValueError):
            errors.append(f"case_postcondition:{case_id}:{pointer}:path_missing")
            continue
        if actual != condition["equals"]:
            errors.append(f"case_postcondition:{case_id}:{pointer}:value_mismatch")


def main() -> int:
    errors: list[str] = []
    model = validate_document(
        errors,
        "seed/canonical/source/seed-model.json",
        "seed/canonical/schemas/seed-model.schema.json",
        "model",
    )
    for group in ("concepts", "requirements", "invariants"):
        ids = [item["id"] for item in model[group]]
        if len(ids) != len(set(ids)):
            errors.append("duplicate:" + group)
    kinds = [item["kind"] for item in model["operations"]]
    expected_kinds = [
        "REGISTER_REQUEST",
        "SUBMIT_RESOLUTION",
        "EVALUATE_RESOLUTION",
    ]
    if kinds != expected_kinds:
        errors.append("operation_catalogue")
    roles = [item.get("role") for item in model["operations"]]
    if roles != ["STATE_TRANSITION", "STATE_TRANSITION", "OBSERVER"]:
        errors.append("operation_roles")
    if model["resolution_algebra"] != {
        "values": ["UNKNOWN", "ALLOW", "BLOCK"],
        "derived": "UNKNOWN",
        "stored_terminal": ["ALLOW", "BLOCK"],
        "effect_permitted_if": "ALLOW",
        "fail_closed_values": ["UNKNOWN", "BLOCK"],
        "conflict_result": "UNKNOWN",
        "unknown_semantics": model["resolution_algebra"]["unknown_semantics"],
    }:
        errors.append("resolution_algebra")
    if model["implementation_boundary"]["implementation_precedence"] != "NONE":
        errors.append("implementation_precedence")

    protocol = validate_document(
        errors,
        "seed/canonical/protocol/protocol-profile.json",
        "seed/canonical/schemas/protocol-profile.schema.json",
        "protocol_profile",
    )
    schema_paths = [ROOT / item["path"] for item in protocol["schemas"]]
    if protocol["schema_count"] != len(protocol["schemas"]):
        errors.append("protocol_schema_count")
    active_dir = ROOT / "seed/canonical/protocol/schemas"
    physical_schemas = {path.resolve() for path in active_dir.glob("*.json")}
    declared_schemas = {path.resolve() for path in schema_paths}
    if physical_schemas != declared_schemas:
        errors.append(
            "protocol_schema_surface:"
            f"undeclared={sorted(path.name for path in physical_schemas - declared_schemas)}:"
            f"missing={sorted(path.name for path in declared_schemas - physical_schemas)}"
        )
    for item, path in zip(protocol["schemas"], schema_paths, strict=True):
        if not path.is_file() or digest(path) != item["sha256"]:
            errors.append("protocol_schema_digest:" + item["name"])
            continue
        try:
            Draft202012Validator.check_schema(load(path))
        except Exception as exc:
            errors.append("invalid_schema:" + item["name"] + ":" + str(exc))

    registry = registry_for(schema_paths)
    case_schema = load(
        ROOT / "seed/canonical/protocol/schemas/conformance-case.schema.json"
    )
    profile = validate_document(
        errors,
        "seed/canonical/conformance/conformance-profile.json",
        "seed/canonical/schemas/conformance-profile.schema.json",
        "conformance_profile",
    )
    validator = Draft202012Validator(case_schema, registry=registry)
    seen: set[str] = set()
    for item in profile["cases"]:
        path = ROOT / item["path"]
        if item["case_id"] in seen:
            errors.append("duplicate_case:" + item["case_id"])
        seen.add(item["case_id"])
        if not path.is_file() or digest(path) != item["sha256"]:
            errors.append("case_digest:" + item["case_id"])
            continue
        case = load(path)
        if case.get("case_id") != item["case_id"]:
            errors.append("case_identity:" + item["case_id"])
        for error in validator.iter_errors(case):
            location = "/" + "/".join(map(str, error.absolute_path))
            errors.append(
                "case_schema:" + item["case_id"] + ":" + location + ":" + error.message
            )
        if case["expected"] != item["expected"]:
            errors.append("case_expected:" + item["case_id"])
        try:
            actual, final_store = execute_case(case)
        except Exception as exc:
            errors.append("case_execution:" + item["case_id"] + ":" + str(exc))
        else:
            if actual != case["expected"]:
                errors.append("case_oracle:" + item["case_id"])
            validate_postconditions(errors, item["case_id"], case, final_store)

    validate_document(
        errors,
        "seed/canonical/assurance/invariant-coverage.json",
        "seed/canonical/schemas/invariant-coverage.schema.json",
        "invariant_coverage",
    )
    validate_document(
        errors,
        "seed/canonical/assurance/limitations.json",
        "seed/canonical/schemas/assurance-limitations.schema.json",
        "assurance_limitations",
    )
    validate_document(
        errors,
        "seed/canonical/assurance/canon-tla-refinement.json",
        "seed/canonical/schemas/canon-tla-refinement.schema.json",
        "canon_tla_refinement",
    )
    validate_document(
        errors,
        "seed/canonical/assurance/repository-release-gates.json",
        "seed/canonical/schemas/repository-release-gates.schema.json",
        "repository_release_gates",
    )
    validate_document(
        errors,
        "REPOSITORY_STATUS.json",
        "seed/canonical/schemas/repository-status.schema.json",
        "repository_status",
    )
    try:
        Graph().parse(ROOT / "seed/canonical/shapes/seed.shacl.ttl", format="turtle")
    except Exception as exc:
        errors.append("seed_shacl_parse:" + str(exc))

    if errors:
        for error in errors:
            print("SEED_CANON_ERROR=" + error)
        return 1
    print(f"SEED_CONCEPTS={len(model['concepts'])}")
    print(f"SEED_REQUIREMENTS={len(model['requirements'])}")
    print(f"SEED_INVARIANTS={len(model['invariants'])}")
    print(f"SEED_OPERATIONS={len(model['operations'])}")
    state_transition_count = sum(
        item.get("role") == "STATE_TRANSITION" for item in model["operations"]
    )
    observer_count = sum(item.get("role") == "OBSERVER" for item in model["operations"])
    print(f"SEED_STATE_TRANSITIONS={state_transition_count}")
    print(f"SEED_OBSERVERS={observer_count}")
    print(f"SEED_CONFORMANCE_CASES={profile['case_count']}")
    print("SEED_CANON_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
