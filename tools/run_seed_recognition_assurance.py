#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from tools.run_external_conformance import invoke, load, validate
    from tools.seed_recognition_assurance_cases import case_manifest, generate_cases, validate_cases
    from tools.seed_resolution_oracle import execute_case
except ModuleNotFoundError:
    from run_external_conformance import invoke, load, validate
    from seed_recognition_assurance_cases import case_manifest, generate_cases, validate_cases
    from seed_resolution_oracle import execute_case

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "assurance/seed-implementation-assurance/ASSURANCE_CONFORMANCE_PROFILE.json"
CASES_MANIFEST_PATH = ROOT / "assurance/seed-implementation-assurance/GENERATED_CASES_MANIFEST.json"
V60_PACKAGE_PATH = ROOT / "assurance/seed-recognition-boundary/ASSURANCE_PACKAGE.json"
CANON_PACKAGE_PATH = ROOT / "seed/canonical/CANON_PACKAGE.json"
CANON_CONFORMANCE_PROFILE_PATH = ROOT / "seed/canonical/conformance/conformance-profile.json"
ENVELOPE_SCHEMA_PATH = (
    ROOT / "seed/canonical/schemas/implementation-conformance-envelope.schema.json"
)
SEED_RESOLUTION_PATH = ROOT / "seed/canonical/formal/SeedResolution.tla"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def check_bindings(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    subject = profile["subject"]
    v60 = load(V60_PACKAGE_PATH)
    canon = load(CANON_PACKAGE_PATH)
    conformance = load(CANON_CONFORMANCE_PROFILE_PATH)

    checks = {
        "seed_canon_id": canon.get("canon_id"),
        "seed_canon_version": canon.get("canon_version"),
        "seed_canon_package_digest": canon.get("package_digest"),
        "seed_resolution_sha256": digest(SEED_RESOLUTION_PATH),
        "v60_assurance_id": v60.get("assurance_id"),
        "v60_assurance_package_digest": v60.get("package_digest"),
        "seed_conformance_protocol": conformance.get("protocol"),
        "seed_conformance_profile": conformance.get("profile_id"),
    }
    for field, actual in checks.items():
        if subject.get(field) != actual:
            errors.append(f"subject_binding:{field}:expected={subject.get(field)}:actual={actual}")
    if profile.get("normative") is not False or profile.get("normative_precedence") != "NONE":
        errors.append("profile_normative_boundary")
    return errors


def compare_case(case: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    expected_actual, expected_store = execute_case(case)
    errors: list[str] = []
    if response.get("case_id") != case["case_id"]:
        errors.append("case_id_mismatch")
    if response.get("actual") != expected_actual:
        errors.append("actual_mismatch")
    if response.get("final_store") != expected_store:
        errors.append("canonical_final_store_projection_mismatch")
    return {
        "case_id": case["case_id"],
        "category": case["description"].split("]", 1)[0].removeprefix("["),
        "pass": not errors,
        "errors": errors,
        "actual": response.get("actual"),
        "expected": expected_actual,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--adapter-cwd", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    profile = load(PROFILE_PATH)
    errors = check_bindings(profile)
    cases = generate_cases()
    generation_errors = validate_cases(cases)
    errors.extend("generated_case:" + item for item in generation_errors)
    generated_manifest = case_manifest(cases)
    committed_manifest = load(CASES_MANIFEST_PATH)
    if generated_manifest != committed_manifest:
        errors.append("generated_case_manifest_drift")

    protocol = profile["subject"]["seed_conformance_protocol"]
    envelope_schema = load(ENVELOPE_SCHEMA_PATH)
    rows: list[dict[str, Any]] = []
    implementation: Any = None
    deterministic_replay = False
    protocol_operations_verified: list[str] = []

    if not errors:
        try:
            description = invoke(
                args.adapter,
                {"protocol": protocol, "operation": "describe"},
                args.adapter_cwd,
                args.timeout,
            )
            validate(envelope_schema, "describe_response", description)
            implementation = description["implementation"]
            protocol_operations_verified.append("describe")

            probe_case = cases[0]
            probe = invoke(
                args.adapter,
                {"protocol": protocol, "operation": "execute_case", "case": probe_case},
                args.adapter_cwd,
                args.timeout,
            )
            validate(envelope_schema, "case_result", probe)
            probe_row = compare_case(probe_case, probe)
            if not probe_row["pass"]:
                errors.append("mandatory_execute_case_probe_failed")
            else:
                protocol_operations_verified.append("execute_case")

            request = {"protocol": protocol, "operation": "execute_cases", "cases": cases}
            first_batch = invoke(args.adapter, request, args.adapter_cwd, args.timeout)
            second_batch = invoke(args.adapter, request, args.adapter_cwd, args.timeout)
            validate(envelope_schema, "batch_response", first_batch)
            validate(envelope_schema, "batch_response", second_batch)
            deterministic_replay = first_batch == second_batch
            if not deterministic_replay:
                errors.append("adapter_batch_not_deterministic")
            else:
                protocol_operations_verified.append("execute_cases")

            results = first_batch.get("results", [])
            case_ids = [item.get("case_id") for item in results]
            expected_ids = [case["case_id"] for case in cases]
            if len(case_ids) != len(set(case_ids)):
                errors.append("adapter_duplicate_case_ids")
            if len(case_ids) != len(expected_ids) or set(case_ids) != set(expected_ids):
                errors.append("adapter_case_set_mismatch")
            else:
                indexed = {item["case_id"]: item for item in results}
                for item in results:
                    validate(envelope_schema, "case_result", item)
                rows = [compare_case(case, indexed[case["case_id"]]) for case in cases]
                if not all(row["pass"] for row in rows):
                    errors.append("one_or_more_assurance_cases_failed")
        except Exception as exc:
            errors.append(f"adapter_failure:{type(exc).__name__}:{exc}")

    category_totals = Counter(row["category"] for row in rows)
    category_passed = Counter(row["category"] for row in rows if row["pass"])
    category_report = {
        name: {"passed": category_passed[name], "total": total}
        for name, total in sorted(category_totals.items())
    }
    passed = sum(bool(row["pass"]) for row in rows)
    report = {
        "document_type": "aset-seed-recognition-assurance-results",
        "schema_version": 1,
        "profile": profile["profile_id"],
        "normative": False,
        "verdict_scope": profile["verdict_scope"],
        "implementation": implementation,
        "subject": profile["subject"],
        "generated_case_set_digest": generated_manifest["case_set_digest"],
        "cases_total": len(cases),
        "cases_executed": len(rows),
        "cases_passed": passed,
        "category_results": category_report,
        "protocol_operations_verified": protocol_operations_verified,
        "deterministic_replay": deterministic_replay,
        "canonical_final_store_projection_required": True,
        "claim_boundary": profile["claim_boundary"],
        "errors": errors,
        "results": rows,
        "pass": not errors and len(rows) == len(cases) and passed == len(cases),
    }

    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"SEED_RECOGNITION_ASSURANCE_CASES={passed}/{len(cases)}")
    print(f"SEED_RECOGNITION_ASSURANCE_CASE_SET_DIGEST={generated_manifest['case_set_digest']}")
    print(
        "SEED_RECOGNITION_ASSURANCE_DETERMINISTIC_REPLAY="
        + ("PASS" if deterministic_replay else "FAIL")
    )
    print(
        "SEED_RECOGNITION_ASSURANCE_CANONICAL_PROJECTION="
        + ("PASS" if rows and all(row["pass"] for row in rows) else "FAIL")
    )
    print("SEED_RECOGNITION_ASSURANCE_VERDICT=" + ("PASS" if report["pass"] else "FAIL"))
    for error in errors:
        print("SEED_RECOGNITION_ASSURANCE_ERROR=" + error)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
