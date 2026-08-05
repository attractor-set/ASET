from __future__ import annotations

import argparse
import json
from collections import deque
from collections.abc import Callable, Iterable

from component_common import ASET_ROOT, ROOT, canonical_digest, load, schema_errors

FORMAL_ROOT = ASET_ROOT / "shared/formal"
PROFILE = FORMAL_ROOT / "formal-profile.json"
RESULTS = FORMAL_ROOT / "results.json"
PROFILE_SCHEMA = ASET_ROOT / "shared/schemas/component-formal-profile.schema.json"
RESULTS_SCHEMA = ASET_ROOT / "shared/schemas/component-formal-results.schema.json"

State = tuple[bool | int, ...]
Successors = Callable[[State], Iterable[tuple[str, State]]]
Invariant = Callable[[State], list[str]]


def explore(initial: State, successors: Successors, invariant: Invariant) -> dict[str, object]:
    queue = deque([initial])
    visited = {initial}
    transitions = 0
    failures: list[dict[str, object]] = []
    while queue:
        state = queue.popleft()
        errors = invariant(state)
        if errors:
            failures.append({"state": list(state), "errors": errors})
            continue
        for _action, candidate in successors(state):
            transitions += 1
            if candidate not in visited:
                visited.add(candidate)
                queue.append(candidate)
    return {
        "states": len(visited),
        "transitions": transitions,
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }


def context_model() -> dict[str, object]:
    initial: State = (0, 0, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        source, head, permit, consumed, patched = state
        if source == head and not permit:
            yield "IssuePermit", (source, head, True, consumed, patched)
        if not patched and head < 2:
            yield "ConcurrentAdvance", (source, int(head) + 1, permit, consumed, patched)
        if permit and not consumed and source == head:
            yield "Cross", (source, int(head) + 1, False, True, True)

    def invariant(state: State) -> list[str]:
        _source, _head, _permit, consumed, patched = state
        errors: list[str] = []
        if patched and not consumed:
            errors.append("PatchRequiresExactSource")
        if consumed and not patched:
            errors.append("OneCrossing")
        return errors

    return explore(initial, successors, invariant)


def core_model() -> dict[str, object]:
    initial: State = (False, False, False, 0)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        decision, permit, consumed, crossings = state
        if not decision:
            yield "Resolve", (True, permit, consumed, crossings)
        if decision and not permit and not consumed:
            yield "Issue", (decision, True, consumed, crossings)
        if permit and not consumed:
            yield "Cross", (decision, False, True, int(crossings) + 1)

    def invariant(state: State) -> list[str]:
        decision, permit, _consumed, crossings = state
        errors: list[str] = []
        if permit and not decision:
            errors.append("DecisionBeforePermit")
        if int(crossings) > 1:
            errors.append("PermitAtMostOnce")
        return errors

    return explore(initial, successors, invariant)


def gateway_model() -> dict[str, object]:
    initial: State = (0, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        context_version, rendered, tool_effect = state
        if not rendered:
            yield "Render", (context_version, True, tool_effect)

    def invariant(state: State) -> list[str]:
        context_version, _rendered, tool_effect = state
        errors: list[str] = []
        if context_version != 0:
            errors.append("ContextUnchanged")
        if tool_effect:
            errors.append("NoToolEffect")
        return errors

    return explore(initial, successors, invariant)


def master_model() -> dict[str, object]:
    initial: State = (False, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        proposal, authority, permit, outcome = state
        if not proposal:
            yield "Plan", (True, authority, permit, outcome)

    def invariant(state: State) -> list[str]:
        proposal, authority, permit, outcome = state
        errors: list[str] = []
        if proposal and authority:
            errors.append("AdvisoryOnly")
        if permit or outcome:
            errors.append("NoSelfAuthorization")
        return errors

    return explore(initial, successors, invariant)


def memory_model() -> dict[str, object]:
    initial: State = (False, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        retrieved, verified, permit, mutated = state
        if not retrieved:
            yield "Retrieve", (True, verified, permit, mutated)
        if not permit:
            yield "AuthorizeMutation", (retrieved, verified, True, mutated)
        if permit and not mutated:
            yield "Mutate", (retrieved, verified, permit, True)

    def invariant(state: State) -> list[str]:
        retrieved, verified, permit, mutated = state
        errors: list[str] = []
        if retrieved and verified:
            errors.append("RetrievalNotVerification")
        if mutated and not permit:
            errors.append("MutationAuthorized")
        return errors

    return explore(initial, successors, invariant)


def monade_model() -> dict[str, object]:
    initial: State = (False, False, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        bound, intent, observed, verified, outcome = state
        if not bound:
            yield "Bind", (True, intent, observed, verified, outcome)
        if bound and not intent:
            yield "Dispatch", (bound, True, observed, verified, outcome)
        if intent and not observed:
            yield "Observe", (bound, intent, True, verified, outcome)
        if observed and not verified:
            yield "Verify", (bound, intent, observed, True, outcome)
        if verified and not outcome:
            yield "Accept", (bound, intent, observed, verified, True)

    def invariant(state: State) -> list[str]:
        _bound, intent, observed, verified, outcome = state
        errors: list[str] = []
        if observed and not intent:
            errors.append("IntentBeforeObservation")
        if outcome and not verified:
            errors.append("OutcomeVerified")
        return errors

    return explore(initial, successors, invariant)


def protocol_model() -> dict[str, object]:
    initial: State = (False, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        schema_valid, canonical, admitted, authority = state
        if not schema_valid:
            yield "Validate", (True, canonical, admitted, authority)
        if schema_valid and not canonical:
            yield "Canonicalize", (schema_valid, True, admitted, authority)
        if canonical and not admitted:
            yield "Admit", (schema_valid, canonical, True, authority)

    def invariant(state: State) -> list[str]:
        schema_valid, canonical, admitted, authority = state
        errors: list[str] = []
        if admitted and not (schema_valid and canonical):
            errors.append("SchemaBeforeAdmission")
        if authority:
            errors.append("NoBusinessAuthority")
        return errors

    return explore(initial, successors, invariant)


def system_model() -> dict[str, object]:
    initial: State = (False, False, False, False, False, False)

    def successors(state: State) -> Iterable[tuple[str, State]]:
        expectation, execution, intent, observed, verified, outcome = state
        if not expectation:
            yield "AuthorizeExpectation", (True, execution, intent, observed, verified, outcome)
        if expectation and not execution:
            yield "AuthorizeExecution", (expectation, True, intent, observed, verified, outcome)
        if execution and not intent:
            yield "Dispatch", (expectation, execution, True, observed, verified, outcome)
        if intent and not observed:
            yield "Observe", (expectation, execution, intent, True, verified, outcome)
        if observed and not verified:
            yield "Verify", (expectation, execution, intent, observed, True, outcome)
        if verified and not outcome:
            yield "Recognize", (expectation, execution, intent, observed, verified, True)

    def invariant(state: State) -> list[str]:
        expectation, execution, _intent, _observed, verified, outcome = state
        errors: list[str] = []
        if execution and not expectation:
            errors.append("SeparatePermits")
        if outcome and not verified:
            errors.append("OutcomeRequiresVerification")
        return errors

    return explore(initial, successors, invariant)


MODELS: dict[str, Callable[[], dict[str, object]]] = {
    "context": context_model,
    "core": core_model,
    "gateway": gateway_model,
    "master": master_model,
    "memory": memory_model,
    "monade": monade_model,
    "protocol": protocol_model,
    "system-composition": system_model,
}


def canonical_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build_results() -> dict[str, object]:
    profile = load(PROFILE)
    model_results: list[dict[str, object]] = []
    for model in profile["models"]:
        key = str(model["id"])
        tla_path = ROOT / str(model["tla_path"])
        cfg_path = ROOT / str(model["cfg_path"])
        structural_errors: list[str] = []
        if key not in MODELS:
            structural_errors.append("bounded implementation missing")
        if not tla_path.is_file() or not cfg_path.is_file():
            structural_errors.append("formal projection missing")
        else:
            tla = tla_path.read_text(encoding="utf-8")
            cfg = cfg_path.read_text(encoding="utf-8")
            for invariant in model["invariants"]:
                if str(invariant) not in tla or str(invariant) not in cfg:
                    structural_errors.append(f"invariant marker missing:{invariant}")
        bounded = (
            MODELS[key]()
            if key in MODELS
            else {"states": 0, "transitions": 0, "failures": [], "verdict": "FAIL"}
        )
        failures = [*structural_errors, *[str(item) for item in bounded["failures"]]]
        model_results.append(
            {
                "id": key,
                "states": bounded["states"],
                "transitions": bounded["transitions"],
                "invariants": model["invariants"],
                "failures": failures,
                "verdict": "PASS" if not failures and bounded["verdict"] == "PASS" else "FAIL",
            }
        )
    failed = [item for item in model_results if item["verdict"] == "FAIL"]
    return {
        "document_type": "aset-component-bounded-model-check-results",
        "schema_version": 1,
        "profile": "0.1-rc1",
        "method": "BOUNDED_EXHAUSTIVE_PYTHON_PROJECTION",
        "models_total": len(model_results),
        "models_passed": len(model_results) - len(failed),
        "models_failed": len(failed),
        "verdict": "PASS" if not failed else "FAIL",
        "models": model_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(RESULTS.relative_to(ROOT)))
    args = parser.parse_args()
    profile = load(PROFILE)
    profile_errors = schema_errors(load(PROFILE_SCHEMA), profile)
    if profile.get("canonical_digest") != canonical_digest(profile):
        profile_errors.append("canonical digest mismatch")
    if profile_errors:
        for error in profile_errors:
            print(f"COMPONENT_FORMAL_PROFILE_ERROR={error}")
        return 1
    result = build_results()
    result_errors = schema_errors(load(RESULTS_SCHEMA), result)
    if result_errors:
        for error in result_errors:
            print(f"COMPONENT_FORMAL_RESULT_ERROR={error}")
        return 1
    output = ROOT / args.output
    text = canonical_text(result)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != text:
            print("COMPONENT_FORMAL_RESULTS=DIFFERENT")
            return 1
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8", newline="\n")
    print(f"COMPONENT_MODEL_CHECK={result['models_passed']}/{result['models_total']}")
    print(f"COMPONENT_MODEL_CHECK_VERDICT={result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
