from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator
from pyshacl import validate as shacl_validate
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]

MODEL = ROOT / "seed/canonical/source/seed-model.json"
MODEL_SCHEMA = ROOT / "seed/canonical/schemas/seed-model.schema.json"
STATUS = ROOT / "REPOSITORY_STATUS.json"
STATUS_SCHEMA = ROOT / "seed/canonical/schemas/repository-status.schema.json"
GATES = ROOT / "seed/canonical/assurance/repository-release-gates.json"
GATES_SCHEMA = ROOT / "seed/canonical/schemas/repository-release-gates.schema.json"
LIMITATIONS = ROOT / "seed/canonical/assurance/limitations.json"
LIMITATIONS_SCHEMA = ROOT / "seed/canonical/schemas/assurance-limitations.schema.json"
FREEZE_ENTRY = ROOT / "seed/canonical/release/RC12_FREEZE_ENTRY.json"
FREEZE_ENTRY_SCHEMA = ROOT / "seed/canonical/schemas/rc12-freeze-entry.schema.json"
MIGRATION = ROOT / "seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json"
FINDINGS = ROOT / "audit/FINDING_CLOSURE_MATRIX.json"
SKOS = ROOT / "seed/canonical/terminology/seed.skos.ttl"
SHAPES = ROOT / "seed/canonical/shapes/seed.shacl.ttl"
ONTOLOGY = ROOT / "seed/canonical/ontology/seed.ttl"
TBX = ROOT / "seed/canonical/terminology/seed.tbx"

REQUIRED_DOCS = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "README.ru.md",
    ROOT / "README.pt-BR.md",
    ROOT / "docs/repository/PRODUCTION_READINESS.md",
    ROOT / "docs/repository/RELEASE_PROCESS.md",
    ROOT / "docs/repository/BLACK_BOX_AUDIT_METHOD.md",
    ROOT / "docs/repository/OPERATIONS_RUNBOOK.md",
    ROOT / "docs/repository/DEPENDENCY_POLICY.md",
    ROOT / "docs/runtime/PRODUCTION_PROFILE.md",
    ROOT / "docs/runtime/DEPLOYMENT_CHECKLIST.md",
    ROOT / "docs/runtime/THREAT_MODEL.md",
    ROOT / "seed/canonical/release/RC12_RELEASE_CANDIDATE.json",
    ROOT / "seed/canonical/release/RC12_FREEZE_ENTRY.json",
    ROOT / "audit/PDCA_HISTORY.md",
    ROOT / "seed/canonical/decisions/ADR-001-semantic-canon-authority.md",
    ROOT / "seed/canonical/protocol/protocol-profile.json",
    ROOT / "seed/canonical/conformance/conformance-profile.json",
    ROOT / "seed/canonical/formal/SeedRC12.tla",
    ROOT / "seed/canonical/formal/SeedRC12.cfg",
]


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


def unique(values) -> bool:
    materialized = list(values)
    return len(materialized) == len(set(materialized))


def validate_instance(path: Path, schema_path: Path, errors: list[str]) -> object:
    instance = strict_load(path)
    schema = strict_load(schema_path)
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(x) for x in error.absolute_path)
        errors.append(f"schema:{path.relative_to(ROOT)}:{location}:{error.message}")
    return instance


def run_check(command: list[str], errors: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        errors.append("command:" + " ".join(command) + "\n" + result.stdout + result.stderr)


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*.json")):
        relative_parts = path.relative_to(ROOT).parts
        if any(
            part in {".git", ".venv", "dist", "__pycache__"}
            for part in relative_parts
        ):
            continue
        try:
            strict_load(path)
        except Exception as error:
            errors.append(f"json:{path.relative_to(ROOT)}:{error}")

    model = validate_instance(MODEL, MODEL_SCHEMA, errors)
    status = validate_instance(STATUS, STATUS_SCHEMA, errors)
    gates = validate_instance(GATES, GATES_SCHEMA, errors)
    limitations = validate_instance(LIMITATIONS, LIMITATIONS_SCHEMA, errors)
    freeze_entry = validate_instance(FREEZE_ENTRY, FREEZE_ENTRY_SCHEMA, errors)
    migration = strict_load(MIGRATION)
    findings = strict_load(FINDINGS)

    concept_ids = [item["id"] for item in model["concepts"]]
    requirement_ids = [item["id"] for item in model["requirements"]]
    invariant_ids = [item["id"] for item in model["invariants"]]
    transition_ids = [item["id"] for item in model["transitions"]]
    for label, values in (
        ("concept", concept_ids),
        ("requirement", requirement_ids),
        ("invariant", invariant_ids),
        ("transition", transition_ids),
    ):
        if not unique(values):
            errors.append(f"duplicate {label} identifier")

    if model["languages"] != ["ru", "en", "pt-BR"]:
        errors.append("language set must be ru, en, pt-BR")
    if model["status"] != "RC12_RELEASE_CANDIDATE_READY":
        errors.append("machine canon is not an rc12 release candidate")
    observed_counts = (
        len(concept_ids),
        len(requirement_ids),
        len(invariant_ids),
        len(transition_ids),
    )
    if observed_counts != (27, 40, 37, 18):
        errors.append("rc12 canonical counts differ from the frozen candidate profile")

    gate_ids = [gate["id"] for gate in gates["gates"]]
    if not unique(gate_ids) or len(gate_ids) != 23:
        errors.append("repository gate registry must contain 23 unique gates")
    if not gates.get("fail_closed") or not all(gate["mandatory"] for gate in gates["gates"]):
        errors.append("repository gates must be mandatory and fail closed")

    limitation_ids = [item["id"] for item in limitations["limitations"]]
    if not unique(limitation_ids) or len(limitation_ids) != 7:
        errors.append("limitation registry must contain seven unique entries")
    external_audit_pending = any(
        item["id"] == "LIMIT-005" and item["status"] == "PENDING"
        for item in limitations["limitations"]
    )
    if not external_audit_pending:
        errors.append("external third-party audit limitation must remain PENDING")

    if (
        freeze_entry.get("technical_status") != "READY_FOR_EXACT_BYTE_FREEZE"
        or freeze_entry.get("owner_freeze_approval") != "PENDING"
        or freeze_entry.get("exact_byte_freeze") != "NOT_EXECUTED"
        or freeze_entry.get("blocking_findings") != 0
    ):
        errors.append("rc12 technical freeze entry is not correctly bounded")

    expected_migration = {
        "rc11_requirements": 26,
        "rc11_transition_kinds": 18,
        "rc11_schemas": 39,
        "fully_migrated_to_rc12": 83,
        "deferred_with_explicit_disposition": 0,
        "unclassified": 0,
    }
    summary = migration.get("summary", {})
    for key, expected in expected_migration.items():
        if summary.get(key) != expected:
            errors.append(f"migration summary {key} must equal {expected}")
    if migration.get("target_status") != "RC12_RELEASE_CANDIDATE_READY":
        errors.append("migration target is not the rc12 release candidate")

    if findings.get("open_blocking_findings") != []:
        errors.append("open blocking repository audit findings exist")

    expected_status = {
        "repository_production_readiness": "DOCUMENTATION_AND_BOUNDED_RUNTIME_PRODUCTION_READY",
        "seed_runtime_production": "PRODUCTION_READY_SINGLE_NODE_SQLITE_PROFILE",
        "next_seed_status": "RC12_RELEASE_CANDIDATE_READY",
        "machine_readable_canon": "NORMATIVE_CANON_COMPLETE",
        "external_third_party_audit": "PENDING",
    }
    for key, expected in expected_status.items():
        if status.get(key) != expected:
            errors.append(f"repository status {key} must equal {expected}")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing required document:{path.relative_to(ROOT)}")

    canonical_schemas = ROOT / "seed/canonical/protocol/schemas"
    runtime_schemas = ROOT / "src/aset_seed/schemas"
    canonical_names = sorted(path.name for path in canonical_schemas.glob("*.json"))
    runtime_names = sorted(path.name for path in runtime_schemas.glob("*.json"))
    if len(canonical_names) != 39 or canonical_names != runtime_names:
        errors.append("canonical/runtime schema inventory mismatch")
    else:
        for name in canonical_names:
            if (canonical_schemas / name).read_bytes() != (runtime_schemas / name).read_bytes():
                errors.append(f"canonical/runtime schema bytes differ:{name}")

    for path in [SKOS, SHAPES, ONTOLOGY]:
        try:
            Graph().parse(path, format="turtle")
        except Exception as error:
            errors.append(f"rdf:{path.relative_to(ROOT)}:{error}")
    try:
        ET.parse(TBX)
    except Exception as error:
        errors.append(f"tbx:{error}")
    try:
        conforms, _, report = shacl_validate(
            data_graph=str(SKOS),
            shacl_graph=str(SHAPES),
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
        )
        if not conforms:
            errors.append(f"shacl:{report}")
    except Exception as error:
        errors.append(f"shacl-execution:{error}")

    for command in (
        [sys.executable, "tools/generate_editions.py", "--check"],
        [sys.executable, "tools/generate_semantic_views.py", "--check"],
        [sys.executable, "tools/check_language.py"],
        [sys.executable, "tools/validate_rc12_canon.py"],
        [sys.executable, "tools/build_rc12_envelope.py", "--check"],
        [sys.executable, "tools/verify_frozen_release.py"],
        [sys.executable, "tools/materialize_rc11.py", "--check"],
        [sys.executable, "tools/materialize_rc11.py", "--check-git"],
        [sys.executable, "tools/rebuild_manifest.py", "--check"],
    ):
        run_check(command, errors)

    if errors:
        for error in errors:
            print(f"VALIDATION_ERROR={error}")
        return 1

    print(f"CONCEPTS={len(concept_ids)}")
    print(f"REQUIREMENTS={len(requirement_ids)}")
    print(f"INVARIANTS={len(invariant_ids)}")
    print(f"TRANSITIONS={len(transition_ids)}")
    print("PROTOCOL_SCHEMAS=39")
    print("RC11_TO_RC12_MIGRATION=83/83")
    print(f"REPOSITORY_GATES={len(gate_ids)}")
    print(f"ASSURANCE_LIMITATIONS={len(limitation_ids)}")
    print("REPOSITORY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
