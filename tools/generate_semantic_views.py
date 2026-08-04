from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "seed/canonical/source/seed-model.json"
ONTOLOGY = ROOT / "seed/canonical/ontology/seed.ttl"
SKOS = ROOT / "seed/canonical/terminology/seed.skos.ttl"
TBX = ROOT / "seed/canonical/terminology/seed.tbx"


def load_model() -> dict:
    return json.loads(MODEL.read_text(encoding="utf-8"))


def render_ontology(model: dict) -> str:
    lines = [
        "@prefix aset: <https://aset.example/seed#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "aset:SeedOntology a owl:Ontology ;",
        '    rdfs:label "ASET Seed 0.1-rc12 ontology"@en .',
        "",
    ]
    for concept in model["concepts"]:
        local = concept["id"].split(".", 1)[1]
        labels = concept["labels"]
        lines.extend(
            [
                f"aset:{local} a owl:Class ;",
                f'    rdfs:label {json.dumps(labels["ru"], ensure_ascii=False)}@ru ;',
                f'    rdfs:label {json.dumps(labels["en"], ensure_ascii=False)}@en ;',
                f'    rdfs:label {json.dumps(labels["pt-BR"], ensure_ascii=False)}@pt-BR ;',
                "    rdfs:comment "
                + json.dumps(concept["definitions"]["en"], ensure_ascii=False)
                + "@en .",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_skos(model: dict) -> str:
    lines = [
        "@prefix aset: <https://aset.example/seed#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "",
        "aset:SeedConceptScheme a skos:ConceptScheme ;",
        '    skos:prefLabel "ASET Seed 0.1-rc12 concept scheme"@en .',
        "",
    ]
    for concept in model["concepts"]:
        local = concept["id"].split(".", 1)[1]
        labels = concept["labels"]
        lines.extend(
            [
                f"aset:{local} a skos:Concept ;",
                "    skos:inScheme aset:SeedConceptScheme ;",
                f'    skos:notation {json.dumps(concept["id"])} ;',
                f'    skos:prefLabel {json.dumps(labels["ru"], ensure_ascii=False)}@ru ;',
                f'    skos:prefLabel {json.dumps(labels["en"], ensure_ascii=False)}@en ;',
                f'    skos:prefLabel {json.dumps(labels["pt-BR"], ensure_ascii=False)}@pt-BR ;',
                "    skos:definition "
                + json.dumps(concept["definitions"]["en"], ensure_ascii=False)
                + "@en .",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_tbx(model: dict) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<tbx xmlns="urn:iso:std:iso:30042:ed-2" type="TBX-Basic">',
        '  <tbxHeader><fileDesc><titleStmt><title>'
        'ASET Seed 0.1-rc12 terminology'
        '</title></titleStmt></fileDesc></tbxHeader>',
        '  <text><body style="dca">',
    ]
    for concept in model["concepts"]:
        lines.append(f'    <conceptEntry id="{escape(concept["id"])}">')
        for language in ["ru", "en", "pt-BR"]:
            term = escape(concept["labels"][language])
            lines.append(
                f'      <langSec xml:lang="{language}"><termSec><term>{term}</term>'
                '<termNote type="administrativeStatus">preferred</termNote></termSec></langSec>'
            )
        lines.append("    </conceptEntry>")
    lines.extend(["  </body></text>", "</tbx>"])
    return "\n".join(lines).rstrip() + "\n"


def outputs() -> dict[Path, str]:
    model = load_model()
    return {ONTOLOGY: render_ontology(model), SKOS: render_skos(model), TBX: render_tbx(model)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failures = []
    for path, expected in outputs().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
    if failures:
        for failure in failures:
            print(f"SEMANTIC_VIEW_ERROR={failure}")
        return 1
    print("SEMANTIC_VIEWS_PARITY=PASS" if args.check else "SEMANTIC_VIEWS_GENERATED=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
