from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "aset/profiles/monade-attempt-evidence/canonical"
PROFILE = BASE / "PROFILE.json"
PACKAGE = BASE / "PROFILE_PACKAGE.json"
INVARIANTS = BASE / "assurance/invariants.json"
CASES = BASE / "conformance/cases.json"
STATE_SPACE = BASE / "formal/state-space.json"
ATTEMPT_SCHEMA = BASE / "schemas/attempt-record.schema.json"
OBSERVATION_SCHEMA = BASE / "schemas/learning-observation.schema.json"
CONFORMANCE_RESULTS = BASE / "conformance/results.json"
MODEL_RESULTS = BASE / "formal/results.json"

PACKAGE_FILES = (
    "aset/profiles/monade-attempt-evidence/canonical/PROFILE.json",
    "aset/profiles/monade-attempt-evidence/canonical/assurance/invariants.json",
    "aset/profiles/monade-attempt-evidence/canonical/conformance/cases.json",
    "aset/profiles/monade-attempt-evidence/canonical/formal/state-space.json",
    "aset/profiles/monade-attempt-evidence/canonical/schemas/attempt-record.schema.json",
    "aset/profiles/monade-attempt-evidence/canonical/schemas/learning-observation.schema.json",
)

NEGATIVE_DISPOSITIONS = {
    "EXECUTION_FAILED",
    "VERIFICATION_REJECTED",
    "CANON_REJECTED",
    "PERMIT_REJECTED",
    "QUARANTINED",
}


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict[str, object]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_digest(value: dict[str, object]) -> str:
    material = dict(value)
    material.pop("canonical_digest", None)
    return "sha256:" + hashlib.sha256(canonical_bytes(material)).hexdigest()


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_text(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"


def schema_error_codes(schema: dict[str, object], document: object) -> list[str]:
    return [
        "SCHEMA_VALIDATION"
        for _ in Draft202012Validator(schema).iter_errors(document)
    ]


def validate_attempt_semantics(document: dict[str, object]) -> list[str]:
    errors: list[str] = []
    disposition = str(document.get("disposition"))
    if document.get("canonical_state_changed") is not False:
        errors.append("CANONICAL_STATE_MUTATION_FORBIDDEN")
    if document.get("candidate_parent_allowed") is not False:
        errors.append("CANDIDATE_PARENT_FORBIDDEN")
    if disposition in NEGATIVE_DISPOSITIONS and document.get("terminal") is not True:
        errors.append("NEGATIVE_DISPOSITION_NOT_TERMINAL")
    if document.get("recognized_outcome") is not False:
        errors.append("MONADE_CANNOT_RECOGNIZE_OUTCOME")
    if disposition in NEGATIVE_DISPOSITIONS and document.get("accepted_for_recognition") is True:
        errors.append("NEGATIVE_ATTEMPT_CANNOT_BE_ACCEPTED_FOR_RECOGNITION")
    if document.get("accepted_for_recognition") is True and disposition not in {
        "VERIFIED_POSITIVE",
        "VERIFIED_NEGATIVE",
        "ACCEPTED_FOR_RECOGNITION",
    }:
        errors.append("UNVERIFIED_RESULT_ACCEPTED_FOR_RECOGNITION")
    retry_of = document.get("retry_of")
    if retry_of is not None and retry_of == document.get("attempt_id"):
        errors.append("RETRY_REUSES_ATTEMPT_ID")
    if document.get("record_append_only") is not True:
        errors.append("ATTEMPT_RECORD_NOT_APPEND_ONLY")
    if document.get("master_projection") != "READ_ONLY":
        errors.append("MASTER_PROJECTION_NOT_READ_ONLY")
    return sorted(set(errors))


def validate_observation_semantics(document: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if document.get("master_access") != "READ_ONLY":
        errors.append("MASTER_PROJECTION_NOT_READ_ONLY")
    if document.get("authority_effect") != "NONE":
        errors.append("MASTER_PROJECTION_AUTHORITY_FORBIDDEN")
    return sorted(set(errors))
