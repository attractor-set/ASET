#!/usr/bin/env python3
from __future__ import annotations

import argparse

from monade_attempt_profile_common import (
    ATTEMPT_SCHEMA,
    CASES,
    CONFORMANCE_RESULTS,
    OBSERVATION_SCHEMA,
    canonical_text,
    load,
    schema_error_codes,
    validate_attempt_semantics,
    validate_observation_semantics,
)


def evaluate(case: dict[str, object]) -> dict[str, object]:
    document = case["document"]
    assert isinstance(document, dict)
    subject = str(case["subject"])
    if subject == "attempt_record":
        errors = schema_error_codes(load(ATTEMPT_SCHEMA), document)
        if not errors:
            errors.extend(validate_attempt_semantics(document))
    else:
        errors = schema_error_codes(load(OBSERVATION_SCHEMA), document)
        if not errors:
            errors.extend(validate_observation_semantics(document))
    errors = sorted(set(errors))
    observed_valid = not errors
    expected_valid = bool(case["expected_valid"])
    expected_codes = set(map(str, case.get("expected_error_codes", [])))
    passed = observed_valid == expected_valid and expected_codes <= set(errors)
    return {
        "case_id": case["id"],
        "expected_valid": expected_valid,
        "observed_valid": observed_valid,
        "error_codes": errors,
        "passed": passed,
    }


def build_results() -> dict[str, object]:
    cases = load(CASES)["cases"]
    assert isinstance(cases, list)
    rows = [evaluate(case) for case in cases if isinstance(case, dict)]
    passed = sum(bool(row["passed"]) for row in rows)
    return {
        "document_type": "aset-monade-attempt-profile-conformance-results",
        "profile_id": "ASET-MONADE-ATTEMPT-EVIDENCE-V1",
        "cases_total": len(rows),
        "cases_passed": passed,
        "cases_failed": len(rows) - passed,
        "results": rows,
        "verdict": "PASS" if passed == len(rows) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = build_results()
    content = canonical_text(results)
    if args.check:
        if not CONFORMANCE_RESULTS.is_file() or CONFORMANCE_RESULTS.read_text(encoding="utf-8") != content:
            print("MONADE_ATTEMPT_CONFORMANCE_PARITY=DIFFERENT")
            return 1
    else:
        CONFORMANCE_RESULTS.write_text(content, encoding="utf-8", newline="\n")
    print(f"MONADE_ATTEMPT_CONFORMANCE={results['cases_passed']}/{results['cases_total']}")
    print(f"MONADE_ATTEMPT_CONFORMANCE_VERDICT={results['verdict']}")
    return 0 if results["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
