#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "ASET-IMPLEMENTATION-CONFORMANCE-V1"


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


def invoke(command: str, request: dict[str, Any], cwd: Path, timeout: float) -> dict[str, Any]:
    completed = subprocess.run(
        shlex.split(command),
        cwd=cwd,
        input=json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode:
        raise RuntimeError(f"adapter exit {completed.returncode}: {completed.stderr.strip()}")
    try:
        value = json.loads(completed.stdout, object_pairs_hook=strict)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"adapter returned invalid or multiple JSON values: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("adapter response must be an object")
    return value


def validate(schema: dict[str, Any], definition: str, value: dict[str, Any]) -> None:
    validator = Draft202012Validator({"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]})
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.message}" for error in errors
        )
        raise RuntimeError(f"adapter response schema failure ({definition}): {rendered}")


def check_case(case: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    if response["case_id"] != case["case_id"]:
        raise RuntimeError(f"case response mismatch:{case['case_id']}")
    actual = response["actual"]
    expected = case["expected"]
    passed = actual == expected
    state = response["final_state"]
    assertion_errors: list[str] = []
    for assertion in case.get("postconditions", []):
        cursor: Any = state
        try:
            for part in assertion["path"].split("/")[1:]:
                cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            assertion_errors.append(f"{assertion['path']}:unresolvable:{type(exc).__name__}")
            passed = False
            continue
        if cursor != assertion["equals"]:
            assertion_errors.append(f"{assertion['path']}:value_mismatch")
            passed = False
    return {
        "case_id": case["case_id"],
        "pass": passed,
        "actual": actual,
        "expected": expected,
        "assertion_errors": assertion_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canon-root", type=Path, default=ROOT)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--adapter-cwd", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    canon = args.canon_root.resolve()
    profile = load(canon / "seed/canonical/conformance/conformance-profile.json")
    envelope_schema = load(
        canon / "seed/canonical/schemas/implementation-conformance-envelope.schema.json"
    )
    cases: list[dict[str, Any]] = []
    for entry in profile["cases"]:
        path = canon / entry["path"]
        if digest(path) != entry["sha256"]:
            raise RuntimeError(f"case digest mismatch:{entry['case_id']}")
        case = load(path)
        if case.get("case_id") != entry["case_id"]:
            raise RuntimeError(f"case identity mismatch:{entry['case_id']}")
        cases.append(case)

    description = invoke(
        args.adapter,
        {"protocol": PROTOCOL, "operation": "describe"},
        args.adapter_cwd,
        args.timeout,
    )
    validate(envelope_schema, "describe_response", description)

    probe_case = cases[0]
    probe = invoke(
        args.adapter,
        {"protocol": PROTOCOL, "operation": "execute_case", "case": probe_case},
        args.adapter_cwd,
        args.timeout,
    )
    validate(envelope_schema, "case_result", probe)
    probe_result = check_case(probe_case, probe)
    if not probe_result["pass"]:
        raise RuntimeError("mandatory execute_case probe failed")

    request = {"protocol": PROTOCOL, "operation": "execute_cases", "cases": cases}
    first_batch = invoke(args.adapter, request, args.adapter_cwd, args.timeout)
    second_batch = invoke(args.adapter, request, args.adapter_cwd, args.timeout)
    validate(envelope_schema, "batch_response", first_batch)
    validate(envelope_schema, "batch_response", second_batch)
    if first_batch != second_batch:
        raise RuntimeError("adapter batch result is not deterministic across exact replay")

    results = first_batch["results"]
    case_ids = [item["case_id"] for item in results]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("adapter returned duplicate case_id values")
    expected_ids = [case["case_id"] for case in cases]
    if set(case_ids) != set(expected_ids) or len(case_ids) != len(expected_ids):
        raise RuntimeError("adapter result set does not exactly match requested cases")
    indexed = {item["case_id"]: item for item in results}
    rows = [check_case(case, indexed[case["case_id"]]) for case in cases]

    report = {
        "document_type": "aset-external-implementation-conformance-results",
        "protocol": PROTOCOL,
        "implementation": description["implementation"],
        "operations_verified": ["describe", "execute_case", "execute_cases"],
        "deterministic_replay": True,
        "cases_total": len(rows),
        "cases_passed": sum(bool(row["pass"]) for row in rows),
        "pass": all(bool(row["pass"]) for row in rows),
        "results": rows,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"IMPLEMENTATION_CONFORMANCE={report['cases_passed']}/{report['cases_total']}")
    print("IMPLEMENTATION_CONFORMANCE_PROTOCOL_OPERATIONS=3/3")
    print("IMPLEMENTATION_CONFORMANCE_DETERMINISTIC_REPLAY=PASS")
    print("IMPLEMENTATION_CONFORMANCE_VERDICT=" + ("PASS" if report["pass"] else "FAIL"))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
