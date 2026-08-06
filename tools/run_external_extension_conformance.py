#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = "seed/canonical/conformance/extension-conformance-protocol.json"
BINDING_SCHEMA_PATH = "seed/canonical/schemas/extension-seed-binding.schema.json"
MAP_SCHEMA_PATH = "seed/canonical/schemas/extension-conformance-map.schema.json"
ENVELOPE_SCHEMA_PATH = "seed/canonical/schemas/extension-conformance-envelope.schema.json"


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


def canonical_bytes(value: object) -> bytes:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    return (text + "\n").encode("utf-8")


def validate_document(schema: dict[str, Any], value: Any, label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.message}"
            for error in errors
        )
        raise RuntimeError(f"{label} schema failure: {rendered}")


def validate_envelope(
    envelope_schema: dict[str, Any],
    definition: str,
    value: dict[str, Any],
) -> None:
    schema = {
        "$ref": f"#/$defs/{definition}",
        "$defs": envelope_schema["$defs"],
    }
    validate_document(schema, value, f"adapter {definition}")


def invoke(
    command: str,
    request: dict[str, Any],
    cwd: Path,
    timeout: float,
) -> dict[str, Any]:
    completed = subprocess.run(
        shlex.split(command),
        cwd=cwd,
        input=json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n",
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"adapter exit {completed.returncode}: {message}")
    try:
        value = json.loads(completed.stdout, object_pairs_hook=strict)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"adapter returned invalid or multiple JSON values: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("adapter response must be an object")
    return value


def verify_seed_binding(
    canon_root: Path,
    extension_root: Path,
    binding_path: Path,
    binding_schema: dict[str, Any],
    protocol_id: str,
) -> dict[str, Any]:
    binding = load(binding_path)
    validate_document(binding_schema, binding, "Seed binding")

    package_path = canon_root / "seed/canonical/CANON_PACKAGE.json"
    package = load(package_path)
    expected = {
        "canon_id": package["canon_id"],
        "canon_version": package["canon_version"],
        "canon_package_file_digest": digest(package_path),
        "canon_package_internal_digest": package["package_digest"],
        "extension_conformance_protocol": protocol_id,
    }
    for key, value in expected.items():
        if binding.get(key) != value:
            raise RuntimeError(
                f"Seed binding mismatch for {key}: expected {value!r}, "
                f"got {binding.get(key)!r}"
            )
    map_path = extension_root / binding["extension_conformance_map"]
    if not map_path.is_file():
        raise RuntimeError("extension conformance map is missing")
    return binding


def verify_extension_package(extension_root: Path) -> tuple[dict[str, Any], set[str]]:
    package_path = extension_root / "extension/canonical/CANON_PACKAGE.json"
    package = load(package_path)
    if package.get("implementation_precedence") != "NONE":
        raise RuntimeError("extension package grants implementation precedence")

    declared_digest = package.get("package_digest")
    unsigned = dict(package)
    unsigned.pop("package_digest", None)
    actual_digest = "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    if actual_digest != declared_digest:
        raise RuntimeError("extension package self-digest mismatch")

    packaged_paths: set[str] = set()
    for item in package.get("files", []):
        relative = item["path"]
        path = extension_root / relative
        if not path.is_file():
            raise RuntimeError(f"extension package file missing: {relative}")
        if digest(path) != item["sha256"]:
            raise RuntimeError(f"extension package digest mismatch: {relative}")
        if relative in packaged_paths:
            raise RuntimeError(f"duplicate extension package path: {relative}")
        packaged_paths.add(relative)
    return package, packaged_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canon-root", type=Path, default=ROOT)
    parser.add_argument("--extension-root", type=Path, required=True)
    parser.add_argument("--binding", default="upstream/ASET_SEED_BINDING.json")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--adapter-cwd", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    canon_root = args.canon_root.resolve()
    extension_root = args.extension_root.resolve()
    adapter_cwd = (args.adapter_cwd or extension_root).resolve()

    protocol = load(canon_root / PROTOCOL_PATH)
    protocol_id = protocol["protocol_id"]
    protocol_schema = load(
        canon_root / "seed/canonical/schemas/extension-conformance-protocol.schema.json"
    )
    binding_schema = load(canon_root / BINDING_SCHEMA_PATH)
    map_schema = load(canon_root / MAP_SCHEMA_PATH)
    envelope_schema = load(canon_root / ENVELOPE_SCHEMA_PATH)
    validate_document(protocol_schema, protocol, "extension conformance protocol")

    binding_path = extension_root / args.binding
    binding = verify_seed_binding(
        canon_root,
        extension_root,
        binding_path,
        binding_schema,
        protocol_id,
    )
    package, packaged_paths = verify_extension_package(extension_root)

    required_package_paths = {
        args.binding,
        binding["extension_conformance_map"],
    }
    missing_from_package = sorted(required_package_paths - packaged_paths)
    if missing_from_package:
        raise RuntimeError(
            "extension package omits upstream conformance material: "
            + ", ".join(missing_from_package)
        )

    mapping = load(extension_root / binding["extension_conformance_map"])
    validate_document(map_schema, mapping, "extension conformance map")
    if mapping["protocol_id"] != protocol_id:
        raise RuntimeError("extension conformance map protocol mismatch")
    if mapping["extension_id"] != package["extension_id"]:
        raise RuntimeError("extension conformance map extension_id mismatch")
    if mapping["extension_canon_id"] != package["canon_id"]:
        raise RuntimeError("extension conformance map canon_id mismatch")
    if mapping["seed_binding"] != args.binding:
        raise RuntimeError("extension conformance map binding path mismatch")
    if mapping["adapter"] != args.adapter:
        raise RuntimeError("adapter command differs from the packaged conformance map")

    roles = {item["role_id"]: item["expected"] for item in protocol["boundary_roles"]}
    mapped_roles = [item["role_id"] for item in mapping["mappings"]]
    if len(mapped_roles) != len(set(mapped_roles)):
        raise RuntimeError("extension conformance map contains duplicate role_id values")
    if set(mapped_roles) != set(roles):
        raise RuntimeError("extension conformance map does not cover the exact Seed role set")

    cases: list[dict[str, Any]] = []
    role_by_case: dict[str, str] = {}
    for item in mapping["mappings"]:
        relative = item["case_path"]
        if relative not in packaged_paths:
            raise RuntimeError(f"mapped case is outside extension canon package: {relative}")
        case_path = extension_root / relative
        if digest(case_path) != item["case_sha256"]:
            raise RuntimeError(f"mapped case digest mismatch: {relative}")
        case = load(case_path)
        case_id = case.get("case_id")
        if not isinstance(case_id, str):
            raise RuntimeError(f"mapped case has no case_id: {relative}")
        if case_id in role_by_case:
            raise RuntimeError(f"one extension case maps to multiple Seed roles: {case_id}")
        role_by_case[case_id] = item["role_id"]
        cases.append(case)

    description = invoke(
        args.adapter,
        {"protocol": protocol_id, "operation": "describe"},
        adapter_cwd,
        args.timeout,
    )
    validate_envelope(envelope_schema, "describe_response", description)
    expected_extension = {
        "extension_id": package["extension_id"],
        "canon_id": package["canon_id"],
        "version": package["extension_version"],
        "package_digest": package["package_digest"],
    }
    if description["extension"] != expected_extension:
        raise RuntimeError("adapter extension identity differs from canon package")
    described_binding = description["seed_binding"]
    for key in described_binding:
        if described_binding[key] != binding[key]:
            raise RuntimeError(f"adapter Seed binding differs for {key}")

    probe = invoke(
        args.adapter,
        {"protocol": protocol_id, "operation": "execute_case", "case": cases[0]},
        adapter_cwd,
        args.timeout,
    )
    validate_envelope(envelope_schema, "case_result", probe)
    if probe["case_id"] != cases[0]["case_id"]:
        raise RuntimeError("mandatory execute_case probe returned a different case_id")
    if probe["actual"] != cases[0]["expected"]:
        raise RuntimeError("mandatory execute_case probe differs from extension expectation")

    request = {"protocol": protocol_id, "operation": "execute_cases", "cases": cases}
    first_batch = invoke(args.adapter, request, adapter_cwd, args.timeout)
    second_batch = invoke(args.adapter, request, adapter_cwd, args.timeout)
    validate_envelope(envelope_schema, "batch_response", first_batch)
    validate_envelope(envelope_schema, "batch_response", second_batch)
    if first_batch != second_batch:
        raise RuntimeError("extension adapter is not deterministic across exact replay")

    results = first_batch["results"]
    result_ids = [item["case_id"] for item in results]
    expected_ids = [case["case_id"] for case in cases]
    if len(result_ids) != len(set(result_ids)) or set(result_ids) != set(expected_ids):
        raise RuntimeError("adapter result set does not exactly match mapped cases")
    indexed = {item["case_id"]: item for item in results}

    rows: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["case_id"]
        role_id = role_by_case[case_id]
        response = indexed[case_id]
        actual = response["actual"]
        extension_pass = actual == case["expected"]
        boundary_expected = roles[role_id]
        boundary_actual = {key: actual[key] for key in boundary_expected}
        seed_pass = boundary_actual == boundary_expected
        rows.append(
            {
                "role_id": role_id,
                "case_id": case_id,
                "extension_case_pass": extension_pass,
                "seed_boundary_pass": seed_pass,
                "actual": actual,
                "seed_expected": boundary_expected,
            }
        )

    passed = all(row["extension_case_pass"] and row["seed_boundary_pass"] for row in rows)
    seed_package = load(canon_root / "seed/canonical/CANON_PACKAGE.json")
    report = {
        "document_type": "aset-external-extension-conformance-results",
        "protocol": protocol_id,
        "seed": {
            "canon_id": seed_package["canon_id"],
            "canon_version": seed_package["canon_version"],
            "package_digest": seed_package["package_digest"],
        },
        "extension": expected_extension,
        "operations_verified": ["describe", "execute_case", "execute_cases"],
        "deterministic_replay": True,
        "roles_total": len(rows),
        "roles_passed": sum(
            bool(row["extension_case_pass"] and row["seed_boundary_pass"])
            for row in rows
        ),
        "pass": passed,
        "results": rows,
        "claim_boundary": protocol["claim_boundary"],
    }
    if args.output:
        output = args.output if args.output.is_absolute() else extension_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"EXTENSION_CONFORMANCE={report['roles_passed']}/{report['roles_total']}")
    print("EXTENSION_CONFORMANCE_PROTOCOL_OPERATIONS=3/3")
    print("EXTENSION_CONFORMANCE_DETERMINISTIC_REPLAY=PASS")
    print("EXTENSION_CONFORMANCE_VERDICT=" + ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
