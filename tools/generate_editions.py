from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
OUTPUTS = {
    "ru": ROOT / "docs/generated/ru/ASET_Seed_Resolution_0.2-alpha.2.md",
    "en": ROOT / "docs/generated/en/ASET_Seed_Resolution_0.2-alpha.2.md",
    "pt-BR": ROOT / "docs/generated/pt-BR/ASET_Seed_Resolution_0.2-alpha.2.md",
}
LEGACY_OUTPUTS = {
    "ru": ROOT / "docs/generated/ru/ASET_Seed_Next.md",
    "en": ROOT / "docs/generated/en/ASET_Seed_Next.md",
    "pt-BR": ROOT / "docs/generated/pt-BR/ASET_Seed_Next.md",
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def load_model() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def render(model: dict, language: str) -> str:
    publication = model["publication"]
    headings = publication["headings"]
    digest = hashlib.sha256(canonical_bytes(model)).hexdigest()
    lines = [
        f'# {publication["titles"][language]}',
        "",
        f'**{headings["version"][language]}:** `{model["version"]}`',
        "",
        f'**{headings["status"][language]}:** `{model["status"]}`',
        "",
        f'**{headings["canonical_model_sha256"][language]}:** `sha256:{digest}`',
        "",
        f'> {headings["notice"][language]}',
        "",
        f'## {headings["assurance"][language]}',
        "",
        f'- `implementation_status`: `{model["implementation_boundary"]["normative_status"]}`',
        f'- `implementation_precedence`: `{model["implementation_boundary"]["implementation_precedence"]}`',
        f'- `external_third_party_audit`: `{model["assurance"]["external_third_party_audit"]}`',
        "",
        f'## {headings["concepts"][language]}',
        "",
    ]
    identifier = headings["identifier"][language]
    modality = headings["modality"][language]
    predicate = headings["predicate"][language]
    for concept in model["concepts"]:
        lines.extend(
            [
                f'### {concept["labels"][language]} (`{concept["symbol"]}`)',
                "",
                concept["definitions"][language],
                "",
                f'{identifier}: `{concept["id"]}`',
                "",
            ]
        )
    lines.extend([f'## {headings["requirements"][language]}', ""])
    for requirement in model["requirements"]:
        lines.extend(
            [
                f'### `{requirement["id"]}`',
                "",
                requirement["texts"][language],
                "",
                f'{modality}: `{requirement["modality"]}`',
                "",
                f'{predicate}: `{requirement["predicate"]}`',
                "",
                f'`verification`: {", ".join(f"`{item}`" for item in requirement["verification"])}',
                "",
            ]
        )
    lines.extend([f'## {headings["invariants"][language]}', ""])
    for invariant in model["invariants"]:
        lines.append(f'- `{invariant["id"]}` — {invariant["texts"][language]}')
    lines.extend(["", f'## {headings["transitions"][language]}', ""])
    for transition in model["transitions"]:
        lines.extend(
            [
                f'### `{transition["id"]}` — `{transition["kind"]}`',
                "",
                f'- `payload_schema`: `{transition["payload_schema"]}`',
                f'- `authority_rule`: {transition["authority_rule"]}',
                f'- `scope_rule`: {transition["scope_rule"]}',
                "- `created_artifacts`: "
                + ", ".join(
                    f"`{item}`" for item in transition["created_artifacts"]
                ),
                "",
            ]
        )
    lines.extend(
        [
            f'## {headings["implementation_boundary"][language]}',
            "",
            f'- `normative_status`: `{model["implementation_boundary"]["normative_status"]}`',
            f'- `implementation_precedence`: `{model["implementation_boundary"]["implementation_precedence"]}`',
            f'- `conformance_protocol_ref`: `{model["implementation_boundary"]["conformance_protocol_ref"]}`',
            "- `unspecified_by_seed`: " + ", ".join(f"`{item}`" for item in model["implementation_boundary"]["unspecified_by_seed"]),
            "",
        ]
    )
    return "\n".join(lines)


def expected_outputs() -> dict[Path, str]:
    model = load_model()
    outputs = {path: render(model, language) for language, path in OUTPUTS.items()}
    outputs.update({path: outputs[OUTPUTS[language]] for language, path in LEGACY_OUTPUTS.items()})
    return outputs


def generate() -> int:
    for path, content in expected_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print("GENERATED_EDITIONS=3")
    print("GENERATED_COMPATIBILITY_ALIASES=3")
    return 0


def check() -> int:
    failures = []
    for path, expected in expected_outputs().items():
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"different:{path.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"ERROR={failure}")
        return 1
    print("GENERATED_EDITIONS_PARITY=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return check() if args.check else generate()


if __name__ == "__main__":
    raise SystemExit(main())
