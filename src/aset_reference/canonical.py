"""Canonical JSON, immutable JSON values, and digest helpers."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any

JsonValue = None | bool | int | float | str | tuple["JsonValue", ...] | Mapping[str, "JsonValue"]


def freeze_json(value: Any) -> JsonValue:
    """Validate and recursively freeze one JSON value."""
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite numbers are not valid JSON")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be strings")
            frozen[key] = freeze_json(item)
        return MappingProxyType(frozen)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(freeze_json(item) for item in value)
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def plain_json(value: JsonValue) -> Any:
    """Return plain mutable containers suitable for JSON serialization."""
    if isinstance(value, Mapping):
        return {key: plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [plain_json(item) for item in value]
    return value


def canonical_json(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for a JSON-compatible value."""
    normalized = plain_json(freeze_json(value))
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_digest(value: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()
