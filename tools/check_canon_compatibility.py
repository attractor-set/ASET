#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("seed/canonical/source/seed-model.json")
DECLARATION_PATH = ROOT / "seed/canonical/migration/CANON_CHANGE_DECLARATION.json"


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_bytes(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=strict)
    if not isinstance(value, dict):
        raise ValueError("canon model must be a JSON object")
    return value


def load(path: Path) -> dict[str, Any]:
    return load_bytes(path.read_bytes())


def git_show(ref: str, path: Path) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path.as_posix()}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def canonical_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def by_id(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(item[key]): item for item in items}


def semantic_item(item: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    result.pop("verification", None)
    result.pop("assurance_refs", None)
    return result


def compare_group(
    approved: dict[str, Any], candidate: dict[str, Any], group: str, key: str
) -> dict[str, list[str]]:
    old = by_id(approved.get(group, []), key)
    new = by_id(candidate.get(group, []), key)
    return {
        "removed": sorted(set(old) - set(new)),
        "added": sorted(set(new) - set(old)),
        "changed": sorted(
            identifier
            for identifier in set(old) & set(new)
            if semantic_item(old[identifier]) != semantic_item(new[identifier])
        ),
    }


def classify(report: dict[str, Any]) -> str:
    groups = report["groups"]
    if any(
        value
        for group in groups.values()
        for key, value in group.items()
        if key in {"removed", "changed"}
    ):
        return "BREAKING"
    if any(group["added"] for group in groups.values()):
        return "MONOTONIC_EXTENSION"
    if report["top_level_changed"]:
        return "BREAKING"
    return "NONE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-ref", required=True)
    parser.add_argument(
        "--output", type=Path, default=Path("dist/canon-compatibility.json")
    )
    args = parser.parse_args()

    approved = load_bytes(git_show(args.approved_ref, MODEL_PATH))
    candidate_path = ROOT / MODEL_PATH
    candidate = load(candidate_path)

    groups = {
        "concepts": compare_group(approved, candidate, "concepts", "id"),
        "requirements": compare_group(approved, candidate, "requirements", "id"),
        "invariants": compare_group(approved, candidate, "invariants", "id"),
        "transitions": compare_group(approved, candidate, "transitions", "kind"),
    }
    ignored = {
        "assurance",
        "publication",
        "status",
        "implementation_boundary",
        "model_id",
        "version",
    }
    top_level_changed = sorted(
        key
        for key in set(approved) | set(candidate)
        if key not in ignored
        and key not in {"concepts", "requirements", "invariants", "transitions"}
        and approved.get(key) != candidate.get(key)
    )
    report: dict[str, Any] = {
        "document_type": "aset-canon-compatibility-report",
        "approved_ref": args.approved_ref,
        "candidate_model_sha256": canonical_digest(candidate_path),
        "groups": groups,
        "top_level_changed": top_level_changed,
    }
    change_class = classify(report)
    report["change_class"] = change_class

    errors: list[str] = []
    if change_class != "NONE":
        if not DECLARATION_PATH.is_file():
            errors.append("missing change declaration")
        else:
            declaration = load(DECLARATION_PATH)
            if declaration.get("change_class") != change_class:
                errors.append("declared change class does not match detected class")
            if (
                declaration.get("candidate_model_sha256")
                != report["candidate_model_sha256"]
            ):
                errors.append("change declaration candidate digest is stale")
            for field in ("decision_ref", "rationale"):
                if not declaration.get(field):
                    errors.append(f"change declaration missing {field}")
            decision_ref = declaration.get("decision_ref")
            if isinstance(decision_ref, str) and not (ROOT / decision_ref).is_file():
                errors.append("change declaration decision_ref does not exist")

    report["errors"] = errors
    report["verdict"] = "PASS" if not errors else "FAIL"
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

    print(f"CANON_CHANGE_CLASS={change_class}")
    print("CANON_COMPATIBILITY=" + report["verdict"])
    for error in errors:
        print("CANON_COMPATIBILITY_ERROR=" + error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
