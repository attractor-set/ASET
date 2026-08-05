from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path

from component_common import ASET_ROOT, COMPONENT_KEYS, ROOT, component_path, load

LANGUAGES = ("ru", "en", "pt-BR")
LANGUAGE_DIR = {"ru": "ru", "en": "en", "pt-BR": "pt-BR"}
SYSTEM_PATH = ASET_ROOT / "system/canonical/source/system-composition-model.json"
FOREIGN_TERMS_PATH = ROOT / "seed/canonical/terminology/foreign-terms.json"

HEADINGS = {
    "ru": {
        "source": "Исходная граница",
        "owns": "Владение",
        "must_not": "Запрещённые ответственности",
        "operations": "Операции и отображение на Seed",
        "requirements": "Требования",
        "invariants": "Инварианты",
        "limitations": "Границы assurance",
        "assets": "Машиночитаемые активы канона",
    },
    "en": {
        "source": "Source boundary",
        "owns": "Ownership",
        "must_not": "Forbidden responsibilities",
        "operations": "Operations and Seed mapping",
        "requirements": "Requirements",
        "invariants": "Invariants",
        "limitations": "Assurance boundaries",
        "assets": "Machine-readable canon assets",
    },
    "pt-BR": {
        "source": "Limite de origem",
        "owns": "Propriedade",
        "must_not": "Responsabilidades proibidas",
        "operations": "Operações e mapeamento para o Seed",
        "requirements": "Requisitos",
        "invariants": "Invariantes",
        "limitations": "Limites de assurance",
        "assets": "Ativos do cânone legíveis por máquina",
    },
}


def apply_language_policy(text: str, language: str) -> str:
    policy = load(FOREIGN_TERMS_PATH)
    languages = policy["languages"]
    assert isinstance(languages, dict)
    rules = languages[language]
    assert isinstance(rules, list)

    segments = text.split("`")
    for index in range(0, len(segments), 2):
        segment = segments[index]
        for rule in rules:
            assert isinstance(rule, dict)
            forbidden = str(rule["forbidden"])
            preferred = str(rule["preferred"])
            pattern = re.compile(
                rf"(?<!\w){re.escape(forbidden)}(?!\w)",
                flags=re.IGNORECASE | re.UNICODE,
            )

            segment = pattern.sub(
                lambda match, value=preferred: (
                    value[:1].upper() + value[1:]
                    if match.group(0)[:1].isupper()
                    else value
                ),
                segment,
            )
        segments[index] = segment
    return "`".join(segments)


def component_title(component: dict[str, object], language: str) -> str:
    name = str(component["component_id"]).split(".")[-1].replace("-", " ").title()
    return f"ASET {name} {component['version']}"


def render_component_markdown(component: dict[str, object], language: str) -> str:
    headings = HEADINGS[language]
    purpose = component["purpose"]
    assert isinstance(purpose, dict)
    source = component["source_baseline"]
    assert isinstance(source, dict)
    lines = [
        f"# {component_title(component, language)}",
        "",
        str(purpose[language]),
        "",
        f"- `component_id`: `{component['component_id']}`",
        f"- `version`: `{component['version']}`",
        f"- `status`: `{component['status']}`",
        f"- `canonical_digest`: `{component['canonical_digest']}`",
        "",
        f"## {headings['source']}",
        "",
        f"- `ASET`: `{source['version']}`",
        f"- `archive_sha256`: `{source['archive_sha256']}`",
        f"- `model_digest`: `{source['model_digest']}`",
        f"- `specification_digest`: `{source['specification_digest']}`",
        "",
        f"## {headings['owns']}",
        "",
    ]
    lines.extend(f"- `{item}`" for item in component["owns"])
    lines.extend(["", f"## {headings['must_not']}", ""])
    lines.extend(f"- {item}" for item in component["must_not"])
    lines.extend(["", f"## {headings['operations']}", ""])
    for operation in component["operations"]:
        mapping = operation["seed_mapping"]
        sequence = " → ".join(mapping["sequence"]) or "none"
        description = operation["description"]
        lines.extend(
            [
                f"### `{operation['id']}` — {operation['name']}",
                "",
                str(description[language]),
                "",
                f"- `classification`: `{operation['classification']}`",
                f"- `seed_transition_required`: `{mapping['seed_transition_required']}`",
                f"- `seed_sequence`: `{sequence}`",
                f"- `outcome_recognition_required`: `{mapping['outcome_recognition_required']}`",
                "",
            ]
        )
    lines.extend(
        [
            f"## {headings['requirements']}",
            "",
            f"Count: `{len(component['requirement_ids'])}`",
            "",
            ", ".join(f"`{item}`" for item in component["requirement_ids"]),
            "",
            f"## {headings['invariants']}",
            "",
        ]
    )
    for invariant in [*component["invariants"], *component["boundary_invariants"]]:
        lines.append(f"- `{invariant['id']}` — {invariant['statement']}")
    lines.extend(["", f"## {headings['limitations']}", ""])
    for limitation in component["assurance"]["limitations"]:
        lines.append(
            f"- `{limitation['id']}` (`{limitation['severity']}`) — "
            f"{limitation['statement']} Required evidence: {limitation['required_evidence']}"
        )
    lines.extend(["", f"## {headings['assets']}", ""])
    for name, relative in component["canon_assets"].items():
        lines.append(f"- `{name}`: `{relative}`")
    rendered = "\n".join(lines).rstrip() + "\n"
    return apply_language_policy(rendered, language)


def render_system_markdown(system: dict[str, object], language: str) -> str:
    title = {
        "ru": "ASET System Composition",
        "en": "ASET System Composition",
        "pt-BR": "ASET System Composition",
    }[language]
    lines = [
        f"# {title} {system['version']}",
        "",
        f"- `status`: `{system['status']}`",
        f"- `canonical_digest`: `{system['canonical_digest']}`",
        f"- `seed_version`: `{system['seed_compatibility']['version']}`",
        "",
        "## Components",
        "",
    ]
    for component in system["components"]:
        lines.append(
            f"- `{component['component_id']}` `{component['version']}` — "
            f"`{component['canonical_digest']}`"
        )
    lines.extend(["", "## Gates", ""])
    for gate in system["gates"]:
        lines.append(
            f"- `{gate['id']}` — producer `{gate['producer_component']}`, "
            f"authority `{gate['authority_component']}`, schema `{gate['schema_component']}`"
        )
    lines.extend(["", "## Workflow", ""])
    lines.extend(f"1. {step}" for step in system["workflow"])
    rendered = "\n".join(lines).rstrip() + "\n"
    return apply_language_policy(rendered, language)


def local_name(identifier: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in identifier)


def render_ontology(component: dict[str, object]) -> str:
    component_local = local_name(str(component["component_id"]))
    lines = [
        "@prefix aset: <https://w3id.org/aset/component/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "aset:Component a rdfs:Class .",
        "aset:Operation a rdfs:Class .",
        "aset:owns a rdf:Property .",
        "aset:mapsToSeed a rdf:Property .",
        "",
        f"aset:{component_local} a aset:Component ;",
        f'    rdfs:label "{component["component_id"]}" ;',
    ]
    owned = [f"aset:{local_name(str(item))}" for item in component["owns"]]
    if owned:
        lines.append("    aset:owns " + ", ".join(owned) + " .")
    else:
        lines[-1] = lines[-1].rstrip(" ;") + " ."
    lines.append("")
    for operation in component["operations"]:
        op_local = local_name(str(operation["id"]))
        sequence = " -> ".join(operation["seed_mapping"]["sequence"]) or "none"
        lines.extend(
            [
                f"aset:{op_local} a aset:Operation ;",
                f'    rdfs:label "{operation["name"]}" ;',
                f'    aset:mapsToSeed "{sequence}" .',
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_skos(component: dict[str, object]) -> str:
    scheme = local_name(str(component["component_id"])) + "Scheme"
    lines = [
        "@prefix aset: <https://w3id.org/aset/component/> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "",
        f"aset:{scheme} a skos:ConceptScheme ;",
        f'    skos:prefLabel "{component["component_id"]} terminology"@en .',
        "",
    ]
    entries = [(str(item), str(item), None) for item in component["owns"]]
    entries.extend(
        (
            str(operation["id"]),
            str(operation["name"]),
            operation["description"],
        )
        for operation in component["operations"]
    )
    for identifier, label, descriptions in entries:
        local = local_name(identifier)
        if descriptions is None:
            descriptions = {
                "ru": f"Нормативное понятие компонента {component['component_id']}.",
                "en": f"Normative concept owned by {component['component_id']}.",
                "pt-BR": f"Conceito normativo de {component['component_id']}.",
            }
        lines.extend(
            [
                f"aset:{local} a skos:Concept ;",
                f"    skos:inScheme aset:{scheme} ;",
                f'    skos:notation "{identifier}" ;',
                f'    skos:prefLabel "{label}"@ru ;',
                f'    skos:prefLabel "{label}"@en ;',
                f'    skos:prefLabel "{label}"@pt-BR ;',
                f'    skos:definition "{str(descriptions["en"]).replace(chr(34), chr(39))}"@en .',
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_shapes(component: dict[str, object]) -> str:
    del component
    return """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix aset: <https://w3id.org/aset/component/> .

aset:ComponentConceptShape a sh:NodeShape ;
    sh:targetClass skos:Concept ;
    sh:property [ sh:path skos:notation ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path skos:prefLabel ; sh:uniqueLang true ; sh:minCount 3 ] .
"""


def render_tbx(component: dict[str, object]) -> str:
    entries = [(str(item), str(item)) for item in component["owns"]]
    entries.extend((str(item["id"]), str(item["name"])) for item in component["operations"])
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<tbx xmlns="urn:iso:std:iso:30042:ed-2" type="TBX-Basic">',
        (
            "  <tbxHeader><fileDesc><titleStmt><title>"
            f"{escape(str(component['component_id']))}"
            "</title></titleStmt></fileDesc></tbxHeader>"
        ),
        '  <text><body style="dca">',
    ]
    for identifier, label in entries:
        lines.append(f'    <conceptEntry id="{escape(identifier)}">')
        for language in LANGUAGES:
            lines.append(
                f'      <langSec xml:lang="{language}"><termSec><term>{escape(label)}</term>'
                '<termNote type="administrativeStatus">preferred</termNote></termSec></langSec>'
            )
        lines.append("    </conceptEntry>")
    lines.extend(["  </body></text>", "</tbx>"])
    return "\n".join(lines).rstrip() + "\n"


def expected_outputs() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for key in COMPONENT_KEYS:
        component = load(component_path(key))
        for language in LANGUAGES:
            output = ROOT / (
                f"docs/generated/{LANGUAGE_DIR[language]}/"
                f"ASET_{key.replace('-', '_').title()}_{component['version']}.md"
            )
            outputs[output] = render_component_markdown(component, language)
        base = ASET_ROOT / f"components/{key}/canonical"
        outputs[base / f"ontology/{key}.ttl"] = render_ontology(component)
        outputs[base / f"terminology/{key}.skos.ttl"] = render_skos(component)
        outputs[base / f"shapes/{key}.shacl.ttl"] = render_shapes(component)
        outputs[base / f"terminology/{key}.tbx"] = render_tbx(component)
    system = load(SYSTEM_PATH)
    for language in LANGUAGES:
        outputs[
            ROOT / f"docs/generated/{LANGUAGE_DIR[language]}/ASET_System_{system['version']}.md"
        ] = render_system_markdown(system, language)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failures: list[str] = []
    for path, expected in expected_outputs().items():
        if args.check:
            if not path.is_file():
                failures.append(f"missing:{path.relative_to(ROOT)}")
            elif path.read_text(encoding="utf-8") != expected:
                failures.append(f"different:{path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
    if failures:
        for failure in failures:
            print(f"COMPONENT_VIEW_ERROR={failure}")
        return 1
    print(
        "COMPONENT_VIEWS_PARITY=PASS"
        if args.check
        else f"COMPONENT_VIEWS_GENERATED={len(expected_outputs())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
