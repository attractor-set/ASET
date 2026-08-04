from __future__ import annotations

import argparse
import json
from pathlib import Path


def indexed(items):
    return {item["id"]: item for item in items}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old")
    parser.add_argument("new")
    arguments = parser.parse_args()

    old = json.loads(
        Path(arguments.old).read_text(encoding="utf-8")
    )
    new = json.loads(
        Path(arguments.new).read_text(encoding="utf-8")
    )

    old_requirements = indexed(old["requirements"])
    new_requirements = indexed(new["requirements"])

    added = sorted(
        set(new_requirements) - set(old_requirements)
    )
    removed = sorted(
        set(old_requirements) - set(new_requirements)
    )

    changed = []

    for identifier in sorted(
        set(old_requirements) & set(new_requirements)
    ):
        before = old_requirements[identifier]
        after = new_requirements[identifier]

        fields = [
            "subject",
            "modality",
            "predicate",
            "texts",
        ]

        differences = {
            field: {
                "before": before[field],
                "after": after[field],
            }
            for field in fields
            if before[field] != after[field]
        }

        if differences:
            changed.append(
                {
                    "id": identifier,
                    "differences": differences,
                }
            )

    report = {
        "classification": (
            "NORMATIVE_CHANGE"
            if added or removed or changed
            else "NO_NORMATIVE_CHANGE"
        ),
        "added": added,
        "removed": removed,
        "changed": changed,
    }

    print(
        json.dumps(
            report,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
