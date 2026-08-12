#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any, Callable

try:
    from tools.alpha4_operational_expression import (
        OperationalExpressionError,
        compile_operational_jit,
        derive_operational_graphs,
        semantic_projection as operational_projection,
    )
    from tools.alpha4_relational_expression import (
        RelationalExpressionError,
        apply_reference_graph,
        derive_relational_graphs,
        semantic_projection as relational_projection,
    )
except ModuleNotFoundError:
    from alpha4_operational_expression import (
        OperationalExpressionError,
        compile_operational_jit,
        derive_operational_graphs,
        semantic_projection as operational_projection,
    )
    from alpha4_relational_expression import (
        RelationalExpressionError,
        apply_reference_graph,
        derive_relational_graphs,
        semantic_projection as relational_projection,
    )

ROOT = Path(__file__).resolve().parents[1]


class PairedExpressionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PairedExpressionError(message)


def load_graph(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PairedExpressionError(f"graph document must be an object: {path}")
    return value


def write_graph(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_release_graphs(root: Path, target: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    target.mkdir(parents=True, exist_ok=True)
    operational = derive_operational_graphs(root)
    relational = derive_relational_graphs(root)
    write_graph(target / "operational-graph.json", operational)
    write_graph(target / "relational-graph.json", relational)
    return operational, relational


def _observe(call: Callable[[], dict[str, Any]]) -> tuple[str, Any]:
    try:
        return ("ok", call())
    except ValueError:
        return ("error", None)


def _witness_variants(
    current: dict[str, Any], evidence: str | None, outcome: str
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


def _outcome_by_component(projection: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for component_id, nodes in projection.items():
        values = [
            str(node["value"])
            for node in nodes
            if node.get("op") == "SET_RECOGNITION"
        ]
        if values:
            require(len(values) == 1, f"{component_id}: multiple recognition effects")
            outcomes[component_id] = values[0]
    return outcomes


def check_paired_expression(
    root: Path = ROOT,
    release_root: Path | None = None,
) -> dict[str, Any]:
    expected_operational = derive_operational_graphs(root)
    expected_relational = derive_relational_graphs(root)

    if release_root is None:
        operational = expected_operational
        relational = expected_relational
    else:
        operational = load_graph(release_root / "expression/paired/operational-graph.json")
        relational = load_graph(release_root / "expression/paired/relational-graph.json")
        require(
            operational == expected_operational,
            "release operational graph differs from actual operational source derivation",
        )
        require(
            relational == expected_relational,
            "release relational graph differs from actual relational source derivation",
        )

    operational_semantics = operational_projection(operational)
    relational_semantics = relational_projection(relational)
    require(
        operational_semantics == relational_semantics,
        "independently derived expression graphs are not semantically congruent",
    )

    jit_apply = compile_operational_jit(operational)
    outcomes = _outcome_by_component(relational_semantics)
    subjects = ("subject-1", "subject-2")
    authorities = ("authority-1", "authority-2")
    recognition_values = ("UNKNOWN", "ALLOW", "BLOCK")
    evidence_values = ("evidence-1", "evidence-2")
    evidence_sets = (
        (),
        ("evidence-1",),
        ("evidence-2",),
        ("evidence-1", "evidence-2"),
    )
    evidence_arguments: tuple[str | None, ...] = (None, *evidence_values)
    cases = 0
    for component_id in sorted(relational_semantics):
        for subject, authority, recognition, observed, evidence in itertools.product(
            subjects,
            authorities,
            recognition_values,
            evidence_sets,
            evidence_arguments,
        ):
            current = {
                "subject": subject,
                "authority": authority,
                "recognition": recognition,
                "evidence": tuple(observed),
            }
            outcome = outcomes.get(component_id)
            variants = (
                _witness_variants(current, evidence, outcome)
                if outcome is not None
                else [frozenset()]
            )
            for authority_recognition in variants:
                fast = _observe(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: jit_apply(
                        c,
                        cid,
                        evidence=ev,
                        authority_recognition=ar,
                    )
                )
                reference = _observe(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: apply_reference_graph(
                        relational,
                        c,
                        cid,
                        evidence=ev,
                        authority_recognition=ar,
                    )
                )
                require(
                    fast == reference,
                    "JIT operational expression differs from relational reference expression",
                )
                cases += 1

    return {
        "document_type": "aset-paired-expression-congruence-evidence",
        "profile_id": "ASET-PAIRED-EXPRESSION-0.4-ALPHA",
        "operational_derivation": "RESTRICTED_OPERATIONAL_SOURCE_TO_GRAPH",
        "relational_derivation": "FORMAL_RELATIONAL_SOURCE_TO_GRAPH",
        "graph_relation": "INDEPENDENT_DERIVATION_CROSS_CONGRUENCE",
        "runtime_relation": "JIT_REFERENCE_BOUNDED_OBSERVATIONAL_CONGRUENCE",
        "components_checked": len(operational_semantics),
        "cases_checked": cases,
        "jit_materialization": "EPHEMERAL_IN_MEMORY",
        "semantic_precedence": "NONE",
        "status": "PASS",
    }


def print_evidence(evidence: dict[str, Any]) -> None:
    count = evidence["components_checked"]
    cases = evidence["cases_checked"]
    print(f"ALPHA4_PAIRED_GRAPH_CONGRUENCE={count}/{count} PASS")
    print(f"ALPHA4_JIT_REFERENCE_CONGRUENCE={cases}/{cases} PASS")
    print("ALPHA4_PAIRED_EXPRESSION=PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path)
    args = parser.parse_args(argv)
    try:
        release_root = args.release_root
        if release_root is not None and not release_root.is_absolute():
            release_root = ROOT / release_root
        evidence = check_paired_expression(ROOT, release_root)
        print_evidence(evidence)
        return 0
    except (
        KeyError,
        TypeError,
        ValueError,
        PairedExpressionError,
        OperationalExpressionError,
        RelationalExpressionError,
    ) as error:
        print(f"ALPHA4_PAIRED_EXPRESSION_ERROR={error}")
        print("ALPHA4_PAIRED_EXPRESSION=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
