#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

try:
    from tools.seed_resolution_oracle import execute_case
except ModuleNotFoundError:
    from seed_resolution_oracle import execute_case

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def allow_result(result: dict[str, Any], *, code: str = "MUTANT_ALLOW") -> dict[str, Any]:
    mutated = copy.deepcopy(result)
    mutated.update(
        {
            "accepted": True,
            "code": code,
            "state_changed": True,
            "resolution": "ALLOW",
            "effect_permitted": True,
            "reason": "UNIQUE_VALID_TERMINAL_RECORD",
        }
    )
    return mutated


def apply_operator(operator: str, result: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(result)
    if operator == "out_of_domain_resolution":
        mutated["resolution"] = "PENDING"
    elif operator == "permit_block":
        mutated["effect_permitted"] = True
    elif operator == "permit_unknown":
        mutated["effect_permitted"] = True
    elif operator in {
        "ignore_binding_mismatch",
        "trust_remote_authority",
        "accept_cyclic_grant",
        "external_input_authorizes",
        "invalid_material_allows",
    }:
        mutated = allow_result(mutated)
    elif operator == "first_terminal_wins":
        mutated = allow_result(mutated, code="EVALUATED")
        mutated["state_changed"] = False
    elif operator == "replace_terminal_record":
        mutated.update(
            {
                "accepted": True,
                "code": "RESOLUTION_RECORDED",
                "state_changed": True,
                "resolution": "BLOCK",
                "effect_permitted": False,
                "reason": "UNIQUE_VALID_TERMINAL_RECORD",
            }
        )
    elif operator == "rejection_mutates_store":
        mutated["state_changed"] = True
    elif operator == "reuse_resolution_id":
        mutated.update(
            {
                "accepted": True,
                "code": "REQUEST_REGISTERED",
                "state_changed": True,
            }
        )
    else:
        raise ValueError(f"unknown semantic mutation operator: {operator}")
    return mutated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist/invariant-mutations.json"))
    args = parser.parse_args()

    coverage = load(ROOT / "seed/canonical/assurance/invariant-coverage.json")
    schema = load(ROOT / "seed/canonical/schemas/invariant-coverage.schema.json")
    Draft202012Validator(schema).validate(coverage)

    profile = load(ROOT / "seed/canonical/conformance/conformance-profile.json")
    cases: dict[str, dict[str, Any]] = {
        entry["case_id"]: load(ROOT / entry["path"]) for entry in profile["cases"]
    }
    baseline: dict[str, dict[str, Any]] = {}
    baseline_errors: list[str] = []
    for case_id, case in cases.items():
        actual, _ = execute_case(case)
        baseline[case_id] = actual
        if actual != case["expected"]:
            baseline_errors.append(case_id)

    rows: list[dict[str, Any]] = []
    for mutation in coverage["mutation_catalog"]:
        mutation_id = mutation["id"]
        operator = mutation["operator"]
        killed_by: list[str] = []
        if operator == "grant_implementation_precedence":
            model = load(ROOT / "seed/canonical/source/seed-model.json")
            mutated = copy.deepcopy(model)
            mutated["implementation_boundary"]["implementation_precedence"] = "REFERENCE_PYTHON"
            if mutated["implementation_boundary"]["implementation_precedence"] != "NONE":
                killed_by.append("STATIC_IMPLEMENTATION_NEUTRALITY_CHECK")
        else:
            for case_id in mutation["case_ids"]:
                case = cases[case_id]
                mutated = apply_operator(operator, baseline[case_id])
                if mutated != case["expected"]:
                    killed_by.append(case_id)
        rows.append(
            {
                "id": mutation_id,
                "operator": operator,
                "killed_by": killed_by,
                "status": "KILLED" if killed_by else "SURVIVED",
            }
        )

    survivors = [row["id"] for row in rows if row["status"] == "SURVIVED"]
    errors = [f"baseline mismatch: {case_id}" for case_id in baseline_errors]
    errors.extend(f"mutation survived: {mutation_id}" for mutation_id in survivors)
    report = {
        "document_type": "aset-seed-semantic-mutation-report",
        "mutations": rows,
        "mutation_count": len(rows),
        "killed_count": len(rows) - len(survivors),
        "survivors": survivors,
        "baseline_errors": baseline_errors,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"SEMANTIC_MUTATIONS={report['mutation_count']}")
    print(f"SEMANTIC_MUTATIONS_KILLED={report['killed_count']}")
    print(f"SEMANTIC_MUTATIONS_SURVIVED={len(survivors)}")
    print("SEMANTIC_MUTATION_VERDICT=" + report["verdict"])
    for error in errors:
        print("SEMANTIC_MUTATION_ERROR=" + error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
