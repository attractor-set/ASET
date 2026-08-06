#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-report", type=Path, default=Path("dist/invariant-mutations.json"))
    parser.add_argument("--output", type=Path, default=Path("dist/invariant-coverage.json"))
    args = parser.parse_args()

    model = load(ROOT / "seed/canonical/source/seed-model.json")
    profile = load(ROOT / "seed/canonical/conformance/conformance-profile.json")
    registry = load(ROOT / "seed/canonical/assurance/verification-registry.json")
    coverage = load(ROOT / "seed/canonical/assurance/invariant-coverage.json")
    schema = load(ROOT / "seed/canonical/schemas/invariant-coverage.schema.json")

    errors: list[str] = []
    for error in Draft202012Validator(schema).iter_errors(coverage):
        location = "/" + "/".join(map(str, error.absolute_path))
        errors.append(f"coverage schema {location}: {error.message}")

    requirement_ids = {item["id"] for item in model["requirements"]}
    invariant_ids = {item["id"] for item in model["invariants"]}
    transition_ids = {item["id"] for item in model["transitions"]}
    case_entries = {item["case_id"]: item for item in profile["cases"]}
    formal_names = {item["name"] for item in registry["formal_properties"]}
    mutation_ids = {item["id"] for item in coverage["mutation_catalog"]}

    covered_requirements = {item["id"] for item in coverage["requirements"]}
    covered_invariants = {item["id"] for item in coverage["invariants"]}
    covered_transitions = {item["id"] for item in coverage["transitions"]}
    if covered_requirements != requirement_ids:
        errors.append(
            f"requirement coverage mismatch: missing={sorted(requirement_ids-covered_requirements)} "
            f"extra={sorted(covered_requirements-requirement_ids)}"
        )
    if covered_invariants != invariant_ids:
        errors.append(
            f"invariant coverage mismatch: missing={sorted(invariant_ids-covered_invariants)} "
            f"extra={sorted(covered_invariants-invariant_ids)}"
        )
    if covered_transitions != transition_ids:
        errors.append(
            f"transition coverage mismatch: missing={sorted(transition_ids-covered_transitions)} "
            f"extra={sorted(covered_transitions-transition_ids)}"
        )

    referenced_formal: set[str] = set()
    referenced_cases: set[str] = set()
    referenced_mutations: set[str] = set()
    for group in ("requirements", "invariants"):
        for entry in coverage[group]:
            unknown_formal = set(entry["formal_properties"]) - formal_names
            unknown_cases = set(entry["conformance_cases"]) - set(case_entries)
            unknown_mutations = set(entry["semantic_mutations"]) - mutation_ids
            if unknown_formal:
                errors.append(f"{entry['id']} unknown formal properties: {sorted(unknown_formal)}")
            if unknown_cases:
                errors.append(f"{entry['id']} unknown conformance cases: {sorted(unknown_cases)}")
            if unknown_mutations:
                errors.append(f"{entry['id']} unknown semantic mutations: {sorted(unknown_mutations)}")
            referenced_formal.update(entry["formal_properties"])
            referenced_cases.update(entry["conformance_cases"])
            referenced_mutations.update(entry["semantic_mutations"])
            for invariant_id in entry.get("invariants", []):
                if invariant_id not in invariant_ids:
                    errors.append(f"{entry['id']} references unknown invariant {invariant_id}")

    for entry in coverage["transitions"]:
        for case_id in entry["positive_cases"]:
            if case_id not in case_entries or case_entries[case_id]["polarity"] != "positive":
                errors.append(f"{entry['id']} invalid positive case {case_id}")
        for case_id in entry["negative_cases"]:
            if case_id not in case_entries or case_entries[case_id]["polarity"] != "negative":
                errors.append(f"{entry['id']} invalid negative case {case_id}")
        referenced_cases.update(entry["positive_cases"])
        referenced_cases.update(entry["negative_cases"])

    if formal_names - referenced_formal:
        errors.append(f"orphan formal properties: {sorted(formal_names-referenced_formal)}")
    if mutation_ids - referenced_mutations:
        errors.append(f"orphan semantic mutations: {sorted(mutation_ids-referenced_mutations)}")
    if set(case_entries) - referenced_cases:
        errors.append(f"orphan conformance cases: {sorted(set(case_entries)-referenced_cases)}")

    mutation_report_path = ROOT / args.mutation_report
    if not mutation_report_path.is_file():
        errors.append(f"missing mutation report: {args.mutation_report}")
        mutation_report = {}
    else:
        mutation_report = load(mutation_report_path)
        if mutation_report.get("verdict") != "PASS":
            errors.append("semantic mutation report is not PASS")
        report_ids = {item["id"] for item in mutation_report.get("mutations", [])}
        if report_ids != mutation_ids:
            errors.append("semantic mutation report catalogue differs from coverage catalogue")

    report = {
        "document_type": "aset-seed-invariant-coverage-report",
        "requirements_total": len(requirement_ids),
        "requirements_covered": len(covered_requirements & requirement_ids),
        "invariants_total": len(invariant_ids),
        "invariants_covered": len(covered_invariants & invariant_ids),
        "transitions_total": len(transition_ids),
        "transitions_covered": len(covered_transitions & transition_ids),
        "formal_properties": len(formal_names),
        "conformance_cases": len(case_entries),
        "semantic_mutations": len(mutation_ids),
        "semantic_mutations_killed": mutation_report.get("killed_count", 0),
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"INVARIANT_COVERAGE_REQUIREMENTS={report['requirements_covered']}/{report['requirements_total']}")
    print(f"INVARIANT_COVERAGE_INVARIANTS={report['invariants_covered']}/{report['invariants_total']}")
    print(f"INVARIANT_COVERAGE_TRANSITIONS={report['transitions_covered']}/{report['transitions_total']}")
    print(f"INVARIANT_COVERAGE_FORMAL_PROPERTIES={report['formal_properties']}")
    print(f"INVARIANT_COVERAGE_CONFORMANCE_CASES={report['conformance_cases']}")
    print(f"INVARIANT_COVERAGE_MUTATIONS={report['semantic_mutations_killed']}/{report['semantic_mutations']}")
    print("INVARIANT_COVERAGE=" + report["verdict"])
    for error in errors:
        print("INVARIANT_COVERAGE_ERROR=" + error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
