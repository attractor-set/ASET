#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import re
from pathlib import Path
from typing import Any, Callable

try:
    from tools.alpha4_binding_graph import parse_seed_bindings
    from tools.alpha4_relational_expression import (
        apply_reference_graph,
        derive_relational_graphs,
    )
except ModuleNotFoundError:
    from alpha4_binding_graph import parse_seed_bindings
    from alpha4_relational_expression import (
        apply_reference_graph,
        derive_relational_graphs,
    )

ROOT = Path(__file__).resolve().parents[1]


class ReleaseProfileCongruenceError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseProfileCongruenceError(message)


def _expected_records(root: Path) -> list[dict[str, Any]]:
    bindings = parse_seed_bindings(root)
    pair_by_id = {item.component_id: item for item in bindings.pairs}
    graphs = derive_relational_graphs(root)
    records: list[dict[str, Any]] = []
    for component in graphs["components"]:
        component_id = str(component["component_id"])
        pair = pair_by_id[component_id]
        nodes = component["nodes"]
        rin = next(
            str(node["value"]) for node in nodes if node["op"] == "CHECK_RECOGNITION"
        )
        set_values = [
            str(node["value"]) for node in nodes if node["op"] == "SET_RECOGNITION"
        ]
        rout = set_values[0] if set_values else rin
        ops = {str(node["op"]) for node in nodes}
        records.append(
            {
                "component_id": component_id,
                "operational_word": pair.operational_word,
                "formal_operator": pair.formal_operator,
                "recognition_in": rin,
                "recognition_out": rout,
                "operation_kind": (
                    "OBSERVE_EVIDENCE"
                    if "ADD_EVIDENCE" in ops
                    else "RECOGNIZE"
                    if "SET_RECOGNITION" in ops
                    else "PRESERVE"
                ),
                "authority_requirement": (
                    "LOCAL_EXACT_SUBJECT_EVIDENCE"
                    if "REQUIRE_LOCAL_AUTHORITY_WITNESS" in ops
                    else "NONE"
                ),
            }
        )
    return records


def parse_controlled_english(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    require(
        "Seed membership: external companion" in text,
        "English companion boundary missing",
    )
    parsed: dict[str, dict[str, str]] = {}
    for block in re.split(r"(?m)^### ", text)[1:]:
        lines = block.strip().splitlines()
        component_id = lines[0].strip()
        fields: dict[str, str] = {}
        for line in lines[1:]:
            match = re.match(r"^([A-Za-z]+): `(.*)`$", line)
            if match:
                fields[match.group(1)] = match.group(2)
        rin, rout = [part.strip() for part in fields["Recognition"].split("->", 1)]
        parsed[component_id] = {
            "component_id": component_id,
            "operational_word": fields["Operational"],
            "formal_operator": fields["Relational"],
            "recognition_in": rin,
            "recognition_out": rout,
            "operation_kind": fields["Operation"],
            "authority_requirement": fields["Authority"],
        }
    return parsed


def check_english_congruence(root: Path, profiles_root: Path) -> dict[str, Any]:
    expected = {item["component_id"]: item for item in _expected_records(root)}
    actual = parse_controlled_english(profiles_root / "en/Seed.md")
    require(
        actual == expected,
        "controlled English round-trip differs from relational source",
    )
    return {
        "relation": "CONTROLLED_ROUND_TRIP_CONGRUENCE",
        "components_checked": len(expected),
        "status": "PASS",
    }


def execute_python(path: Path) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    source = path.read_text(encoding="utf-8")
    require(
        "release companion" in source, "generated Python companion boundary missing"
    )
    exec(compile(source, str(path), "exec"), namespace)
    return namespace


def observe_call(call: Callable[[], dict[str, Any]]) -> tuple[str, Any]:
    try:
        return ("ok", call())
    except ValueError:
        return ("error", None)


def witness_variants(
    current: dict[str, Any],
    evidence: str | None,
    outcome: str,
) -> list[frozenset[tuple[str, str, str, str]]]:
    if evidence is None:
        return [frozenset()]
    subject = str(current["subject"])
    authority = str(current["authority"])
    other_subject = "subject-2" if subject == "subject-1" else "subject-1"
    other_authority = "authority-2" if authority == "authority-1" else "authority-1"
    other_evidence = "evidence-2" if evidence == "evidence-1" else "evidence-1"
    other_outcome = "BLOCK" if outcome == "ALLOW" else "ALLOW"
    return [
        frozenset(),
        frozenset({(authority, subject, evidence, outcome)}),
        frozenset({(authority, other_subject, evidence, outcome)}),
        frozenset({(other_authority, subject, evidence, outcome)}),
        frozenset({(authority, subject, other_evidence, outcome)}),
        frozenset({(authority, subject, evidence, other_outcome)}),
    ]


def check_python_congruence(root: Path, profiles_root: Path) -> dict[str, Any]:
    relational = derive_relational_graphs(root)
    namespace = execute_python(profiles_root / "python/aset_seed_alpha4.py")
    apply_component = namespace.get("apply_component")
    require(callable(apply_component), "generated Python apply_component missing")
    semantic_nodes = {
        str(item["component_id"]): item["nodes"] for item in relational["components"]
    }
    outcomes = {
        component_id: next(
            (str(node["value"]) for node in nodes if node["op"] == "SET_RECOGNITION"),
            None,
        )
        for component_id, nodes in semantic_nodes.items()
    }
    subjects = ("subject-1", "subject-2")
    authorities = ("authority-1", "authority-2")
    recognition_values = ("UNKNOWN", "ALLOW", "BLOCK")
    evidence_values = ("evidence-1", "evidence-2")
    evidence_sets = ((), ("evidence-1",), ("evidence-2",), ("evidence-1", "evidence-2"))
    evidence_arguments: tuple[str | None, ...] = (None, *evidence_values)
    cases = 0
    for component_id in sorted(semantic_nodes):
        for subject, authority, recognition, observed, evidence in itertools.product(
            subjects, authorities, recognition_values, evidence_sets, evidence_arguments
        ):
            current = {
                "subject": subject,
                "authority": authority,
                "recognition": recognition,
                "evidence": tuple(observed),
            }
            outcome = outcomes[component_id]
            variants = (
                witness_variants(current, evidence, outcome)
                if outcome
                else [frozenset()]
            )
            for authority_recognition in variants:
                expected = observe_call(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                        apply_reference_graph(
                            relational,
                            c,
                            cid,
                            evidence=ev,
                            authority_recognition=ar,
                        )
                    )
                )
                actual = observe_call(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                        apply_component(
                            c,
                            cid,
                            evidence=ev,
                            authority_recognition=ar,
                        )
                    )
                )
                require(
                    actual == expected,
                    "generated Python differs from relational reference",
                )
                cases += 1
    return {
        "relation": "BOUNDED_EXHAUSTIVE_OBSERVATIONAL_CONGRUENCE",
        "cases_checked": cases,
        "status": "PASS",
    }


def check_release_profile_congruence(root: Path, profiles_root: Path) -> dict[str, Any]:
    return {
        "document_type": "aset-release-profile-congruence-evidence",
        "profile_scope": "CI_RELEASE_COMPANIONS",
        "semantic_precedence": "NONE",
        "english": check_english_congruence(root, profiles_root),
        "python": check_python_congruence(root, profiles_root),
        "status": "PASS",
    }


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles-root", type=Path, required=True)
    args = parser.parse_args(argv)
    profiles_root = (
        args.profiles_root
        if args.profiles_root.is_absolute()
        else ROOT / args.profiles_root
    )
    try:
        evidence = check_release_profile_congruence(ROOT, profiles_root)
        english = evidence["english"]
        python = evidence["python"]
        count = english["components_checked"]
        print(f"ALPHA4_RELEASE_ENGLISH_PROFILE_CONGRUENCE={count}/{count} PASS")
        cases = python["cases_checked"]
        print(f"ALPHA4_RELEASE_PYTHON_PROFILE_CONGRUENCE={cases}/{cases} PASS")
        print("ALPHA4_RELEASE_PROFILE_CONGRUENCE=PASS")
        return 0
    except (
        ReleaseProfileCongruenceError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        print(f"ALPHA4_RELEASE_PROFILE_CONGRUENCE_ERROR={error}")
        print("ALPHA4_RELEASE_PROFILE_CONGRUENCE=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
