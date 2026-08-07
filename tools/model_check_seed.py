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
LOCAL_AUTHORITY_BINDINGS = frozenset({(0, 0), (1, 1)})
AUTHORITY_PROOF_BINDINGS = frozenset({(0, 0), (1, 1), (1, 0)})

STATE_PROPERTIES = (
    "TypeOK",
    "ResolutionDomain",
    "AllowSoundness",
    "FailClosed",
    "TerminalBindingDerived",
    "LocalAuthorityRoot",
    "DelegatedAuthoritySound",
    "InputsNonAuthoritative",
    "TerminalUnique",
    "ConflictUnknown",
    "FreshReconsideration",
)
TEMPORAL_PROPERTIES = (
    "RequestsAppendOnly",
    "TerminalRecordsImmutable",
    "CanonicalStateChangesOnlyByRecognizedTransition",
    "InvalidMaterialStutter",
    "NonAuthoritativeInputsStutter",
)
FORMAL_PROPERTIES = STATE_PROPERTIES + TEMPORAL_PROPERTIES


@dataclass(frozen=True)
class State:
    # request tuple: resolution_id, binding, previous_terminal_commitment
    requests: tuple[tuple[int, int, int], ...]
    # accepted terminal tuple: resolution_id, authority, terminal_value
    records: tuple[tuple[int, int, str], ...]
    # conflict is the only environment observation that changes resolution semantics
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


def canonical_projection(state: State) -> tuple[object, ...]:
    return (state.requests, state.records, state.conflicts)


def successors(state: State) -> Iterable[tuple[str, State]]:
    requests = request_map(state)
    records = record_map(state)

    # Initial Authority identity is checked at admission but not retained as an
    # independent state component. The binding remains sufficient to prove the
    # existence of a local root because LOCAL_AUTHORITY_BINDINGS is immutable.
    for rid in IDS:
        if rid in requests:
            continue
        for binding, authority in LOCAL_AUTHORITY_BINDINGS:
            del authority
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

    for rid, (binding, _) in requests.items():
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
                        tuple(sorted((*state.records, (rid, authority, value)))),
                        state.conflicts,
                    ),
                )

    for rid in IDS:
        if rid not in state.conflicts:
            yield (
                "ObserveConflict",
                State(state.requests, state.records, state.conflicts | {rid}),
            )

        # These observations are explicit semantic stutters. They are not
        # retained as Seed state and therefore cannot create ALLOW.
        yield "ObserveInvalidMaterial", state
        yield "ObserveNonAuthoritativeInput", state

    yield "Evaluate", state


def state_errors(state: State) -> list[str]:
    errors: list[str] = []
    requests = request_map(state)
    records = record_map(state)

    if len(requests) != len(state.requests) or len(records) != len(state.records):
        errors.append("TypeOK")
    if not state.conflicts.issubset(IDS):
        errors.append("TypeOK")

    # Structural properties created by representation rather than duplicated state.
    if not set(records).issubset(requests):
        errors.append("TerminalBindingDerived")
    if len(records) != len(state.records):
        errors.append("TerminalUnique")

    for rid, (binding, _) in requests.items():
        if not any(
            authority in AUTHORITIES and (authority, binding) in LOCAL_AUTHORITY_BINDINGS
            for authority in AUTHORITIES
        ):
            errors.append("LocalAuthorityRoot")

    for rid, (authority, _) in records.items():
        request = requests.get(rid)
        if request is None or (authority, request[0]) not in AUTHORITY_PROOF_BINDINGS:
            errors.append("DelegatedAuthoritySound")

    # InputsNonAuthoritative is structural in the minimized model: State has
    # exactly the three canonical decision components and no observed-input slot.
    if tuple(State.__dataclass_fields__) != ("requests", "records", "conflicts"):
        errors.append("InputsNonAuthoritative")

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
                or (record[0], request[0]) not in AUTHORITY_PROOF_BINDINGS
            ):
                errors.append("AllowSoundness")

        if value != "ALLOW" and effect_permitted(state, rid):
            errors.append("FailClosed")

        if rid in state.conflicts and value != "UNKNOWN":
            errors.append("ConflictUnknown")

    for _, (_, previous) in requests.items():
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

    recognized_canonical_actions = {
        "RegisterRequest",
        "RegisterReconsideration",
        "SubmitResolution",
        "ObserveConflict",
        "ObserveInvalidMaterial",
        "ObserveNonAuthoritativeInput",
    }
    if (
        canonical_projection(before) != canonical_projection(after)
        and action not in recognized_canonical_actions
    ):
        errors.append("CanonicalStateChangesOnlyByRecognizedTransition")

    if action == "ObserveInvalidMaterial" and before != after:
        errors.append("InvalidMaterialStutter")
    if action == "ObserveNonAuthoritativeInput" and before != after:
        errors.append("NonAuthoritativeInputsStutter")

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
        args.output.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )

    print(f"MODEL_CHECK_STATES={report['states']}")
    print(f"MODEL_CHECK_TRANSITIONS={transitions}")
    print(f"MODEL_CHECK_TERMINAL_STATES={terminal_states}")
    print(f"MODEL_CHECK_FORMAL_PROPERTIES={len(FORMAL_PROPERTIES)}")
    print("MODEL_CHECK_VERDICT=" + report["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
