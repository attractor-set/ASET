#!/usr/bin/env python3
from __future__ import annotations

from jsonschema import Draft202012Validator

from monade_attempt_profile_common import (
    ATTEMPT_SCHEMA,
    CASES,
    INVARIANTS,
    OBSERVATION_SCHEMA,
    PACKAGE,
    PACKAGE_FILES,
    PROFILE,
    ROOT,
    STATE_SPACE,
    canonical_digest,
    file_digest,
    load,
)


def main() -> int:
    errors: list[str] = []
    profile = load(PROFILE)
    package = load(PACKAGE)
    invariants = load(INVARIANTS)
    cases = load(CASES)
    state_space = load(STATE_SPACE)
    attempt_schema = load(ATTEMPT_SCHEMA)
    observation_schema = load(OBSERVATION_SCHEMA)

    if profile.get("canonical_digest") != canonical_digest(profile):
        errors.append("profile canonical digest mismatch")
    if profile.get("normative_for_seed") is not False:
        errors.append("profile must not be normative for Seed")
    if profile.get("required_for_seed_conformance") is not False:
        errors.append("profile must remain optional for Seed conformance")
    if profile.get("implementation_precedence") != "NONE":
        errors.append("implementation precedence differs")
    boundary = profile.get("seed_boundary", {})
    if not isinstance(boundary, dict) or boundary.get("seed_model_unchanged") is not True:
        errors.append("Seed boundary not preserved")
    master = profile.get("master_integration", {})
    if not isinstance(master, dict) or master.get("mode") != "READ_ONLY_LEARNING_OBSERVATION_PROJECTION":
        errors.append("Master projection boundary differs")
    if isinstance(master, dict) and master.get("master_specification_change_required") is not False:
        errors.append("Master specification dependency introduced")

    rows = package.get("files", [])
    if not isinstance(rows, list) or [item.get("path") for item in rows if isinstance(item, dict)] != list(PACKAGE_FILES):
        errors.append("profile package inventory differs")
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            errors.append("invalid profile package row")
            continue
        path = ROOT / str(item.get("path"))
        if not path.is_file() or item.get("sha256") != file_digest(path):
            errors.append(f"profile package byte mismatch:{item.get('path')}")

    invariant_rows = invariants.get("invariants", [])
    ids = [str(item.get("id")) for item in invariant_rows if isinstance(item, dict)]
    if len(ids) != 10 or len(ids) != len(set(ids)):
        errors.append("profile invariant inventory differs")

    case_rows = cases.get("cases", [])
    case_ids = [str(item.get("id")) for item in case_rows if isinstance(item, dict)]
    if len(case_ids) != 12 or len(case_ids) != len(set(case_ids)):
        errors.append("profile conformance case inventory differs")
    for case in case_rows if isinstance(case_rows, list) else []:
        if not isinstance(case, dict):
            errors.append("invalid profile conformance case")
            continue
        subject = case.get("subject")
        document = case.get("document")
        if subject == "attempt_record":
            schema = attempt_schema
        elif subject == "learning_observation":
            schema = observation_schema
        else:
            errors.append(f"unknown case subject:{case.get('id')}")
            continue
        if not isinstance(document, dict):
            errors.append(f"case document invalid:{case.get('id')}")
            continue
        # Negative cases may intentionally violate the schema. Ensure the schema itself is valid.
        Draft202012Validator.check_schema(schema)

    nodes = state_space.get("nodes", [])
    transitions = state_space.get("transitions", [])
    expected = state_space.get("expected", {})
    if not isinstance(nodes, list) or len(nodes) != expected.get("states"):
        errors.append("bounded state inventory differs")
    if not isinstance(transitions, list) or len(transitions) != expected.get("transitions"):
        errors.append("bounded transition inventory differs")

    seed_package = load(ROOT / "seed/canonical/CANON_PACKAGE.json")
    seed_paths = {str(item.get("path")) for item in seed_package.get("files", []) if isinstance(item, dict)}
    if any(path.startswith("aset/profiles/") for path in seed_paths):
        errors.append("optional profile leaked into Seed canon package")

    if errors:
        for error in errors:
            print(f"MONADE_ATTEMPT_PROFILE_ERROR={error}")
        print("MONADE_ATTEMPT_PROFILE_VALIDATION=FAIL")
        return 1
    print("MONADE_ATTEMPT_PROFILE_INVARIANTS=10")
    print("MONADE_ATTEMPT_PROFILE_CASES=12")
    print("MONADE_ATTEMPT_PROFILE_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
