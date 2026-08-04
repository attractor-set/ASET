from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
OUTPUTS = {
    "ru": ROOT / "docs/generated/ru/ASET_Seed_0.1-rc12.md",
    "en": ROOT / "docs/generated/en/ASET_Seed_0.1-rc12.md",
    "pt-BR": ROOT / "docs/generated/pt-BR/ASET_Seed_0.1-rc12.md",
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
        f'- `runtime_profile`: `{model["runtime_profile"]["status"]}`',
        f'- `production_claim_scope`: `{model["assurance"]["production_claim_scope"]}`',
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
                f'- `authorization_rule`: {transition["authorization_rule"]}',
                "- `created_artifacts`: "
                + ", ".join(
                    f"`{item}`" for item in transition["created_artifacts"]
                ),
                "",
            ]
        )
    lines.extend(
        [
            f'## {headings["runtime"][language]}',
            "",
            f'- `profile_id`: `{model["runtime_profile"]["profile_id"]}`',
            f'- `status`: `{model["runtime_profile"]["status"]}`',
            f'- `implementation_version`: `{model["runtime_profile"]["implementation_version"]}`',
            f'- `wire_schema_version`: `{model["runtime_profile"]["wire_schema_version"]}`',
            f'- `proof_default`: `{model["runtime_profile"]["proof_boundary"]["default"]}`',
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
