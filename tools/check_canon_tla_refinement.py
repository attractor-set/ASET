#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
RELATION_PATH = ROOT / "seed/canonical/assurance/canon-tla-refinement.json"
SCHEMA_PATH = ROOT / "seed/canonical/schemas/canon-tla-refinement.schema.json"
TARGET_PATH = ROOT / "seed/canonical/formal/SeedResolution.tla"
PROJECTION_PATH = ROOT / "seed/canonical/formal/SeedCanonProjection.tla"
PROOF_PATH = ROOT / "seed/canonical/formal/SeedCanonRefinementProofs.tla"
GENERATOR_PATH = ROOT / "tools/generate_canon_tla_projection.py"

EXPECTED_REQUIREMENT_STATUS = {
    "ASET-SEED-REQ-001": "PARTIAL_OPAQUE_BINDING",
    "ASET-SEED-REQ-002": "PROVED_IN_DECLARED_PROJECTION",
    "ASET-SEED-REQ-003": "PROVED_IN_DECLARED_PROJECTION",
    "ASET-SEED-REQ-004": "PROVED_IN_DECLARED_PROJECTION",
    "ASET-SEED-REQ-005": "PARTIAL_EXTERNAL_MATERIAL_BOUNDARY",
    "ASET-SEED-REQ-006": "PARTIAL_AUTHORITY_ABSTRACTION",
    "ASET-SEED-REQ-007": "ABSTRACTED_AUTHORITY_RECOGNITION",
    "ASET-SEED-REQ-008": "STRUCTURAL_BOUNDARY_OUTSIDE_STATE_MACHINE",
    "ASET-SEED-REQ-009": "PROVED_IN_DECLARED_PROJECTION",
    "ASET-SEED-REQ-010": "PARTIAL_NO_CONTENT_ADDRESS_PROOF",
    "ASET-SEED-REQ-011": "PARTIAL_TERMINAL_COMMITMENT_ABSTRACTION",
    "ASET-SEED-REQ-012": "META_OUTSIDE_BEHAVIORAL_MODEL",
}

EXPECTED_INVARIANT_STATUS = {
    "SEED-INV-001": "PROVED_IN_DECLARED_PROJECTION",
    "SEED-INV-002": "PROVED_IN_DECLARED_PROJECTION",
    "SEED-INV-003": "PROVED_IN_DECLARED_PROJECTION",
    "SEED-INV-004": "PARTIAL_OPAQUE_BINDING",
    "SEED-INV-005": "PARTIAL_AUTHORITY_ABSTRACTION",
    "SEED-INV-006": "ABSTRACTED_AUTHORITY_RECOGNITION",
    "SEED-INV-007": "STRUCTURAL_BOUNDARY_OUTSIDE_STATE_MACHINE",
    "SEED-INV-008": "PROVED_IN_DECLARED_PROJECTION",
    "SEED-INV-009": "PARTIAL_EXTERNAL_MATERIAL_BOUNDARY",
    "SEED-INV-010": "PARTIAL_NO_CONTENT_ADDRESS_PROOF",
    "SEED-INV-011": "PROVED_IN_DECLARED_PROJECTION",
    "SEED-INV-012": "PARTIAL_TERMINAL_COMMITMENT_ABSTRACTION",
}


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def theorems(text: str) -> set[str]:
    return set(
        re.findall(
            r"^THEOREM\s+([A-Za-z][A-Za-z0-9_]*)\s*==",
            text,
            flags=re.MULTILINE,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/canon-tla-refinement-check.json"),
    )
    args = parser.parse_args()

    errors: list[str] = []
    model = load(MODEL_PATH)
    relation = load(RELATION_PATH)
    schema = load(SCHEMA_PATH)

    validator = Draft202012Validator(schema)
    for error in sorted(
        validator.iter_errors(relation),
        key=lambda item: list(item.path),
    ):
        errors.append("schema: " + error.message)

    if relation["source_model"]["sha256"] != digest(MODEL_PATH):
        errors.append("source model digest mismatch")
    if relation["source_model"]["model_id"] != model["model_id"]:
        errors.append("source model id mismatch")
    if relation["source_model"]["version"] != model["version"]:
        errors.append("source model version mismatch")
    if relation["target_model"]["sha256"] != digest(TARGET_PATH):
        errors.append("target model digest mismatch")

    expected_requirements = [
        (item["id"], item["predicate"]) for item in model["requirements"]
    ]
    actual_requirements = [
        (item["id"], item["predicate"]) for item in relation["requirement_coverage"]
    ]
    if actual_requirements != expected_requirements:
        errors.append("requirement coverage differs from machine canon")

    actual_requirement_status = {
        item["id"]: item["status"] for item in relation["requirement_coverage"]
    }
    if actual_requirement_status != EXPECTED_REQUIREMENT_STATUS:
        errors.append("requirement projection status profile differs")

    expected_invariants = [item["id"] for item in model["invariants"]]
    actual_invariants = [item["id"] for item in relation["invariant_coverage"]]
    if actual_invariants != expected_invariants:
        errors.append("invariant coverage differs from machine canon")

    actual_invariant_status = {
        item["id"]: item["status"] for item in relation["invariant_coverage"]
    }
    if actual_invariant_status != EXPECTED_INVARIANT_STATUS:
        errors.append("invariant projection status profile differs")

    action_by_kind = {
        "REGISTER_REQUEST": "RegisterRequest",
        "SUBMIT_RESOLUTION": "SubmitResolution",
        "EVALUATE_RESOLUTION": "EvaluateResolution",
    }
    expected_operations = [
        (item["id"], item["kind"], action_by_kind[item["kind"]])
        for item in model["operations"]
    ]
    actual_operations = [
        (item["id"], item["kind"], item["tla_action"])
        for item in relation["operation_coverage"]
    ]
    if actual_operations != expected_operations:
        errors.append("operation coverage differs from machine canon")

    if set(relation["resolution_algebra_fields"]) != set(model["resolution_algebra"]):
        errors.append("resolution algebra field coverage differs from machine canon")

    abstraction_ids = [item["id"] for item in relation["abstractions"]]
    if abstraction_ids != [
        "OPAQUE_BINDING",
        "AUTHORITY_RECOGNITION_BOUNDARY",
        "TERMINAL_COMMITMENT_ORACLE",
        "ENVIRONMENT_CONFLICT_STATE",
    ]:
        errors.append("declared abstraction profile differs")

    projection_text = PROJECTION_PATH.read_text(encoding="utf-8") if PROJECTION_PATH.is_file() else ""
    if "EXTENDS SeedResolution" in projection_text or "INSTANCE SeedResolution" in projection_text:
        errors.append("generated projection depends on target SeedResolution module")
    if "V5 is a standalone projection" not in projection_text:
        errors.append("standalone projection marker missing")

    generator = subprocess.run(
        [sys.executable, str(GENERATOR_PATH), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if generator.returncode:
        errors.append("generated projection parity failed")

    proof_theorems = theorems(PROOF_PATH.read_text(encoding="utf-8"))
    final_theorem = relation["proof"]["final_theorem"]
    if final_theorem not in proof_theorems:
        errors.append("refinement final theorem is absent from proof module")

    report = {
        "document_type": "aset-canon-tla-refinement-check",
        "schema_version": 1,
        "source_model_sha256": digest(MODEL_PATH),
        "target_model_sha256": digest(TARGET_PATH),
        "projection_sha256": (
            digest(PROJECTION_PATH) if PROJECTION_PATH.is_file() else None
        ),
        "requirements_classified": len(actual_requirements),
        "invariants_classified": len(actual_invariants),
        "operations_classified": len(actual_operations),
        "resolution_algebra_fields_classified": len(
            relation["resolution_algebra_fields"]
        ),
        "projection_parity_returncode": generator.returncode,
        "final_theorem": final_theorem,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        "CANON_TLA_REQUIREMENTS="
        f"{len(actual_requirements)}/{len(expected_requirements)}"
    )
    print(f"CANON_TLA_INVARIANTS={len(actual_invariants)}/{len(expected_invariants)}")
    print(
        f"CANON_TLA_OPERATIONS={len(actual_operations)}/{len(expected_operations)}"
    )
    print(
        "CANON_TLA_RESOLUTION_ALGEBRA="
        f"{len(relation['resolution_algebra_fields'])}/"
        f"{len(model['resolution_algebra'])}"
    )
    print(
        "CANON_TLA_PROJECTION_PARITY="
        + ("PASS" if generator.returncode == 0 else "FAIL")
    )
    print("CANON_TLA_REFINEMENT_CHECK=" + report["verdict"])
    for error in errors:
        print("CANON_TLA_REFINEMENT_ERROR=" + error)

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
