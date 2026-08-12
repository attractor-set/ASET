#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from tools.alpha4_binding_graph import parse_seed_bindings
except ModuleNotFoundError:
    from alpha4_binding_graph import parse_seed_bindings

ROOT = Path(__file__).resolve().parents[1]


class RelationalExpressionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RelationalExpressionError(message)


def strip_tla_comments(text: str) -> str:
    without_blocks = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    return re.sub(r"(?m)\\\*.*$", "", without_blocks)


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def extract_operator_body(text: str, operator: str) -> str:
    text = strip_tla_comments(text)
    pattern = re.compile(
        rf"(?ms)^{re.escape(operator)}\(s, t, e\) ==\s*(?P<body>.*?)"
        rf"(?=^[A-Z][A-Za-z0-9_]*\(s, t, e\) ==|^=+)"
    )
    match = pattern.search(text)
    if match is None:
        raise RelationalExpressionError(f"formal operator missing: {operator}")
    return compact(match.group("body"))


def _component_index(root: Path) -> dict[str, Any]:
    bindings = parse_seed_bindings(root)
    return {item.formal_operator: item for item in bindings.pairs}


def _recognition_input(body: str, operator: str) -> str:
    match = re.search(r's\.recognition="(?P<value>UNKNOWN|ALLOW|BLOCK)"', body)
    if match is None:
        raise RelationalExpressionError(f"{operator}: recognition precondition missing")
    return match.group("value")


def _nodes_for(body: str, operator: str) -> list[dict[str, Any]]:
    rin = _recognition_input(body, operator)
    nodes: list[dict[str, Any]] = [
        {"id": "n0", "op": "INPUT_STATE"},
        {"id": "n1", "op": "CHECK_RECOGNITION", "value": rin},
    ]
    evidence_update = compact("t = [s EXCEPT !.evidence = @ \\cup {e}]")
    if evidence_update in body:
        require(
            compact("e \\in EvidenceItems") in body,
            f"{operator}: evidence domain missing",
        )
        nodes += [
            {"id": "n2", "op": "REQUIRE_EVIDENCE_ARGUMENT"},
            {"id": "n3", "op": "ADD_EVIDENCE"},
            {"id": "n4", "op": "RETURN_STATE"},
        ]
        return nodes

    update = re.search(r't=\[sEXCEPT!\.recognition="(?P<value>ALLOW|BLOCK)"\]', body)
    if update is not None:
        outcome = update.group("value")
        require(
            compact("e \\in s.evidence") in body,
            f"{operator}: observed evidence guard missing",
        )
        witness = compact(
            f'<<s.authority, s.subject, e, "{outcome}">> \\in AuthorityRecognition'
        )
        require(witness in body, f"{operator}: local authority witness missing")
        nodes += [
            {"id": "n2", "op": "REQUIRE_EVIDENCE_ARGUMENT"},
            {"id": "n3", "op": "REQUIRE_OBSERVED_EVIDENCE"},
            {"id": "n4", "op": "REQUIRE_LOCAL_AUTHORITY_WITNESS", "value": outcome},
            {"id": "n5", "op": "SET_RECOGNITION", "value": outcome},
            {"id": "n6", "op": "RETURN_STATE"},
        ]
        return nodes

    require(compact("t = s") in body, f"{operator}: unsupported relational effect")
    nodes += [
        {"id": "n2", "op": "PRESERVE_STATE"},
        {"id": "n3", "op": "RETURN_STATE"},
    ]
    return nodes


def derive_relational_graphs(root: Path = ROOT) -> dict[str, Any]:
    index = _component_index(root)
    text = (root / "seed/alpha4/formal/ComponentRelations.tla").read_text(
        encoding="utf-8"
    )
    components = []
    for operator in sorted(index):
        item = index[operator]
        body = extract_operator_body(text, operator)
        nodes = _nodes_for(body, operator)
        components.append(
            {
                "component_id": item.component_id,
                "source_operator": operator,
                "nodes": nodes,
                "edges": [
                    [nodes[index]["id"], nodes[index + 1]["id"]]
                    for index in range(len(nodes) - 1)
                ],
            }
        )
    return {
        "document_type": "aset-relational-expression-graph-set",
        "derivation": "FORMAL_RELATIONAL_SOURCE",
        "semantic_precedence": "NONE",
        "components": components,
    }


def semantic_projection(graph_set: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    value = graph_set.get("components")
    require(isinstance(value, list), "relational graph components missing")
    projected: dict[str, list[dict[str, Any]]] = {}
    for item in value:
        require(isinstance(item, dict), "relational graph component must be an object")
        nodes = item.get("nodes")
        require(isinstance(nodes, list), "relational graph nodes missing")
        projected[str(item["component_id"])] = [
            {key: node[key] for key in ("op", "value") if key in node}
            for node in nodes
            if isinstance(node, dict)
        ]
    return projected


def _component_graph(graph_set: dict[str, Any], component_id: str) -> dict[str, Any]:
    value = graph_set.get("components")
    require(isinstance(value, list), "relational graph components missing")
    matches = [
        item
        for item in value
        if isinstance(item, dict) and item.get("component_id") == component_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown component: {component_id}")
    return matches[0]


def apply_reference_graph(
    graph_set: dict[str, Any],
    current: dict[str, Any],
    component_id: str,
    *,
    evidence: str | None = None,
    authority_recognition: frozenset[tuple[str, str, str, str]] = frozenset(),
) -> dict[str, Any]:
    component = _component_graph(graph_set, component_id)
    nodes = component.get("nodes")
    require(isinstance(nodes, list), f"{component_id}: nodes missing")
    result = dict(current)
    for node in nodes:
        require(isinstance(node, dict), f"{component_id}: node must be an object")
        op = str(node["op"])
        if op == "INPUT_STATE":
            continue
        if op == "CHECK_RECOGNITION":
            if current["recognition"] != node["value"]:
                raise ValueError("recognition precondition")
        elif op == "REQUIRE_EVIDENCE_ARGUMENT":
            if evidence is None:
                raise ValueError("evidence required")
        elif op == "REQUIRE_OBSERVED_EVIDENCE":
            if evidence not in current["evidence"]:
                raise ValueError("observed evidence required")
        elif op == "REQUIRE_LOCAL_AUTHORITY_WITNESS":
            witness = (
                str(current["authority"]),
                str(current["subject"]),
                evidence,
                str(node["value"]),
            )
            if witness not in authority_recognition:
                raise ValueError("local authority witness required")
        elif op == "ADD_EVIDENCE":
            observed = set(current["evidence"])
            observed.add(evidence)
            result["evidence"] = tuple(sorted(observed))
        elif op == "SET_RECOGNITION":
            result["recognition"] = node["value"]
        elif op == "PRESERVE_STATE":
            continue
        elif op == "RETURN_STATE":
            return result
        else:
            raise RelationalExpressionError(
                f"{component_id}: unsupported graph operation: {op}"
            )
    raise RelationalExpressionError(f"{component_id}: graph has no RETURN_STATE")
