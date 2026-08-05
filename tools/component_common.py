from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ASET_ROOT = ROOT / "aset"
COMPONENT_KEYS = (
    "context",
    "core",
    "gateway",
    "master",
    "memory",
    "monade",
    "protocol",
)


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


def component_path(key: str) -> Path:
    return ASET_ROOT / f"components/{key}/canonical/source/{key}-model.json"


def component_paths() -> list[Path]:
    return [component_path(key) for key in COMPONENT_KEYS]


def schema_errors(schema: dict[str, object], value: object) -> list[str]:
    return [
        "/".join(map(str, error.absolute_path)) + ":" + error.message
        for error in Draft202012Validator(schema).iter_errors(value)
    ]
