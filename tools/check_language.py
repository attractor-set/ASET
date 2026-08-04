from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLICY = (
    ROOT
    / "seed"
    / "canonical"
    / "terminology"
    / "foreign-terms.json"
)

DOCUMENTS = {
    "ru": ROOT / "docs" / "generated" / "ru",
    "en": ROOT / "docs" / "generated" / "en",
    "pt-BR": ROOT / "docs" / "generated" / "pt-BR",
}


def contains_term(text: str, term: str) -> bool:
    pattern = re.compile(
        rf"(?<!\w){re.escape(term)}(?!\w)",
        flags=re.IGNORECASE | re.UNICODE,
    )
    return bool(pattern.search(text))


def main() -> int:
    policy = json.loads(
        POLICY.read_text(encoding="utf-8")
    )

    failures: list[str] = []

    for language, directory in DOCUMENTS.items():
        rules = policy["languages"][language]

        for path in sorted(directory.rglob("*.md")):
            text = path.read_text(encoding="utf-8")

            for rule in rules:
                forbidden = rule["forbidden"]

                if contains_term(text, forbidden):
                    failures.append(
                        f"{path}:{forbidden}:"
                        f'{rule["preferred"]}'
                    )

    if failures:
        for failure in failures:
            print(f"FOREIGN_TERM_ERROR={failure}")
        return 1

    print("FOREIGN_TERM_POLICY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
