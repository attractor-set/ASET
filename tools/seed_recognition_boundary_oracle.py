#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class State:
    phase: str
    binding: str | None = None
    previous: str | None = None
    authority: str | None = None


ABSENT = State("ABSENT")
EXPECTED_DEPTH = {
    "ABSENT": 0,
    "PENDING": 1,
    "ALLOW": 2,
    "BLOCK": 2,
    "INVALIDATED_ALLOW": 3,
    "INVALIDATED_BLOCK": 3,
}


def powerset(items):
    items = tuple(items)
    for mask in range(1 << len(items)):
        yield frozenset(
            items[i] for i in range(len(items)) if mask & (1 << i)
        )


def recognized_bindings(rab):
    return frozenset(binding for _, binding in rab)


def successors(state, authorities, previous_values, rab):
    out: set[State] = set()
    if state.phase == "ABSENT":
        for _, binding in rab:
            for previous in previous_values:
                out.add(State("PENDING", binding, previous, None))
    elif state.phase == "PENDING":
        for authority in authorities:
            if (authority, state.binding) in rab:
                out.add(State("ALLOW", state.binding, state.previous, authority))
                out.add(State("BLOCK", state.binding, state.previous, authority))
    elif state.phase == "ALLOW":
        out.add(
            State(
                "INVALIDATED_ALLOW",
                state.binding,
                state.previous,
                state.authority,
            )
        )
    elif state.phase == "BLOCK":
        out.add(
            State(
                "INVALIDATED_BLOCK",
                state.binding,
                state.previous,
                state.authority,
            )
        )
    return frozenset(out)


def exact_normal_form(previous_values, rab):
    states = {ABSENT}
    for binding in recognized_bindings(rab):
        for previous in previous_values:
            states.add(State("PENDING", binding, previous, None))
    for authority, binding in rab:
        for previous in previous_values:
            for phase in (
                "ALLOW",
                "BLOCK",
                "INVALIDATED_ALLOW",
                "INVALIDATED_BLOCK",
            ):
                states.add(State(phase, binding, previous, authority))
    return frozenset(states)


def shortest_depths(authorities, previous_values, rab):
    depth = {ABSENT: 0}
    queue = deque([ABSENT])
    while queue:
        source = queue.popleft()
        for target in successors(source, authorities, previous_values, rab):
            if target not in depth:
                depth[target] = depth[source] + 1
                queue.append(target)
    return depth


def exact_count(previous_values, rab) -> int:
    return (
        1
        + len(recognized_bindings(rab)) * len(previous_values)
        + 4 * len(rab) * len(previous_values)
    )


def min_fixed_width_bits(count: int) -> int:
    if count < 1:
        raise ValueError("count must be positive")
    width = 0
    capacity = 1
    while capacity < count:
        capacity *= 2
        width += 1
    return width


def check_profile(authorities, previous_values, rab) -> tuple[int, int]:
    exact = exact_normal_form(previous_values, rab)
    depths = shortest_depths(authorities, previous_values, rab)
    reachable = frozenset(depths)
    if exact != reachable:
        raise AssertionError(("reachable/exact mismatch", exact - reachable, reachable - exact))
    if len(exact) != exact_count(previous_values, rab):
        raise AssertionError("parametric cardinality mismatch")
    for state, depth in depths.items():
        if depth != EXPECTED_DEPTH[state.phase]:
            raise AssertionError(("unexpected phase depth", state, depth))
        if state.phase.startswith("INVALIDATED_") and successors(
            state, authorities, previous_values, rab
        ):
            raise AssertionError(("invalidated state has successor", state))
    return len(exact), max(depths.values(), default=0)


def run_exhaustive_audit() -> dict[str, int | bool | str]:
    profiles = 0
    max_states = 0
    max_depth = 0
    max_bits = 0

    for binding_count in range(1, 4):
        bindings = tuple(f"B{i}" for i in range(binding_count))
        for authority_count in range(1, 4):
            authorities = tuple(f"A{i}" for i in range(authority_count))
            pairs = tuple(
                (authority, binding)
                for authority in authorities
                for binding in bindings
            )
            for rab in powerset(pairs):
                for previous_count in range(1, 4):
                    previous_values = tuple(f"P{i}" for i in range(previous_count))
                    count, depth = check_profile(authorities, previous_values, rab)
                    bits = min_fixed_width_bits(count)
                    if (1 << bits) < count:
                        raise AssertionError("fixed-width capacity lower bound violated")
                    if bits > 0 and (1 << (bits - 1)) >= count:
                        raise AssertionError("fixed-width lower bound is not minimal")
                    profiles += 1
                    max_states = max(max_states, count)
                    max_depth = max(max_depth, depth)
                    max_bits = max(max_bits, bits)

    rich_rab = frozenset(
        {
            ("A0", "B0"),
            ("A1", "B0"),
            ("A0", "B1"),
        }
    )
    rich_previous = ("P0", "P1")
    rich_count, rich_depth = check_profile(("A0", "A1"), rich_previous, rich_rab)
    rich_bits = min_fixed_width_bits(rich_count)
    if (rich_count, rich_depth, rich_bits) != (29, 3, 5):
        raise AssertionError("rich witness drift")

    return {
        "profiles_checked": profiles,
        "max_reachable_local_states": max_states,
        "max_shortest_reachability_depth": max_depth,
        "max_min_fixed_width_bits": max_bits,
        "rich_exact_states": rich_count,
        "rich_max_depth": rich_depth,
        "rich_min_fixed_width_bits": rich_bits,
        "formula": "1+|B_rec|*|P|+4*|RAB|*|P|",
        "exact_equals_reachable": True,
        "invalidated_has_outgoing_local_step": False,
        "shannon_entropy_claim": False,
        "global_seed_state_bit_claim": False,
    }


def main() -> int:
    report = run_exhaustive_audit()
    print("SEED_RECOGNITION_BOUNDARY_ORACLE=START")
    print(f"EXHAUSTIVE_CANONICAL_PROFILES_CHECKED={report['profiles_checked']}")
    print(f"MAX_REACHABLE_LOCAL_STATES={report['max_reachable_local_states']}")
    print(
        "MAX_SHORTEST_REACHABILITY_DEPTH="
        f"{report['max_shortest_reachability_depth']}"
    )
    print(f"MAX_MIN_FIXED_WIDTH_BITS={report['max_min_fixed_width_bits']}")
    print(f"FORMULA={report['formula']}")
    print("EXACT_NORMAL_FORM_EQUALS_REACHABLE_LOCAL_STATES=TRUE")
    print(f"RICH_EXACT_STATES={report['rich_exact_states']}")
    print(f"RICH_MAX_DEPTH={report['rich_max_depth']}")
    print(f"RICH_MIN_FIXED_WIDTH_BITS={report['rich_min_fixed_width_bits']}")
    print("SHANNON_ENTROPY_CLAIM=FALSE")
    print("GLOBAL_SEED_STATE_BIT_CLAIM=FALSE")
    print("SEED_RECOGNITION_BOUNDARY_ORACLE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
