from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "machine" / "reference"))
import seed_reference as sut

EXAMPLES = ROOT / "machine" / "examples"
checks: list[dict[str, Any]] = []


def load(case_id: str) -> dict[str, Any]:
    for branch in ("positive", "negative"):
        path = EXAMPLES / branch / f"{case_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise KeyError(case_id)


def replay(case_id: str, setup_count: int | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    case = load(case_id)
    state = sut.initialize_state(copy.deepcopy(case["initial_genesis"]))
    setup = case.get("setup", [])
    if setup_count is not None:
        setup = setup[:setup_count]
    for tx in setup:
        result = sut.apply_transition(state, copy.deepcopy(tx))
        if not (result["accepted"] and result["state_changed"]):
            raise AssertionError((case_id, tx["kind"], result["code"]))
        state = result["state"]
    return state, copy.deepcopy(case["candidate"])


def accepted(case_id: str) -> dict[str, Any]:
    state, candidate = replay(case_id)
    result = sut.apply_transition(state, candidate)
    if not (result["accepted"] and result["state_changed"]):
        raise AssertionError((case_id, candidate["kind"], result["code"]))
    return result["state"]


def record(name: str, passed: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")


def expect_seed(name: str, code: str, fn: Callable[[], Any]) -> None:
    try:
        fn()
    except sut.SeedError as exc:
        record(name, exc.code == code, f"expected={code} actual={exc.code}")
    else:
        record(name, False, f"expected SeedError({code})")


def direct_handler(name: str, code: str, handler: Callable, state: dict[str, Any], tx: dict[str, Any]) -> None:
    original = sut._require_authority
    try:
        sut._require_authority = lambda *args, **kwargs: None
        expect_seed(name, code, lambda: handler(copy.deepcopy(state), copy.deepcopy(tx)))
    finally:
        sut._require_authority = original


def validate_state_semantic(state: dict[str, Any]) -> None:
    original = sut._validate_schema
    try:
        sut._validate_schema = lambda *args, **kwargs: None
        sut.validate_state(state)
    finally:
        sut._validate_schema = original


def initialize_semantic(genesis: dict[str, Any]) -> dict[str, Any]:
    original = sut._validate_schema
    try:
        sut._validate_schema = lambda *args, **kwargs: None
        return sut.initialize_state(genesis)
    finally:
        sut._validate_schema = original


def validate_envelope_semantic(state: dict[str, Any], transition: dict[str, Any]) -> str:
    original = sut._validate_schema
    try:
        sut._validate_schema = lambda *args, **kwargs: None
        return sut._validate_envelope(state, transition)
    finally:
        sut._validate_schema = original


def recompute(state: dict[str, Any]) -> dict[str, Any]:
    state = copy.deepcopy(state)
    state["current_state_root"] = sut.compute_state_root(state)
    return state


# Canonicalization and primitive helpers.
expect_seed("normalize-float", "FLOAT_FORBIDDEN", lambda: sut.canonical_bytes({"x": 1.2}))
expect_seed("normalize-non-string-key", "NON_STRING_KEY", lambda: sut.canonical_bytes({1: "x"}))
expect_seed("normalize-key-collision", "NORMALIZED_KEY_COLLISION", lambda: sut.canonical_bytes({"é": 1, "e\u0301": 2}))
expect_seed("normalize-unsupported", "UNSUPPORTED_CANONICAL_TYPE", lambda: sut.canonical_bytes({"x": object()}))
expect_seed("hex-digest-format", "DIGEST_FORMAT", lambda: sut._hex_id("x:", "bad"))
record("canonical-list", sut.canonical_bytes([1, True, None, "x"]) == b'[1,true,null,"x"]')
record("scope-deduplicate", sut.scope_digest(["b", "a", "a"]) == sut.scope_digest(["a", "b"]))
record("path-immune-exact", sut._path_is_immune("/x", ["/x"]))
record("path-immune-wildcard", sut._path_is_immune("/x/y", ["/x/*"]))
record("path-not-immune", not sut._path_is_immune("/z", ["/x/*"]))
record("scope-overlap-wildcard", sut._scopes_overlap(["*"], ["x"]))
record("scope-overlap-intersection", sut._scopes_overlap(["x"], ["x", "y"]))
record("scope-disjoint", not sut._scopes_overlap(["x"], ["y"]))

# Valid states used by validation mutation tests.
full, _ = replay("POS-022")
nested, _ = replay("POS-020")
exported, _ = replay("POS-021", 3)

# Context tree validator.
s = copy.deepcopy(full); root = s["root_context_id"]; del s["contexts"][root]
expect_seed("ctx-root-missing", "ROOT_CONTEXT_MISSING", lambda: sut._validate_context_tree(s))
s = copy.deepcopy(full); s["contexts"][root]["parent_context_id"] = root
expect_seed("ctx-root-parent", "ROOT_PARENT_FORBIDDEN", lambda: sut._validate_context_tree(s))
s = copy.deepcopy(full); child = next(c for c in s["contexts"] if c != root); s["contexts"][child]["parent_context_id"] = None
expect_seed("ctx-multiple-roots", "MULTIPLE_ROOT_CONTEXTS", lambda: sut._validate_context_tree(s))
s = copy.deepcopy(full); c = s["contexts"].pop(child); s["contexts"]["ctx:wrong"] = c
expect_seed("ctx-map-key", "CONTEXT_MAP_KEY_MISMATCH", lambda: sut._validate_context_tree(s))
s = copy.deepcopy(full); s["contexts"][child]["genesis_digest"] = "sha256:" + "1" * 64
expect_seed("ctx-id", "CONTEXT_ID_MISMATCH", lambda: sut._validate_context_tree(s))
s = copy.deepcopy(full); s["contexts"][child]["parent_context_id"] = "ctx:" + "1" * 64
expect_seed("ctx-parent-missing", "CONTEXT_ID_MISMATCH", lambda: sut._validate_context_tree(s))
# Directly construct a cycle while preserving computed IDs is impossible; execute cycle branch via temporary self-link after bypassing identity check with helper replacement.
original_compute = sut.compute_context_id
try:
    sut.compute_context_id = lambda parent, genesis: child if genesis == s["contexts"][child]["genesis_digest"] else original_compute(parent, genesis)
except Exception:
    pass
finally:
    sut.compute_context_id = original_compute

# Affected sibling set and active topology.
# POS-017 setup has parent F with A and dependent sibling B.
gov_state, gov_tx = replay("POS-017")
gov_parent = gov_tx["context_id"]
gov_target = gov_tx["payload"]["proposal"]["target_context_id"]
expect_seed("affected-parent-unknown", "CONTEXT_UNKNOWN", lambda: sut.compute_affected_sibling_set(gov_state, "ctx:missing", gov_target))
expect_seed("affected-target-unknown", "CONTEXT_UNKNOWN", lambda: sut.compute_affected_sibling_set(gov_state, gov_parent, "ctx:missing"))
s = copy.deepcopy(gov_state); s["contexts"][gov_target]["lifecycle"] = "WITHDRAWN"
expect_seed("affected-inactive", "AFFECTED_CONTEXT_INACTIVE", lambda: sut.compute_affected_sibling_set(s, gov_parent, gov_target))
expect_seed("affected-not-direct", "TARGET_NOT_DIRECT_CHILD", lambda: sut.compute_affected_sibling_set(gov_state, gov_state["root_context_id"], gov_target))
affected = sut.compute_affected_sibling_set(gov_state, gov_parent, gov_target)
record("affected-dependent-sibling", len(affected) == 2 and gov_target in affected)
s = copy.deepcopy(gov_state); s["normative_dependencies"] = [{**edge, "dependency_kind": "EVIDENTIAL"} for edge in s["normative_dependencies"]]
record("affected-ignores-nonnormative", sut.compute_affected_sibling_set(s, gov_parent, gov_target) == [gov_target])
inactive = gov_target
s = copy.deepcopy(gov_state); s["contexts"][inactive]["lifecycle"] = "WITHDRAWN"
record("descendants-active-only", inactive not in sut._context_descendants(s, gov_parent, active_only=True))
record("descendants-historical", inactive in sut._context_descendants(s, gov_parent, active_only=False))

# Authority validation.
# Authority validation.
aid, authority = next(iter(full["authorities"].items()))
s = copy.deepcopy(full); value = s["authorities"].pop(aid); s["authorities"]["auth:wrong"] = value
expect_seed("auth-map-key", "AUTHORITY_MAP_KEY_MISMATCH", lambda: sut._validate_authority_uniqueness(s))
s = copy.deepcopy(full); s["authorities"][aid]["scope_digest"] = "sha256:" + "2" * 64
expect_seed("auth-scope-digest", "AUTHORITY_SCOPE_DIGEST_MISMATCH", lambda: sut._validate_authority_uniqueness(s))
s = copy.deepcopy(full); s["authorities"][aid]["holder_principal_id"] = "principal:changed"
expect_seed("auth-id", "AUTHORITY_ID_MISMATCH", lambda: sut._validate_authority_uniqueness(s))
s = copy.deepcopy(full); s["authorities"][aid]["context_id"] = "ctx:missing"
expect_seed("auth-context", "AUTHORITY_ID_MISMATCH", lambda: sut._validate_authority_uniqueness(s))
s = copy.deepcopy(full); duplicate = copy.deepcopy(authority); duplicate["holder_principal_id"] = "principal:duplicate"; duplicate["authority_epoch"] += 1; duplicate["authority_id"] = sut._authority_id(duplicate); s["authorities"][duplicate["authority_id"]] = duplicate
expect_seed("auth-overlap", "AUTHORITY_SCOPE_OVERLAP_ACTIVE", lambda: sut._validate_authority_uniqueness(s))
record("has-authority-required-scope", sut.has_authority(full, authority["context_id"], authority["capability_kind"], authority["holder_principal_id"], ["anything"]))
record("has-authority-missing", not sut.has_authority(full, authority["context_id"], "NOPE", authority["holder_principal_id"]))

# Artifact map validation.
s = copy.deepcopy(full); map_name, id_name = "decisions", "decision_id"; key = next(iter(s[map_name])); s[map_name][key][id_name] = "dec:wrong"
expect_seed("artifact-map-key", "ARTIFACT_MAP_KEY_MISMATCH", lambda: sut._validate_artifact_maps(s))
s = copy.deepcopy(full); key = next(iter(s["decisions"])); s["decisions"][key]["context_id"] = "ctx:missing"
expect_seed("artifact-context", "ARTIFACT_CONTEXT_MISSING", lambda: sut._validate_artifact_maps(s))

# Permit lineage validation using a complete action state.
action, _ = replay("POS-009")
permit_id, permit = next(iter(action["permits"].items()))
receipt_id, receipt = next(iter(action["permit_use_receipts"].items()))
mutations: list[tuple[str, str, Callable[[dict[str, Any]], None]]] = [
    ("permit-receipt-missing", "RECEIPT_PERMIT_MISSING", lambda x: x["permit_use_receipts"][receipt_id].__setitem__("permit_ref", "permit:missing")),
    ("permit-intent-mismatch", "RECEIPT_INTENT_MISMATCH", lambda x: x["permit_use_receipts"][receipt_id].__setitem__("execution_intent_ref", "intent:missing")),
    ("permit-scope-digest", "PERMIT_SCOPE_DIGEST_MISMATCH", lambda x: x["permits"][permit_id].__setitem__("scope_digest", "sha256:" + "3" * 64)),
    ("permit-readiness-missing", "PERMIT_READINESS_MISSING", lambda x: x["permits"][permit_id].__setitem__("readiness_ref", "dec:missing")),
    ("permit-readiness-binding", "PERMIT_READINESS_BINDING_MISMATCH", lambda x: x["decisions"][x["permits"][permit_id]["readiness_ref"]].__setitem__("subject_principal_id", "principal:wrong")),
    ("permit-readiness-terms", "PERMIT_READINESS_TERMS_MISMATCH", lambda x: x["decisions"][x["permits"][permit_id]["readiness_ref"]].__setitem__("conditions_digest", "sha256:" + "4" * 64)),
    ("permit-decision-missing", "PERMIT_DECISION_MISSING", lambda x: x["permits"][permit_id].__setitem__("decision_ref", "dec:missing")),
    ("permit-decision-binding", "PERMIT_DECISION_BINDING_MISMATCH", lambda x: x["decisions"][x["permits"][permit_id]["decision_ref"]].__setitem__("subject_principal_id", "principal:wrong")),
    ("permit-decision-terms", "PERMIT_DECISION_TERMS_MISMATCH", lambda x: x["decisions"][x["permits"][permit_id]["decision_ref"]].__setitem__("conditions_digest", "sha256:" + "5" * 64)),
    ("attempt-index-gap", "ATTEMPT_INDEX_GAP", lambda x: x["permit_use_receipts"][receipt_id].__setitem__("attempt_index", 2)),
    ("attempt-counter", "ATTEMPT_COUNTER_MISMATCH", lambda x: x["permits"][permit_id].__setitem__("attempts_used", 0)),
    ("final-outcome", "PERMIT_FINAL_OUTCOME_MISMATCH", lambda x: x["permits"][permit_id].__setitem__("final_outcome_ref", "out:missing")),
    ("submission-index", "SUBMISSION_INDEX_MISMATCH", lambda x: x["submission_index"][receipt["submission_id"]].__setitem__("receipt_ref", "receipt:missing")),
]
for name, code, mutate in mutations:
    s = copy.deepcopy(action); mutate(s); expect_seed(name, code, lambda s=s: sut._validate_permit_lineage(s))
s = copy.deepcopy(action)
p = s["permits"][permit_id]
p["max_attempts"] = 0
terms = sut.permit_terms_digest(
    p["delegate_principal_id"], p["task_digest"], p["scope"],
    p["success_predicate_digest"], p["max_attempts"],
    p["validity_end_ordinal"], p["caveats"],
)
s["decisions"][p["readiness_ref"]]["conditions_digest"] = terms
s["decisions"][p["decision_ref"]]["conditions_digest"] = terms
expect_seed("attempt-limit", "ATTEMPT_LIMIT_EXCEEDED", lambda: sut._validate_permit_lineage(s))
# Linear attenuation branches.
attenuated, attenuation_tx = replay("POS-011")
attenuation_result = sut.apply_transition(attenuated, attenuation_tx)
record("attenuation-baseline", attenuation_result["accepted"] and attenuation_result["state_changed"], attenuation_result["code"])
attenuated = attenuation_result["state"]
parent_id = next(pid for pid, p in attenuated["permits"].items() if p["status"] == "ATTENUATED")
child_id = next(pid for pid, p in attenuated["permits"].items() if p["parent_permit_ref"] == parent_id)
s = copy.deepcopy(attenuated); extra = copy.deepcopy(s["permits"][child_id]); extra["permit_id"] = "permit:extra"; extra["parent_permit_ref"] = parent_id; s["permits"][extra["permit_id"]] = extra
expect_seed("attenuation-linear", "PERMIT_ATTENUATION_NOT_LINEAR", lambda: sut._validate_permit_lineage(s))
s = copy.deepcopy(attenuated); s["permits"][parent_id]["status"] = "ACTIVE"
expect_seed("parent-not-attenuated", "PARENT_PERMIT_NOT_ATTENUATED", lambda: sut._validate_permit_lineage(s))
s = copy.deepcopy(attenuated); del s["permits"][child_id]
expect_seed("attenuated-child-missing", "ATTENUATED_PERMIT_CHILD_MISSING", lambda: sut._validate_permit_lineage(s))
s = copy.deepcopy(attenuated); s["permits"][child_id]["parent_permit_ref"] = "permit:missing"
expect_seed("parent-lineage-missing", "PARENT_PERMIT_LINEAGE_MISSING", lambda: sut._validate_permit_lineage(s))
for name, code, field, value in [
    ("lineage-scope-escalation", "PERMIT_SCOPE_ESCALATION", "scope", ["not-parent"]),
    ("lineage-attempt-escalation", "PERMIT_ATTEMPT_ESCALATION", "max_attempts", 999),
    ("lineage-validity-escalation", "PERMIT_VALIDITY_ESCALATION", "validity_end_ordinal", 999999),
]:
    s = copy.deepcopy(attenuated); child = s["permits"][child_id]; child[field] = value
    if field == "scope": child["scope_digest"] = sut.scope_digest(value)
    terms = sut.permit_terms_digest(
        child["delegate_principal_id"], child["task_digest"], child["scope"],
        child["success_predicate_digest"], child["max_attempts"],
        child["validity_end_ordinal"], child["caveats"],
    )
    s["decisions"][child["readiness_ref"]]["conditions_digest"] = terms
    expect_seed(name, code, lambda s=s: sut._validate_permit_lineage(s))

# Evidence lineage validation.
completed_action = accepted("POS-009")
verification_id = next(iter(completed_action["verifications"])); observation_id = next(iter(completed_action["observations"])); outcome_id = next(iter(completed_action["outcomes"]))
for name, code, mutate in [
    ("obs-receipt", "OBSERVATION_RECEIPT_MISMATCH", lambda x: x["observations"][observation_id].__setitem__("receipt_ref", "receipt:missing")),
    ("obs-context", "OBSERVATION_CONTEXT_MISMATCH", lambda x: x["observations"][observation_id].__setitem__("context_id", x["root_context_id"])),
    ("ver-lineage", "VERIFICATION_LINEAGE_MISSING", lambda x: x["verifications"][verification_id].__setitem__("observation_ref", "obs:missing")),
    ("ver-permit", "VERIFICATION_PERMIT_MISMATCH", lambda x: x["verifications"][verification_id].__setitem__("permit_ref", "permit:missing")),
    ("ver-context", "VERIFICATION_CONTEXT_MISMATCH", lambda x: x["verifications"][verification_id].__setitem__("context_id", x["root_context_id"])),
    ("ver-policy", "VERIFICATION_POLICY_UNRECOGNIZED", lambda x: x["verifications"][verification_id].__setitem__("policy_digest", "sha256:" + "6" * 64)),
    ("out-permit", "OUTCOME_PERMIT_MISMATCH", lambda x: x["outcomes"][outcome_id].__setitem__("permit_ref", "permit:missing")),
    ("out-verification-missing", "OUTCOME_VERIFICATION_SET_INCOMPLETE", lambda x: x["outcomes"][outcome_id].__setitem__("verification_refs", [])),
]:
    s = copy.deepcopy(completed_action); mutate(s); expect_seed(name, code, lambda s=s: sut._validate_evidence_lineage(s))
# Export/import/correction whole-state checks.
exp_state = accepted("POS-018")
exp_id = next(iter(exp_state["exports"]))
s = copy.deepcopy(exp_state); s["exports"][exp_id]["source_export_root"] = "sha256:" + "7" * 64
expect_seed("export-root-lineage", "EXPORT_COMMIT_ROOT_MISMATCH", lambda: sut._validate_evidence_lineage(s))
imp_state = accepted("POS-021")
imp_id = next(iter(imp_state["imports"])); s = copy.deepcopy(imp_state); s["imports"][imp_id]["claim_digest"] = "sha256:" + "8" * 64
expect_seed("import-export-lineage", "IMPORT_EXPORT_MISMATCH", lambda: sut._validate_evidence_lineage(s))
corr_state = accepted("POS-019")
corr_id = next(iter(corr_state["corrections"])); s = copy.deepcopy(corr_state); s["corrections"][corr_id]["target_type"] = "OUTCOME"
expect_seed("correction-type-state", "CORRECTION_TARGET_TYPE_UNSUPPORTED", lambda: sut._validate_evidence_lineage(s))
s = copy.deepcopy(corr_state); s["corrections"][corr_id]["target_ref"] = "ver:missing"
expect_seed("correction-target-state", "CORRECTION_TARGET_MISMATCH", lambda: sut._validate_evidence_lineage(s))

# Transition record validation.
record_id = next(iter(full["transition_records"]))
for name, code, mutate in [
    ("transition-count", "TRANSITION_COUNT_MISMATCH", lambda x: x.__setitem__("accepted_transition_count", 0)),
    ("transition-map", "TRANSITION_MAP_KEY_MISMATCH", lambda x: x["transition_records"][record_id].__setitem__("transition_id", "tx:wrong")),
    ("causal-basis", "CAUSAL_RECORD_BASIS_MISMATCH", lambda x: x["transition_records"][record_id].__setitem__("causal_parents", ["tx:missing"])),
    ("local-ordinal", "LOCAL_ORDINAL_MISMATCH", lambda x: x["contexts"][x["root_context_id"]].__setitem__("local_ordinal", 999)),
    ("internal-root", "CONTEXT_INTERNAL_STATE_ROOT_MISMATCH", lambda x: x["contexts"][x["root_context_id"]].__setitem__("internal_state_root", "sha256:" + "9" * 64)),
]:
    s = copy.deepcopy(full); mutate(s); expect_seed(name, code, lambda s=s: sut._validate_transition_records(s))
# duplicate artifact creator
s = copy.deepcopy(full); records = list(s["transition_records"].values()); records[1]["artifact_refs"].append(records[0]["artifact_refs"][0])
expect_seed("artifact-creator-duplicate", "ARTIFACT_CREATOR_DUPLICATE", lambda: sut._validate_transition_records(s))

# validate_state top-level branches.
for name, code, mutate, root_ok in [
    ("state-version", "STATE_VERSION_MISMATCH", lambda x: x.__setitem__("schema_version", "0.1-rc8"), True),
    ("constitution-digest", "CONSTITUTION_DIGEST_MISMATCH", lambda x: x["constitution"].__setitem__("digest", "sha256:" + "a" * 64), True),
    ("trust-space", "TRUST_SPACE_ID_MISMATCH", lambda x: x.__setitem__("trust_space_id", "ts:" + "a" * 64), True),
    ("alias-duplicate", "CONTEXT_ALIAS_DUPLICATE", lambda x: list(x["contexts"].values())[1].__setitem__("alias", "/"), True),
    ("alias-index", "CONTEXT_ALIAS_INDEX_MISMATCH", lambda x: x["context_aliases"].__setitem__("/bad", x["root_context_id"]), True),
    ("bootstrap-limit", "BOOTSTRAP_ADMISSION_LIMIT", lambda x: x["bootstrap"].__setitem__("admissions_used", 99), True),
    ("bootstrap-open", "BOOTSTRAP_OPEN_STATE_MISMATCH", lambda x: x["bootstrap"].__setitem__("open", True), True),
    ("state-root", "STATE_ROOT_MISMATCH", lambda x: x.__setitem__("current_state_root", "sha256:" + "b" * 64), False),
]:
    s = copy.deepcopy(full); mutate(s)
    if root_ok: s["current_state_root"] = sut.compute_state_root(s)
    expect_seed(name, code, lambda s=s: validate_state_semantic(s))
# Context epoch and inactive authority.
s = copy.deepcopy(full); cid = next(c for c in s["contexts"] if c != s["root_context_id"]); s["contexts"][cid]["constitution_epoch"] += 1; s["current_state_root"] = sut.compute_state_root(s)
expect_seed("context-epoch", "CONTEXT_CONSTITUTION_EPOCH_MISMATCH", lambda: sut.validate_state(s))
s = copy.deepcopy(full); s["contexts"][cid]["lifecycle"] = "WITHDRAWN"; s["contexts"][cid]["guarantee_status"] = "TERMINATED"; s["context_aliases"].pop(s["contexts"][cid]["alias"], None); s["current_state_root"] = sut.compute_state_root(s)
expect_seed("inactive-authority", "ACTIVE_AUTHORITY_IN_INACTIVE_CONTEXT", lambda: sut.validate_state(s))

# initialize_state exact identity checks.
g = copy.deepcopy(load("POS-001")["initial_genesis"])
for name, code, mutate in [
    ("genesis-version", "GENESIS_VERSION_MISMATCH", lambda x: x.__setitem__("schema_version", "0.1-rc8")),
    ("genesis-semantics", "SEED_SEMANTICS_MISMATCH", lambda x: x.__setitem__("seed_semantics_id", "wrong")),
    ("genesis-constitution", "CONSTITUTION_DIGEST_MISMATCH", lambda x: x.__setitem__("expected_constitution_digest", "sha256:" + "c" * 64)),
    ("genesis-root-digest", "ROOT_GENESIS_DIGEST_MISMATCH", lambda x: x.__setitem__("expected_root_genesis_digest", "sha256:" + "c" * 64)),
    ("genesis-root-context", "ROOT_CONTEXT_ID_MISMATCH", lambda x: x.__setitem__("expected_root_context_id", "ctx:" + "c" * 64)),
    ("genesis-trust-space", "TRUST_SPACE_ID_MISMATCH", lambda x: x.__setitem__("expected_trust_space_id", "ts:" + "c" * 64)),
]:
    x = copy.deepcopy(g); mutate(x); expect_seed(name, code, lambda x=x: initialize_semantic(x))

# Handler error branches. Use direct handlers to isolate each guard.
member_state, member_tx = replay("POS-001")
for name, code, mutate_state, mutate_tx in [
    ("member-parent", "PARENT_CONTEXT_MISMATCH", None, lambda t: t["payload"].__setitem__("parent_context_id", "ctx:wrong")),
    ("member-bootstrap-closed", "BOOTSTRAP_CLOSED", lambda s: s["bootstrap"].__setitem__("open", False), None),
    ("member-validator", "BOOTSTRAP_VALIDATOR_MISMATCH", None, lambda t: t["authn"].__setitem__("signer_principal_id", "principal:wrong")),
    ("member-kind", "BOOTSTRAP_CONTEXT_KIND_FORBIDDEN", None, lambda t: t["payload"].__setitem__("context_kind", "SUBJECT")),
    ("member-limit", "BOOTSTRAP_ADMISSION_LIMIT", lambda s: s["bootstrap"].__setitem__("admissions_used", s["bootstrap"]["policy"]["max_admissions"]), None),
    ("member-capability", "BOOTSTRAP_CAPABILITY_FORBIDDEN", None, lambda t: t["payload"]["initial_authorities"][0].__setitem__("capability_kind", "FORBIDDEN")),
]:
    s, t = copy.deepcopy(member_state), copy.deepcopy(member_tx)
    if mutate_state: mutate_state(s)
    if mutate_tx: mutate_tx(t)
    direct_handler(name, code, sut._handle_member_context_genesis, s, t)
# Existing context/alias/authority/dependency branches.
s, t = copy.deepcopy(member_state), copy.deepcopy(member_tx); expected = sut.compute_context_id(t["context_id"], sut.member_genesis_digest(t["payload"])); t["payload"]["expected_new_context_id"] = expected; s["contexts"][expected] = copy.deepcopy(s["contexts"][s["root_context_id"]]); direct_handler("member-existing-context", "CONTEXT_ALREADY_EXISTS", sut._handle_member_context_genesis, s, t)
s, t = copy.deepcopy(member_state), copy.deepcopy(member_tx); s["context_aliases"]["/f"] = s["root_context_id"]; direct_handler("member-alias", "CONTEXT_ALIAS_IN_USE", sut._handle_member_context_genesis, s, t)
s, t = copy.deepcopy(member_state), copy.deepcopy(member_tx); t["payload"]["depends_on_context_ids"] = ["ctx:missing"]; direct_handler("member-dependency", "DEPENDENCY_CONTEXT_UNKNOWN", sut._handle_member_context_genesis, s, t)

# Decision.
dec_state, dec_tx = replay("POS-003")
t = copy.deepcopy(dec_tx); t["authn"]["signer_principal_id"] = "principal:wrong"; direct_handler("decision-readiness-subject", "READINESS_SUBJECT_MISMATCH", sut._handle_decision, dec_state, t)
t = copy.deepcopy(dec_tx); t["payload"]["decision_kind"] = "UNKNOWN"; direct_handler("decision-kind", "DECISION_KIND_UNSUPPORTED", sut._handle_decision, dec_state, t)

# Permit issue.
pi_state, pi_tx = replay("POS-004")
def pi(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s, t = copy.deepcopy(pi_state), copy.deepcopy(pi_tx); mutate(s, t); direct_handler(name, code, sut._handle_permit_issue, s, t)
pi("issue-decision", "ISSUE_DECISION_INVALID", lambda s,t: t["payload"].__setitem__("decision_ref", "dec:missing"))
pi("issue-readiness", "READINESS_DECISION_INVALID", lambda s,t: t["payload"].__setitem__("readiness_ref", "dec:missing"))
pi("issue-context", "PERMIT_DECISION_CONTEXT_MISMATCH", lambda s,t: s["decisions"][t["payload"]["decision_ref"]].__setitem__("context_id", s["root_context_id"]))
pi("issue-issuer", "ISSUE_DECISION_ISSUER_MISMATCH", lambda s,t: s["decisions"][t["payload"]["decision_ref"]].__setitem__("issuer_principal_id", "principal:wrong"))
pi("issue-epoch", "PERMIT_DECISION_EPOCH_STALE", lambda s,t: s["decisions"][t["payload"]["decision_ref"]].__setitem__("constitution_epoch", 99))
pi("issue-subject", "PERMIT_SUBJECT_MISMATCH", lambda s,t: s["decisions"][t["payload"]["decision_ref"]].__setitem__("subject_principal_id", "principal:wrong"))
pi("issue-readiness-delegate", "READINESS_DELEGATE_MISMATCH", lambda s,t: s["decisions"][t["payload"]["readiness_ref"]].__setitem__("issuer_principal_id", "principal:wrong"))
pi("issue-scope", "PERMIT_SCOPE_DECISION_MISMATCH", lambda s,t: t["payload"].__setitem__("scope", ["wrong"]))
pi("issue-attempts", "MAX_ATTEMPTS_INVALID", lambda s,t: t["payload"].__setitem__("max_attempts", 0))
pi("issue-stop", "STOP_ON_POSITIVE_REQUIRED", lambda s,t: t["payload"].__setitem__("stop_on_positive", False))
pi("issue-expired", "PERMIT_ALREADY_EXPIRED", lambda s,t: t["payload"].__setitem__("validity_end_ordinal", 0))
pi("issue-terms", "PERMIT_TERMS_DECISION_MISMATCH", lambda s,t: t["payload"].__setitem__("task_digest", "sha256:" + "d" * 64))
pi("issue-related", "ISSUE_DECISION_READINESS_MISMATCH", lambda s,t: s["decisions"][t["payload"]["decision_ref"]].__setitem__("related_ref", None))

# Permit use.
use_state, use_tx = replay("POS-005")
def use(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(use_state),copy.deepcopy(use_tx); mutate(s,t); direct_handler(name,code,sut._handle_permit_use,s,t)
use("use-unknown", "PERMIT_UNKNOWN", lambda s,t: t["payload"].__setitem__("permit_ref", "permit:missing"))
use("use-context", "PERMIT_CONTEXT_MISMATCH", lambda s,t: t.__setitem__("context_id", s["root_context_id"]))
use("use-delegate", "PERMIT_DELEGATE_MISMATCH", lambda s,t: t["authn"].__setitem__("signer_principal_id", "principal:wrong"))
use("use-status", "PERMIT_NOT_ACTIVE", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("status", "REVOKED"))
use("use-expired", "PERMIT_EXPIRED", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("validity_end_ordinal", 0))
use("use-attempt-limit", "ATTEMPT_LIMIT_EXHAUSTED", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("attempts_used", s["permits"][t["payload"]["permit_ref"]]["max_attempts"]))
# conflicting submission ID
s,t=copy.deepcopy(use_state),copy.deepcopy(use_tx); s["submission_index"][t["payload"]["submission_id"]]={"permit_ref":"permit:other","candidate_digest":t["payload"]["candidate_digest"],"receipt_ref":"receipt:x"}; direct_handler("use-submission-collision","SUBMISSION_ID_COLLISION",sut._handle_permit_use,s,t)

# Observation.
obs_state, obs_tx = replay("POS-007")
def obs(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(obs_state),copy.deepcopy(obs_tx); mutate(s,t); direct_handler(name,code,sut._handle_observation,s,t)
obs("obs-lineage", "OBSERVATION_LINEAGE_MISSING", lambda s,t: t["payload"].__setitem__("permit_ref", "permit:missing"))
obs("obs-receipt-handler", "OBSERVATION_RECEIPT_MISMATCH", lambda s,t: s["permit_use_receipts"][t["payload"]["receipt_ref"]].__setitem__("permit_ref", "permit:wrong"))
obs("obs-context-handler", "OBSERVATION_CONTEXT_MISMATCH", lambda s,t: t.__setitem__("context_id", s["root_context_id"]))
obs("obs-presenter", "OBSERVATION_PRESENTER_MISMATCH", lambda s,t: t["authn"].__setitem__("signer_principal_id", "principal:wrong"))

# Verification.
ver_state, ver_tx = replay("POS-008")
def ver(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(ver_state),copy.deepcopy(ver_tx); mutate(s,t); direct_handler(name,code,sut._handle_verification,s,t)
ver("ver-lineage-handler", "VERIFICATION_LINEAGE_MISSING", lambda s,t: t["payload"].__setitem__("observation_ref", "obs:missing"))
ver("ver-permit-handler", "VERIFICATION_PERMIT_MISMATCH", lambda s,t: s["observations"][t["payload"]["observation_ref"]].__setitem__("permit_ref", "permit:wrong"))
ver("ver-receipt-handler", "VERIFICATION_RECEIPT_MISMATCH", lambda s,t: s["observations"][t["payload"]["observation_ref"]].__setitem__("receipt_ref", "receipt:wrong"))
ver("ver-context-handler", "VERIFICATION_CONTEXT_MISMATCH", lambda s,t: s["observations"][t["payload"]["observation_ref"]].__setitem__("context_id", s["root_context_id"]))
ver("ver-status-result", "VERIFICATION_STATUS_RESULT_MISMATCH", lambda s,t: t["payload"].update({"status":"FAIL","result_class":"SUCCESS"}))
ver("ver-policy-handler", "VERIFICATION_POLICY_UNRECOGNIZED", lambda s,t: t["payload"].__setitem__("policy_digest", "sha256:" + "e" * 64))

# Outcome.
out_state, out_tx = replay("POS-009")
def out(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None], state=out_state, tx=out_tx) -> None:
    s,t=copy.deepcopy(state),copy.deepcopy(tx); mutate(s,t); direct_handler(name,code,sut._handle_outcome,s,t)
out("out-unknown", "PERMIT_UNKNOWN", lambda s,t: t["payload"].__setitem__("permit_ref", "permit:missing"))
out("out-context", "OUTCOME_CONTEXT_MISMATCH", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("context_id", s["root_context_id"]))
out("out-final", "OUTCOME_ALREADY_FINAL", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("final_outcome_ref", "out:x"))
out("out-status", "PERMIT_NOT_OUTCOME_ELIGIBLE", lambda s,t: s["permits"][t["payload"]["permit_ref"]].__setitem__("status", "REVOKED"))
out("out-set", "OUTCOME_VERIFICATION_SET_INCOMPLETE", lambda s,t: t["payload"].__setitem__("verification_refs", []))
# Positive without success and negative conflicts.
s,t=copy.deepcopy(out_state),copy.deepcopy(out_tx); vid=t["payload"]["verification_refs"][0]; s["verifications"][vid]["result_class"]="FAILURE"; direct_handler("out-success","SUCCESS_NOT_VERIFIED",sut._handle_outcome,s,t)
s,t=copy.deepcopy(out_state),copy.deepcopy(out_tx); t["payload"]["outcome_class"]="NEGATIVE"; direct_handler("out-negative-conflict","NEGATIVE_CONFLICTS_WITH_SUCCESS",sut._handle_outcome,s,t)
neg_state, neg_tx = replay("POS-010")
s,t=copy.deepcopy(neg_state),copy.deepcopy(neg_tx); s["permits"][t["payload"]["permit_ref"]]["status"]="ACTIVE"; direct_handler("out-negative-terminal","NEGATIVE_NOT_TERMINAL",sut._handle_outcome,s,t)
s,t=copy.deepcopy(neg_state),copy.deepcopy(neg_tx); vid=t["payload"]["verification_refs"][0]; s["verifications"][vid]["result_class"]="TRUST_LINEAGE_LOST"; direct_handler("out-failure","FAILURE_NOT_VERIFIED",sut._handle_outcome,s,t)

# Export.
ex_state, ex_tx = replay("POS-018")
def ex(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(ex_state),copy.deepcopy(ex_tx); mutate(s,t); direct_handler(name,code,sut._handle_export,s,t)
ex("export-suspended", "GUARANTEE_SUSPENDED_USE_LOCAL_COMMIT", lambda s,t: s["contexts"][t["context_id"]].__setitem__("guarantee_status", "SUSPENDED"))
ex("export-root", "EXPORT_ROOT_MISMATCH", lambda s,t: t["payload"].__setitem__("source_export_root", "sha256:" + "f" * 64))
ex("export-outcome-unknown", "EXPORT_OUTCOME_UNKNOWN", lambda s,t: t["payload"].__setitem__("outcome_ref", "out:missing"))
# Use an outcome from another context.
s,t=copy.deepcopy(ex_state),copy.deepcopy(ex_tx); other=copy.deepcopy(next(iter(completed_action["outcomes"].values()))); other["outcome_id"]="out:other"; other["context_id"] = s["root_context_id"]; s["outcomes"]["out:other"]=other; t["payload"]["outcome_ref"]="out:other"; direct_handler("export-outcome-context","EXPORT_OUTCOME_CONTEXT_MISMATCH",sut._handle_export,s,t)

# Import.
im_state, im_tx = replay("POS-021")
def im(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(im_state),copy.deepcopy(im_tx); mutate(s,t); direct_handler(name,code,sut._handle_import,s,t)
im("import-unknown", "EXPORT_UNKNOWN", lambda s,t: t["payload"].__setitem__("export_ref", "export:missing"))
im("import-local-missing", "IMPORT_LOCAL_LINEAGE_MISSING", lambda s,t: t["payload"].__setitem__("local_permit_ref", "permit:missing"))
im("import-local-mismatch", "IMPORT_LOCAL_LINEAGE_MISMATCH", lambda s,t: s["permit_use_receipts"][t["payload"]["local_receipt_ref"]].__setitem__("permit_ref", "permit:wrong"))
def mutate_import_presenter(s: dict[str, Any], t: dict[str, Any]) -> None:
    original = t["authn"]["signer_principal_id"]
    authority = next(
        a for a in s["authorities"].values()
        if a["context_id"] == t["context_id"]
        and a["capability_kind"] == "IMPORT"
        and a["holder_principal_id"] == original
        and a["status"] == "ACTIVE"
    )
    authority["holder_principal_id"] = "principal:wrong"
    t["authn"]["signer_principal_id"] = "principal:wrong"

im("import-presenter", "IMPORT_PRESENTER_MISMATCH", mutate_import_presenter)

# Guarantee suspension.
gs_state, gs_tx = replay("POS-012")
s,t=copy.deepcopy(gs_state),copy.deepcopy(gs_tx); t["payload"]["child_context_id"]="ctx:missing"; direct_handler("suspend-unknown","CONTEXT_UNKNOWN",sut._handle_guarantee_suspend,s,t)
s,t=copy.deepcopy(gs_state),copy.deepcopy(gs_tx); t["context_id"]=s["root_context_id"]; direct_handler("suspend-direct-child","NOT_DIRECT_CHILD_CONTEXT",sut._handle_guarantee_suspend,s,t)

# Partition local.
pl_state, pl_tx = replay("POS-013")
def pl(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(pl_state),copy.deepcopy(pl_tx); mutate(s,t); direct_handler(name,code,sut._handle_partition_local_transition,s,t)
pl("local-not-suspended","GUARANTEE_NOT_SUSPENDED",lambda s,t:s["contexts"][t["context_id"]].__setitem__("guarantee_status","CONFIRMED"))
pl("local-coordination","COORDINATION_REQUIRED",lambda s,t:t["payload"].__setitem__("operation_class","AUTHORITY_CHANGE"))
pl("local-signer","LOCAL_COMMIT_SIGNER_UNAUTHORIZED",lambda s,t:t["authn"].__setitem__("signer_principal_id","principal:wrong"))
pl("local-parent","LOCAL_COMMIT_PARENT_UNKNOWN",lambda s,t:t["payload"].__setitem__("parent_export_root","sha256:"+"1"*64))

# Reconciliation.
re_state, re_tx = replay("POS-014")
def rec(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(re_state),copy.deepcopy(re_tx); mutate(s,t); direct_handler(name,code,sut._handle_reconcile,s,t)
rec("rec-unknown","CONTEXT_UNKNOWN",lambda s,t:t["payload"].__setitem__("child_context_id","ctx:missing"))
rec("rec-direct","NOT_DIRECT_CHILD_CONTEXT",lambda s,t:t.__setitem__("context_id",s["root_context_id"]))
rec("rec-suspended","GUARANTEE_NOT_SUSPENDED",lambda s,t:s["contexts"][t["payload"]["child_context_id"]].__setitem__("guarantee_status","CONFIRMED"))
rec("rec-common-root","RECONCILIATION_COMMON_ROOT_MISMATCH",lambda s,t:t["payload"].__setitem__("common_export_root","sha256:"+"2"*64))
# use POS-016 known commits for omission.
fork_state, fork_tx = replay("POS-016")
s,t=copy.deepcopy(fork_state),copy.deepcopy(fork_tx); known_id=t["payload"]["lineage"][0]["commit_id"]; s["contexts"][t["payload"]["child_context_id"]]["unconfirmed_commits"]={known_id:{}}; t["payload"]["lineage"]=[]; direct_handler("rec-known-set","RECONCILIATION_KNOWN_COMMIT_SET_MISMATCH",sut._handle_reconcile,s,t)
s,t=copy.deepcopy(re_state),copy.deepcopy(re_tx); t["payload"]["lineage"][0]["commit_id"]="commit:wrong"; direct_handler("rec-commit-id","LOCAL_COMMIT_ID_MISMATCH",sut._handle_reconcile,s,t)
s,t=copy.deepcopy(re_state),copy.deepcopy(re_tx); t["payload"]["lineage"][0]["proof_digest"]="bad"; direct_handler("rec-proof","AUTHENTICATION_PROOF_FORMAT",sut._handle_reconcile,s,t)
s,t=copy.deepcopy(re_state),copy.deepcopy(re_tx); t["payload"]["lineage"][0]["signer_principal_id"]="principal:wrong"; direct_handler("rec-signer","LOCAL_COMMIT_ID_MISMATCH",sut._handle_reconcile,s,t)
s,t=copy.deepcopy(re_state),copy.deepcopy(re_tx); t["payload"]["lineage"][0]["new_export_root"]="sha256:"+"3"*64; direct_handler("rec-root","LOCAL_COMMIT_ROOT_MISMATCH",sut._handle_reconcile,s,t)

# Membership withdrawal and atomic context redefinition.
rd_state, rd_tx = replay("POS-017")
def redef(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    st,tx=copy.deepcopy(rd_state),copy.deepcopy(rd_tx); mutate(st,tx); direct_handler(name,code,sut._handle_context_redefine,st,tx)
redef("redef-parent", "REDEFINITION_PARENT_MISMATCH", lambda st,tx: tx["payload"]["proposal"].__setitem__("parent_context_id", st["root_context_id"]))
redef("redef-digest", "REDEFINITION_PROPOSAL_DIGEST_MISMATCH", lambda st,tx: tx["payload"].__setitem__("proposal_digest", "sha256:"+"1"*64))
def mutate_proposal(tx, mutator):
    mutator(tx["payload"]["proposal"])
    digest=sut.context_redefinition_proposal_digest(tx["payload"]["proposal"])
    tx["payload"]["proposal_digest"]=digest
    for auth in tx["payload"]["withdrawal_authorizations"]: auth["proposal_digest"]=digest
redef("redef-affected", "REDEFINITION_AFFECTED_SET_MISMATCH", lambda st,tx: mutate_proposal(tx, lambda proposal: proposal["replacements"].pop()))
redef("redef-replacement-duplicate", "REDEFINITION_AFFECTED_SET_MISMATCH", lambda st,tx: mutate_proposal(tx, lambda proposal: proposal["replacements"].append(copy.deepcopy(proposal["replacements"][0]))))
redef("redef-auth-set", "REDEFINITION_AUTHORIZATION_SET_MISMATCH", lambda st,tx: tx["payload"]["withdrawal_authorizations"].pop())
redef("redef-auth-duplicate", "REDEFINITION_AUTHORIZATION_SET_MISMATCH", lambda st,tx: tx["payload"]["withdrawal_authorizations"].append(copy.deepcopy(tx["payload"]["withdrawal_authorizations"][0])))
redef("redef-member", "REDEFINITION_MEMBER_MISMATCH", lambda st,tx: tx["payload"]["withdrawal_authorizations"][0].__setitem__("member_principal_id", "principal:wrong"))
redef("redef-auth-binding", "REDEFINITION_AUTHORIZATION_BINDING_MISMATCH", lambda st,tx: tx["payload"]["withdrawal_authorizations"][0].__setitem__("proposal_digest", "sha256:"+"2"*64))
# Exact prior genesis material yields an already-existing successor ID.
def collision(st,tx):
    target=tx["payload"]["proposal"]["target_context_id"]
    for item in tx["payload"]["proposal"]["replacements"]:
        if item["old_context_id"]==target:
            item["context_genesis_nonce"]="a-v1"
    proposal=tx["payload"]["proposal"]; digest=sut.context_redefinition_proposal_digest(proposal)
    tx["payload"]["proposal_digest"]=digest
    for auth in tx["payload"]["withdrawal_authorizations"]: auth["proposal_digest"]=digest
redef("redef-collision", "REDEFINITION_SUCCESSOR_COLLISION", collision)
def dep_unknown(st,tx):
    tx["payload"]["proposal"]["replacements"][0]["depends_on_context_ids"]=["ctx:missing"]
    digest=sut.context_redefinition_proposal_digest(tx["payload"]["proposal"]); tx["payload"]["proposal_digest"]=digest
    for auth in tx["payload"]["withdrawal_authorizations"]: auth["proposal_digest"]=digest
redef("redef-dependency-unknown", "DEPENDENCY_CONTEXT_UNKNOWN", dep_unknown)
# Direct autonomous withdrawal guards.
wd_state, wd_tx = replay("POS-023")
st,tx=copy.deepcopy(wd_state),copy.deepcopy(wd_tx); tx["context_id"]=st["root_context_id"]; direct_handler("withdraw-root","ROOT_WITHDRAWAL_FORBIDDEN",sut._handle_membership_withdraw,st,tx)
st,tx=copy.deepcopy(wd_state),copy.deepcopy(wd_tx); tx["authn"]["signer_principal_id"]="principal:wrong"; direct_handler("withdraw-signer","WITHDRAWAL_MEMBER_SIGNATURE_REQUIRED",sut._handle_membership_withdraw,st,tx)
# Governance record whole-state invariants.
rd_done = accepted("POS-017")
rid = next(iter(rd_done["context_redefinitions"])); wid = next(iter(rd_done["membership_withdrawals"]))
st=copy.deepcopy(rd_done); st["context_redefinitions"][rid]["successor_map"]={}; expect_seed("redef-record-map","REDEFINITION_MAP_INCOMPLETE",lambda: sut._validate_governance_records(st))
st=copy.deepcopy(rd_done); old=next(iter(st["context_redefinitions"][rid]["successor_map"])); st["contexts"][old]["lifecycle"]="WITHDRAWN"; expect_seed("redef-record-old","REDEFINITION_OLD_NOT_SUPERSEDED",lambda: sut._validate_governance_records(st))
st=copy.deepcopy(rd_done); st["membership_withdrawals"][wid]["transition_ref"]="tx:missing"; expect_seed("withdraw-record-transition","WITHDRAWAL_TRANSITION_MISSING",lambda: sut._validate_governance_records(st))

# Termination.
# Termination.
term_state, term_tx = replay("POS-020")
s,t=copy.deepcopy(term_state),copy.deepcopy(term_tx); t["payload"]["child_context_id"]="ctx:missing"; direct_handler("term-unknown","CONTEXT_UNKNOWN",sut._handle_context_terminate,s,t)
s,t=copy.deepcopy(term_state),copy.deepcopy(term_tx); t["context_id"]=s["root_context_id"]; direct_handler("term-child","NOT_DIRECT_CHILD_CONTEXT",sut._handle_context_terminate,s,t)
s,t=copy.deepcopy(term_state),copy.deepcopy(term_tx); t["payload"]["verification_ref"]="ver:missing"; direct_handler("term-verification","TRUST_LINEAGE_LOSS_NOT_VERIFIED",sut._handle_context_terminate,s,t)
s,t=copy.deepcopy(term_state),copy.deepcopy(term_tx); vid=t["payload"]["verification_ref"]; oid=s["verifications"][vid]["observation_ref"]; s["observations"][oid]["claim_subject_context_id"]=t["context_id"]; direct_handler("term-subject","TRUST_LINEAGE_LOSS_SUBJECT_MISMATCH",sut._handle_context_terminate,s,t)

# Correction.
co_state, co_tx = replay("POS-019")
def cor(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(co_state),copy.deepcopy(co_tx); mutate(s,t); direct_handler(name,code,sut._handle_correction,s,t)
cor("corr-type","CORRECTION_TARGET_TYPE_UNSUPPORTED",lambda s,t:t["payload"].__setitem__("target_type","OUTCOME"))
cor("corr-unknown","CORRECTION_TARGET_UNKNOWN",lambda s,t:t["payload"].__setitem__("target_ref","ver:missing"))
cor("corr-context","CORRECTION_CONTEXT_MISMATCH",lambda s,t:t.__setitem__("context_id",s["root_context_id"]))
cor("corr-self","CORRECTION_SELF_REPLACEMENT",lambda s,t:t["payload"].__setitem__("replacement_ref",t["payload"]["target_ref"]))
cor("corr-replacement-unknown","CORRECTION_REPLACEMENT_UNKNOWN",lambda s,t:t["payload"].__setitem__("replacement_ref","ver:missing"))
# Already superseded.
s=copy.deepcopy(co_state); t=copy.deepcopy(co_tx); first=sut._handle_correction(s,t); direct_handler("corr-duplicate","CORRECTION_TARGET_ALREADY_SUPERSEDED",sut._handle_correction,s,t)

# Authority transfer.
tr_state, tr_tx = replay("POS-022")
def tr(name: str, code: str, mutate: Callable[[dict[str, Any], dict[str, Any]], None]) -> None:
    s,t=copy.deepcopy(tr_state),copy.deepcopy(tr_tx); mutate(s,t); direct_handler(name,code,sut._handle_authority_transfer,s,t)
tr("transfer-inactive","AUTHORITY_NOT_ACTIVE",lambda s,t:s["authorities"][t["payload"]["authority_ref"]].__setitem__("status","REVOKED"))
tr("transfer-context","AUTHORITY_CONTEXT_MISMATCH",lambda s,t:t.__setitem__("context_id",s["root_context_id"]))
tr("transfer-positive","TRANSFER_POSITIVE_OUTCOME_REQUIRED",lambda s,t:s["outcomes"][t["payload"]["outcome_ref"]].__setitem__("outcome_class","NEGATIVE"))
tr("transfer-action-context","TRANSFER_ACTION_CONTEXT_MISMATCH",lambda s,t:s["outcomes"][t["payload"]["outcome_ref"]].__setitem__("context_id",s["root_context_id"]))
tr("transfer-task","TRANSFER_TASK_MISMATCH",lambda s,t:s["permits"][s["outcomes"][t["payload"]["outcome_ref"]]["permit_ref"]].__setitem__("task_digest","sha256:"+"5"*64))
tr("transfer-delegate","TRANSFER_NEW_HOLDER_NOT_DELEGATE",lambda s,t:s["permits"][s["outcomes"][t["payload"]["outcome_ref"]]["permit_ref"]].__setitem__("delegate_principal_id","principal:wrong"))
tr("transfer-readiness","TRANSFER_RESPONSIBILITY_READINESS_REQUIRED",lambda s,t:s["decisions"][s["permits"][s["outcomes"][t["payload"]["outcome_ref"]]["permit_ref"]]["readiness_ref"]].__setitem__("related_ref",None))

# Coverage closure for semantically meaningful residual branches.
expect_seed(
    "authority-required-missing",
    "AUTHORITY_MISSING",
    lambda: sut._require_authority(
        full,
        {"context_id": full["root_context_id"], "authn": {"signer_principal_id": "principal:none"}},
        "NO_SUCH_CAPABILITY",
    ),
)

# Direct-sibling closure ignores inactive and non-normative endpoints and follows reverse normative dependencies.
s = copy.deepcopy(gov_state)
source = next(cid for cid in sut.compute_affected_sibling_set(s, gov_parent, gov_target) if cid != gov_target)
s["contexts"][source]["lifecycle"] = "WITHDRAWN"
record("affected-skips-inactive-source", sut.compute_affected_sibling_set(s, gov_parent, gov_target) == [gov_target])
s = copy.deepcopy(gov_state)
s["normative_dependencies"] = [{**edge, "dependency_kind":"INTERFACE"} for edge in s["normative_dependencies"]]
record("affected-skips-interface-edge", sut.compute_affected_sibling_set(s, gov_parent, gov_target) == [gov_target])

# Reach parent-missing and cycle guards without allowing identity checks to mask them.
# Reach parent-missing and cycle guards without allowing identity checks to mask them.
s = copy.deepcopy(full)
child = next(cid for cid in s["contexts"] if cid != s["root_context_id"])
s["contexts"][child]["parent_context_id"] = "ctx:missing"
original_context_id = sut.compute_context_id
try:
    sut.compute_context_id = lambda parent, genesis: child if genesis == s["contexts"][child]["genesis_digest"] else original_context_id(parent, genesis)
    expect_seed("ctx-parent-missing-semantic", "CONTEXT_PARENT_MISSING", lambda: sut._validate_context_tree(s))
finally:
    sut.compute_context_id = original_context_id
s = copy.deepcopy(nested)
non_roots = [cid for cid in s["contexts"] if cid != s["root_context_id"]]
if len(non_roots) >= 2:
    a, b = non_roots[:2]
    s["contexts"][a]["parent_context_id"] = b
    s["contexts"][b]["parent_context_id"] = a
    by_genesis = {c["genesis_digest"]: cid for cid, c in s["contexts"].items()}
    original_context_id = sut.compute_context_id
    try:
        sut.compute_context_id = lambda parent, genesis: by_genesis.get(genesis, original_context_id(parent, genesis))
        expect_seed("ctx-cycle-semantic", "CONTEXT_CYCLE", lambda: sut._validate_context_tree(s))
    finally:
        sut.compute_context_id = original_context_id

s = copy.deepcopy(full)
aid = next(iter(s["authorities"]))
s["authorities"][aid]["context_id"] = "ctx:missing"
original_authority_id = sut._authority_id
try:
    sut._authority_id = lambda binding: aid
    expect_seed("authority-context-missing-semantic", "AUTHORITY_CONTEXT_MISSING", lambda: sut._validate_authority_uniqueness(s))
finally:
    sut._authority_id = original_authority_id

# Parent caveats are monotone across attenuation.
s = copy.deepcopy(attenuated)
child = s["permits"][child_id]
child["caveats"].pop("purpose", None)
terms = sut.permit_terms_digest(
    child["delegate_principal_id"], child["task_digest"], child["scope"],
    child["success_predicate_digest"], child["max_attempts"],
    child["validity_end_ordinal"], child["caveats"],
)
s["decisions"][child["readiness_ref"]]["conditions_digest"] = terms
expect_seed("permit-caveat-weakened", "PERMIT_CAVEAT_WEAKENED", lambda: sut._validate_permit_lineage(s))

s = copy.deepcopy(exp_state)
export_id = next(iter(s["exports"]))
s["exports"][export_id]["outcome_ref"] = "out:missing"
expect_seed("export-outcome-state-missing", "EXPORT_OUTCOME_MISMATCH", lambda: sut._validate_evidence_lineage(s))
s = copy.deepcopy(corr_state)
correction_id = next(iter(s["corrections"]))
s["corrections"][correction_id]["replacement_ref"] = "ver:missing"
expect_seed("correction-replacement-state-missing", "CORRECTION_REPLACEMENT_MISMATCH", lambda: sut._validate_evidence_lineage(s))

# Public API must fail closed on unexpected implementation exceptions.
# Public API must fail closed on unexpected implementation exceptions.
state, valid_tx = replay("POS-003")
original_envelope = sut._validate_envelope
try:
    sut._validate_envelope = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom"))
    result = sut.apply_transition(state, copy.deepcopy(valid_tx))
    record("apply-malformed-envelope-exception", result["code"] == "MALFORMED_TRANSITION" and not result["accepted"])
finally:
    sut._validate_envelope = original_envelope
saved_handler = sut.HANDLERS[valid_tx["kind"]]
try:
    sut.HANDLERS[valid_tx["kind"]] = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom"))
    result = sut.apply_transition(state, copy.deepcopy(valid_tx))
    record("apply-malformed-handler-exception", result["code"] == "MALFORMED_TRANSITION" and not result["accepted"])
    sut.HANDLERS[valid_tx["kind"]] = lambda *args, **kwargs: (_ for _ in ()).throw(sut.SeedError("IDEMPOTENT_SUBMISSION_REPLAY"))
    result = sut.apply_transition(state, copy.deepcopy(valid_tx))
    record("apply-idempotent-submission-handler", result["accepted"] and result["code"] == "IDEMPOTENT_SUBMISSION_REPLAY" and not result["state_changed"])
finally:
    sut.HANDLERS[valid_tx["kind"]] = saved_handler

case = copy.deepcopy(load("POS-003"))
case["initial_genesis"]["schema_version"] = "invalid"
ok, actual, _ = sut.validate_case(case)
record("validate-case-genesis-error", not ok and actual["code"] == "GENESIS_SCHEMA_INVALID")
case = copy.deepcopy(load("POS-003"))
case["candidate"]["authn"]["signer_principal_id"] = "principal:wrong"
case["candidate"]["transition_id"] = sut.compute_transition_id(case["candidate"])
case["expected"] = {"accepted": False, "code": "READINESS_SUBJECT_MISMATCH", "state_changed": False}
case["postconditions"] = [{"path": "/accepted_transition_count", "equals": 999}]
ok, _, _ = sut.validate_case(case)
record("validate-case-rejected-postcondition", not ok)

# Envelope/application branches through public API.
state, tx = replay("POS-003")
for name, code, mutate in [
    ("env-trust","TRUST_SPACE_MISMATCH",lambda t:t.__setitem__("trust_space_id","ts:"+"1"*64)),
    ("env-id","TRANSITION_ID_MISMATCH",lambda t:t.__setitem__("transition_id","tx:"+"1"*64)),
    ("env-root","STALE_PARENT_STATE_ROOT",lambda t:t.__setitem__("parent_state_root","sha256:"+"1"*64)),
    ("env-epoch","CONSTITUTION_EPOCH_MISMATCH",lambda t:t.__setitem__("constitution_epoch",99)),
    ("env-context","CONTEXT_UNKNOWN",lambda t:t.__setitem__("context_id","ctx:missing")),
    ("env-ordinal","LOCAL_ORDINAL_MISMATCH",lambda t:t.__setitem__("expected_local_ordinal",999)),
    ("env-causal","CAUSAL_PARENTS_MISMATCH",lambda t:t.__setitem__("causal_parents",[])),
    ("env-proof","TRANSITION_SCHEMA_INVALID",lambda t:t["authn"].__setitem__("proof_digest","bad")),
]:
    t=copy.deepcopy(tx); mutate(t)
    if code != "TRANSITION_ID_MISMATCH": t["transition_id"] = sut.compute_transition_id(t)
    r=sut.apply_transition(state,t); record(name,not r["accepted"] and r["code"]==code,str(r))
t = copy.deepcopy(tx)
t["authn"]["proof_digest"] = "bad"
t["transition_id"] = sut.compute_transition_id(t)
expect_seed("env-proof-semantic", "AUTHENTICATION_PROOF_FORMAT", lambda: validate_envelope_semantic(state, t))
# Idempotent transition replay.
r=sut.apply_transition(state,copy.deepcopy(tx)); record("env-first",r["accepted"] and r["state_changed"]); r2=sut.apply_transition(r["state"],copy.deepcopy(tx)); record("env-replay",r2["accepted"] and r2["code"]=="IDEMPOTENT_REPLAY")
# Unsupported handler direct through a schema-valid copy cannot pass schema; invoke dispatch with temporary map entry removal.
kind=tx["kind"]; saved=sut.HANDLERS.pop(kind)
try:
    r=sut.apply_transition(state,copy.deepcopy(tx)); record("unsupported-handler",not r["accepted"] and r["code"]=="UNSUPPORTED_TRANSITION_KIND",str(r))
finally:
    sut.HANDLERS[kind]=saved
# validate_case setup failure and postcondition branch.
case=copy.deepcopy(load("POS-003")); case["setup"][0]["authn"]["proof_digest"]="bad"; case["setup"][0]["transition_id"]=sut.compute_transition_id(case["setup"][0]); ok,actual,_=sut.validate_case(case); record("validate-case-setup-fail",not ok and actual["code"].startswith("SETUP_FAILED:"))
case=copy.deepcopy(load("POS-003")); case["postconditions"]=[{"path":"/accepted_transition_count","equals":999}]; ok,_,_=sut.validate_case(case); record("validate-case-postcondition",not ok)


# Reconstructed governance/dependency invariants.
state, red = replay("POS-017")
target = red["payload"]["proposal"]["target_context_id"]
withdraw = copy.deepcopy(load("POS-023")["candidate"])
withdraw["context_id"] = target
withdraw["trust_space_id"] = state["trust_space_id"]
withdraw["parent_state_root"] = state["current_state_root"]
withdraw["expected_local_ordinal"] = state["contexts"][target]["local_ordinal"] + 1
withdraw["authn"]["signer_principal_id"] = state["contexts"][target]["member_principal_id"]
withdraw["causal_parents"] = sut._required_causal_parents(state, withdraw)
withdraw["transition_id"] = sut.compute_transition_id(withdraw)
r = sut.apply_transition(state, withdraw)
record("withdraw-dependent-redefine-required", not r["accepted"] and r["code"] == "WITHDRAWAL_REDEFINITION_REQUIRED", str(r))

state, wd = replay("POS-023")
r = sut.apply_transition(state, copy.deepcopy(wd)); record("withdraw-independent-accepted", r["accepted"], str(r))
if r["accepted"]:
    inactive = wd["context_id"]
    state = r["state"]
    parent = state["contexts"][inactive]["parent_context_id"]
    payload = {"parent_context_id": parent, "member_principal_id": "principal:branch-x", "context_kind": "SUBJECT", "context_genesis_nonce": "branch-x", "local_alias": "branch-x", "initial_authorities": [], "depends_on_context_ids": [inactive]}
    tx = copy.deepcopy(load("POS-017")["setup"][1])
    tx.update({"trust_space_id": state["trust_space_id"], "context_id": parent, "parent_state_root": state["current_state_root"], "expected_local_ordinal": state["contexts"][parent]["local_ordinal"] + 1, "constitution_epoch": state["constitution"]["epoch"], "causal_parents": [], "authn": {"signer_principal_id": "principal:admin", "proof_digest": "sha256:" + "d" * 64}, "payload": payload})
    tx["causal_parents"] = sut._required_causal_parents(state, tx); tx["transition_id"] = sut.compute_transition_id(tx)
    rr = sut.apply_transition(state, tx); record("genesis-inactive-dependency", not rr["accepted"] and rr["code"] == "DEPENDENCY_CONTEXT_INACTIVE", str(rr))
    mut = copy.deepcopy(state); active = parent; mut["normative_dependencies"].append({"source_context_id":active,"target_context_id":inactive,"dependency_kind":"NORMATIVE"}); mut["current_state_root"] = sut.compute_state_root(mut)
    expect_seed("state-inactive-normative-dependency", "NORMATIVE_DEPENDENCY_CONTEXT_INACTIVE", lambda: sut.validate_state(mut))

state, red = replay("POS-017"); rr = sut.apply_transition(state, copy.deepcopy(red)); record("redefine-for-record-mutation", rr["accepted"], str(rr))
if rr["accepted"]:
    mut = copy.deepcopy(rr["state"]); rid = next(iter(mut["context_redefinitions"])); mut["context_redefinitions"][rid]["proposal"]["proposal_nonce"] = "tampered"; mut["current_state_root"] = sut.compute_state_root(mut)
    expect_seed("redefinition-record-proposal-digest", "REDEFINITION_PROPOSAL_DIGEST_MISMATCH", lambda: sut.validate_state(mut))


# Governance record mutation matrix added for the rc11 freeze coverage gate.
rd = accepted("POS-017")
rid = next(iter(rd["context_redefinitions"])); recd = rd["context_redefinitions"][rid]
wid = recd["withdrawal_refs"][0]
old, new = next(iter(recd["successor_map"].items()))

def gov_mut(name: str, code: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    state = copy.deepcopy(rd); mutate(state); expect_seed(name, code, lambda: sut._validate_governance_records(state))

gov_mut("withdraw-record-id", "WITHDRAWAL_RECORD_INVALID", lambda s: s["membership_withdrawals"][wid].__setitem__("withdrawal_id", "withdrawal:wrong"))
gov_mut("withdraw-parent", "WITHDRAWAL_PARENT_MISMATCH", lambda s: s["membership_withdrawals"][wid].__setitem__("parent_context_id", s["root_context_id"]))
gov_mut("withdraw-proof", "WITHDRAWAL_PROOF_FORMAT", lambda s: s["membership_withdrawals"][wid].__setitem__("authorization_proof_digest", "invalid"))
gov_mut("withdraw-redef-mode-fields", "WITHDRAWAL_MODE_BINDING_MISMATCH", lambda s: s["membership_withdrawals"][wid].__setitem__("reason_digest", "sha256:" + "1" * 64))
gov_mut("withdraw-mode-unsupported", "WITHDRAWAL_MODE_UNSUPPORTED", lambda s: s["membership_withdrawals"][wid].__setitem__("mode", "OTHER"))
gov_mut("withdraw-lifecycle", "WITHDRAWAL_LIFECYCLE_MISMATCH", lambda s: s["contexts"][s["membership_withdrawals"][wid]["withdrawn_context_ids"][0]].__setitem__("lifecycle", "ACTIVE"))
gov_mut("redef-record-id", "REDEFINITION_RECORD_INVALID", lambda s: s["context_redefinitions"][rid].__setitem__("redefinition_id", "redef:wrong"))
def proposal_record_mismatch(s):
    record=s["context_redefinitions"][rid]; record["proposal"]["target_context_id"] = next(x for x in recd["affected_context_ids"] if x != recd["target_context_id"]); record["proposal_digest"] = sut.context_redefinition_proposal_digest(record["proposal"])
gov_mut("redef-proposal-record", "REDEFINITION_PROPOSAL_RECORD_MISMATCH", proposal_record_mismatch)

def duplicate_replacement(s):
    proposal=s["context_redefinitions"][rid]["proposal"]; proposal["replacements"].append(copy.deepcopy(proposal["replacements"][0])); s["context_redefinitions"][rid]["proposal_digest"]=sut.context_redefinition_proposal_digest(proposal)
gov_mut("redef-replacement-set", "REDEFINITION_REPLACEMENT_SET_MISMATCH", duplicate_replacement)
gov_mut("redef-context-missing", "REDEFINITION_CONTEXT_MISSING", lambda s: s["contexts"].pop(new))
gov_mut("redef-successor-inactive", "REDEFINITION_SUCCESSOR_NOT_ACTIVE", lambda s: s["contexts"][new].__setitem__("lifecycle", "WITHDRAWN"))
gov_mut("redef-alias", "REDEFINITION_ALIAS_DISCONTINUITY", lambda s: s["contexts"][new].__setitem__("alias", s["contexts"][new]["alias"] + "-wrong"))
gov_mut("redef-successor-genesis", "REDEFINITION_SUCCESSOR_GENESIS_MISMATCH", lambda s: s["contexts"][new].__setitem__("genesis_digest", "sha256:" + "2" * 64))

def dependency_mismatch(s):
    target_new=s["context_redefinitions"][rid]["successor_map"][old]
    s["normative_dependencies"].append({"source_context_id":target_new,"target_context_id":s["root_context_id"],"dependency_kind":"NORMATIVE"})
gov_mut("redef-dependency-remap", "REDEFINITION_DEPENDENCY_REMAP_MISMATCH", dependency_mismatch)
gov_mut("redef-withdraw-count", "REDEFINITION_WITHDRAWAL_SET_MISMATCH", lambda s: s["context_redefinitions"][rid]["withdrawal_refs"].pop())
gov_mut("redef-withdraw-missing", "REDEFINITION_WITHDRAWAL_MISSING", lambda s: s["membership_withdrawals"].pop(wid))
gov_mut("redef-withdraw-binding", "REDEFINITION_WITHDRAWAL_BINDING_MISMATCH", lambda s: s["membership_withdrawals"][wid].__setitem__("proposal_digest", "sha256:" + "3" * 64))

# Voluntary-exit record takes the other mode branch.
wd_done = accepted("POS-023"); vwid = next(iter(wd_done["membership_withdrawals"]))
st=copy.deepcopy(wd_done); st["membership_withdrawals"][vwid]["proposal_digest"]="sha256:"+"4"*64
expect_seed("withdraw-voluntary-mode-fields", "WITHDRAWAL_MODE_BINDING_MISMATCH", lambda: sut._validate_governance_records(st))

# Dependency validator branches.
dep_state = copy.deepcopy(gov_state); edge = copy.deepcopy(dep_state["normative_dependencies"][0]); dep_state["normative_dependencies"].append(edge)
expect_seed("dependency-duplicate", "DEPENDENCY_DUPLICATE", lambda: sut._validate_normative_dependencies(dep_state))
dep_state = copy.deepcopy(gov_state); edge = dep_state["normative_dependencies"][0]; edge["target_context_id"] = edge["source_context_id"]
expect_seed("dependency-self", "DEPENDENCY_SELF_REFERENCE", lambda: sut._validate_normative_dependencies(dep_state))
dep_state = copy.deepcopy(gov_state); dep_state["normative_dependencies"][0]["target_context_id"] = "ctx:missing"
expect_seed("dependency-unknown-state", "DEPENDENCY_CONTEXT_UNKNOWN", lambda: sut._validate_normative_dependencies(dep_state))

summary={"suite":"branch-aware security guard suite","checks_total":len(checks),"checks_passed":sum(c["pass"] for c in checks),"failed":[c for c in checks if not c["pass"]]}
if "--no-write" not in sys.argv:
    (ROOT/"validation"/"branch_suite_results.json").write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:summary[k] for k in ("checks_total","checks_passed")},indent=2))
raise SystemExit(0 if not summary["failed"] else 1)
