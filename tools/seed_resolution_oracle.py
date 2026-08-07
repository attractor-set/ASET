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


def authority_recognition_valid(
    store: dict[str, list[dict[str, Any]]],
    request: dict[str, Any],
    record: dict[str, Any],
) -> AuthorityVerdict:
    """Validate the Seed-level Authority recognition boundary.

    Seed does not interpret delegation chains. Concrete signatures, grant chains,
    federation proofs and other evidence may justify an Authority recognition,
    but the canonical kernel consumes only the already-recognized exact-binding
    result represented by a valid ResolutionAuthorityBinding.
    """
    bindings = [
        item
        for item in store["authority_bindings"]
        if authority_binding_valid(item)
    ]
    by_digest = {item["authority_binding_digest"]: item for item in bindings}
    root = by_digest.get(request["initial_authority_binding_digest"])
    if root is None:
        return AuthorityVerdict(False, "LOCAL_AUTHORITY_BINDING_INVALID")

    binding = request["binding"]
    exact = (
        root.get("context_id") == binding.get("context_id")
        and root.get("policy_epoch") == binding.get("policy_epoch")
        and root.get("binding_digest") == binding.get("binding_digest")
    )
    if not exact:
        return AuthorityVerdict(False, "LOCAL_AUTHORITY_BINDING_MISMATCH")

    target = record.get("authority_id")
    target_bindings = [item for item in bindings if item.get("authority_id") == target]
    if not target_bindings:
        return AuthorityVerdict(False, "TERMINAL_AUTHORITY_UNRECOGNIZED")
    if not any(
        item.get("context_id") == binding.get("context_id")
        and item.get("policy_epoch") == binding.get("policy_epoch")
        and item.get("binding_digest") == binding.get("binding_digest")
        for item in target_bindings
    ):
        return AuthorityVerdict(False, "TERMINAL_AUTHORITY_BINDING_MISMATCH")
    return AuthorityVerdict(True, "EXACT_BINDING_AUTHORITY_RECOGNIZED")


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
    evidence = record.get("authority_evidence_digests")
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        return False, "AUTHORITY_EVIDENCE_INVALID"
    authority = authority_recognition_valid(store, request, record)
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


def recognized_terminal_record_digests(
    store: dict[str, Any],
    externally_recognized: list[str] | tuple[str, ...] = (),
) -> set[str]:
    """Return terminal commitments recognized at the verification boundary.

    `externally_recognized` represents proof material already validated by an
    implementation/profile (for example an accumulator membership witness). It
    is deliberately not canonical Seed state. Valid terminal records still
    retained in the current store are recognized directly.
    """
    recognized = {item for item in externally_recognized if isinstance(item, str)}
    requests_by_id: dict[str, list[dict[str, Any]]] = {}
    for request in store.get("requests", []):
        rid = request.get("resolution_id")
        if isinstance(rid, str):
            requests_by_id.setdefault(rid, []).append(request)
    for record in store.get("records", []):
        rid = record.get("resolution_id")
        candidates = requests_by_id.get(rid, [])
        if len(candidates) != 1 or not request_valid(candidates[0]):
            continue
        ok, _ = record_valid(store, candidates[0], record)
        digest = record.get("record_digest")
        if ok and isinstance(digest, str):
            recognized.add(digest)
    return recognized


def register_request(
    store: dict[str, list[dict[str, Any]]],
    request: dict[str, Any],
    externally_recognized: list[str] | tuple[str, ...] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
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

    previous_digest = request.get("previous_terminal_record_digest")
    if previous_digest is not None:
        if previous_digest not in recognized_terminal_record_digests(store, externally_recognized):
            return actual(
                False,
                "PREVIOUS_TERMINAL_COMMITMENT_UNRECOGNIZED",
                False,
                evaluate(before, resolution_id),
            ), before

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
    externally_recognized: list[str] | tuple[str, ...] = (),
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
        return register_request(store, request, externally_recognized)
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
    externally_recognized = case.get("recognized_terminal_record_digests", [])
    for operation in case.get("setup", []):
        result, store = execute_operation(store, operation, externally_recognized)
        if not result["accepted"]:
            raise ValueError(f"setup rejected for {case['case_id']}: {result['code']}")
    return execute_operation(store, case["candidate"], externally_recognized)
