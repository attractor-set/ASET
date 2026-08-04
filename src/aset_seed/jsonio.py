from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StrictJsonError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJsonError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def loads_strict(text: str, *, max_bytes: int = 8 * 1024 * 1024) -> Any:
    try:
        encoded = text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise StrictJsonError("JSON input cannot be encoded as UTF-8") from error
    if len(encoded) > max_bytes:
        raise StrictJsonError("JSON document exceeds configured byte limit")
    try:
        return json.loads(text, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise StrictJsonError(str(error)) from error


def load_strict(path: Path, *, max_bytes: int = 8 * 1024 * 1024) -> Any:
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise StrictJsonError("JSON document exceeds configured byte limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise StrictJsonError("JSON input is not UTF-8") from error
    return loads_strict(text, max_bytes=max_bytes)


def dumps_canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
