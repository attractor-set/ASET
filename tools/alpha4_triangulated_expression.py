#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any, Callable

try:
    from tools.alpha4_causal_expression import (
        CausalExpressionError,
        apply_causal_graph,
        check_causal_invariant,
        derive_causal_graphs,
        semantic_projection as causal_projection,
    )
    from tools.alpha4_manifest import BindingPlan
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
    from alpha4_causal_expression import (
        CausalExpressionError,
        apply_causal_graph,
        check_causal_invariant,
        derive_causal_graphs,
        semantic_projection as causal_projection,
    )
    from alpha4_manifest import BindingPlan
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


class TriangulatedExpressionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TriangulatedExpressionError(message)


def load_graph(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"graph document must be an object: {path}")
    return value


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


def _outcome_by_component(
    projection: dict[str, list[dict[str, Any]]],
) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for component_id, nodes in projection.items():
        values = [
            str(node["value"]) for node in nodes if node.get("op") == "SET_RECOGNITION"
        ]
        if values:
            require(len(values) == 1, f"{component_id}: multiple recognition effects")
            outcomes[component_id] = values[0]
    return outcomes


def check_triangulated_expression(
    root: Path = ROOT,
    release_root: Path | None = None,
    plan: BindingPlan | None = None,
) -> dict[str, Any]:
    expected_operational = derive_operational_graphs(root, plan)
    expected_relational = derive_relational_graphs(root, plan)
    expected_causal = derive_causal_graphs(root, plan)

    if release_root is None:
        operational = expected_operational
        relational = expected_relational
        causal = expected_causal
    else:
        operational = load_graph(
            release_root / "expression/paired/operational-graph.json"
        )
        relational = load_graph(
            release_root / "expression/paired/relational-graph.json"
        )
        causal = load_graph(release_root / "expression/causal/causal-graph.json")
        require(
            operational == expected_operational,
            (
                "release operational graph differs from actual operational "
                "source derivation"
            ),
        )
        require(
            relational == expected_relational,
            "release relational graph differs from actual relational source derivation",
        )
        require(
            causal == expected_causal,
            "release causal graph differs from actual causal source derivation",
        )

    operational_semantics = operational_projection(operational)
    relational_semantics = relational_projection(relational)
    causal_semantics = causal_projection(causal)
    require(
        operational_semantics == relational_semantics,
        "operational and relational graph projections are incongruent",
    )
    require(
        operational_semantics == causal_semantics,
        "operational and causal graph projections are incongruent",
    )
    require(
        relational_semantics == causal_semantics,
        "relational and causal graph projections are incongruent",
    )

    invariant = check_causal_invariant(causal)
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
                operational_result = _observe(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                        jit_apply(c, cid, evidence=ev, authority_recognition=ar)
                    )
                )
                relational_result = _observe(
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
                causal_result = _observe(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                        apply_causal_graph(
                            causal,
                            c,
                            cid,
                            evidence=ev,
                            authority_recognition=ar,
                        )
                    )
                )
                require(
                    operational_result == relational_result == causal_result,
                    "operational, relational, and causal observations diverge",
                )
                cases += 1

    return {
        "document_type": "aset-triangulated-expression-congruence-evidence",
        "profile_id": "ASET-TRIANGULATED-EXPRESSION-0.4-ALPHA",
        "semantic_delta": "NONE",
        "derivations": {
            "operational": "RESTRICTED_OPERATIONAL_SOURCE_TO_GRAPH",
            "relational": "FORMAL_RELATIONAL_SOURCE_TO_GRAPH",
            "causal": "RESTRICTED_1_SAFE_CAUSAL_SOURCE_TO_GRAPH",
        },
        "pairwise_relations": {
            "operational_relational": "PASS",
            "operational_causal": "PASS",
            "relational_causal": "PASS",
        },
        "graph_relation": "THREE_WAY_INDEPENDENT_DERIVATION_CONGRUENCE",
        "runtime_relation": "THREE_WAY_BOUNDED_OBSERVATIONAL_CONGRUENCE",
        "causal_invariant": invariant,
        "components_checked": len(operational_semantics),
        "cases_checked": cases,
        "semantic_precedence": "NONE",
        "status": "PASS",
    }


def print_evidence(evidence: dict[str, Any]) -> None:
    count = evidence["components_checked"]
    cases = evidence["cases_checked"]
    invariant = evidence["causal_invariant"]
    transitions = invariant["transitions_checked"]
    print(f"ALPHA4_OPERATIONAL_RELATIONAL_GRAPH_CONGRUENCE={count}/{count} PASS")
    print(f"ALPHA4_OPERATIONAL_CAUSAL_GRAPH_CONGRUENCE={count}/{count} PASS")
    print(f"ALPHA4_RELATIONAL_CAUSAL_GRAPH_CONGRUENCE={count}/{count} PASS")
    print(f"ALPHA4_CAUSAL_RECOGNITION_TOKEN_INVARIANT={transitions}/{transitions} PASS")
    print(f"ALPHA4_TRIANGULATED_RUNTIME_CONGRUENCE={cases}/{cases} PASS")
    print("ALPHA4_TRIANGULATED_EXPRESSION=PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path)
    args = parser.parse_args(argv)
    try:
        release_root = args.release_root
        if release_root is not None and not release_root.is_absolute():
            release_root = ROOT / release_root
        evidence = check_triangulated_expression(ROOT, release_root)
        print_evidence(evidence)
        return 0
    except (
        KeyError,
        OSError,
        TypeError,
        ValueError,
        TriangulatedExpressionError,
        CausalExpressionError,
        OperationalExpressionError,
        RelationalExpressionError,
    ) as error:
        print(f"ALPHA4_TRIANGULATED_EXPRESSION_ERROR={error}")
        print("ALPHA4_TRIANGULATED_EXPRESSION=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
