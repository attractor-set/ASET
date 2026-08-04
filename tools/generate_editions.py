from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    ROOT
    / "seed"
    / "canonical"
    / "source"
    / "seed-model.json"
)

OUTPUTS = {
    "ru": (
        ROOT
        / "docs"
        / "generated"
        / "ru"
        / "ASET_Seed_Next.md"
    ),
    "en": (
        ROOT
        / "docs"
        / "generated"
        / "en"
        / "ASET_Seed_Next.md"
    ),
    "pt-BR": (
        ROOT
        / "docs"
        / "generated"
        / "pt-BR"
        / "ASET_Seed_Next.md"
    ),
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def load_model() -> dict:
    return json.loads(
        MODEL_PATH.read_text(encoding="utf-8")
    )


def render(model: dict, language: str) -> str:
    publication = model["publication"]
    headings = publication["headings"]

    digest = hashlib.sha256(
        canonical_bytes(model)
    ).hexdigest()

    version_label = headings["version"][language]
    status_label = headings["status"][language]

    digest_label = headings[
        "canonical_model_sha256"
    ][language]

    identifier_label = headings["identifier"][language]
    modality_label = headings["modality"][language]
    predicate_label = headings["predicate"][language]

    lines = [
        f'# {publication["titles"][language]}',
        "",
        f'**{version_label}:** `{model["version"]}`',
        "",
        f'**{status_label}:** `{model["status"]}`',
        "",
        f'**{digest_label}:** `sha256:{digest}`',
        "",
        f'> {headings["notice"][language]}',
        "",
        f'## {headings["status"][language]}',
        "",
        f'`{model["status"]}`',
        "",
        f'## {headings["concepts"][language]}',
        "",
    ]

    for concept in model["concepts"]:
        label = concept["labels"][language]
        symbol = concept["symbol"]
        definition = concept["definitions"][language]

        lines.extend(
            [
                f"### {label} (`{symbol}`)",
                "",
                definition,
                "",
                (
                    f'{identifier_label}: '
                    f'`{concept["id"]}`'
                ),
                "",
            ]
        )

    lines.extend(
        [
            f'## {headings["requirements"][language]}',
            "",
        ]
    )

    for requirement in model["requirements"]:
        text = requirement["texts"][language]

        lines.extend(
            [
                f'### `{requirement["id"]}`',
                "",
                text,
                "",
                (
                    f'{modality_label}: '
                    f'`{requirement["modality"]}`'
                ),
                "",
                (
                    f'{predicate_label}: '
                    f'`{requirement["predicate"]}`'
                ),
                "",
            ]
        )

    lines.extend(
        [
            f'## {headings["invariants"][language]}',
            "",
        ]
    )

    for invariant in model["invariants"]:
        text = invariant["texts"][language]

        lines.append(
            f'- `{invariant["id"]}` — {text}'
        )

    lines.append("")

    return "\n".join(lines)


def expected_outputs() -> dict[Path, str]:
    model = load_model()

    return {
        path: render(model, language)
        for language, path in OUTPUTS.items()
    }


def generate() -> int:
    for path, content in expected_outputs().items():
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )

    print("GENERATED_EDITIONS=3")
    return 0


def check() -> int:
    failures: list[str] = []

    for path, expected in expected_outputs().items():
        if not path.is_file():
            failures.append(f"missing:{path}")
            continue

        actual = path.read_text(encoding="utf-8")

        if actual != expected:
            failures.append(f"different:{path}")

    if failures:
        for failure in failures:
            print(f"ERROR={failure}")

        return 1

    print("GENERATED_EDITIONS_PARITY=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--check",
        action="store_true",
    )

    arguments = parser.parse_args()

    if arguments.check:
        return check()

    return generate()


if __name__ == "__main__":
    raise SystemExit(main())
