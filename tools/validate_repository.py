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
MIGRATION = ROOT / "seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json"
FINDINGS = ROOT / "audit/FINDING_CLOSURE_MATRIX.json"
SKOS = ROOT / "seed/canonical/terminology/seed.skos.ttl"
SHAPES = ROOT / "seed/canonical/shapes/seed.shacl.ttl"
ONTOLOGY = ROOT / "seed/canonical/ontology/seed.ttl"
TBX = ROOT / "seed/canonical/terminology/seed.tbx"

REQUIRED_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ru.md",
    ROOT / "README.pt-BR.md",
    ROOT / "docs/repository/PRODUCTION_READINESS.md",
    ROOT / "docs/repository/RELEASE_PROCESS.md",
    ROOT / "docs/repository/BLACK_BOX_AUDIT_METHOD.md",
    ROOT / "docs/repository/OPERATIONS_RUNBOOK.md",
    ROOT / "docs/repository/DEPENDENCY_POLICY.md",
    ROOT / "audit/PDCA_HISTORY.md",
    ROOT / "seed/canonical/decisions/ADR-001-semantic-canon-authority.md",
]


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )


def unique(values) -> bool:
    materialized = list(values)
    return len(materialized) == len(set(materialized))


def validate_instance(path: Path, schema_path: Path, errors: list[str]) -> object:
    instance = strict_load(path)
    schema = strict_load(schema_path)
    validator = Draft202012Validator(schema)
    for error in sorted(
        validator.iter_errors(instance),
        key=lambda item: list(item.absolute_path),
    ):
        errors.append(
            f"schema:{path.relative_to(ROOT)}:"
            + "/".join(str(x) for x in error.absolute_path)
            + ":"
            + error.message
        )
    return instance


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*.json")):
        if any(
            part in {".git", ".venv", "dist", "__pycache__"}
            for part in path.relative_to(ROOT).parts
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
    migration = strict_load(MIGRATION)
    findings = strict_load(FINDINGS)

    concept_ids = [concept["id"] for concept in model["concepts"]]
    requirement_ids = [requirement["id"] for requirement in model["requirements"]]
    invariant_ids = [invariant["id"] for invariant in model["invariants"]]

    if not unique(concept_ids):
        errors.append("duplicate concept identifier")
    if not unique(requirement_ids):
        errors.append("duplicate requirement identifier")
    if not unique(invariant_ids):
        errors.append("duplicate invariant identifier")
    if model["languages"] != ["ru", "en", "pt-BR"]:
        errors.append("language set must be ru, en, pt-BR")

    gate_ids = [gate["id"] for gate in gates["gates"]]
    if not unique(gate_ids):
        errors.append("duplicate repository gate identifier")
    if len(gate_ids) < 10 or not all(gate["mandatory"] for gate in gates["gates"]):
        errors.append("repository gate registry is incomplete or non-mandatory")

    limitation_ids = [item["id"] for item in limitations["limitations"]]
    if not unique(limitation_ids):
        errors.append("duplicate limitation identifier")

    summary = migration.get("summary", {})
    expected_migration = {
        "rc11_requirements": 26,
        "rc11_transition_kinds": 18,
        "rc11_schemas": 39,
        "unclassified": 0,
    }
    for key, expected in expected_migration.items():
        if summary.get(key) != expected:
            errors.append(f"migration summary {key} must equal {expected}")

    if findings.get("open_blocking_findings") != []:
        errors.append("open blocking repository audit findings exist")

    if (
        status["repository_production_readiness"]
        != "DOCUMENTATION_REPOSITORY_PRODUCTION_READY"
    ):
        errors.append("repository readiness status is not production-ready")
    if status["seed_runtime_production"] != "HOLD":
        errors.append("runtime production boundary must remain HOLD")
    if status["next_seed_status"] != "BOOTSTRAP_SCAFFOLD_NOT_RELEASED":
        errors.append("rc12 development boundary changed unexpectedly")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing required document:{path.relative_to(ROOT)}")

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

    commands = [
        [sys.executable, "tools/generate_editions.py", "--check"],
        [sys.executable, "tools/check_language.py"],
        [sys.executable, "tools/verify_frozen_release.py"],
        [sys.executable, "tools/materialize_rc11.py", "--check"],
        [sys.executable, "tools/rebuild_manifest.py", "--check"],
    ]

    for command in commands:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(
                "command:"
                + " ".join(command)
                + "\n"
                + result.stdout
                + result.stderr
            )

    if errors:
        for error in errors:
            print(f"VALIDATION_ERROR={error}")
        return 1

    print(f"CONCEPTS={len(concept_ids)}")
    print(f"REQUIREMENTS={len(requirement_ids)}")
    print(f"INVARIANTS={len(invariant_ids)}")
    print(f"REPOSITORY_GATES={len(gate_ids)}")
    print(f"ASSURANCE_LIMITATIONS={len(limitation_ids)}")
    print("OPEN_BLOCKING_FINDINGS=0")
    print("REPOSITORY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
