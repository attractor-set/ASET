#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict, deque

from monade_attempt_profile_common import MODEL_RESULTS, STATE_SPACE, canonical_text, load


def build_results() -> dict[str, object]:
    model = load(STATE_SPACE)
    nodes = model["nodes"]
    transitions = model["transitions"]
    assert isinstance(nodes, list)
    assert isinstance(transitions, list)
    by_id = {str(node["id"]): node for node in nodes if isinstance(node, dict)}
    outgoing: dict[str, list[str]] = defaultdict(list)
    errors: list[str] = []
    for transition in transitions:
        assert isinstance(transition, dict)
        source = str(transition["from"])
        target = str(transition["to"])
        if source not in by_id or target not in by_id:
            errors.append(f"unknown transition endpoint:{source}->{target}")
        outgoing[source].append(target)

    initial = str(model["initial_state"])
    reached: set[str] = set()
    queue: deque[str] = deque([initial])
    while queue:
        current = queue.popleft()
        if current in reached:
            continue
        reached.add(current)
        queue.extend(outgoing.get(current, []))

    for identifier, node in by_id.items():
        negative = bool(node["negative"])
        if node.get("canonical_state_changed") is not False:
            errors.append(f"canonical state changed:{identifier}")
        if node.get("candidate_parent_allowed") is not False:
            errors.append(f"candidate parent allowed:{identifier}")
        if node.get("record_append_only") is not True:
            errors.append(f"record not append-only:{identifier}")
        if node.get("parent_reference") != "EXACT":
            errors.append(f"parent reference differs:{identifier}")
        if node.get("permit_reference") != "EXACT":
            errors.append(f"permit reference differs:{identifier}")
        if node.get("evidence_refs_content_addressed") is not True:
            errors.append(f"evidence reference not content addressed:{identifier}")
        if node.get("master_projection") != "READ_ONLY":
            errors.append(f"Master projection not read-only:{identifier}")
        if node.get("recognized_outcome") is not False:
            errors.append(f"Monade recognizes Outcome:{identifier}")
        if node.get("retry_reuses_attempt_id") is not False:
            errors.append(f"retry reuses attempt ID:{identifier}")
        if negative and node.get("terminal") is not True:
            errors.append(f"negative state not terminal:{identifier}")
        if negative and outgoing.get(identifier):
            errors.append(f"negative state has successor:{identifier}")

    negative_count = sum(bool(node["negative"]) for node in by_id.values())
    expected = model["expected"]
    if len(reached) != expected["states"]:
        errors.append(f"reachable states differ:{len(reached)}")
    if len(transitions) != expected["transitions"]:
        errors.append(f"transition count differs:{len(transitions)}")
    if negative_count != expected["negative_terminal_states"]:
        errors.append(f"negative state count differs:{negative_count}")

    return {
        "document_type": "aset-monade-attempt-profile-model-check",
        "profile_id": "ASET-MONADE-ATTEMPT-EVIDENCE-V1",
        "states": len(reached),
        "transitions": len(transitions),
        "negative_terminal_states": negative_count,
        "invariants_checked": 10,
        "errors": sorted(errors),
        "verdict": "PASS" if not errors else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = build_results()
    content = canonical_text(results)
    if args.check:
        if not MODEL_RESULTS.is_file() or MODEL_RESULTS.read_text(encoding="utf-8") != content:
            print("MONADE_ATTEMPT_MODEL_PARITY=DIFFERENT")
            return 1
    else:
        MODEL_RESULTS.write_text(content, encoding="utf-8", newline="\n")
    print(f"MONADE_ATTEMPT_MODEL_STATES={results['states']}")
    print(f"MONADE_ATTEMPT_MODEL_TRANSITIONS={results['transitions']}")
    print(f"MONADE_ATTEMPT_NEGATIVE_TERMINALS={results['negative_terminal_states']}")
    print(f"MONADE_ATTEMPT_MODEL_VERDICT={results['verdict']}")
    return 0 if results["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
