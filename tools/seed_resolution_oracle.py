#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def without(value: dict[str, Any], key: str) -> dict[str, Any]:
    return {name: item for name, item in value.items() if name != key}


def valid_digest(value: dict[str, Any], field: str) -> bool:
    candidate = value.get(field)
    return isinstance(candidate, str) and candidate == digest_value(without(value, field))


def empty_store() -> dict[str, list[dict[str, Any]]]:
    return {
        "requests": [],
        "records": [],
        "authority_bindings": [],
        "authority_grants": [],
    }


def indexed(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str):
            result[value] = item
    return result


def binding_valid(binding: dict[str, Any]) -> bool:
    return valid_digest(binding, "binding_digest")


def authority_binding_valid(binding: dict[str, Any]) -> bool:
    return valid_digest(binding, "authority_binding_digest")


def grant_valid(grant: dict[str, Any]) -> bool:
    return valid_digest(grant, "grant_digest")


def request_valid(request: dict[str, Any]) -> bool:
    binding = request.get("binding")
    return (
        isinstance(binding, dict)
        and binding_valid(binding)
        and valid_digest(request, "request_digest")
    )


def record_digest_valid(record: dict[str, Any]) -> bool:
    return valid_digest(record, "record_digest")


@dataclass(frozen=True)
class AuthorityVerdict:
    valid: bool
    reason: str


def authority_proof_valid(
    store: dict[str, list[dict[str, Any]]],
    request: dict[str, Any],
    record: dict[str, Any],
) -> AuthorityVerdict:
    bindings = indexed(store["authority_bindings"], "authority_binding_digest")
    root = bindings.get(request["initial_authority_binding_digest"])
    if root is None or not authority_binding_valid(root):
        return AuthorityVerdict(False, "LOCAL_AUTHORITY_BINDING_INVALID")
    binding = request["binding"]
    if (
        root.get("context_id") != binding.get("context_id")
        or root.get("policy_epoch") != binding.get("policy_epoch")
        or root.get("binding_digest") != binding.get("binding_digest")
    ):
        return AuthorityVerdict(False, "LOCAL_AUTHORITY_BINDING_MISMATCH")

    current = root.get("authority_id")
    target = record.get("authority_id")
    proof = record.get("authority_proof_digests")
    if not isinstance(proof, list):
        return AuthorityVerdict(False, "AUTHORITY_PROOF_INVALID")
    if current == target:
        return AuthorityVerdict(not proof, "LOCAL_ROOT_AUTHORITY" if not proof else "UNEXPECTED_AUTHORITY_PROOF")
    if not root.get("delegation_allowed"):
        return AuthorityVerdict(False, "DELEGATION_NOT_ALLOWED")

    grants = indexed(store["authority_grants"], "grant_digest")
    seen = {current}
    previous_digest: str | None = None
    for position, grant_digest in enumerate(proof):
        grant = grants.get(grant_digest)
        if grant is None or not grant_valid(grant):
            return AuthorityVerdict(False, "AUTHORITY_GRANT_INVALID")
        if grant.get("binding_digest") != binding.get("binding_digest"):
            return AuthorityVerdict(False, "AUTHORITY_GRANT_BINDING_MISMATCH")
        if grant.get("issuer_authority_id") != current:
            return AuthorityVerdict(False, "AUTHORITY_GRANT_CHAIN_MISMATCH")
        if grant.get("previous_grant_digest") != previous_digest:
            return AuthorityVerdict(False, "AUTHORITY_GRANT_PREDECESSOR_MISMATCH")
        subject = grant.get("subject_authority_id")
        if subject in seen:
            return AuthorityVerdict(False, "AUTHORITY_GRANT_CYCLE")
        if position < len(proof) - 1 and not grant.get("delegation_allowed"):
            return AuthorityVerdict(False, "DELEGATION_NOT_ALLOWED")
        seen.add(subject)
        current = subject
        previous_digest = grant_digest

    if current != target:
        return AuthorityVerdict(False, "AUTHORITY_PROOF_TARGET_MISMATCH")
    return AuthorityVerdict(True, "DELEGATED_AUTHORITY")


def record_valid(
    store: dict[str, list[dict[str, Any]]],
    request: dict[str, Any],
    record: dict[str, Any],
) -> tuple[bool, str]:
    if not record_digest_valid(record):
        return False, "RECORD_DIGEST_INVALID"
    if record.get("resolution") not in {"ALLOW", "BLOCK"}:
        return False, "TERMINAL_RESOLUTION_INVALID"
    if record.get("resolution_id") != request.get("resolution_id"):
        return False, "RESOLUTION_ID_MISMATCH"
    if record.get("request_digest") != request.get("request_digest"):
        return False, "REQUEST_DIGEST_MISMATCH"
    if record.get("binding_digest") != request["binding"].get("binding_digest"):
        return False, "BINDING_MISMATCH"
    authority = authority_proof_valid(store, request, record)
    if not authority.valid:
        return False, authority.reason
    return True, authority.reason


def evaluate(
    store: dict[str, list[dict[str, Any]]],
    resolution_id: str,
) -> dict[str, Any]:
    requests = [item for item in store["requests"] if item.get("resolution_id") == resolution_id]
    if len(requests) != 1 or not request_valid(requests[0]):
        return {
            "resolution_id": resolution_id,
            "resolution": "UNKNOWN",
            "effect_permitted": False,
            "reason": "REQUEST_NOT_FOUND_OR_INVALID",
            "terminal_record_digest": None,
        }
    request = requests[0]
    valid: list[dict[str, Any]] = []
    invalid_present = False
    for record in store["records"]:
        if record.get("resolution_id") != resolution_id:
            continue
        ok, _ = record_valid(store, request, record)
        if ok:
            valid.append(record)
        else:
            invalid_present = True
    unique = {item["record_digest"]: item for item in valid}
    valid = list(unique.values())
    if len(valid) == 1:
        record = valid[0]
        return {
            "resolution_id": resolution_id,
            "resolution": record["resolution"],
            "effect_permitted": record["resolution"] == "ALLOW",
            "reason": "UNIQUE_VALID_TERMINAL_RECORD",
            "terminal_record_digest": record["record_digest"],
        }
    if len(valid) > 1:
        reason = "CONFLICTING_TERMINAL_RECORDS"
    elif invalid_present:
        reason = "NO_VALID_TERMINAL_RECORD"
    else:
        reason = "TERMINAL_RECORD_ABSENT"
    return {
        "resolution_id": resolution_id,
        "resolution": "UNKNOWN",
        "effect_permitted": False,
        "reason": reason,
        "terminal_record_digest": None,
    }


def actual(accepted: bool, code: str, state_changed: bool, evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "accepted": accepted,
        "code": code,
        "state_changed": state_changed,
        "resolution": evaluation["resolution"],
        "effect_permitted": evaluation["effect_permitted"],
        "reason": evaluation["reason"],
    }


def register_request(store: dict[str, list[dict[str, Any]]], request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    resolution_id = str(request.get("resolution_id", "invalid-resolution"))
    before = copy.deepcopy(store)
    if not request_valid(request):
        return actual(False, "REQUEST_INVALID", False, evaluate(before, resolution_id)), before
    if any(item.get("resolution_id") == resolution_id for item in store["requests"]):
        return actual(False, "RESOLUTION_ID_NOT_FRESH", False, evaluate(before, resolution_id)), before

    bindings = indexed(store["authority_bindings"], "authority_binding_digest")
    authority = bindings.get(request["initial_authority_binding_digest"])
    if authority is None or not authority_binding_valid(authority):
        return actual(False, "LOCAL_AUTHORITY_BINDING_INVALID", False, evaluate(before, resolution_id)), before
    binding = request["binding"]
    if (
        authority.get("context_id") != binding.get("context_id")
        or authority.get("policy_epoch") != binding.get("policy_epoch")
        or authority.get("binding_digest") != binding.get("binding_digest")
    ):
        return actual(False, "LOCAL_AUTHORITY_BINDING_MISMATCH", False, evaluate(before, resolution_id)), before

    previous_id = request.get("previous_resolution_id")
    previous_digest = request.get("previous_terminal_record_digest")
    if previous_id is None:
        if previous_digest is not None:
            return actual(False, "RECONSIDERATION_LINK_INVALID", False, evaluate(before, resolution_id)), before
    else:
        if previous_id == resolution_id:
            return actual(False, "RESOLUTION_ID_NOT_FRESH", False, evaluate(before, resolution_id)), before
        previous = evaluate(store, previous_id)
        if previous["resolution"] not in {"ALLOW", "BLOCK"}:
            return actual(False, "PREVIOUS_RESOLUTION_NOT_TERMINAL", False, evaluate(before, resolution_id)), before
        if previous_digest != previous["terminal_record_digest"]:
            return actual(False, "PREVIOUS_TERMINAL_RECORD_MISMATCH", False, evaluate(before, resolution_id)), before

    store = copy.deepcopy(store)
    store["requests"].append(copy.deepcopy(request))
    return actual(True, "REQUEST_REGISTERED", True, evaluate(store, resolution_id)), store


def submit_resolution(store: dict[str, list[dict[str, Any]]], record: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    resolution_id = str(record.get("resolution_id", "invalid-resolution"))
    before = copy.deepcopy(store)
    requests = [item for item in store["requests"] if item.get("resolution_id") == resolution_id]
    if len(requests) != 1 or not request_valid(requests[0]):
        return actual(False, "REQUEST_NOT_FOUND_OR_INVALID", False, evaluate(before, resolution_id)), before
    request = requests[0]
    ok, reason = record_valid(store, request, record)
    if not ok:
        return actual(False, reason, False, evaluate(before, resolution_id)), before

    existing = [item for item in store["records"] if item.get("resolution_id") == resolution_id]
    if any(item.get("record_digest") == record.get("record_digest") for item in existing):
        return actual(True, "IDEMPOTENT_REPLAY", False, evaluate(before, resolution_id)), before
    if existing:
        return actual(False, "TERMINAL_IMMUTABLE", False, evaluate(before, resolution_id)), before

    store = copy.deepcopy(store)
    store["records"].append(copy.deepcopy(record))
    evaluation = evaluate(store, resolution_id)
    return actual(True, "RESOLUTION_RECORDED", True, evaluation), store


def execute_operation(
    store: dict[str, list[dict[str, Any]]],
    operation: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    kind = operation.get("kind")
    payload = operation.get("payload")
    if not isinstance(payload, dict):
        evaluation = evaluate(store, "invalid-resolution")
        return actual(False, "OPERATION_INVALID", False, evaluation), copy.deepcopy(store)
    if kind == "REGISTER_REQUEST":
        request = payload.get("request")
        if not isinstance(request, dict):
            return actual(False, "OPERATION_INVALID", False, evaluate(store, "invalid-resolution")), copy.deepcopy(store)
        return register_request(store, request)
    if kind == "SUBMIT_RESOLUTION":
        record = payload.get("record")
        if not isinstance(record, dict):
            return actual(False, "OPERATION_INVALID", False, evaluate(store, "invalid-resolution")), copy.deepcopy(store)
        return submit_resolution(store, record)
    if kind == "EVALUATE_RESOLUTION":
        resolution_id = payload.get("resolution_id")
        if not isinstance(resolution_id, str):
            return actual(False, "OPERATION_INVALID", False, evaluate(store, "invalid-resolution")), copy.deepcopy(store)
        return actual(True, "EVALUATED", False, evaluate(store, resolution_id)), copy.deepcopy(store)
    return actual(False, "OPERATION_UNKNOWN", False, evaluate(store, "invalid-resolution")), copy.deepcopy(store)


def execute_case(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    store = copy.deepcopy(case["initial_store"])
    for operation in case.get("setup", []):
        result, store = execute_operation(store, operation)
        if not result["accepted"]:
            raise ValueError(f"setup rejected for {case['case_id']}: {result['code']}")
    return execute_operation(store, case["candidate"])
