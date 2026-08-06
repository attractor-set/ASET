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
NO_PREVIOUS = -1
LOCAL_AUTHORITY_BINDINGS = frozenset({(0, 0), (1, 1)})
AUTHORITY_PROOF_BINDINGS = frozenset({(0, 0), (1, 1), (1, 0)})

STATE_PROPERTIES = (
    "TypeOK",
    "ResolutionDomain",
    "AllowSoundness",
    "FailClosed",
    "ExactBinding",
    "LocalAuthorityRoot",
    "DelegatedAuthoritySound",
    "InputsNonAuthoritative",
    "TerminalUnique",
    "InvalidOrConflictUnknown",
    "FreshReconsideration",
)
TEMPORAL_PROPERTIES = (
    "RequestsAppendOnly",
    "TerminalRecordsImmutable",
    "RejectedOperationPreservesStore",
    "ObservedInputsAppendOnly",
)
FORMAL_PROPERTIES = STATE_PROPERTIES + TEMPORAL_PROPERTIES


@dataclass(frozen=True)
class State:
    # request tuple: resolution_id, binding, initial_authority, previous_resolution
    requests: tuple[tuple[int, int, int, int], ...]
    # record tuple: resolution_id, binding, authority, terminal_value
    records: tuple[tuple[int, int, int, str], ...]
    conflicts: frozenset[int]
    invalid_material: frozenset[int]
    observed_inputs: frozenset[int]
    rejected: bool


def initial() -> State:
    return State((), (), frozenset(), frozenset(), frozenset(), False)


def request_map(state: State) -> dict[int, tuple[int, int, int]]:
    return {rid: (binding, authority, previous) for rid, binding, authority, previous in state.requests}


def record_map(state: State) -> dict[int, tuple[int, int, str]]:
    return {rid: (binding, authority, value) for rid, binding, authority, value in state.records}


def resolution_of(state: State, rid: int) -> str:
    requests = request_map(state)
    records = record_map(state)
    if rid not in requests or rid in state.conflicts or rid not in records:
        return "UNKNOWN"
    return records[rid][2]


def effect_permitted(state: State, rid: int) -> bool:
    return resolution_of(state, rid) == "ALLOW"


def canonical_projection(state: State) -> tuple[object, ...]:
    return (
        state.requests,
        state.records,
        state.conflicts,
        state.invalid_material,
        state.observed_inputs,
    )


def successors(state: State) -> Iterable[tuple[str, State]]:
    requests = request_map(state)
    records = record_map(state)

    for rid in IDS:
        if rid in requests:
            continue
        for binding, authority in LOCAL_AUTHORITY_BINDINGS:
            yield (
                "RegisterRequest",
                State(
                    tuple(sorted((*state.requests, (rid, binding, authority, NO_PREVIOUS)))),
                    state.records,
                    state.conflicts,
                    state.invalid_material,
                    state.observed_inputs,
                    state.rejected,
                ),
            )
        for previous in IDS:
            if previous == rid or resolution_of(state, previous) not in TERMINALS:
                continue
            for binding, authority in LOCAL_AUTHORITY_BINDINGS:
                yield (
                    "RegisterReconsideration",
                    State(
                        tuple(sorted((*state.requests, (rid, binding, authority, previous)))),
                        state.records,
                        state.conflicts,
                        state.invalid_material,
                        state.observed_inputs,
                        state.rejected,
                    ),
                )

    for rid, (binding, _, _) in requests.items():
        if rid in records or rid in state.conflicts:
            continue
        for authority, proof_binding in AUTHORITY_PROOF_BINDINGS:
            if proof_binding != binding:
                continue
            for value in TERMINALS:
                yield (
                    "SubmitResolution",
                    State(
                        state.requests,
                        tuple(sorted((*state.records, (rid, binding, authority, value)))),
                        state.conflicts,
                        state.invalid_material,
                        state.observed_inputs,
                        state.rejected,
                    ),
                )

    for rid in IDS:
        if rid not in state.conflicts:
            yield (
                "ObserveConflict",
                State(
                    state.requests,
                    state.records,
                    state.conflicts | {rid},
                    state.invalid_material,
                    state.observed_inputs,
                    state.rejected,
                ),
            )
        if rid not in state.invalid_material:
            yield (
                "ObserveInvalidMaterial",
                State(
                    state.requests,
                    state.records,
                    state.conflicts,
                    state.invalid_material | {rid},
                    state.observed_inputs,
                    state.rejected,
                ),
            )
        if rid not in state.observed_inputs:
            yield (
                "ObserveNonAuthoritativeInput",
                State(
                    state.requests,
                    state.records,
                    state.conflicts,
                    state.invalid_material,
                    state.observed_inputs | {rid},
                    state.rejected,
                ),
            )

    if not state.rejected:
        yield (
            "RejectOperation",
            State(
                state.requests,
                state.records,
                state.conflicts,
                state.invalid_material,
                state.observed_inputs,
                True,
            ),
        )
    yield "Evaluate", state


def state_errors(state: State) -> list[str]:
    errors: list[str] = []
    requests = request_map(state)
    records = record_map(state)

    if len(requests) != len(state.requests) or len(records) != len(state.records):
        errors.append("TypeOK")
    if not state.conflicts.issubset(IDS) or not state.invalid_material.issubset(IDS):
        errors.append("TypeOK")
    if not state.observed_inputs.issubset(IDS):
        errors.append("TypeOK")

    for rid in IDS:
        value = resolution_of(state, rid)
        if value not in {"UNKNOWN", "ALLOW", "BLOCK"}:
            errors.append("ResolutionDomain")
        if effect_permitted(state, rid):
            record = records.get(rid)
            if (
                rid not in requests
                or rid in state.conflicts
                or record is None
                or record[2] != "ALLOW"
                or record[0] != requests[rid][0]
                or (record[1], record[0]) not in AUTHORITY_PROOF_BINDINGS
            ):
                errors.append("AllowSoundness")
        if value != "ALLOW" and effect_permitted(state, rid):
            errors.append("FailClosed")

        if rid in records and rid in requests and records[rid][0] != requests[rid][0]:
            errors.append("ExactBinding")
        if rid in requests and (requests[rid][1], requests[rid][0]) not in LOCAL_AUTHORITY_BINDINGS:
            errors.append("LocalAuthorityRoot")
        if rid in records and (records[rid][1], records[rid][0]) not in AUTHORITY_PROOF_BINDINGS:
            errors.append("DelegatedAuthoritySound")
        if rid in state.observed_inputs and rid not in records and value != "UNKNOWN":
            errors.append("InputsNonAuthoritative")
        if rid in state.conflicts and value != "UNKNOWN":
            errors.append("TerminalUnique")
        if (
            (rid in state.conflicts or (rid in state.invalid_material and rid not in records))
            and value != "UNKNOWN"
        ):
            errors.append("InvalidOrConflictUnknown")

    for rid, (_, _, previous) in requests.items():
        if previous == NO_PREVIOUS:
            continue
        if previous == rid or previous not in requests or previous not in records:
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
    if action == "RejectOperation" and canonical_projection(before) != canonical_projection(after):
        errors.append("RejectedOperationPreservesStore")
    if not before.observed_inputs.issubset(after.observed_inputs):
        errors.append("ObservedInputsAppendOnly")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    queue = deque([(initial(), 0)])
    seen = {initial()}
    transitions = 0
    failures: list[dict[str, object]] = []
    terminal_states = 0

    while queue:
        state, depth = queue.popleft()
        errors = state_errors(state)
        if errors:
            failures.append({"state": repr(state), "errors": errors})
            continue
        terminal_states += sum(resolution_of(state, rid) in TERMINALS for rid in IDS)
        if depth >= args.depth:
            continue
        for action, successor in successors(state):
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

    report = {
        "document_type": "aset-seed-minimal-kernel-bounded-model-check",
        "depth": args.depth,
        "states": len(seen),
        "transitions": transitions,
        "terminal_states": terminal_states,
        "state_properties": list(STATE_PROPERTIES),
        "temporal_properties": list(TEMPORAL_PROPERTIES),
        "invariants": list(FORMAL_PROPERTIES),
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"MODEL_CHECK_STATES={report['states']}")
    print(f"MODEL_CHECK_TRANSITIONS={transitions}")
    print(f"MODEL_CHECK_TERMINAL_STATES={terminal_states}")
    print(f"MODEL_CHECK_FORMAL_PROPERTIES={len(FORMAL_PROPERTIES)}")
    print("MODEL_CHECK_VERDICT=" + report["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
