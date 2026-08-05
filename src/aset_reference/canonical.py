"""Seed-compatible canonical JSON and immutable JSON helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any

from aset_seed.core import (
    SeedError,
)
from aset_seed.core import (
    canonical_bytes as seed_canonical_bytes,
)
from aset_seed.core import (
    domain_digest as seed_domain_digest,
)

JsonValue = None | bool | int | str | tuple["JsonValue", ...] | Mapping[str, "JsonValue"]


def normalized_json(value: Any) -> Any:
    """Return the Seed NFC/integer-only normalization of a JSON value."""
    try:
        return json.loads(seed_canonical_bytes(value).decode("utf-8"))
    except SeedError as exc:
        raise ValueError(exc.code) from exc


def freeze_json(value: Any) -> JsonValue:
    """Normalize and recursively freeze one JSON value."""
    normalized = normalized_json(value)

    def freeze(item: Any) -> JsonValue:
        if item is None or isinstance(item, (bool, int, str)):
            return item
        if isinstance(item, list):
            return tuple(freeze(value) for value in item)
        if isinstance(item, dict):
            return MappingProxyType({key: freeze(value) for key, value in item.items()})
        raise TypeError(f"unsupported normalized JSON value: {type(item).__name__}")

    return freeze(normalized)


def plain_json(value: Any) -> Any:
    """Return mutable JSON containers from an immutable value."""
    if isinstance(value, Mapping):
        return {key: plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [plain_json(item) for item in value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [plain_json(item) for item in value]
    return value


def canonical_json(value: Any) -> bytes:
    """Return exact Seed canonical bytes."""
    try:
        return seed_canonical_bytes(value)
    except SeedError as exc:
        raise ValueError(exc.code) from exc


def domain_digest(domain: str, value: Any) -> str:
    """Return a Seed length-framed, domain-separated SHA-256 digest."""
    try:
        return seed_domain_digest(domain, value)
    except SeedError as exc:
        raise ValueError(exc.code) from exc
