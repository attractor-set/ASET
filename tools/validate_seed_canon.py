#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from rdflib import Graph
from referencing import Registry, Resource

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
    kinds = [item["kind"] for item in model["transitions"]]
    expected_kinds = [
        "OPEN_RESOLUTION",
        "RESOLVE_ACCEPT",
        "RESOLVE_DENY",
        "ESCALATE_UNKNOWN",
    ]
    if kinds != expected_kinds:
        errors.append("transition_catalogue")
    lattice = model["decision_lattice"]
    if lattice["initial"] != "UNKNOWN" or lattice["terminal"] != [
        "ACCEPT",
        "DENY",
    ]:
        errors.append("decision_lattice")
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

    validate_document(
        errors,
        "seed/canonical/assurance/limitations.json",
        "seed/canonical/schemas/assurance-limitations.schema.json",
        "assurance_limitations",
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
    print(f"SEED_TRANSITIONS={len(model['transitions'])}")
    print(f"SEED_CONFORMANCE_CASES={profile['case_count']}")
    print("SEED_CANON_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
