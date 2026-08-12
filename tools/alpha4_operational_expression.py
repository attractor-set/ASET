#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

try:
    from tools.alpha4_binding_graph import parse_seed_bindings
except ModuleNotFoundError:
    from alpha4_binding_graph import parse_seed_bindings

ROOT = Path(__file__).resolve().parents[1]


class OperationalExpressionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OperationalExpressionError(message)


def _component_index(root: Path) -> dict[str, Any]:
    bindings = parse_seed_bindings(root)
    return {item.operational_word: item for item in bindings.pairs}


def _parse_words(text: str) -> dict[str, dict[str, Any]]:
    words: dict[str, dict[str, Any]] = {}
    pattern = re.compile(
        r":\s+(?P<word>[A-Z0-9-]+)\s+"
        r"\(\s*(?P<before>.*?)\s+--\s+(?P<after>.*?)\s*\)\s+"
        r"(?P<guard>UNKNOWN\?|ALLOW\?|BLOCK\?)\s+"
        r"(?P<primitive>OBSERVE|LOCAL-ALLOW!|LOCAL-BLOCK!|NOP)\s*;"
    )
    guard_values = {"UNKNOWN?": "UNKNOWN", "ALLOW?": "ALLOW", "BLOCK?": "BLOCK"}
    for match in pattern.finditer(text):
        word = match.group("word")
        require(word not in words, f"duplicate operational word: {word}")
        rin = guard_values[match.group("guard")]
        primitive = match.group("primitive")
        if primitive == "LOCAL-ALLOW!":
            rout = "ALLOW"
        elif primitive == "LOCAL-BLOCK!":
            rout = "BLOCK"
        else:
            rout = rin
        words[word] = {
            "recognition_in": rin,
            "recognition_out": rout,
            "structural_in": match.group("before").split(),
            "structural_out": match.group("after").split(),
            "guard": match.group("guard"),
            "primitive": primitive,
        }
    require(words, "no restricted operational words found")
    return words


def _nodes_for(word: dict[str, Any]) -> list[dict[str, Any]]:
    rin = str(word["recognition_in"])
    rout = str(word["recognition_out"])
    primitive = str(word["primitive"])
    nodes: list[dict[str, Any]] = [
        {"id": "n0", "op": "INPUT_STATE"},
        {"id": "n1", "op": "CHECK_RECOGNITION", "value": rin},
    ]
    if primitive == "OBSERVE":
        require(rin == rout, "OBSERVE must preserve recognition boundary")
        nodes += [
            {"id": "n2", "op": "REQUIRE_EVIDENCE_ARGUMENT"},
            {"id": "n3", "op": "ADD_EVIDENCE"},
            {"id": "n4", "op": "RETURN_STATE"},
        ]
    elif primitive in {"LOCAL-ALLOW!", "LOCAL-BLOCK!"}:
        outcome = "ALLOW" if primitive == "LOCAL-ALLOW!" else "BLOCK"
        require(rout == outcome, f"{primitive} boundary differs from primitive outcome")
        nodes += [
            {"id": "n2", "op": "REQUIRE_EVIDENCE_ARGUMENT"},
            {"id": "n3", "op": "REQUIRE_OBSERVED_EVIDENCE"},
            {"id": "n4", "op": "REQUIRE_LOCAL_AUTHORITY_WITNESS", "value": outcome},
            {"id": "n5", "op": "SET_RECOGNITION", "value": outcome},
            {"id": "n6", "op": "RETURN_STATE"},
        ]
    elif primitive == "NOP":
        require(rin == rout, "NOP must preserve recognition boundary")
        nodes += [
            {"id": "n2", "op": "PRESERVE_STATE"},
            {"id": "n3", "op": "RETURN_STATE"},
        ]
    else:
        raise OperationalExpressionError(
            f"unsupported restricted operational primitive: {primitive}"
        )
    return nodes


def derive_operational_graphs(root: Path = ROOT) -> dict[str, Any]:
    index = _component_index(root)
    words = _parse_words(
        (root / "seed/alpha4/operational/components.forth").read_text(encoding="utf-8")
    )
    require(
        words.keys() == index.keys(),
        "operational word set differs from component identity set",
    )
    components = []
    for word in sorted(words):
        item = index[word]
        parsed = words[word]
        nodes = _nodes_for(parsed)
        components.append(
            {
                "component_id": item.component_id,
                "source_word": word,
                "source_primitive": str(parsed["primitive"]),
                "structural_in": [
                    str(value).lower() for value in parsed["structural_in"]
                ],
                "structural_out": [
                    str(value).lower() for value in parsed["structural_out"]
                ],
                "nodes": nodes,
                "edges": [
                    [nodes[index]["id"], nodes[index + 1]["id"]]
                    for index in range(len(nodes) - 1)
                ],
            }
        )
    return {
        "document_type": "aset-operational-expression-graph-set",
        "derivation": "RESTRICTED_OPERATIONAL_SOURCE",
        "semantic_precedence": "NONE",
        "components": components,
    }


def semantic_projection(graph_set: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    value = graph_set.get("components")
    require(isinstance(value, list), "operational graph components missing")
    projected: dict[str, list[dict[str, Any]]] = {}
    for item in value:
        require(isinstance(item, dict), "operational graph component must be an object")
        nodes = item.get("nodes")
        require(isinstance(nodes, list), "operational graph nodes missing")
        projected[str(item["component_id"])] = [
            {key: node[key] for key in ("op", "value") if key in node}
            for node in nodes
            if isinstance(node, dict)
        ]
    return projected


def _compile_component(component: dict[str, Any]) -> Callable[..., dict[str, Any]]:
    component_id = str(component["component_id"])
    nodes = component.get("nodes")
    require(isinstance(nodes, list), f"{component_id}: nodes missing")
    lines = [
        "def _apply(current, evidence=None, authority_recognition=frozenset()):",
        "    result = dict(current)",
    ]
    for node in nodes:
        require(isinstance(node, dict), f"{component_id}: node must be an object")
        op = str(node["op"])
        if op == "INPUT_STATE":
            continue
        if op == "CHECK_RECOGNITION":
            lines += [
                f"    if current['recognition'] != {str(node['value'])!r}:",
                "        raise ValueError('recognition precondition')",
            ]
        elif op == "REQUIRE_EVIDENCE_ARGUMENT":
            lines += [
                "    if evidence is None:",
                "        raise ValueError('evidence required')",
            ]
        elif op == "REQUIRE_OBSERVED_EVIDENCE":
            lines += [
                "    if evidence not in current['evidence']:",
                "        raise ValueError('observed evidence required')",
            ]
        elif op == "REQUIRE_LOCAL_AUTHORITY_WITNESS":
            outcome = str(node["value"])
            lines += [
                "    witness = (str(current['authority']), str(current['subject']), evidence, "
                f"{outcome!r})",
                "    if witness not in authority_recognition:",
                "        raise ValueError('local authority witness required')",
            ]
        elif op == "ADD_EVIDENCE":
            lines += [
                "    observed = set(current['evidence'])",
                "    observed.add(evidence)",
                "    result['evidence'] = tuple(sorted(observed))",
            ]
        elif op == "SET_RECOGNITION":
            lines.append(f"    result['recognition'] = {str(node['value'])!r}")
        elif op == "PRESERVE_STATE":
            continue
        elif op == "RETURN_STATE":
            lines.append("    return result")
        else:
            raise OperationalExpressionError(
                f"{component_id}: unsupported graph operation: {op}"
            )
    namespace: dict[str, Any] = {}
    source = "\n".join(lines) + "\n"
    exec(compile(source, f"<aset-alpha4-jit:{component_id}>", "exec"), namespace)
    function = namespace.get("_apply")
    require(callable(function), f"{component_id}: JIT compilation failed")
    return function


def compile_operational_jit(
    graph_set: dict[str, Any],
) -> Callable[..., dict[str, Any]]:
    value = graph_set.get("components")
    require(isinstance(value, list), "operational graph components missing")
    compiled: dict[str, Callable[..., dict[str, Any]]] = {}
    for item in value:
        require(isinstance(item, dict), "operational graph component must be an object")
        component_id = str(item["component_id"])
        compiled[component_id] = _compile_component(item)

    def apply_component(
        current: dict[str, Any],
        component_id: str,
        *,
        evidence: str | None = None,
        authority_recognition: frozenset[tuple[str, str, str, str]] = frozenset(),
    ) -> dict[str, Any]:
        try:
            function = compiled[component_id]
        except KeyError as error:
            raise ValueError(f"unknown component: {component_id}") from error
        return function(
            current,
            evidence=evidence,
            authority_recognition=authority_recognition,
        )

    return apply_component
