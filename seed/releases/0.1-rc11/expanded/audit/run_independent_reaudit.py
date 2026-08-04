from __future__ import annotations

import copy
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "machine" / "reference"))
import seed_reference as sut


def load_json(path: Path) -> Any:
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate key {key} in {path}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def normalize(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return value
    if isinstance(value, float):
        raise ValueError("float")
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", key): normalize(item) for key, item in value.items()}
    raise ValueError(type(value))


def independent_digest(domain: str, value: Any) -> str:
    payload = json.dumps(
        normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    framed = domain.encode("ascii") + b"\x00" + len(payload).to_bytes(8, "big") + payload
    return "sha256:" + hashlib.sha256(framed).hexdigest()


def independent_state_root(state: dict[str, Any]) -> str:
    material = copy.deepcopy(state)
    material.pop("current_state_root", None)
    return independent_digest("ASET/TrustSpaceState/v1", material)


checks: list[dict[str, Any]] = []


def check(check_id: str, title: str, condition: bool, detail: str = "") -> None:
    checks.append(
        {"id": check_id, "title": title, "pass": bool(condition), "detail": detail}
    )


# Load every schema independently and construct a separate registry.
schemas: dict[str, dict[str, Any]] = {}
resources = []
for path in sorted((ROOT / "machine" / "schemas").glob("*.json")):
    schema = load_json(path)
    schemas[path.name] = schema
    resources.append((schema["$id"], Resource.from_contents(schema)))
registry = Registry().with_resources(resources)
validators = {
    name: Draft202012Validator(schema, registry=registry)
    for name, schema in schemas.items()
}
check("SCHEMA-COUNT", "exact schema count", len(schemas) == 39, str(len(schemas)))
check(
    "SCHEMA-ID-UNIQUE",
    "schema identifiers are unique",
    len({schema["$id"] for schema in schemas.values()}) == len(schemas),
)
check(
    "SCHEMA-ID-VERSION",
    "all schema identifiers belong to rc11",
    all("/0.1-rc11/" in schema["$id"] for schema in schemas.values()),
)

transition_schema = schemas["transition.schema.json"]
schema_kinds = {
    variant["properties"]["kind"]["const"] for variant in transition_schema["oneOf"]
}
runtime_kinds = set(sut.HANDLERS) | {"RECONCILE"}
check("KIND-PARITY", "schema and runtime transition kinds match", schema_kinds == runtime_kinds)
check("KIND-NO-AMENDMENT", "removed amendment kind is absent", "AMENDMENT" not in schema_kinds)
check(
    "KIND-NO-CONSENT-STATE",
    "no destructive pending-consent transition exists",
    "REDEFINITION_CONSENT" not in schema_kinds,
)

# Execute all traces once. Prefix caching avoids replaying identical immutable setup traces.
case_paths: list[str] = []
for index_name in ("positive-index.json", "negative-index.json"):
    index = load_json(ROOT / "conformance" / index_name)
    case_paths.extend(index["cases"])
check("CORPUS-COUNT", "exact conformance case count", len(case_paths) == 55, str(len(case_paths)))
check("CORPUS-UNIQUE", "case paths are unique", len(case_paths) == len(set(case_paths)))

prefix_cache: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
positive_kinds: set[str] = set()
for rel in case_paths:
    case = load_json(ROOT / rel)
    cid = case["case_id"]
    schema_errors = list(validators["conformance-case.schema.json"].iter_errors(case))
    check(f"CASE-SCHEMA-{cid}", "case validates against normative schema", not schema_errors, "; ".join(err.message for err in schema_errors))

    genesis_key = independent_digest("ASET/AuditGenesisCache/v1", case["initial_genesis"])
    try:
        state = sut.initialize_state(copy.deepcopy(case["initial_genesis"]))
        check(f"INITIAL-ROOT-{cid}", "initial state root independently recomputes", state["current_state_root"] == independent_state_root(state))
    except sut.SeedError as exc:
        expected = case["expected"]
        correct = not expected["accepted"] and expected["code"] == exc.code
        check(f"TRACE-{cid}", "invalid Genesis yields expected rejection", correct, exc.code)
        continue

    setup_ok = True
    prefix: list[str] = []
    for transition in case.get("setup", []):
        prefix.append(transition["transition_id"])
        cache_key = (genesis_key, tuple(prefix))
        cached = prefix_cache.get(cache_key)
        if cached is not None:
            state = copy.deepcopy(cached)
            continue
        result = sut.apply_transition(state, copy.deepcopy(transition))
        if not result["accepted"] or not result["state_changed"]:
            setup_ok = False
            check(f"SETUP-{cid}", "setup trace is reachable", False, result["code"])
            break
        state = result["state"]
        prefix_cache[cache_key] = copy.deepcopy(state)
    if setup_ok:
        check(f"SETUP-{cid}", "setup trace is reachable", True)
        state_errors = list(validators["trust-space-state.schema.json"].iter_errors(state))
        check(f"STATE-SCHEMA-{cid}", "reachable setup state validates", not state_errors, "; ".join(err.message for err in state_errors))
        check(f"SETUP-ROOT-{cid}", "setup state root independently recomputes", state["current_state_root"] == independent_state_root(state))
        result = sut.apply_transition(state, copy.deepcopy(case["candidate"]))
        actual = {
            "accepted": result["accepted"],
            "code": result["code"],
            "state_changed": result["state_changed"],
        }
        check(f"TRACE-{cid}", "candidate result matches oracle", actual == case["expected"], f"{actual} != {case['expected']}")
        if case["expected"]["accepted"]:
            positive_kinds.add(case["candidate"]["kind"])
            check(f"FINAL-ROOT-{cid}", "accepted final state root independently recomputes", result["state"]["current_state_root"] == independent_state_root(result["state"]))

check("KIND-POSITIVE-COVERAGE", "each transition kind has a positive trace", positive_kinds == schema_kinds, str(sorted(schema_kinds - positive_kinds)))

# Independent mutation checks against whole-state invariants.
def expect_state_code(check_id: str, title: str, state: dict[str, Any], code: str) -> None:
    candidate = copy.deepcopy(state)
    candidate["current_state_root"] = sut.compute_state_root(candidate)
    try:
        sut.validate_state(candidate)
        observed = "ACCEPTED"
    except sut.SeedError as exc:
        observed = exc.code
    check(check_id, title, observed == code, observed)


def case_state(case_id: str, include_candidate: bool = False) -> dict[str, Any]:
    sub = "positive" if case_id.startswith("POS") else "negative"
    case = load_json(ROOT / "machine" / "examples" / sub / f"{case_id}.json")
    state = sut.initialize_state(copy.deepcopy(case["initial_genesis"]))
    for transition in case.get("setup", []):
        result = sut.apply_transition(state, copy.deepcopy(transition))
        if not result["accepted"] or not result["state_changed"]:
            raise AssertionError((case_id, result["code"]))
        state = result["state"]
    if include_candidate:
        result = sut.apply_transition(state, copy.deepcopy(case["candidate"]))
        if not result["accepted"] or not result["state_changed"]:
            raise AssertionError((case_id, result["code"]))
        state = result["state"]
    return state

state = case_state("POS-017", include_candidate=True)
redefinition_id = next(iter(state["context_redefinitions"]))
mutated = copy.deepcopy(state)
mutated["context_redefinitions"][redefinition_id]["proposal"]["proposal_nonce"] = "audit-tamper"
expect_state_code("MUT-REDEF-PROPOSAL", "redefinition record binds full proposal", mutated, "REDEFINITION_PROPOSAL_DIGEST_MISMATCH")

mutated = copy.deepcopy(state)
old, new = next(iter(mutated["context_redefinitions"][redefinition_id]["successor_map"].items()))
mutated["contexts"][new]["alias"] += "-tampered"
expect_state_code("MUT-REDEF-ALIAS", "successor alias continuity is invariant", mutated, "CONTEXT_ALIAS_INDEX_MISMATCH")

state = case_state("POS-023", include_candidate=True)
withdrawal_id = next(iter(state["membership_withdrawals"]))
mutated = copy.deepcopy(state)
mutated["membership_withdrawals"][withdrawal_id]["mode"] = "REDEFINITION"
expect_state_code("MUT-WITHDRAW-MODE", "withdrawal mode fields remain coherent", mutated, "WITHDRAWAL_MODE_BINDING_MISMATCH")

state = case_state("POS-009")
permit_id = next(iter(state["permits"]))
mutated = copy.deepcopy(state)
mutated["permits"][permit_id]["success_predicate_digest"] = independent_digest("X", {"unknown": 1})
expect_state_code("MUT-PERMIT-POLICY", "Permit success policy must be constitutional", mutated, "PERMIT_SUCCESS_PREDICATE_UNRECOGNIZED")

mutated = copy.deepcopy(state)
context_id = mutated["permits"][permit_id]["context_id"]
mutated["contexts"][context_id]["lifecycle"] = "WITHDRAWN"
mutated["context_aliases"].pop(mutated["contexts"][context_id]["alias"], None)
# Authority is detected before Permit; revoke it to reach the Permit-specific guard.
for authority in mutated["authorities"].values():
    if authority["context_id"] == context_id and authority["status"] == "ACTIVE":
        authority["status"] = "REVOKED"
expect_state_code("MUT-ACTIVE-PERMIT", "active Permit cannot exist in inactive Context", mutated, "ACTIVE_PERMIT_IN_INACTIVE_CONTEXT")

state = case_state("POS-023", include_candidate=True)
withdrawn = next(cid for cid, context in state["contexts"].items() if context["lifecycle"] == "WITHDRAWN")
active = state["contexts"][withdrawn]["parent_context_id"]
mutated = copy.deepcopy(state)
mutated["normative_dependencies"].append({"source_context_id": active, "target_context_id": withdrawn, "dependency_kind": "NORMATIVE"})
expect_state_code("MUT-INACTIVE-DEPENDENCY", "normative dependency endpoints must remain active", mutated, "NORMATIVE_DEPENDENCY_CONTEXT_INACTIVE")

# Canonical hash properties are checked without using runtime digest helpers.
check("HASH-NFC", "NFC-equivalent strings hash identically", independent_digest("X", {"v": "e\u0301"}) == independent_digest("X", {"v": "é"}))
check("HASH-DOMAIN", "domain separation changes digest", independent_digest("A", {"v": 1}) != independent_digest("B", {"v": 1}))
check("HASH-ORDER", "JSON object order does not change digest", independent_digest("X", {"a": 1, "b": 2}) == independent_digest("X", {"b": 2, "a": 1}))

failed = [item for item in checks if not item["pass"]]
summary = {
    "audit_id": "ASET-SEED-INDEPENDENT-REAUDIT-0.1-RC11",
    "version": sut.VERSION,
    "method": "separate schema registry, cached trace replay, independent canonical hashing, whole-state mutation analysis",
    "checks_total": len(checks),
    "checks_passed": len(checks) - len(failed),
    "verdict": "PASS_WITH_LIMITATIONS" if not failed else "REWORK_REQUIRED",
    "failed_checks": failed,
    "limitations": [
        "proof_digest is an abstract authenticated-verifier reference; concrete signature and credential verification are not implemented",
        "crash durability, transactional storage, multi-process serialization and production concurrency are not established",
        "distributed consensus is outside the minimal profile",
        "root Constitution is immutable inside one Genesis lineage; semantic change requires a new Genesis",
        "external third-party audit and production refinement remain pending",
        "physical-world truth remains the responsibility of federation procedures and concrete implementations",
    ],
    "checks": checks,
}
if "--no-write" not in sys.argv:
    (ROOT / "validation" / "independent_reaudit_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
print(json.dumps({key: summary[key] for key in ("checks_total", "checks_passed", "verdict")}, ensure_ascii=False, indent=2))
raise SystemExit(0 if not failed else 1)
