#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

try:
    from tools.seed_resolution_oracle import digest_value, empty_store, execute_case
except ModuleNotFoundError:
    from seed_resolution_oracle import digest_value, empty_store, execute_case

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "seed/canonical/protocol/schemas"
CASE_SCHEMA = SCHEMA_DIR / "conformance-case.schema.json"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest_literal(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _binding(name: str) -> dict[str, Any]:
    body = {
        "context_id": "ctx.assurance",
        "state_root": _digest_literal("state:" + name),
        "question_digest": _digest_literal("question:" + name),
        "policy_epoch": 1,
        "scope": ["effect:assurance"],
    }
    return {**body, "binding_digest": digest_value(body)}


def _authority_binding(authority: str, binding: dict[str, Any]) -> dict[str, Any]:
    body = {
        "authority_id": authority,
        "context_id": binding["context_id"],
        "policy_epoch": binding["policy_epoch"],
        "binding_digest": binding["binding_digest"],
    }
    return {**body, "authority_binding_digest": digest_value(body)}


def _request(
    resolution_id: str,
    binding: dict[str, Any],
    initial_authority_binding_digest: str,
    previous: str | None,
) -> dict[str, Any]:
    body = {
        "resolution_id": resolution_id,
        "binding": copy.deepcopy(binding),
        "initial_authority_binding_digest": initial_authority_binding_digest,
        "previous_terminal_record_digest": previous,
    }
    return {**body, "request_digest": digest_value(body)}


def _record(
    request: dict[str, Any],
    authority: str,
    resolution: str,
    suffix: str,
) -> dict[str, Any]:
    body = {
        "request_digest": request["request_digest"],
        "resolution_id": request["resolution_id"],
        "binding_digest": request["binding"]["binding_digest"],
        "resolution": resolution,
        "authority_id": authority,
        "authority_evidence_digests": [_digest_literal("authority-evidence:" + suffix)],
        "basis_digests": [_digest_literal("basis:" + suffix)],
    }
    return {**body, "record_digest": digest_value(body)}


def _register(request: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "REGISTER_REQUEST", "payload": {"request": copy.deepcopy(request)}}


def _submit(record: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "SUBMIT_RESOLUTION", "payload": {"record": copy.deepcopy(record)}}


def _evaluate(resolution_id: str) -> dict[str, Any]:
    return {"kind": "EVALUATE_RESOLUTION", "payload": {"resolution_id": resolution_id}}


def _case(
    case_id: str,
    category: str,
    description: str,
    initial_store: dict[str, Any],
    setup: list[dict[str, Any]],
    candidate: dict[str, Any],
    recognized: list[str] | None = None,
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "case_id": case_id,
        "description": f"[{category}] {description}",
        "initial_store": copy.deepcopy(initial_store),
        "setup": copy.deepcopy(setup),
        "candidate": copy.deepcopy(candidate),
        "expected": {},
        "postconditions": [],
    }
    if recognized:
        case["recognized_terminal_record_digests"] = list(recognized)
    expected, final_store = execute_case(case)
    case["expected"] = expected
    case["postconditions"] = _exact_projection_postconditions(final_store)
    return case


def _exact_projection_postconditions(store: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind adapter output to the canonical protocol store projection.

    The implementation remains representation-independent internally; the external
    adapter is the witness that projects its state into the canonical protocol
    store. These postconditions intentionally compare only canonical fields.
    """
    conditions: list[dict[str, Any]] = []
    for collection in ("requests", "records", "authority_bindings"):
        conditions.append({"path": f"/{collection}", "equals": copy.deepcopy(store[collection])})
    return conditions


def generate_cases() -> list[dict[str, Any]]:
    b0 = _binding("B0")
    b1 = _binding("B1")
    a0_b0 = _authority_binding("authority.A0", b0)
    a1_b0 = _authority_binding("authority.A1", b0)
    a0_b1 = _authority_binding("authority.A0", b1)
    authority_bindings = [a0_b0, a1_b0, a0_b1]
    authority_by_pair = {
        ("authority.A0", "B0"): a0_b0,
        ("authority.A1", "B0"): a1_b0,
        ("authority.A0", "B1"): a0_b1,
    }
    bindings = {"B0": b0, "B1": b1}
    previous = {
        "P0": _digest_literal("previous:P0"),
        "P1": _digest_literal("previous:P1"),
    }
    recognized_previous = list(previous.values())

    cases: list[dict[str, Any]] = []
    cases.append(
        _case(
            "ASSURE-ABSENT-001",
            "effective-class",
            "Absent resolution evaluates to UNKNOWN and leaves the canonical store unchanged.",
            empty_store(),
            [],
            _evaluate("assure.absent"),
        )
    )

    # Rich pending witness: 2 recognized bindings x 2 previous commitments.
    for b_name in ("B0", "B1"):
        for p_name in ("P0", "P1"):
            authority_binding = authority_by_pair[("authority.A0", b_name)]
            rid = f"assure.pending.{b_name}.{p_name}"
            request = _request(
                rid,
                bindings[b_name],
                authority_binding["authority_binding_digest"],
                previous[p_name],
            )
            cases.append(
                _case(
                    f"ASSURE-PENDING-{b_name}-{p_name}",
                    "pending-payload",
                    "Registration preserves the exact binding and previous terminal commitment.",
                    {"requests": [], "records": [], "authority_bindings": authority_bindings},
                    [],
                    _register(request),
                    recognized_previous,
                )
            )

    # Rich terminal witness: every recognized authority-binding pair x previous x decision.
    pairs = [
        ("authority.A0", "B0"),
        ("authority.A1", "B0"),
        ("authority.A0", "B1"),
    ]
    for pair_index, (authority, b_name) in enumerate(pairs, start=1):
        for p_name in ("P0", "P1"):
            for resolution in ("ALLOW", "BLOCK"):
                authority_binding = authority_by_pair[(authority, b_name)]
                rid = f"assure.terminal.{pair_index}.{p_name}.{resolution.lower()}"
                request = _request(
                    rid,
                    bindings[b_name],
                    authority_binding["authority_binding_digest"],
                    previous[p_name],
                )
                record = _record(request, authority, resolution, rid)
                cases.append(
                    _case(
                        f"ASSURE-TERMINAL-{pair_index}-{p_name}-{resolution}",
                        "terminal-payload",
                        (
                            "Terminalization preserves binding, previous commitment, "
                            "terminal authority and decision."
                        ),
                        {"requests": [], "records": [], "authority_bindings": authority_bindings},
                        [_register(request)],
                        _submit(record),
                        recognized_previous,
                    )
                )

    # Terminal immutability and idempotence distinguish future behavior of terminal states.
    for resolution in ("ALLOW", "BLOCK"):
        rid = f"assure.replay.{resolution.lower()}"
        request = _request(
            rid,
            b0,
            a0_b0["authority_binding_digest"],
            previous["P0"],
        )
        record = _record(request, "authority.A0", resolution, rid)
        cases.append(
            _case(
                f"ASSURE-IDEMPOTENT-{resolution}",
                "terminal-behavior",
                "Exact replay of the retained terminal record is idempotent.",
                {"requests": [], "records": [], "authority_bindings": authority_bindings},
                [_register(request), _submit(record)],
                _submit(record),
                recognized_previous,
            )
        )
        opposite = "BLOCK" if resolution == "ALLOW" else "ALLOW"
        conflicting = _record(request, "authority.A0", opposite, rid + ".rewrite")
        cases.append(
            _case(
                f"ASSURE-IMMUTABLE-{resolution}-TO-{opposite}",
                "terminal-behavior",
                "A different terminal record cannot rewrite an already retained terminal decision.",
                {"requests": [], "records": [], "authority_bindings": authority_bindings},
                [_register(request), _submit(record)],
                _submit(conflicting),
                recognized_previous,
            )
        )

    # The protocol can observe the effective conflict class from externally materialized state,
    # but it does not expose the formal ObserveConflict action or invalidated provenance tag.
    conflict_request = _request(
        "assure.conflict",
        b0,
        a0_b0["authority_binding_digest"],
        None,
    )
    allow_record = _record(conflict_request, "authority.A0", "ALLOW", "conflict.allow")
    block_record = _record(conflict_request, "authority.A1", "BLOCK", "conflict.block")
    for order, records in (
        ("ALLOW-BLOCK", [allow_record, block_record]),
        ("BLOCK-ALLOW", [block_record, allow_record]),
    ):
        cases.append(
            _case(
                f"ASSURE-CONFLICT-{order}",
                "effective-conflict",
                (
                    "Two independently valid terminal records project to fail-closed UNKNOWN "
                    "irrespective of record order."
                ),
                {
                    "requests": [conflict_request],
                    "records": records,
                    "authority_bindings": authority_bindings,
                },
                [],
                _evaluate(conflict_request["resolution_id"]),
            )
        )

    # A terminal authority recognized only for another binding must not cross
    # the exact binding boundary. The initial request is recognized by A1/B0;
    # the submitted terminal authority A0 is recognized only for B1.
    mismatch_request = _request(
        "assure.authority.mismatch",
        b0,
        a1_b0["authority_binding_digest"],
        None,
    )
    mismatch_record = _record(
        mismatch_request,
        "authority.A0",
        "ALLOW",
        "authority.mismatch",
    )
    mismatch_store = {
        "requests": [mismatch_request],
        "records": [],
        "authority_bindings": [a1_b0, a0_b1],
    }
    cases.append(
        _case(
            "ASSURE-AUTHORITY-BINDING-MISMATCH",
            "exact-authority-binding",
            "Terminal authority recognition cannot cross from a different exact binding.",
            mismatch_store,
            [],
            _submit(mismatch_record),
        )
    )

    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("generated assurance case ids are not unique")
    return cases


def schema_registry() -> Registry:
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        schema = load(path)
        identifier = schema.get("$id")
        if isinstance(identifier, str):
            registry = registry.with_resource(identifier, Resource.from_contents(schema))
    return registry


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    validator = Draft202012Validator(load(CASE_SCHEMA), registry=schema_registry())
    for case in cases:
        for error in validator.iter_errors(case):
            location = "/" + "/".join(map(str, error.absolute_path))
            errors.append(f"{case['case_id']}:{location}:{error.message}")
        actual, final_store = execute_case(case)
        if actual != case["expected"]:
            errors.append(f"{case['case_id']}:oracle_expected_mismatch")
        for condition in case["postconditions"]:
            collection = condition["path"].removeprefix("/")
            if final_store.get(collection) != condition["equals"]:
                errors.append(f"{case['case_id']}:oracle_projection_mismatch:{collection}")
    return errors


def case_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "case_id": case["case_id"],
            "category": case["description"].split("]", 1)[0].removeprefix("["),
            "sha256": sha256_value(case),
        }
        for case in cases
    ]
    category_counts = dict(sorted(Counter(row["category"] for row in rows).items()))
    return {
        "document_type": "aset-seed-recognition-assurance-generated-cases-manifest",
        "schema_version": 1,
        "profile": "ASET-SEED-RECOGNITION-ASSURANCE-V1",
        "generator": "tools/seed_recognition_assurance_cases.py",
        "cases_total": len(rows),
        "category_counts": category_counts,
        "cases": rows,
        "case_set_digest": sha256_value(rows),
    }
