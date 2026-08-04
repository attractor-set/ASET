from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator
from pyshacl import validate as shacl_validate
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]

MODEL = (
    ROOT
    / "seed"
    / "canonical"
    / "source"
    / "seed-model.json"
)

SCHEMA = (
    ROOT
    / "seed"
    / "canonical"
    / "schemas"
    / "seed-model.schema.json"
)

SKOS = (
    ROOT
    / "seed"
    / "canonical"
    / "terminology"
    / "seed.skos.ttl"
)

SHAPES = (
    ROOT
    / "seed"
    / "canonical"
    / "shapes"
    / "seed.shacl.ttl"
)

ONTOLOGY = (
    ROOT
    / "seed"
    / "canonical"
    / "ontology"
    / "seed.ttl"
)

TBX = (
    ROOT
    / "seed"
    / "canonical"
    / "terminology"
    / "seed.tbx"
)


def strict_object(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                f"duplicate JSON member: {key}"
            )
        result[key] = value

    return result


def strict_load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )


def unique(values) -> bool:
    materialized = list(values)
    return len(materialized) == len(set(materialized))


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*.json")):
        try:
            strict_load(path)
        except Exception as error:
            errors.append(f"json:{path}:{error}")

    model = strict_load(MODEL)
    schema = strict_load(SCHEMA)

    validator = Draft202012Validator(schema)

    for error in sorted(
        validator.iter_errors(model),
        key=lambda item: list(item.absolute_path),
    ):
        errors.append(
            "schema:"
            + "/".join(str(x) for x in error.absolute_path)
            + ":"
            + error.message
        )

    concept_ids = [
        concept["id"]
        for concept in model["concepts"]
    ]

    requirement_ids = [
        requirement["id"]
        for requirement in model["requirements"]
    ]

    invariant_ids = [
        invariant["id"]
        for invariant in model["invariants"]
    ]

    if not unique(concept_ids):
        errors.append("duplicate concept identifier")

    if not unique(requirement_ids):
        errors.append("duplicate requirement identifier")

    if not unique(invariant_ids):
        errors.append("duplicate invariant identifier")

    if model["languages"] != ["ru", "en", "pt-BR"]:
        errors.append("language set must be ru, en, pt-BR")

    for path in [SKOS, SHAPES, ONTOLOGY]:
        try:
            Graph().parse(path, format="turtle")
        except Exception as error:
            errors.append(f"rdf:{path}:{error}")

    try:
        ET.parse(TBX)
    except Exception as error:
        errors.append(f"tbx:{error}")

    try:
        conforms, _, report = shacl_validate(
            data_graph=str(SKOS),
            shacl_graph=str(SHAPES),
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
        )

        if not conforms:
            errors.append(f"shacl:{report}")
    except Exception as error:
        errors.append(f"shacl-execution:{error}")

    commands = [
        [
            sys.executable,
            "tools/generate_editions.py",
            "--check",
        ],
        [
            sys.executable,
            "tools/check_language.py",
        ],
        [
            sys.executable,
            "tools/verify_frozen_release.py",
        ],
    ]

    for command in commands:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            errors.append(
                "command:"
                + " ".join(command)
                + "\n"
                + result.stdout
                + result.stderr
            )

    if errors:
        for error in errors:
            print(f"VALIDATION_ERROR={error}")
        return 1

    print(f"CONCEPTS={len(concept_ids)}")
    print(f"REQUIREMENTS={len(requirement_ids)}")
    print(f"INVARIANTS={len(invariant_ids)}")
    print("REPOSITORY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
