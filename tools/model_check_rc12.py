from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class State:
    lifecycle: tuple[str, str]
    authority: tuple[bool, bool]
    permit_active: tuple[bool, bool]
    attempts: tuple[int, int]
    verified: tuple[bool, bool]
    outcome: tuple[bool, bool]
    audit_length: int


def initial() -> State:
    return State(
        lifecycle=("ACTIVE", "ACTIVE"),
        authority=(False, False),
        permit_active=(False, False),
        attempts=(0, 0),
        verified=(False, False),
        outcome=(False, False),
        audit_length=0,
    )


def replace_tuple(values: tuple, index: int, value):
    result = list(values)
    result[index] = value
    return tuple(result)


def successors(state: State):
    for context in range(2):
        if state.lifecycle[context] == "ACTIVE" and not state.authority[context]:
            yield "GrantAuthority", State(
                state.lifecycle,
                replace_tuple(state.authority, context, True),
                state.permit_active,
                state.attempts,
                state.verified,
                state.outcome,
                state.audit_length + 1,
            )
        if state.lifecycle[context] == "ACTIVE":
            yield "Withdraw", State(
                replace_tuple(state.lifecycle, context, "WITHDRAWN"),
                replace_tuple(state.authority, context, False),
                state.permit_active,
                state.attempts,
                state.verified,
                state.outcome,
                state.audit_length + 1,
            )
    for permit in range(2):
        if not state.permit_active[permit] and not state.outcome[permit]:
            yield "IssuePermit", State(
                state.lifecycle,
                state.authority,
                replace_tuple(state.permit_active, permit, True),
                state.attempts,
                state.verified,
                state.outcome,
                state.audit_length + 1,
            )
        if state.permit_active[permit] and state.attempts[permit] < 1:
            yield "UsePermit", State(
                state.lifecycle,
                state.authority,
                state.permit_active,
                replace_tuple(state.attempts, permit, state.attempts[permit] + 1),
                state.verified,
                state.outcome,
                state.audit_length + 1,
            )
        if state.attempts[permit] > 0 and not state.verified[permit]:
            yield "Verify", State(
                state.lifecycle,
                state.authority,
                state.permit_active,
                state.attempts,
                replace_tuple(state.verified, permit, True),
                state.outcome,
                state.audit_length + 1,
            )
        if state.verified[permit] and not state.outcome[permit]:
            yield "RecognizeOutcome", State(
                state.lifecycle,
                state.authority,
                replace_tuple(state.permit_active, permit, False),
                state.attempts,
                state.verified,
                replace_tuple(state.outcome, permit, True),
                state.audit_length + 1,
            )


def invariant_errors(state: State) -> list[str]:
    errors = []
    if any(attempt > 1 for attempt in state.attempts):
        errors.append("AttemptBound")
    if any(state.outcome[i] and not state.verified[i] for i in range(2)):
        errors.append("OutcomeVerified")
    if any(state.lifecycle[i] != "ACTIVE" and state.authority[i] for i in range(2)):
        errors.append("InactiveNoAuthority")
    if state.audit_length < 0:
        errors.append("AuditMonotone")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    queue = deque([(initial(), 0)])
    visited = {initial()}
    transitions = 0
    failures = []
    while queue:
        state, depth = queue.popleft()
        errors = invariant_errors(state)
        if errors:
            failures.append({"state": repr(state), "errors": errors})
            continue
        if depth >= args.depth:
            continue
        for _action, candidate in successors(state):
            transitions += 1
            if candidate not in visited:
                visited.add(candidate)
                queue.append((candidate, depth + 1))
    report = {
        "document_type": "aset-seed-rc12-bounded-model-check",
        "depth": args.depth,
        "states": len(visited),
        "transitions": transitions,
        "invariants": ["AttemptBound", "OutcomeVerified", "InactiveNoAuthority", "AuditMonotone"],
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"MODEL_CHECK_STATES={report['states']}")
    print(f"MODEL_CHECK_TRANSITIONS={report['transitions']}")
    print(f"MODEL_CHECK_VERDICT={report['verdict']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
