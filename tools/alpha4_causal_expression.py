#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from tools.alpha4_manifest import BindingPlan, parse_seed_manifest
except ModuleNotFoundError:
    from alpha4_manifest import BindingPlan, parse_seed_manifest

ROOT = Path(__file__).resolve().parents[1]


class CausalExpressionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CausalExpressionError(message)


@dataclass(frozen=True)
class Place:
    symbol: str
    recognition: str
    initial: int


@dataclass(frozen=True)
class Transition:
    symbol: str
    component_id: str
    source: str
    target: str
    requirements: tuple[str, ...]
    effects: tuple[str, ...]


@dataclass(frozen=True)
class CausalNet:
    schema_version: int
    subject_id: str
    semantic_precedence: str
    places: tuple[Place, ...]
    invariant_id: str
    invariant_places: tuple[str, ...]
    invariant_total: int
    transitions: tuple[Transition, ...]


def _nonempty_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def parse_causal_net(root: Path = ROOT, plan: BindingPlan | None = None) -> CausalNet:
    binding_plan = plan or parse_seed_manifest(root)
    path = root / binding_plan.causal_model
    lines = _nonempty_lines(path)
    require(lines, "empty causal source")

    head = lines[0].split()
    require(
        len(head) == 3 and head[0] == "ASET-CAUSAL-NET",
        "invalid causal net header",
    )
    schema_version = int(head[1])
    subject_id = head[2]
    require(schema_version == 1, "unsupported causal net schema")
    require(
        subject_id == "ASET-SEED-0.4-ALPHA-CAUSAL",
        "causal subject identity mismatch",
    )

    semantic_precedence = ""
    places: list[Place] = []
    invariant_id = ""
    invariant_places: tuple[str, ...] = ()
    invariant_total = -1
    transitions: list[Transition] = []
    index = 1
    while index < len(lines):
        tokens = lines[index].split()
        kind = tokens[0]
        if kind == "SEMANTIC-PRECEDENCE":
            require(len(tokens) == 2, "invalid causal semantic precedence")
            require(not semantic_precedence, "duplicate causal semantic precedence")
            semantic_precedence = tokens[1]
            index += 1
            continue
        if kind == "PLACE":
            require(
                len(tokens) == 5 and tokens[3] == "INITIAL",
                "invalid causal place",
            )
            initial = int(tokens[4])
            require(initial in {0, 1}, "causal place initial marking must be 0 or 1")
            places.append(Place(tokens[1], tokens[2], initial))
            index += 1
            continue
        if kind == "INVARIANT":
            require(
                len(tokens) == 7 and tokens[-2] == "TOTAL",
                "invalid causal invariant",
            )
            require(not invariant_id, "duplicate causal invariant")
            invariant_id = tokens[1]
            invariant_places = tuple(tokens[2:5])
            invariant_total = int(tokens[-1])
            index += 1
            continue
        if kind == "TRANSITION":
            require(len(tokens) == 3, "invalid causal transition declaration")
            symbol, component_id = tokens[1], tokens[2]
            source = ""
            target = ""
            requirements: list[str] = []
            effects: list[str] = []
            index += 1
            while index < len(lines):
                body = lines[index].split()
                if body[0] == "END":
                    require(len(body) == 1, f"{symbol}: invalid END")
                    break
                if body[0] == "FROM":
                    require(len(body) == 2 and not source, f"{symbol}: invalid FROM")
                    source = body[1]
                elif body[0] == "TO":
                    require(len(body) == 2 and not target, f"{symbol}: invalid TO")
                    target = body[1]
                elif body[0] == "REQUIRE":
                    require(len(body) == 2, f"{symbol}: invalid REQUIRE")
                    requirements.append(body[1])
                elif body[0] == "EFFECT":
                    require(len(body) == 2, f"{symbol}: invalid EFFECT")
                    effects.append(body[1])
                else:
                    raise CausalExpressionError(
                        f"{symbol}: unsupported causal statement: {body[0]}"
                    )
                index += 1
            require(
                index < len(lines) and lines[index] == "END",
                f"{symbol}: END missing",
            )
            require(source and target, f"{symbol}: FROM/TO missing")
            transitions.append(
                Transition(
                    symbol=symbol,
                    component_id=component_id,
                    source=source,
                    target=target,
                    requirements=tuple(requirements),
                    effects=tuple(effects),
                )
            )
            index += 1
            continue
        raise CausalExpressionError(f"unsupported causal source statement: {kind}")

    require(semantic_precedence == "NONE", "causal semantic precedence must be NONE")
    require(len(places) == 3, "expected three recognition places")
    require(
        {place.recognition for place in places} == {"UNKNOWN", "ALLOW", "BLOCK"},
        "causal recognition place set mismatch",
    )
    require(
        len({place.symbol for place in places}) == len(places),
        "duplicate causal place symbol",
    )
    initial_by_recognition = {place.recognition: place.initial for place in places}
    require(
        initial_by_recognition == {"UNKNOWN": 1, "ALLOW": 0, "BLOCK": 0},
        "causal initial marking must be exactly UNKNOWN",
    )
    require(invariant_id == "RECOGNITION-ONEHOT", "causal invariant id mismatch")
    require(invariant_total == 1, "recognition invariant total must be one")
    require(
        set(invariant_places) == {place.symbol for place in places},
        "causal invariant does not cover the recognition place set",
    )
    require(len(transitions) == 6, "expected six causal transitions")
    require(
        len({item.symbol for item in transitions}) == len(transitions),
        "duplicate causal transition symbol",
    )
    require(
        len({item.component_id for item in transitions}) == len(transitions),
        "duplicate causal component id",
    )

    bound = {
        item.component_id: item.causal_transition
        for item in binding_plan.causal_bindings
    }
    actual = {item.component_id: item.symbol for item in transitions}
    require(actual == bound, "causal transition set differs from Seed causal bindings")

    place_symbols = {place.symbol for place in places}
    for item in transitions:
        require(item.source in place_symbols, f"{item.symbol}: unknown source place")
        require(item.target in place_symbols, f"{item.symbol}: unknown target place")
        require(
            len(item.requirements) == len(set(item.requirements)),
            f"{item.symbol}: duplicate causal requirement",
        )
        require(
            len(item.effects) == len(set(item.effects)),
            f"{item.symbol}: duplicate causal effect",
        )
        for requirement in item.requirements:
            require(
                requirement
                in {
                    "EVIDENCE_ARGUMENT",
                    "OBSERVED_EVIDENCE",
                    "LOCAL_AUTHORITY_ALLOW",
                    "LOCAL_AUTHORITY_BLOCK",
                },
                f"{item.symbol}: unsupported causal requirement: {requirement}",
            )
        for effect in item.effects:
            require(
                effect in {"ADD_EVIDENCE", "PRESERVE_STATE"},
                f"{item.symbol}: unsupported causal effect: {effect}",
            )

    return CausalNet(
        schema_version=schema_version,
        subject_id=subject_id,
        semantic_precedence=semantic_precedence,
        places=tuple(places),
        invariant_id=invariant_id,
        invariant_places=invariant_places,
        invariant_total=invariant_total,
        transitions=tuple(transitions),
    )


def _recognition_by_place(net: CausalNet) -> dict[str, str]:
    return {place.symbol: place.recognition for place in net.places}


def _semantic_nodes(net: CausalNet, item: Transition) -> list[dict[str, Any]]:
    recognition = _recognition_by_place(net)
    rin = recognition[item.source]
    rout = recognition[item.target]
    nodes: list[dict[str, Any]] = [
        {"id": "n0", "op": "INPUT_STATE"},
        {"id": "n1", "op": "CHECK_RECOGNITION", "value": rin},
    ]
    next_id = 2
    for requirement in item.requirements:
        if requirement == "EVIDENCE_ARGUMENT":
            node = {"id": f"n{next_id}", "op": "REQUIRE_EVIDENCE_ARGUMENT"}
        elif requirement == "OBSERVED_EVIDENCE":
            node = {"id": f"n{next_id}", "op": "REQUIRE_OBSERVED_EVIDENCE"}
        elif requirement == "LOCAL_AUTHORITY_ALLOW":
            node = {
                "id": f"n{next_id}",
                "op": "REQUIRE_LOCAL_AUTHORITY_WITNESS",
                "value": "ALLOW",
            }
        elif requirement == "LOCAL_AUTHORITY_BLOCK":
            node = {
                "id": f"n{next_id}",
                "op": "REQUIRE_LOCAL_AUTHORITY_WITNESS",
                "value": "BLOCK",
            }
        else:
            raise CausalExpressionError(
                f"{item.symbol}: unsupported requirement: {requirement}"
            )
        nodes.append(node)
        next_id += 1

    for effect in item.effects:
        if effect == "ADD_EVIDENCE":
            node = {"id": f"n{next_id}", "op": "ADD_EVIDENCE"}
        elif effect == "PRESERVE_STATE":
            node = {"id": f"n{next_id}", "op": "PRESERVE_STATE"}
        else:
            raise CausalExpressionError(f"{item.symbol}: unsupported effect: {effect}")
        nodes.append(node)
        next_id += 1

    if rin != rout:
        nodes.append({"id": f"n{next_id}", "op": "SET_RECOGNITION", "value": rout})
        next_id += 1
    nodes.append({"id": f"n{next_id}", "op": "RETURN_STATE"})
    return nodes


def derive_causal_graphs(
    root: Path = ROOT, plan: BindingPlan | None = None
) -> dict[str, Any]:
    net = parse_causal_net(root, plan)
    recognition = _recognition_by_place(net)
    components: list[dict[str, Any]] = []
    for item in sorted(net.transitions, key=lambda value: value.component_id):
        nodes = _semantic_nodes(net, item)
        components.append(
            {
                "component_id": item.component_id,
                "source_transition": item.symbol,
                "recognition_from": recognition[item.source],
                "recognition_to": recognition[item.target],
                "requirements": list(item.requirements),
                "effects": list(item.effects),
                "causal_nodes": [
                    {
                        "id": f"place:{item.source}",
                        "kind": "PLACE",
                        "recognition": recognition[item.source],
                    },
                    {"id": f"transition:{item.symbol}", "kind": "TRANSITION"},
                    {
                        "id": f"place:{item.target}",
                        "kind": "PLACE",
                        "recognition": recognition[item.target],
                    },
                ],
                "causal_edges": [
                    [f"place:{item.source}", f"transition:{item.symbol}", "ENABLES"],
                    [f"transition:{item.symbol}", f"place:{item.target}", "PRODUCES"],
                ],
                "nodes": nodes,
                "edges": [
                    [nodes[index]["id"], nodes[index + 1]["id"]]
                    for index in range(len(nodes) - 1)
                ],
            }
        )
    return {
        "document_type": "aset-causal-expression-graph-set",
        "derivation": "RESTRICTED_1_SAFE_CAUSAL_SOURCE",
        "semantic_precedence": "NONE",
        "net": {
            "subject_id": net.subject_id,
            "places": [
                {
                    "symbol": place.symbol,
                    "recognition": place.recognition,
                    "initial": place.initial,
                }
                for place in net.places
            ],
            "invariant": {
                "id": net.invariant_id,
                "places": list(net.invariant_places),
                "total": net.invariant_total,
            },
        },
        "components": components,
    }


def semantic_projection(graph_set: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    value = graph_set.get("components")
    require(isinstance(value, list), "causal graph components missing")
    projected: dict[str, list[dict[str, Any]]] = {}
    for item in value:
        require(isinstance(item, dict), "causal graph component must be an object")
        nodes = item.get("nodes")
        require(isinstance(nodes, list), "causal semantic nodes missing")
        projected[str(item["component_id"])] = [
            {key: node[key] for key in ("op", "value") if key in node}
            for node in nodes
            if isinstance(node, dict)
        ]
    return projected


def check_causal_invariant(graph_set: dict[str, Any]) -> dict[str, Any]:
    net = graph_set.get("net")
    require(isinstance(net, dict), "causal net metadata missing")
    places = net.get("places")
    invariant = net.get("invariant")
    components = graph_set.get("components")
    require(isinstance(places, list), "causal places missing")
    require(isinstance(invariant, dict), "causal invariant missing")
    require(isinstance(components, list), "causal components missing")

    initial = {str(item["symbol"]): int(item["initial"]) for item in places}
    invariant_places = tuple(str(value) for value in invariant.get("places", []))
    total = int(invariant.get("total", -1))
    require(
        sum(initial.get(place, 0) for place in invariant_places) == total == 1,
        "initial recognition marking violates one-hot invariant",
    )

    checked = 0
    for component in components:
        require(isinstance(component, dict), "causal component must be an object")
        edges = component.get("causal_edges")
        require(
            isinstance(edges, list) and len(edges) == 2,
            "causal transition must have one enabling and one producing arc",
        )
        source_edge, target_edge = edges
        require(source_edge[2] == "ENABLES", "causal source arc kind mismatch")
        require(target_edge[2] == "PRODUCES", "causal target arc kind mismatch")
        source = str(source_edge[0]).removeprefix("place:")
        target = str(target_edge[1]).removeprefix("place:")
        require(
            source in invariant_places,
            "causal source is outside recognition invariant",
        )
        require(
            target in invariant_places,
            "causal target is outside recognition invariant",
        )

        for marked in invariant_places:
            marking = {place: int(place == marked) for place in invariant_places}
            if marking[source] != 1:
                continue
            after = dict(marking)
            after[source] -= 1
            after[target] += 1
            require(
                all(value in {0, 1} for value in after.values()),
                "causal transition violates 1-safeness",
            )
            require(
                sum(after.values()) == total,
                "causal transition violates recognition-token conservation",
            )
            checked += 1

    return {
        "invariant_id": str(invariant["id"]),
        "relation": "RECOGNITION_TOKEN_CONSERVATION",
        "transitions_checked": checked,
        "one_safe": True,
        "total": total,
        "status": "PASS",
    }


def apply_causal_graph(
    graph_set: dict[str, Any],
    current: dict[str, Any],
    component_id: str,
    *,
    evidence: str | None = None,
    authority_recognition: frozenset[tuple[str, str, str, str]] = frozenset(),
) -> dict[str, Any]:
    components = graph_set.get("components")
    require(isinstance(components, list), "causal graph components missing")
    component = next(
        (
            item
            for item in components
            if isinstance(item, dict) and item.get("component_id") == component_id
        ),
        None,
    )
    require(component is not None, f"unknown causal component: {component_id}")
    required_recognition = str(component["recognition_from"])
    if current["recognition"] != required_recognition:
        raise ValueError("recognition precondition")

    result = dict(current)
    requirements = component.get("requirements")
    effects = component.get("effects")
    require(isinstance(requirements, list), f"{component_id}: requirements missing")
    require(isinstance(effects, list), f"{component_id}: effects missing")
    for requirement in requirements:
        if requirement == "EVIDENCE_ARGUMENT":
            if evidence is None:
                raise ValueError("evidence required")
        elif requirement == "OBSERVED_EVIDENCE":
            if evidence not in current["evidence"]:
                raise ValueError("observed evidence required")
        elif requirement in {"LOCAL_AUTHORITY_ALLOW", "LOCAL_AUTHORITY_BLOCK"}:
            outcome = "ALLOW" if requirement.endswith("ALLOW") else "BLOCK"
            witness = (
                str(current["authority"]),
                str(current["subject"]),
                evidence,
                outcome,
            )
            if witness not in authority_recognition:
                raise ValueError("local authority witness required")
        else:
            raise CausalExpressionError(
                f"{component_id}: unsupported causal requirement: {requirement}"
            )

    for effect in effects:
        if effect == "ADD_EVIDENCE":
            observed = set(current["evidence"])
            observed.add(evidence)
            result["evidence"] = tuple(sorted(observed))
        elif effect == "PRESERVE_STATE":
            continue
        else:
            raise CausalExpressionError(
                f"{component_id}: unsupported causal effect: {effect}"
            )
    result["recognition"] = str(component["recognition_to"])
    return result


def write_causal_graph(path: Path, graph: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        graph = derive_causal_graphs(ROOT)
        invariant = check_causal_invariant(graph)
        count = len(graph["components"])
        print(f"ALPHA4_CAUSAL_COMPONENTS={count}/{count} PASS")
        print(
            "ALPHA4_CAUSAL_RECOGNITION_TOKEN_INVARIANT="
            f"{invariant['transitions_checked']}/"
            f"{invariant['transitions_checked']} PASS"
        )
        print("ALPHA4_CAUSAL_EXPRESSION=PASS")
        if args.output is not None:
            target = args.output if args.output.is_absolute() else ROOT / args.output
            write_causal_graph(target, graph)
        return 0
    except (CausalExpressionError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"ALPHA4_CAUSAL_EXPRESSION_ERROR={error}")
        print("ALPHA4_CAUSAL_EXPRESSION=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
