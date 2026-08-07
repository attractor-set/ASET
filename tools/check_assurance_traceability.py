#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TLAPS_FINAL_THEOREMS = (
    "SpecImpliesAlwaysSeedStateSafety",
    "SpecImpliesRequestsAppendOnly",
    "SpecImpliesTerminalRecordsImmutable",
    "SpecImpliesSeedStateChangesOnlyByRecognizedTransition",
    "SpecImpliesConflictObservationPreservesSeedState",
)


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def cfg_sections(path: Path) -> dict[str, list[str]]:
    sections = {"INVARIANTS": [], "PROPERTIES": []}
    active: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line in sections:
            active = line
            continue
        if active:
            if not line:
                continue
            if re.match(r"^[A-Z][A-Z_ ]+$", line):
                active = None
                continue
            sections[active].append(line)
    return sections


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-report", type=Path, default=Path("dist/seed-model-check.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("dist/assurance-traceability.json")
    )
    args = parser.parse_args()

    model = load(ROOT / "seed/canonical/source/seed-model.json")
    registry = load(ROOT / "seed/canonical/assurance/verification-registry.json")
    gates_doc = load(ROOT / "seed/canonical/assurance/repository-release-gates.json")
    profile = load(ROOT / "seed/canonical/conformance/conformance-profile.json")

    method_ids = {item["id"] for item in registry["verification_methods"]}
    gate_ids = {item["id"] for item in gates_doc["gates"]}
    requirement_ids = {item["id"] for item in model["requirements"]}
    invariant_ids = {item["id"] for item in model["invariants"]}
    errors: list[str] = []

    tlaps_method = next(
        (
            item
            for item in registry["verification_methods"]
            if item["id"] == "ASET-VERIFY-TLAPS-UNBOUNDED"
        ),
        None,
    )

    if tlaps_method is None:
        errors.append("missing unbounded TLAPS verification method")
    elif "ASET-GATE-028" not in tlaps_method.get(
        "gate_ids",
        [],
    ):
        errors.append(
            "unbounded TLAPS verification method is not bound to ASET-GATE-028"
        )

    proof_path = ROOT / "seed/canonical/formal/SeedResolutionProofs.tla"

    if not proof_path.is_file():
        errors.append("missing SeedResolutionProofs.tla")
    else:
        proof_text = proof_path.read_text(encoding="utf-8")

        if "EXTENDS SeedResolution, TLAPS" not in proof_text:
            errors.append("SeedResolutionProofs.tla does not import TLAPS")

        for theorem in TLAPS_FINAL_THEOREMS:
            pattern = (
                rf"^THEOREM "
                rf"{re.escape(theorem)} ==\s*$"
            )

            if (
                re.search(
                    pattern,
                    proof_text,
                    flags=re.MULTILINE,
                )
                is None
            ):
                errors.append(f"missing TLAPS final theorem: {theorem}")

    for method in registry["verification_methods"]:
        for gate_id in method.get("gate_ids", []):
            if gate_id not in gate_ids:
                errors.append(
                    f"verification method {method['id']} references unknown gate {gate_id}"
                )
        if not method.get("gate_ids") and not method.get("external_profile_gate"):
            errors.append(
                f"verification method {method['id']} has no gate or external boundary"
            )

    for group in ("requirements", "invariants"):
        for item in model[group]:
            unknown = sorted(set(item["verification"]) - method_ids)
            if unknown:
                errors.append(
                    f"{item['id']} references unknown verification methods: {unknown}"
                )

    formal = {item["name"]: item for item in registry["formal_properties"]}
    tla_formal = {
        name: item for name, item in formal.items() if item.get("engine") == "TLA_TLC"
    }
    cfg = cfg_sections(ROOT / "seed/canonical/formal/SeedResolution.cfg")
    cfg_names = set(cfg["INVARIANTS"]) | set(cfg["PROPERTIES"])
    if cfg_names != set(tla_formal):
        errors.append(
            f"TLA property registry mismatch: cfg={sorted(cfg_names)} registry={sorted(tla_formal)}"
        )
    for name in cfg["INVARIANTS"]:
        if tla_formal.get(name, {}).get("kind") != "STATE_INVARIANT":
            errors.append(f"TLA invariant {name} is not registered as STATE_INVARIANT")
    for name in cfg["PROPERTIES"]:
        if tla_formal.get(name, {}).get("kind") != "TEMPORAL_PROPERTY":
            errors.append(f"TLA property {name} is not registered as TEMPORAL_PROPERTY")

    for item in formal.values():
        unknown_invariants = sorted(
            set(item.get("seed_invariants", [])) - invariant_ids
        )
        unknown_requirements = sorted(
            set(item.get("seed_requirements", [])) - requirement_ids
        )
        if unknown_invariants:
            errors.append(
                f"formal property {item['name']} maps unknown invariants: {unknown_invariants}"
            )
        if unknown_requirements:
            errors.append(
                f"formal property {item['name']} maps unknown requirements: {unknown_requirements}"
            )

    model_report_path = ROOT / args.model_report
    if not model_report_path.is_file():
        errors.append(f"missing finite-state model report: {args.model_report}")
    else:
        model_report = load(model_report_path)
        if set(model_report.get("invariants", [])) != set(tla_formal):
            errors.append(
                "finite-state model property set differs from TLA/TLC verification registry"
            )
        if model_report.get("verdict") != "PASS":
            errors.append("finite-state model report is not PASS")
        if model_report.get("saturated") is not True:
            errors.append("finite-state model report is not saturated")

    formal_invariant_coverage = {
        identifier
        for item in formal.values()
        for identifier in item.get("seed_invariants", [])
    }
    if formal_invariant_coverage != invariant_ids:
        errors.append(
            f"formal invariant coverage incomplete: missing={sorted(invariant_ids - formal_invariant_coverage)}"
        )
    formal_requirement_coverage = {
        identifier
        for item in formal.values()
        for identifier in item.get("seed_requirements", [])
    }
    if formal_requirement_coverage != requirement_ids:
        errors.append(
            f"formal requirement coverage incomplete: missing={sorted(requirement_ids - formal_requirement_coverage)}"
        )

    operation_counts: dict[str, Counter[str]] = {}
    for entry in profile["cases"]:
        case = load(ROOT / entry["path"])
        kind = case.get("candidate", {}).get("kind")
        if not isinstance(kind, str):
            errors.append(f"case {entry['case_id']} has no candidate kind")
            continue
        operation_counts.setdefault(kind, Counter())[entry["polarity"]] += 1

    declared_kinds = {item["kind"] for item in model["operations"]}
    if set(operation_counts) - declared_kinds:
        errors.append(
            "cases reference undeclared operation kinds: "
            f"{sorted(set(operation_counts) - declared_kinds)}"
        )

    policy = registry["operation_case_policy"]
    exceptions = {
        (item["operation_kind"], item["missing_polarity"]): item
        for item in policy.get("declared_exceptions", [])
    }
    for kind in sorted(declared_kinds):
        counts = operation_counts.get(kind, Counter())
        for polarity, required in (
            ("positive", policy.get("require_positive_case", False)),
            ("negative", policy.get("require_negative_case", False)),
        ):
            if (
                required
                and counts[polarity] == 0
                and (kind, polarity) not in exceptions
            ):
                errors.append(f"operation {kind} has no {polarity} conformance case")

    report = {
        "document_type": "aset-assurance-traceability-report",
        "verification_methods": len(method_ids),
        "requirements": len(requirement_ids),
        "invariants": len(invariant_ids),
        "formal_properties": sorted(formal),
        "tla_state_invariants": cfg["INVARIANTS"],
        "tla_temporal_properties": cfg["PROPERTIES"],
        "formal_seed_requirements_covered": sorted(formal_requirement_coverage),
        "formal_seed_invariants_covered": sorted(formal_invariant_coverage),
        "operation_case_counts": {
            key: dict(sorted(value.items()))
            for key, value in sorted(operation_counts.items())
        },
        "declared_operation_coverage_exceptions": list(exceptions.values()),
        "tlaps_proof_module": ("seed/canonical/formal/SeedResolutionProofs.tla"),
        "tlaps_final_theorems": list(TLAPS_FINAL_THEOREMS),
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

    print(f"ASSURANCE_REQUIREMENTS={report['requirements']}")
    print(f"ASSURANCE_INVARIANTS={report['invariants']}")
    print(f"ASSURANCE_FORMAL_PROPERTIES={len(formal)}")
    print(f"ASSURANCE_TLA_PROPERTIES={len(tla_formal)}")
    print(f"ASSURANCE_TLAPS_FINAL_THEOREMS={len(TLAPS_FINAL_THEOREMS)}")
    print("ASSURANCE_TRACEABILITY=" + report["verdict"])
    for error in errors:
        print("ASSURANCE_TRACEABILITY_ERROR=" + error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
