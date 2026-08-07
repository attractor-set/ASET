#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
REGISTRY_PATH = ROOT / "seed/canonical/assurance/verification-registry.json"
TRACE_PATH = ROOT / "seed/canonical/assurance/proof-traceability.json"
TRACE_SCHEMA_PATH = ROOT / "seed/canonical/schemas/proof-traceability.schema.json"
FORMAL_MODEL_PATH = ROOT / "seed/canonical/formal/SeedResolution.tla"
PROOF_MODULE_PATH = ROOT / "seed/canonical/formal/SeedResolutionProofs.tla"
TLAPS_RUNNER_PATH = ROOT / "tools/run_tlaps.py"

TEMPORAL_THEOREMS = {
    "RequestsAppendOnly": "SpecImpliesRequestsAppendOnly",
    "TerminalRecordsImmutable": "SpecImpliesTerminalRecordsImmutable",
    "SeedStateChangesOnlyByRecognizedTransition": (
        "SpecImpliesSeedStateChangesOnlyByRecognizedTransition"
    ),
    "ConflictObservationPreservesSeedState": (
        "SpecImpliesConflictObservationPreservesSeedState"
    ),
}

STATE_SAFETY_THEOREM = "SpecImpliesAlwaysSeedStateSafety"


def strict(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value

    return result


def load(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict,
    )


def definitions(text: str) -> set[str]:
    return set(
        re.findall(
            r"^([A-Za-z][A-Za-z0-9_]*)\s*==",
            text,
            flags=re.MULTILINE,
        )
    )


def theorems(text: str) -> set[str]:
    return set(
        re.findall(
            r"^THEOREM\s+"
            r"([A-Za-z][A-Za-z0-9_]*)\s*==",
            text,
            flags=re.MULTILINE,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/proof-traceability-check.json"),
    )
    args = parser.parse_args()

    errors: list[str] = []

    model = load(MODEL_PATH)
    registry = load(REGISTRY_PATH)
    trace = load(TRACE_PATH)
    trace_schema = load(TRACE_SCHEMA_PATH)

    validator = Draft202012Validator(trace_schema)

    for error in sorted(
        validator.iter_errors(trace),
        key=lambda item: list(item.path),
    ):
        errors.append("proof-traceability schema: " + error.message)

    invariant_ids = {item["id"] for item in model["invariants"]}

    requirement_ids = {item["id"] for item in model["requirements"]}

    methods = {item["id"] for item in registry["verification_methods"]}

    tla_properties = {
        item["name"]: item
        for item in registry["formal_properties"]
        if item.get("engine") == "TLA_TLC"
    }

    model_operators = definitions(FORMAL_MODEL_PATH.read_text(encoding="utf-8"))

    proof_theorems = theorems(PROOF_MODULE_PATH.read_text(encoding="utf-8"))

    runner_text = TLAPS_RUNNER_PATH.read_text(encoding="utf-8")

    claims = trace["claims"]

    claim_ids = [claim["id"] for claim in claims]

    if len(claim_ids) != len(set(claim_ids)):
        errors.append("duplicate proof claim id")

    claims_by_id = {claim["id"]: claim for claim in claims}

    referenced_claims: set[str] = set()

    for invariant in model["invariants"]:
        refs = invariant.get(
            "assurance_refs",
            [],
        )

        if len(refs) != 1:
            errors.append(f"{invariant['id']} must have exactly one assurance_ref")
            continue

        claim_id = refs[0]
        referenced_claims.add(claim_id)

        claim = claims_by_id.get(claim_id)

        if claim is None:
            errors.append(
                f"{invariant['id']} references unknown proof claim {claim_id}"
            )
            continue

        if claim["seed_invariants"] != [invariant["id"]]:
            errors.append(f"{claim_id} does not bind exactly to {invariant['id']}")

        suffix = invariant["id"].removeprefix("SEED-INV-")

        expected_claim_id = f"ASET-PROOF-INV-{suffix}"

        if claim_id != expected_claim_id:
            errors.append(f"{invariant['id']} has unstable claim id {claim_id}")

    orphan_claims = set(claim_ids) - referenced_claims

    if orphan_claims:
        errors.append("orphan proof claims: " + ",".join(sorted(orphan_claims)))

    mapped_properties: set[str] = set()

    for claim in claims:
        claim_id = claim["id"]

        invariant = claim["seed_invariants"][0]

        if invariant not in invariant_ids:
            errors.append(f"{claim_id} references unknown invariant {invariant}")
            continue

        if claim["verification_method"] not in methods:
            errors.append(f"{claim_id} references unknown verification method")

        if claim["verification_method"] != "ASET-VERIFY-TLAPS-UNBOUNDED":
            errors.append(f"{claim_id} uses unexpected verification method")

        expected_properties = {
            name
            for name, prop in tla_properties.items()
            if invariant in prop.get("seed_invariants", [])
        }
        actual_properties = {item["operator"] for item in claim["formal_projection"]}
        status = claim["status"]
        if actual_properties != expected_properties:
            errors.append(f"{claim_id} formal-property mapping differs from registry")
        if status == "PROVED_IN_TLA" and not actual_properties:
            errors.append(f"{claim_id} claims PROVED_IN_TLA without a formal projection")
        if status == "PARTIAL_BOUNDARY" and invariant not in {
            "SEED-INV-006", "SEED-INV-007", "SEED-INV-009"
        }:
            errors.append(f"{claim_id} uses PARTIAL_BOUNDARY unexpectedly")

        expected_requirements = {
            requirement
            for name in expected_properties
            for requirement in tla_properties[name].get("seed_requirements", [])
        }

        actual_requirements = set(claim["seed_requirements"])

        unknown_requirements = actual_requirements - requirement_ids

        if unknown_requirements:
            errors.append(f"{claim_id} references unknown Seed requirements")

        if actual_requirements != expected_requirements:
            errors.append(
                f"{claim_id} requirement mapping differs from formal registry"
            )

        for projection in claim["formal_projection"]:
            operator = projection["operator"]
            kind = projection["kind"]
            theorem = projection["proof_theorem"]

            mapped_properties.add(operator)

            formal = tla_properties.get(operator)

            if formal is None:
                errors.append(
                    f"{claim_id} references unknown formal operator {operator}"
                )
                continue

            if formal["kind"] != kind:
                errors.append(f"{claim_id} kind mismatch for {operator}")

            if operator not in model_operators:
                errors.append(f"{operator} is absent from SeedResolution.tla")

            if kind == "STATE_INVARIANT":
                expected_theorem = STATE_SAFETY_THEOREM
            else:
                expected_theorem = TEMPORAL_THEOREMS.get(operator)

            if theorem != expected_theorem:
                errors.append(f"{claim_id} theorem mapping is wrong for {operator}")

            if theorem not in proof_theorems:
                errors.append(f"{theorem} is absent from SeedResolutionProofs.tla")

            if theorem not in runner_text:
                errors.append(
                    f"{theorem} is absent from run_tlaps.py final theorem set"
                )

    registered_properties = set(tla_properties)

    if mapped_properties != registered_properties:
        errors.append(
            "proof property coverage mismatch: "
            f"mapped={sorted(mapped_properties)} "
            f"registered={sorted(registered_properties)}"
        )

    report = {
        "document_type": ("aset-proof-traceability-check"),
        "schema_version": 1,
        "invariants_total": len(invariant_ids),
        "invariants_with_proof_refs": len(referenced_claims),
        "proof_claims": len(claim_ids),
        "registered_tla_properties": len(registered_properties),
        "mapped_tla_properties": len(mapped_properties),
        "orphan_claims": sorted(orphan_claims),
        "errors": errors,
        "verdict": ("PASS" if not errors else "FAIL"),
    }

    output = args.output if args.output.is_absolute() else ROOT / args.output

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            report,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"PROOF_TRACEABILITY_INVARIANTS={len(referenced_claims)}/{len(invariant_ids)}"
    )
    print(f"PROOF_TRACEABILITY_CLAIMS={len(claim_ids)}")
    print(
        "PROOF_TRACEABILITY_FORMAL_PROPERTIES="
        f"{len(mapped_properties)}/"
        f"{len(registered_properties)}"
    )
    print(f"PROOF_TRACEABILITY_ORPHANS={len(orphan_claims)}")
    print("PROOF_TRACEABILITY=" + report["verdict"])

    for error in errors:
        print("PROOF_TRACEABILITY_ERROR=" + error)

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
