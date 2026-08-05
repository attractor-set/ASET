#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def cfg_invariants(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: list[str] = []
    active = False
    for raw in lines:
        line = raw.strip()
        if line == "INVARIANTS":
            active = True
            continue
        if active:
            if not line or re.match(r"^[A-Z][A-Z_ ]+$", line):
                break
            result.append(line)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-report", type=Path, default=Path("dist/rc12-model-check.json"))
    parser.add_argument("--output", type=Path, default=Path("dist/assurance-traceability.json"))
    args = parser.parse_args()

    model = load(ROOT / "seed/canonical/source/seed-model.json")
    registry = load(ROOT / "seed/canonical/assurance/verification-registry.json")
    gates_doc = load(ROOT / "seed/canonical/assurance/repository-release-gates.json")
    profile = load(ROOT / "seed/canonical/conformance/conformance-profile.json")

    method_ids = {item["id"] for item in registry["verification_methods"]}
    gate_ids = {item["id"] for item in gates_doc["gates"]}
    errors: list[str] = []

    for method in registry["verification_methods"]:
        for gate_id in method.get("gate_ids", []):
            if gate_id not in gate_ids:
                errors.append(f"verification method {method['id']} references unknown gate {gate_id}")
        if not method.get("gate_ids") and not method.get("external_profile_gate"):
            errors.append(f"verification method {method['id']} has no gate or external boundary")

    for group in ("requirements", "invariants"):
        for item in model[group]:
            unknown = sorted(set(item["verification"]) - method_ids)
            if unknown:
                errors.append(f"{item['id']} references unknown verification methods: {unknown}")

    formal = {item["name"]: item for item in registry["formal_properties"]}
    cfg_names = cfg_invariants(ROOT / "seed/canonical/formal/SeedRC12.cfg")
    if set(cfg_names) != set(formal):
        errors.append(f"TLA invariant registry mismatch: cfg={cfg_names} registry={sorted(formal)}")
    invariant_ids = {item["id"] for item in model["invariants"]}
    for item in formal.values():
        unknown = sorted(set(item["seed_invariants"]) - invariant_ids)
        if unknown:
            errors.append(f"formal property {item['name']} maps unknown invariants: {unknown}")

    model_report_path = ROOT / args.model_report
    if not model_report_path.is_file():
        errors.append(f"missing bounded model report: {args.model_report}")
    else:
        model_report = load(model_report_path)
        if set(model_report.get("invariants", [])) != set(formal):
            errors.append("bounded model property set differs from verification registry")
        if model_report.get("verdict") != "PASS":
            errors.append("bounded model report is not PASS")

    transition_counts: dict[str, Counter[str]] = {}
    for entry in profile["cases"]:
        case = load(ROOT / entry["path"])
        kind = case.get("candidate", {}).get("kind")
        if not isinstance(kind, str):
            errors.append(f"case {entry['case_id']} has no candidate kind")
            continue
        transition_counts.setdefault(kind, Counter())[entry["polarity"]] += 1

    declared_kinds = {item["kind"] for item in model["transitions"]}
    if set(transition_counts) - declared_kinds:
        errors.append(f"cases reference undeclared transition kinds: {sorted(set(transition_counts)-declared_kinds)}")

    policy = registry["transition_case_policy"]
    exceptions = {
        (item["transition_kind"], item["missing_polarity"]): item
        for item in policy.get("declared_exceptions", [])
    }
    for kind in sorted(declared_kinds):
        counts = transition_counts.get(kind, Counter())
        for polarity, required in (
            ("positive", policy.get("require_positive_case", False)),
            ("negative", policy.get("require_negative_case", False)),
        ):
            if required and counts[polarity] == 0 and (kind, polarity) not in exceptions:
                errors.append(f"transition {kind} has no {polarity} conformance case")

    report = {
        "document_type": "aset-assurance-traceability-report",
        "verification_methods": len(method_ids),
        "requirements": len(model["requirements"]),
        "invariants": len(model["invariants"]),
        "formal_properties": sorted(formal),
        "formal_seed_invariants_covered": sorted(
            {identifier for item in formal.values() for identifier in item["seed_invariants"]}
        ),
        "transition_case_counts": {
            key: dict(sorted(value.items())) for key, value in sorted(transition_counts.items())
        },
        "declared_transition_coverage_exceptions": list(exceptions.values()),
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"ASSURANCE_REQUIREMENTS={report['requirements']}")
    print(f"ASSURANCE_INVARIANTS={report['invariants']}")
    print(f"ASSURANCE_FORMAL_PROPERTIES={len(formal)}")
    print("ASSURANCE_TRACEABILITY=" + report["verdict"])
    for error in errors:
        print("ASSURANCE_TRACEABILITY_ERROR=" + error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
