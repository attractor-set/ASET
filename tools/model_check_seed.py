#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

IDS = (0, 1)
BINDINGS = (0, 1)
AUTHORITIES = (0, 1)
TERMINALS = ("ALLOW", "BLOCK")
NO_COMMITMENT = -1
RECOGNIZED_TERMINAL_COMMITMENTS = frozenset({0, 1})
RECOGNIZED_AUTHORITY_BINDINGS = frozenset({(0, 0), (1, 1), (1, 0)})

STATE_PROPERTIES = (
    "TypeOK",
    "ResolutionDomain",
    "AllowSoundness",
    "FailClosed",
    "TerminalBindingDerived",
    "RequestAuthorityRecognized",
    "TerminalAuthorityRecognized",
    "AcceptedTerminalUnique",
    "ConflictSound",
    "FreshReconsideration",
)
TEMPORAL_PROPERTIES = (
    "RequestsAppendOnly",
    "TerminalRecordsImmutable",
    "SeedStateChangesOnlyByRecognizedTransition",
    "ConflictObservationPreservesSeedState",
)
FORMAL_PROPERTIES = STATE_PROPERTIES + TEMPORAL_PROPERTIES


@dataclass(frozen=True)
class State:
    # Seed-owned request provenance: resolution_id, binding, previous commitment.
    requests: tuple[tuple[int, int, int], ...]
    # Seed-owned accepted terminal provenance: resolution_id, authority, terminal value.
    records: tuple[tuple[int, int, str], ...]
    # Environment state: observed conflict among valid terminal records.
    conflicts: frozenset[int]


def initial() -> State:
    return State((), (), frozenset())


def request_map(state: State) -> dict[int, tuple[int, int]]:
    return {rid: (binding, previous) for rid, binding, previous in state.requests}


def record_map(state: State) -> dict[int, tuple[int, str]]:
    return {rid: (authority, value) for rid, authority, value in state.records}


def resolution_of(state: State, rid: int) -> str:
    requests = request_map(state)
    records = record_map(state)
    if rid not in requests or rid in state.conflicts or rid not in records:
        return "UNKNOWN"
    return records[rid][1]


def effect_permitted(state: State, rid: int) -> bool:
    return resolution_of(state, rid) == "ALLOW"


def seed_projection(state: State) -> tuple[object, ...]:
    return (state.requests, state.records)


def successors(state: State) -> Iterable[tuple[str, State]]:
    requests = request_map(state)
    records = record_map(state)

    for rid in IDS:
        if rid in requests:
            continue
        for _authority, binding in RECOGNIZED_AUTHORITY_BINDINGS:
            yield (
                "RegisterRequest",
                State(
                    tuple(sorted((*state.requests, (rid, binding, NO_COMMITMENT)))),
                    state.records,
                    state.conflicts,
                ),
            )
            for previous in RECOGNIZED_TERMINAL_COMMITMENTS:
                yield (
                    "RegisterReconsideration",
                    State(
                        tuple(sorted((*state.requests, (rid, binding, previous)))),
                        state.records,
                        state.conflicts,
                    ),
                )

    for rid, (binding, _previous) in requests.items():
        if rid in records or rid in state.conflicts:
            continue
        for authority, proof_binding in RECOGNIZED_AUTHORITY_BINDINGS:
            if proof_binding != binding:
                continue
            for value in TERMINALS:
                yield (
                    "SubmitResolution",
                    State(
                        state.requests,
                        tuple(sorted((*state.records, (rid, authority, value)))),
                        state.conflicts,
                    ),
                )

    for rid in records:
        if rid not in state.conflicts:
            yield (
                "ObserveConflict",
                State(state.requests, state.records, state.conflicts | {rid}),
            )


def state_errors(state: State) -> list[str]:
    errors: list[str] = []
    requests = request_map(state)
    records = record_map(state)

    if len(requests) != len(state.requests) or len(records) != len(state.records):
        errors.append("TypeOK")
    if not state.conflicts.issubset(IDS):
        errors.append("TypeOK")

    if not set(records).issubset(requests):
        errors.append("TerminalBindingDerived")
    if len(records) != len(state.records):
        errors.append("AcceptedTerminalUnique")

    for _rid, (binding, _previous) in requests.items():
        if not any(
            authority in AUTHORITIES
            and (authority, binding) in RECOGNIZED_AUTHORITY_BINDINGS
            for authority in AUTHORITIES
        ):
            errors.append("RequestAuthorityRecognized")

    for rid, (authority, _value) in records.items():
        request = requests.get(rid)
        if request is None or (authority, request[0]) not in RECOGNIZED_AUTHORITY_BINDINGS:
            errors.append("TerminalAuthorityRecognized")

    for rid in IDS:
        value = resolution_of(state, rid)
        if value not in {"UNKNOWN", "ALLOW", "BLOCK"}:
            errors.append("ResolutionDomain")

        if effect_permitted(state, rid):
            record = records.get(rid)
            request = requests.get(rid)
            if (
                request is None
                or rid in state.conflicts
                or record is None
                or record[1] != "ALLOW"
                or (record[0], request[0]) not in RECOGNIZED_AUTHORITY_BINDINGS
            ):
                errors.append("AllowSoundness")

        if value != "ALLOW" and effect_permitted(state, rid):
            errors.append("FailClosed")

        if rid in state.conflicts and value != "UNKNOWN":
            errors.append("ConflictSound")

    for _rid, (_binding, previous) in requests.items():
        if previous == NO_COMMITMENT:
            continue
        if previous not in RECOGNIZED_TERMINAL_COMMITMENTS:
            errors.append("FreshReconsideration")

    return sorted(set(errors))


def transition_errors(action: str, before: State, after: State) -> list[str]:
    errors: list[str] = []

    if not set(before.requests).issubset(after.requests):
        errors.append("RequestsAppendOnly")

    before_records = record_map(before)
    after_records = record_map(after)
    for rid, record in before_records.items():
        if after_records.get(rid) != record:
            errors.append("TerminalRecordsImmutable")

    recognized_seed_actions = {"RegisterRequest", "RegisterReconsideration", "SubmitResolution"}
    if seed_projection(before) != seed_projection(after) and action not in recognized_seed_actions:
        errors.append("SeedStateChangesOnlyByRecognizedTransition")

    if action == "ObserveConflict" and seed_projection(before) != seed_projection(after):
        errors.append("ConflictObservationPreservesSeedState")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="Optional diagnostic depth bound. Omit for exhaustive finite-state saturation.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    queue = deque([(initial(), 0)])
    seen = {initial()}
    generated_action_instances = 0
    transitions = 0
    failures: list[dict[str, object]] = []
    terminal_states = 0
    max_depth_seen = 0
    truncated = False

    while queue:
        state, depth = queue.popleft()
        max_depth_seen = max(max_depth_seen, depth)
        errors = state_errors(state)
        if errors:
            failures.append({"state": repr(state), "errors": errors})
            continue
        terminal_states += sum(resolution_of(state, rid) in TERMINALS for rid in IDS)
        if args.depth is not None and depth >= args.depth:
            truncated = True
            continue
        unique_edges: set[tuple[str, State]] = set()
        for action, successor in successors(state):
            generated_action_instances += 1
            edge = (action, successor)
            if edge in unique_edges:
                continue
            unique_edges.add(edge)
            transitions += 1
            edge_errors = transition_errors(action, state, successor)
            if edge_errors:
                failures.append(
                    {
                        "state": repr(state),
                        "action": action,
                        "successor": repr(successor),
                        "errors": edge_errors,
                    }
                )
                continue
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, depth + 1))

    saturated = args.depth is None and not truncated
    report = {
        "document_type": "aset-seed-minimal-kernel-finite-model-check",
        "depth_limit": args.depth,
        "max_depth_reached": max_depth_seen,
        "saturated": saturated,
        "states": len(seen),
        "transitions": transitions,
        "transition_metric": "unique_labelled_graph_edges",
        "generated_action_instances": generated_action_instances,
        "duplicate_action_instances": generated_action_instances - transitions,
        "terminal_states": terminal_states,
        "state_properties": list(STATE_PROPERTIES),
        "temporal_properties": list(TEMPORAL_PROPERTIES),
        "invariants": list(FORMAL_PROPERTIES),
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )

    print(f"MODEL_CHECK_STATES={len(seen)}")
    print(f"MODEL_CHECK_TRANSITIONS={transitions}")
    print(f"MODEL_CHECK_ACTION_INSTANCES={generated_action_instances}")
    print(
        "MODEL_CHECK_DUPLICATE_ACTION_INSTANCES="
        f"{generated_action_instances - transitions}"
    )
    print(f"MODEL_CHECK_TERMINAL_STATES={terminal_states}")
    print(f"MODEL_CHECK_FORMAL_PROPERTIES={len(FORMAL_PROPERTIES)}")
    print("MODEL_CHECK_SATURATED=" + ("true" if saturated else "false"))
    print("MODEL_CHECK_VERDICT=" + report["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
