from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from pathlib import Path
from collections import defaultdict, deque
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

VERSION = "0.1-rc11"
SEED_SEMANTICS_ID = "aset-seed:0.1-rc11"
IMPLEMENTATION_VERSION = "0.1-rc12"
DIGEST_PREFIX = "sha256:"

READINESS_KINDS = {"READINESS_EXECUTE", "READINESS_ACCEPT_RESPONSIBILITY"}
DECISION_CAPABILITY = {
    "ISSUE_PERMIT": "ISSUE_PERMIT",
    "CONFIRM_OUTCOME": "CONFIRM_OUTCOME",
        "SUSPEND_GUARANTEE": "SUSPEND_GUARANTEE",
    "TERMINATE_CONTEXT": "TERMINATE_CONTEXT",
    "TRANSFER_AUTHORITY": "TRANSFER_AUTHORITY",
}
TERMINAL_PERMIT_STATES = {
    "SATISFIED", "EXHAUSTED", "EXPIRED", "REVOKED", "TERMINATED_WITH_CONTEXT", "UNRESOLVED",
    "ATTENUATED",
}
NEGATIVE_COMPLETION_STATES = {"EXHAUSTED", "EXPIRED"}


class SeedError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


_SCHEMA_VALIDATORS: dict[str, Draft202012Validator] | None = None


def _schema_validators() -> dict[str, Draft202012Validator]:
    global _SCHEMA_VALIDATORS
    if _SCHEMA_VALIDATORS is not None:
        return _SCHEMA_VALIDATORS
    schema_dir = Path(__file__).resolve().parent / "schemas"
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(schema_dir.glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        schemas[path.name] = schema
        resources.append((schema["$id"], Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)
    _SCHEMA_VALIDATORS = {
        name: Draft202012Validator(schema, registry=registry)
        for name, schema in schemas.items()
    }
    return _SCHEMA_VALIDATORS


def _validate_schema(name: str, instance: Any, code: str) -> None:
    validator = _schema_validators()[name]
    errors = sorted(validator.iter_errors(instance), key=lambda e: (list(e.absolute_path), e.message))
    if errors:
        raise SeedError(code)


def validate_transition(transition: dict[str, Any]) -> None:
    """Validate a transition against the strict public wire schema."""
    _validate_schema("transition.schema.json", transition, "TRANSITION_SCHEMA_INVALID")


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return value
    if isinstance(value, float):
        raise SeedError("FLOAT_FORBIDDEN")
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise SeedError("NON_STRING_KEY")
            nkey = unicodedata.normalize("NFC", key)
            if nkey in out:
                raise SeedError("NORMALIZED_KEY_COLLISION")
            out[nkey] = _normalize(item)
        return out
    raise SeedError("UNSUPPORTED_CANONICAL_TYPE")


def canonical_bytes(value: Any) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def domain_digest(domain: str, value: Any) -> str:
    payload = canonical_bytes(value)
    framed = domain.encode("ascii") + b"\x00" + len(payload).to_bytes(8, "big") + payload
    return DIGEST_PREFIX + hashlib.sha256(framed).hexdigest()


def _hex_id(prefix: str, digest: str) -> str:
    if not digest.startswith(DIGEST_PREFIX):
        raise SeedError("DIGEST_FORMAT")
    return prefix + digest[len(DIGEST_PREFIX):]


def artifact_id(kind: str, transition_id: str) -> str:
    return _hex_id(kind + ":", domain_digest("ASET/ArtifactID/v1", {"kind": kind, "transition_id": transition_id}))


def scope_digest(scope: Iterable[str]) -> str:
    return domain_digest("ASET/Scope/v1", sorted(set(scope)))


def permit_terms_digest(
    delegate_principal_id: str,
    task_digest: str,
    scope: Iterable[str],
    success_predicate_digest: str,
    max_attempts: int,
    validity_end_ordinal: int,
    caveats: dict[str, Any],
) -> str:
    return domain_digest("ASET/PermitTerms/v1", {
        "delegate_principal_id": delegate_principal_id,
        "task_digest": task_digest,
        "scope": sorted(set(scope)),
        "success_predicate_digest": success_predicate_digest,
        "max_attempts": max_attempts,
        "stop_on_positive": True,
        "validity_end_ordinal": validity_end_ordinal,
        "caveats": copy.deepcopy(caveats),
    })


def constitution_digest(constitution: dict[str, Any]) -> str:
    return domain_digest("ASET/Constitution/v1", constitution)


def root_genesis_material(genesis: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": genesis["schema_version"],
        "seed_semantics_id": genesis["seed_semantics_id"],
        "constitution_digest": constitution_digest(genesis["constitution"]),
        "external_anchor_digest": genesis["external_anchor_digest"],
        "root_context_nonce": genesis["root_context_nonce"],
        "bootstrap_policy": genesis["bootstrap_policy"],
    }


def compute_root_genesis_digest(genesis: dict[str, Any]) -> str:
    return domain_digest("ASET/RootGenesis/v1", root_genesis_material(genesis))


def compute_context_id(parent_context_id: str | None, context_genesis_digest: str) -> str:
    return _hex_id("ctx:", domain_digest(
        "ASET/ContextID/v1",
        {"parent_context_id": parent_context_id, "context_genesis_digest": context_genesis_digest},
    ))


def compute_trust_space_id(seed_semantics_id: str, root_genesis_digest: str, external_anchor_digest: str) -> str:
    return _hex_id("ts:", domain_digest(
        "ASET/TrustSpaceID/v1",
        {
            "seed_semantics_id": seed_semantics_id,
            "root_genesis_digest": root_genesis_digest,
            "external_anchor_digest": external_anchor_digest,
        },
    ))


def member_genesis_digest(payload: dict[str, Any]) -> str:
    material = copy.deepcopy(payload)
    material.pop("expected_new_context_id", None)
    return domain_digest("ASET/MemberContextGenesis/v1", material)


def context_redefinition_proposal_digest(proposal: dict[str, Any]) -> str:
    return domain_digest("ASET/ContextRedefinitionProposal/v1", proposal)


def transition_digest(transition: dict[str, Any]) -> str:
    material = copy.deepcopy(transition)
    material.pop("transition_id", None)
    return domain_digest("ASET/Transition/v1", material)


def compute_transition_id(transition: dict[str, Any]) -> str:
    return _hex_id("tx:", transition_digest(transition))


def compute_state_root(state: dict[str, Any]) -> str:
    material = copy.deepcopy(state)
    material.pop("current_state_root", None)
    return domain_digest("ASET/TrustSpaceState/v1", material)


def _authority_key(binding: dict[str, Any]) -> tuple[str, str, str]:
    # Authority epoch is provenance, not part of the exclusivity key.
    return (
        binding["context_id"],
        binding["capability_kind"],
        binding["scope_digest"],
    )


def _authority_id(binding: dict[str, Any]) -> str:
    return _hex_id("auth:", domain_digest("ASET/AuthorityBinding/v1", {
        "context_id": binding["context_id"],
        "capability_kind": binding["capability_kind"],
        "scope_digest": binding["scope_digest"],
        "holder_principal_id": binding["holder_principal_id"],
        "authority_epoch": binding["authority_epoch"],
        "grant_provenance": binding["grant_provenance"],
    }))


def _binding_from_spec(context_id: str, spec: dict[str, Any], provenance: str, epoch: int = 0) -> dict[str, Any]:
    scope = sorted(set(spec["scope"]))
    binding = {
        "authority_id": "",
        "context_id": context_id,
        "capability_kind": spec["capability_kind"],
        "scope": scope,
        "scope_digest": scope_digest(scope),
        "holder_principal_id": spec["holder_principal_id"],
        "authority_epoch": epoch,
        "status": "ACTIVE",
        "grant_provenance": provenance,
    }
    binding["authority_id"] = _authority_id(binding)
    return binding


def _active_authorities(state: dict[str, Any], context_id: str, capability: str, holder: str) -> list[dict[str, Any]]:
    return [
        a for a in state["authorities"].values()
        if a["status"] == "ACTIVE"
        and a["context_id"] == context_id
        and a["capability_kind"] == capability
        and a["holder_principal_id"] == holder
    ]


def has_authority(
    state: dict[str, Any], context_id: str, capability: str, holder: str, required_scope: Iterable[str] | None = None
) -> bool:
    required = set(required_scope or [])
    matches = _active_authorities(state, context_id, capability, holder)
    for binding in matches:
        scope = set(binding["scope"])
        if "*" in scope or required.issubset(scope):
            return True
    return False


def _require_authority(
    state: dict[str, Any], transition: dict[str, Any], capability: str, required_scope: Iterable[str] | None = None
) -> None:
    actor = transition["authn"]["signer_principal_id"]
    if not has_authority(state, transition["context_id"], capability, actor, required_scope):
        raise SeedError("AUTHORITY_MISSING")


def _context_descendants(
    state: dict[str, Any], context_id: str, *, active_only: bool = False
) -> set[str]:
    children: dict[str, list[str]] = defaultdict(list)
    for cid, context in state["contexts"].items():
        parent = context["parent_context_id"]
        if parent is None:
            continue
        if active_only and context["lifecycle"] != "ACTIVE":
            continue
        children[parent].append(cid)
    result: set[str] = set()
    queue = deque(children.get(context_id, []))
    while queue:
        current = queue.popleft()
        if current in result:
            continue
        result.add(current)
        queue.extend(children.get(current, []))
    return result


def _direct_child_owner(state: dict[str, Any], parent_context_id: str, context_id: str) -> str | None:
    current = context_id
    while current in state["contexts"]:
        parent = state["contexts"][current]["parent_context_id"]
        if parent == parent_context_id:
            return current
        if parent is None:
            return None
        current = parent
    return None


def compute_affected_sibling_set(
    state: dict[str, Any], parent_context_id: str, target_context_id: str
) -> list[str]:
    parent = state["contexts"].get(parent_context_id)
    target = state["contexts"].get(target_context_id)
    if parent is None or target is None:
        raise SeedError("CONTEXT_UNKNOWN")
    if parent["lifecycle"] != "ACTIVE" or target["lifecycle"] != "ACTIVE":
        raise SeedError("AFFECTED_CONTEXT_INACTIVE")
    if target["parent_context_id"] != parent_context_id:
        raise SeedError("TARGET_NOT_DIRECT_CHILD")
    direct_live = {
        cid for cid, context in state["contexts"].items()
        if context["parent_context_id"] == parent_context_id and context["lifecycle"] == "ACTIVE"
    }
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in state["normative_dependencies"]:
        if edge["dependency_kind"] != "NORMATIVE":
            continue
        source = edge["source_context_id"]
        target_ref = edge["target_context_id"]
        if state["contexts"].get(source, {}).get("lifecycle") != "ACTIVE":
            continue
        if state["contexts"].get(target_ref, {}).get("lifecycle") != "ACTIVE":
            continue
        source_owner = _direct_child_owner(state, parent_context_id, source)
        target_owner = _direct_child_owner(state, parent_context_id, target_ref)
        if source_owner in direct_live and target_owner in direct_live and source_owner != target_owner:
            reverse[target_owner].add(source_owner)
    affected = {target_context_id}
    queue = deque([target_context_id])
    while queue:
        current = queue.popleft()
        for source in sorted(reverse.get(current, set())):
            if source not in affected:
                affected.add(source)
                queue.append(source)
    return sorted(affected)

def _path_is_immune(path: str, immunities: list[str]) -> bool:
    for pattern in immunities:
        if pattern.endswith("/*") and path.startswith(pattern[:-1]):
            return True
        if path == pattern:
            return True
    return False


def _validate_context_tree(state: dict[str, Any]) -> None:
    contexts = state["contexts"]
    root = state["root_context_id"]
    if root not in contexts:
        raise SeedError("ROOT_CONTEXT_MISSING")
    if contexts[root]["parent_context_id"] is not None:
        raise SeedError("ROOT_PARENT_FORBIDDEN")
    roots = [cid for cid, c in contexts.items() if c["parent_context_id"] is None]
    if roots != [root]:
        raise SeedError("MULTIPLE_ROOT_CONTEXTS")
    for cid, context in contexts.items():
        if context["context_id"] != cid:
            raise SeedError("CONTEXT_MAP_KEY_MISMATCH")
        if compute_context_id(context["parent_context_id"], context["genesis_digest"]) != cid:
            raise SeedError("CONTEXT_ID_MISMATCH")
        parent = context["parent_context_id"]
        if parent is not None and parent not in contexts:
            raise SeedError("CONTEXT_PARENT_MISSING")
    for cid in contexts:
        seen: set[str] = set()
        current: str | None = cid
        while current is not None:
            if current in seen:
                raise SeedError("CONTEXT_CYCLE")
            seen.add(current)
            current = contexts[current]["parent_context_id"]



def _validate_normative_dependencies(state: dict[str, Any]) -> None:
    seen: set[tuple[str, str, str]] = set()
    for edge in state["normative_dependencies"]:
        source = edge["source_context_id"]
        target = edge["target_context_id"]
        kind = edge["dependency_kind"]
        key = (source, target, kind)
        if key in seen:
            raise SeedError("DEPENDENCY_DUPLICATE")
        seen.add(key)
        if source == target:
            raise SeedError("DEPENDENCY_SELF_REFERENCE")
        if source not in state["contexts"] or target not in state["contexts"]:
            raise SeedError("DEPENDENCY_CONTEXT_UNKNOWN")
        if kind == "NORMATIVE" and (
            state["contexts"][source]["lifecycle"] != "ACTIVE"
            or state["contexts"][target]["lifecycle"] != "ACTIVE"
        ):
            raise SeedError("NORMATIVE_DEPENDENCY_CONTEXT_INACTIVE")


def _scopes_overlap(left: Iterable[str], right: Iterable[str]) -> bool:
    a, b = set(left), set(right)
    return "*" in a or "*" in b or bool(a & b)


def _validate_authority_uniqueness(state: dict[str, Any]) -> None:
    active: list[dict[str, Any]] = []
    for aid, binding in state["authorities"].items():
        if binding["authority_id"] != aid:
            raise SeedError("AUTHORITY_MAP_KEY_MISMATCH")
        if binding["scope_digest"] != scope_digest(binding["scope"]):
            raise SeedError("AUTHORITY_SCOPE_DIGEST_MISMATCH")
        if _authority_id(binding) != aid:
            raise SeedError("AUTHORITY_ID_MISMATCH")
        if binding["context_id"] not in state["contexts"]:
            raise SeedError("AUTHORITY_CONTEXT_MISSING")
        if binding["status"] == "ACTIVE":
            for other in active:
                if (
                    other["context_id"] == binding["context_id"]
                    and other["capability_kind"] == binding["capability_kind"]
                    and _scopes_overlap(other["scope"], binding["scope"])
                ):
                    raise SeedError("AUTHORITY_SCOPE_OVERLAP_ACTIVE")
            active.append(binding)

def _validate_artifact_maps(state: dict[str, Any]) -> None:
    map_ids = {
        "decisions": "decision_id",
        "permits": "permit_id",
        "execution_intents": "execution_intent_id",
        "permit_use_receipts": "receipt_id",
        "observations": "observation_id",
        "verifications": "verification_id",
        "outcomes": "outcome_id",
        "exports": "export_id",
        "imports": "import_id",
        "reconciliations": "reconciliation_id",
        "membership_withdrawals": "withdrawal_id",
        "context_redefinitions": "redefinition_id",
        "corrections": "correction_id",
    }
    for map_name, id_name in map_ids.items():
        for key, value in state[map_name].items():
            if value[id_name] != key:
                raise SeedError("ARTIFACT_MAP_KEY_MISMATCH")
            if value["context_id"] not in state["contexts"]:
                raise SeedError("ARTIFACT_CONTEXT_MISSING")


def _validate_permit_lineage(state: dict[str, Any]) -> None:
    receipts_by_permit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    children_by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in state["permit_use_receipts"].values():
        permit_id = receipt["permit_ref"]
        if permit_id not in state["permits"]:
            raise SeedError("RECEIPT_PERMIT_MISSING")
        receipts_by_permit[permit_id].append(receipt)
        intent = state["execution_intents"].get(receipt["execution_intent_ref"])
        if intent is None or intent["permit_ref"] != permit_id:
            raise SeedError("RECEIPT_INTENT_MISMATCH")
    for permit in state["permits"].values():
        if permit["parent_permit_ref"] is not None:
            children_by_parent[permit["parent_permit_ref"]].append(permit)
    for permit_id, permit in state["permits"].items():
        if permit["scope_digest"] != scope_digest(permit["scope"]):
            raise SeedError("PERMIT_SCOPE_DIGEST_MISMATCH")
        if permit["success_predicate_digest"] not in set(state["constitution"]["body"]["rules"].values()):
            raise SeedError("PERMIT_SUCCESS_PREDICATE_UNRECOGNIZED")
        readiness = state["decisions"].get(permit["readiness_ref"])
        if readiness is None or readiness["decision_kind"] not in READINESS_KINDS:
            raise SeedError("PERMIT_READINESS_MISSING")
        if readiness["context_id"] != permit["context_id"] or readiness["subject_principal_id"] != permit["delegate_principal_id"]:
            raise SeedError("PERMIT_READINESS_BINDING_MISMATCH")
        expected_terms = permit_terms_digest(
            permit["delegate_principal_id"], permit["task_digest"], permit["scope"],
            permit["success_predicate_digest"], permit["max_attempts"],
            permit["validity_end_ordinal"], permit["caveats"],
        )
        if readiness["conditions_digest"] != expected_terms:
            raise SeedError("PERMIT_READINESS_TERMS_MISMATCH")
        if permit["parent_permit_ref"] is None:
            decision = state["decisions"].get(permit["decision_ref"])
            if decision is None or decision["decision_kind"] != "ISSUE_PERMIT":
                raise SeedError("PERMIT_DECISION_MISSING")
            if decision["context_id"] != permit["context_id"] or decision["subject_principal_id"] != permit["delegate_principal_id"]:
                raise SeedError("PERMIT_DECISION_BINDING_MISMATCH")
            if decision["conditions_digest"] != expected_terms or decision["related_ref"] != permit["readiness_ref"]:
                raise SeedError("PERMIT_DECISION_TERMS_MISMATCH")
        else:
            parent = state["permits"].get(permit["parent_permit_ref"])
            if parent is None or parent["context_id"] != permit["context_id"]:
                raise SeedError("PARENT_PERMIT_LINEAGE_MISSING")
            if not set(permit["scope"]).issubset(set(parent["scope"])):
                raise SeedError("PERMIT_SCOPE_ESCALATION")
            if permit["max_attempts"] > parent["max_attempts"] - parent["attempts_used"]:
                raise SeedError("PERMIT_ATTEMPT_ESCALATION")
            if permit["validity_end_ordinal"] > parent["validity_end_ordinal"]:
                raise SeedError("PERMIT_VALIDITY_ESCALATION")
            for key, value in parent["caveats"].items():
                if permit["caveats"].get(key) != value:
                    raise SeedError("PERMIT_CAVEAT_WEAKENED")
        receipts = sorted(receipts_by_permit.get(permit_id, []), key=lambda r: r["attempt_index"])
        expected_indices = list(range(1, len(receipts) + 1))
        if [r["attempt_index"] for r in receipts] != expected_indices:
            raise SeedError("ATTEMPT_INDEX_GAP")
        if permit["attempts_used"] != len(receipts):
            raise SeedError("ATTEMPT_COUNTER_MISMATCH")
        if permit["attempts_used"] > permit["max_attempts"]:
            raise SeedError("ATTEMPT_LIMIT_EXCEEDED")
        if permit["final_outcome_ref"] is not None:
            outcome = state["outcomes"].get(permit["final_outcome_ref"])
            if outcome is None or outcome["permit_ref"] != permit_id:
                raise SeedError("PERMIT_FINAL_OUTCOME_MISMATCH")
    for parent_id, children in children_by_parent.items():
        if len(children) != 1:
            raise SeedError("PERMIT_ATTENUATION_NOT_LINEAR")
        parent = state["permits"].get(parent_id)
        if parent is None or parent["status"] != "ATTENUATED":
            raise SeedError("PARENT_PERMIT_NOT_ATTENUATED")
    for permit_id, permit in state["permits"].items():
        if permit["status"] == "ATTENUATED" and permit_id not in children_by_parent:
            raise SeedError("ATTENUATED_PERMIT_CHILD_MISSING")
    for submission_id, index in state["submission_index"].items():
        receipt = state["permit_use_receipts"].get(index["receipt_ref"])
        if receipt is None or receipt["submission_id"] != submission_id:
            raise SeedError("SUBMISSION_INDEX_MISMATCH")

def _validate_evidence_lineage(state: dict[str, Any]) -> None:
    for observation in state["observations"].values():
        receipt = state["permit_use_receipts"].get(observation["receipt_ref"])
        permit = state["permits"].get(observation["permit_ref"])
        if receipt is None or permit is None or receipt["permit_ref"] != observation["permit_ref"]:
            raise SeedError("OBSERVATION_RECEIPT_MISMATCH")
        if permit["context_id"] != observation["context_id"]:
            raise SeedError("OBSERVATION_CONTEXT_MISMATCH")
    recognized_policies = set(state["constitution"]["body"]["rules"].values())
    for verification in state["verifications"].values():
        observation = state["observations"].get(verification["observation_ref"])
        receipt = state["permit_use_receipts"].get(verification["receipt_ref"])
        if observation is None or receipt is None:
            raise SeedError("VERIFICATION_LINEAGE_MISSING")
        if observation["permit_ref"] != verification["permit_ref"] or receipt["permit_ref"] != verification["permit_ref"]:
            raise SeedError("VERIFICATION_PERMIT_MISMATCH")
        if observation["context_id"] != verification["context_id"]:
            raise SeedError("VERIFICATION_CONTEXT_MISMATCH")
        if verification["policy_digest"] not in recognized_policies:
            raise SeedError("VERIFICATION_POLICY_UNRECOGNIZED")
        permit = state["permits"].get(verification["permit_ref"])
        if permit is None or verification["policy_digest"] != permit["success_predicate_digest"]:
            raise SeedError("VERIFICATION_POLICY_PERMIT_MISMATCH")
    for outcome in state["outcomes"].values():
        permit = state["permits"].get(outcome["permit_ref"])
        if permit is None or permit["context_id"] != outcome["context_id"]:
            raise SeedError("OUTCOME_PERMIT_MISMATCH")
        effective_refs = sorted(
            verification["verification_id"]
            for verification in _effective_verifications_for_permit(state, outcome["permit_ref"])
            if verification["status"] == "PASS"
        )
        if sorted(outcome["verification_refs"]) != effective_refs:
            raise SeedError("OUTCOME_VERIFICATION_SET_INCOMPLETE")
        for verification_ref in outcome["verification_refs"]:
            verification = state["verifications"].get(verification_ref)
            if verification is None:
                raise SeedError("OUTCOME_VERIFICATION_MISSING")
            if verification["permit_ref"] != outcome["permit_ref"] or verification["context_id"] != outcome["context_id"]:
                raise SeedError("OUTCOME_VERIFICATION_MISMATCH")
    for export in state["exports"].values():
        if export["outcome_ref"] is not None:
            outcome = state["outcomes"].get(export["outcome_ref"])
            if outcome is None or outcome["context_id"] != export["context_id"]:
                raise SeedError("EXPORT_OUTCOME_MISMATCH")
        expected_root = domain_digest("ASET/ExportCommit/v1", {
            "previous_export_root": export["previous_export_root"],
            "claim_digest": export["claim_digest"],
            "outcome_ref": export["outcome_ref"],
            "transition_ref": export["transition_ref"],
        })
        if export["source_export_root"] != expected_root:
            raise SeedError("EXPORT_COMMIT_ROOT_MISMATCH")
    for record in state["imports"].values():
        export = state["exports"].get(record["export_ref"])
        if export is None or export["claim_digest"] != record["claim_digest"]:
            raise SeedError("IMPORT_EXPORT_MISMATCH")
    for correction in state["corrections"].values():
        if correction["target_type"] != "VERIFICATION":
            raise SeedError("CORRECTION_TARGET_TYPE_UNSUPPORTED")
        target_map = state["verifications"]
        target = target_map.get(correction["target_ref"])
        if target is None or target["context_id"] != correction["context_id"]:
            raise SeedError("CORRECTION_TARGET_MISMATCH")
        if correction["replacement_ref"] is not None:
            replacement = target_map.get(correction["replacement_ref"])
            if replacement is None or replacement["context_id"] != correction["context_id"]:
                raise SeedError("CORRECTION_REPLACEMENT_MISMATCH")

def _validate_transition_records(state: dict[str, Any]) -> None:
    if state["accepted_transition_count"] != len(state["transition_records"]):
        raise SeedError("TRANSITION_COUNT_MISMATCH")
    artifact_owner: dict[str, str] = {}
    for txid, record in state["transition_records"].items():
        if txid != record["transition_id"]:
            raise SeedError("TRANSITION_MAP_KEY_MISMATCH")
        for artifact in record.get("artifact_refs", []):
            if artifact in artifact_owner:
                raise SeedError("ARTIFACT_CREATOR_DUPLICATE")
            artifact_owner[artifact] = txid
    for record in state["transition_records"].values():
        derived_parents: set[str] = set()
        for basis_ref in record.get("causal_basis_refs", []):
            creator = artifact_owner.get(basis_ref)
            if creator is not None:
                derived_parents.add(creator)
        if sorted(record["causal_parents"]) != sorted(derived_parents):
            raise SeedError("CAUSAL_RECORD_BASIS_MISMATCH")
        for parent in record["causal_parents"]:
            if parent not in state["transition_records"]:
                raise SeedError("CAUSAL_PARENT_MISSING")
            if state["transition_records"][parent]["accepted_index"] >= record["accepted_index"]:
                raise SeedError("CAUSAL_ORDER_INVALID")
    for cid, context in state["contexts"].items():
        records = sorted(
            (r for r in state["transition_records"].values() if r["context_id"] == cid),
            key=lambda r: r["accepted_index"],
        )
        if context["local_ordinal"] != len(records):
            raise SeedError("LOCAL_ORDINAL_MISMATCH")
        internal = (
            domain_digest("ASET/EmptyRootContext/v1", {})
            if context["context_kind"] == "ROOT"
            else domain_digest("ASET/EmptyContextState/v1", {"context_id": cid})
        )
        for record in records:
            internal = domain_digest("ASET/ContextInternalTransition/v1", {
                "previous_internal_state_root": internal,
                "transition_id": record["transition_id"],
                "transition_digest": record["transition_digest"],
            })
        if context["internal_state_root"] != internal:
            raise SeedError("CONTEXT_INTERNAL_STATE_ROOT_MISMATCH")

def _validate_governance_records(state: dict[str, Any]) -> None:
    for wid, record in state["membership_withdrawals"].items():
        if record["withdrawal_id"] != wid or record["context_id"] not in state["contexts"]:
            raise SeedError("WITHDRAWAL_RECORD_INVALID")
        if record["parent_context_id"] != state["contexts"][record["context_id"]]["parent_context_id"]:
            raise SeedError("WITHDRAWAL_PARENT_MISMATCH")
        if record["transition_ref"] not in state["transition_records"]:
            raise SeedError("WITHDRAWAL_TRANSITION_MISSING")
        if not record["authorization_proof_digest"].startswith(DIGEST_PREFIX):
            raise SeedError("WITHDRAWAL_PROOF_FORMAT")
        if record["mode"] == "VOLUNTARY_EXIT":
            if record["proposal_digest"] is not None or record["reason_digest"] is None:
                raise SeedError("WITHDRAWAL_MODE_BINDING_MISMATCH")
        elif record["mode"] == "REDEFINITION":
            if record["proposal_digest"] is None or record["reason_digest"] is not None:
                raise SeedError("WITHDRAWAL_MODE_BINDING_MISMATCH")
        else:
            raise SeedError("WITHDRAWAL_MODE_UNSUPPORTED")
        for cid in record["withdrawn_context_ids"]:
            if cid not in state["contexts"] or state["contexts"][cid]["lifecycle"] == "ACTIVE":
                raise SeedError("WITHDRAWAL_LIFECYCLE_MISMATCH")
    for rid, record in state["context_redefinitions"].items():
        if record["redefinition_id"] != rid or record["context_id"] not in state["contexts"]:
            raise SeedError("REDEFINITION_RECORD_INVALID")
        proposal = record["proposal"]
        if context_redefinition_proposal_digest(proposal) != record["proposal_digest"]:
            raise SeedError("REDEFINITION_PROPOSAL_DIGEST_MISMATCH")
        if proposal["parent_context_id"] != record["context_id"] or proposal["target_context_id"] != record["target_context_id"]:
            raise SeedError("REDEFINITION_PROPOSAL_RECORD_MISMATCH")
        if set(record["affected_context_ids"]) != set(record["successor_map"]):
            raise SeedError("REDEFINITION_MAP_INCOMPLETE")
        replacement_by_old = {item["old_context_id"]: item for item in proposal["replacements"]}
        if len(replacement_by_old) != len(proposal["replacements"]) or set(replacement_by_old) != set(record["affected_context_ids"]):
            raise SeedError("REDEFINITION_REPLACEMENT_SET_MISMATCH")
        for old, new in record["successor_map"].items():
            if old not in state["contexts"] or new not in state["contexts"]:
                raise SeedError("REDEFINITION_CONTEXT_MISSING")
            old_context = state["contexts"][old]
            new_context = state["contexts"][new]
            if old_context["lifecycle"] != "SUPERSEDED":
                raise SeedError("REDEFINITION_OLD_NOT_SUPERSEDED")
            if new_context["lifecycle"] != "ACTIVE":
                raise SeedError("REDEFINITION_SUCCESSOR_NOT_ACTIVE")
            if old_context["alias"] != new_context["alias"]:
                raise SeedError("REDEFINITION_ALIAS_DISCONTINUITY")
            item = replacement_by_old[old]
            member_payload = {
                "parent_context_id": record["context_id"],
                "member_principal_id": old_context["member_principal_id"],
                "context_kind": old_context["context_kind"],
                "context_genesis_nonce": item["context_genesis_nonce"],
                "local_alias": old_context["alias"].rsplit("/", 1)[-1],
                "initial_authorities": copy.deepcopy(item["initial_authorities"]),
                "depends_on_context_ids": list(item["depends_on_context_ids"]),
            }
            if new_context["genesis_digest"] != member_genesis_digest(member_payload):
                raise SeedError("REDEFINITION_SUCCESSOR_GENESIS_MISMATCH")
            if new != compute_context_id(record["context_id"], new_context["genesis_digest"]):
                raise SeedError("REDEFINITION_SUCCESSOR_ID_MISMATCH")
            expected_targets = {record["successor_map"].get(dep, dep) for dep in item["depends_on_context_ids"]}
            actual_targets = {
                edge["target_context_id"] for edge in state["normative_dependencies"]
                if edge["dependency_kind"] == "NORMATIVE" and edge["source_context_id"] == new
            }
            if actual_targets != expected_targets:
                raise SeedError("REDEFINITION_DEPENDENCY_REMAP_MISMATCH")
        if len(record["withdrawal_refs"]) != len(record["affected_context_ids"]):
            raise SeedError("REDEFINITION_WITHDRAWAL_SET_MISMATCH")
        withdrawals = []
        for ref in record["withdrawal_refs"]:
            withdrawal = state["membership_withdrawals"].get(ref)
            if withdrawal is None:
                raise SeedError("REDEFINITION_WITHDRAWAL_MISSING")
            withdrawals.append(withdrawal)
        if {item["context_id"] for item in withdrawals} != set(record["affected_context_ids"]):
            raise SeedError("REDEFINITION_WITHDRAWAL_SET_MISMATCH")
        for withdrawal in withdrawals:
            if (
                withdrawal["mode"] != "REDEFINITION"
                or withdrawal["proposal_digest"] != record["proposal_digest"]
                or withdrawal["transition_ref"] != record["transition_ref"]
            ):
                raise SeedError("REDEFINITION_WITHDRAWAL_BINDING_MISMATCH")


def validate_state(state: dict[str, Any], verify_root: bool = True) -> None:
    _validate_schema("trust-space-state.schema.json", state, "STATE_SCHEMA_INVALID")
    if state["schema_version"] != VERSION or state["seed_semantics_id"] != SEED_SEMANTICS_ID:
        raise SeedError("STATE_VERSION_MISMATCH")
    if state["constitution"]["digest"] != constitution_digest(state["constitution"]["body"]):
        raise SeedError("CONSTITUTION_DIGEST_MISMATCH")
    expected_ts = compute_trust_space_id(
        state["seed_semantics_id"], state["root_genesis_digest"], state["external_anchor_digest"]
    )
    if state["trust_space_id"] != expected_ts:
        raise SeedError("TRUST_SPACE_ID_MISMATCH")
    _validate_context_tree(state)
    live_contexts = {cid: c for cid, c in state["contexts"].items() if c["lifecycle"] == "ACTIVE"}
    aliases = [context["alias"] for context in live_contexts.values()]
    if len(aliases) != len(set(aliases)):
        raise SeedError("CONTEXT_ALIAS_DUPLICATE")
    expected_aliases = {context["alias"]: cid for cid, context in live_contexts.items()}
    if state["context_aliases"] != expected_aliases:
        raise SeedError("CONTEXT_ALIAS_INDEX_MISMATCH")
    if state["constitution"]["epoch"] != 0:
        raise SeedError("ROOT_CONSTITUTION_IMMUTABLE")
    if state["bootstrap"]["admissions_used"] > state["bootstrap"]["policy"]["max_admissions"]:
        raise SeedError("BOOTSTRAP_ADMISSION_LIMIT")
    if state["bootstrap"]["open"] == (state["bootstrap"]["admissions_used"] >= state["bootstrap"]["policy"]["max_admissions"]):
        raise SeedError("BOOTSTRAP_OPEN_STATE_MISMATCH")
    for context in state["contexts"].values():
        if context["lifecycle"] == "ACTIVE" and context["constitution_epoch"] != state["constitution"]["epoch"]:
            raise SeedError("CONTEXT_CONSTITUTION_EPOCH_MISMATCH")
    _validate_normative_dependencies(state)
    _validate_authority_uniqueness(state)
    for authority in state["authorities"].values():
        if authority["status"] == "ACTIVE" and state["contexts"][authority["context_id"]]["lifecycle"] != "ACTIVE":
            raise SeedError("ACTIVE_AUTHORITY_IN_INACTIVE_CONTEXT")
    for permit in state["permits"].values():
        if permit["status"] == "ACTIVE" and state["contexts"][permit["context_id"]]["lifecycle"] != "ACTIVE":
            raise SeedError("ACTIVE_PERMIT_IN_INACTIVE_CONTEXT")
    _validate_artifact_maps(state)
    _validate_permit_lineage(state)
    _validate_evidence_lineage(state)
    _validate_governance_records(state)
    _validate_transition_records(state)
    if verify_root and state["current_state_root"] != compute_state_root(state):
        raise SeedError("STATE_ROOT_MISMATCH")

def initialize_state(genesis: dict[str, Any]) -> dict[str, Any]:
    _validate_schema("root-genesis.schema.json", genesis, "GENESIS_SCHEMA_INVALID")
    if genesis.get("schema_version") != VERSION:
        raise SeedError("GENESIS_VERSION_MISMATCH")
    if genesis.get("seed_semantics_id") != SEED_SEMANTICS_ID:
        raise SeedError("SEED_SEMANTICS_MISMATCH")
    c_digest = constitution_digest(genesis["constitution"])
    if genesis.get("expected_constitution_digest") != c_digest:
        raise SeedError("CONSTITUTION_DIGEST_MISMATCH")
    g_digest = compute_root_genesis_digest(genesis)
    if genesis.get("expected_root_genesis_digest") != g_digest:
        raise SeedError("ROOT_GENESIS_DIGEST_MISMATCH")
    root_context_id = compute_context_id(None, g_digest)
    if genesis.get("expected_root_context_id") != root_context_id:
        raise SeedError("ROOT_CONTEXT_ID_MISMATCH")
    trust_space_id = compute_trust_space_id(SEED_SEMANTICS_ID, g_digest, genesis["external_anchor_digest"])
    if genesis.get("expected_trust_space_id") != trust_space_id:
        raise SeedError("TRUST_SPACE_ID_MISMATCH")
    root_context = {
        "context_id": root_context_id,
        "parent_context_id": None,
        "context_kind": "ROOT",
        "member_principal_id": None,
        "genesis_digest": g_digest,
        "constitution_epoch": 0,
        "local_ordinal": 0,
        "lifecycle": "ACTIVE",
        "guarantee_status": "CONFIRMED",
        "internal_state_root": domain_digest("ASET/EmptyRootContext/v1", {}),
        "export_root": domain_digest("ASET/EmptyRootExport/v1", {}),
        "last_confirmed_export_root": domain_digest("ASET/EmptyRootExport/v1", {}),
        "alias": "/",
    }
    state: dict[str, Any] = {
        "schema_version": VERSION,
        "seed_semantics_id": SEED_SEMANTICS_ID,
        "trust_space_id": trust_space_id,
        "root_genesis_digest": g_digest,
        "external_anchor_digest": genesis["external_anchor_digest"],
        "root_context_id": root_context_id,
        "constitution": {"epoch": 0, "digest": c_digest, "body": copy.deepcopy(genesis["constitution"])},
        "bootstrap": {
            "open": True,
            "admissions_used": 0,
            "policy": copy.deepcopy(genesis["bootstrap_policy"]),
        },
        "accepted_transition_count": 0,
        "current_state_root": "",
        "contexts": {root_context_id: root_context},
        "context_aliases": {"/": root_context_id},
        "authorities": {},
        "decisions": {},
        "permits": {},
        "execution_intents": {},
        "permit_use_receipts": {},
        "submission_index": {},
        "observations": {},
        "verifications": {},
        "outcomes": {},
        "exports": {},
        "imports": {},
        "reconciliations": {},
        "membership_withdrawals": {},
        "context_redefinitions": {},
        "corrections": {},
        "normative_dependencies": [],
        "transition_records": {},
    }
    state["current_state_root"] = compute_state_root(state)
    validate_state(state)
    return state



def _artifact_creator_transition(state: dict[str, Any], artifact_ref: str | None) -> str | None:
    if artifact_ref is None:
        return None
    for txid, record in state["transition_records"].items():
        if artifact_ref in record.get("artifact_refs", []):
            return txid
    authority = state["authorities"].get(artifact_ref)
    if authority is not None and authority.get("grant_provenance") in state["transition_records"]:
        return authority["grant_provenance"]
    return None


def _causal_basis_refs(transition: dict[str, Any]) -> list[str]:
    p = transition.get("payload", {})
    kind = transition.get("kind")
    refs: set[str] = {transition.get("context_id", "")}
    fields: dict[str, list[str]] = {
        "DECISION": ["related_ref"],
        "PERMIT_ISSUE": ["decision_ref", "readiness_ref"],
        "PERMIT_ATTENUATE": ["parent_permit_ref", "readiness_ref"],
        "PERMIT_USE": ["permit_ref"],
        "OBSERVATION": ["permit_ref", "receipt_ref"],
        "VERIFICATION": ["permit_ref", "receipt_ref", "observation_ref"],
        "OUTCOME": ["permit_ref"],
        "EXPORT": ["outcome_ref"],
        "IMPORT": ["export_ref", "local_permit_ref", "local_receipt_ref"],
        "GUARANTEE_SUSPEND": ["child_context_id"],
        "RECONCILE": ["child_context_id"],
        "MEMBERSHIP_WITHDRAW": [],
        "CONTEXT_REDEFINE": [],
        "CONTEXT_TERMINATE": ["child_context_id", "verification_ref"],
        "CORRECTION": ["target_ref", "replacement_ref"],
        "AUTHORITY_TRANSFER": ["authority_ref", "outcome_ref"],
    }
    for field in fields.get(kind, []):
        value = p.get(field)
        if value is not None:
            refs.add(value)
    if kind == "OUTCOME":
        refs.update(p.get("verification_refs", []))
    if kind == "RECONCILE":
        refs.update(item.get("commit_id") for item in p.get("lineage", []))
    if kind == "CONTEXT_REDEFINE":
        proposal = p.get("proposal", {})
        refs.add(proposal.get("target_context_id"))
        refs.update(item.get("old_context_id") for item in proposal.get("replacements", []))
    refs.discard("")
    refs.discard(None)
    return sorted(refs)


def _required_causal_parents(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    refs: set[str] = set()
    for artifact_ref in _causal_basis_refs(transition):
        txid = _artifact_creator_transition(state, artifact_ref)
        if txid:
            refs.add(txid)
    return sorted(refs)

def _validate_envelope(state: dict[str, Any], transition: dict[str, Any]) -> str:
    validate_state(state)
    _validate_schema("transition.schema.json", transition, "TRANSITION_SCHEMA_INVALID")
    if transition["trust_space_id"] != state["trust_space_id"]:
        raise SeedError("TRUST_SPACE_MISMATCH")
    expected_id = compute_transition_id(transition)
    if transition["transition_id"] != expected_id:
        raise SeedError("TRANSITION_ID_MISMATCH")
    digest = transition_digest(transition)
    existing = state["transition_records"].get(transition["transition_id"])
    if existing is not None:
        if existing["transition_digest"] == digest:
            raise SeedError("IDEMPOTENT_REPLAY")
        raise SeedError("TRANSITION_ID_COLLISION")
    if transition["parent_state_root"] != state["current_state_root"]:
        raise SeedError("STALE_PARENT_STATE_ROOT")
    if transition["constitution_epoch"] != state["constitution"]["epoch"]:
        raise SeedError("CONSTITUTION_EPOCH_MISMATCH")
    context = state["contexts"].get(transition["context_id"])
    if context is None:
        raise SeedError("CONTEXT_UNKNOWN")
    if context["lifecycle"] != "ACTIVE":
        raise SeedError("CONTEXT_NOT_ACTIVE")
    if context["guarantee_status"] == "SUSPENDED" and transition["kind"] != "PARTITION_LOCAL_TRANSITION":
        raise SeedError("SUSPENDED_CONTEXT_COORDINATION_REQUIRED")
    if transition["expected_local_ordinal"] != context["local_ordinal"] + 1:
        raise SeedError("LOCAL_ORDINAL_MISMATCH")
    expected_parents = _required_causal_parents(state, transition)
    if transition["causal_parents"] != expected_parents:
        raise SeedError("CAUSAL_PARENTS_MISMATCH")
    if not transition["authn"]["proof_digest"].startswith(DIGEST_PREFIX):
        raise SeedError("AUTHENTICATION_PROOF_FORMAT")
    return digest

def _record_transition(
    state: dict[str, Any], transition: dict[str, Any], digest: str, artifacts: list[str]
) -> None:
    context = state["contexts"][transition["context_id"]]
    context["internal_state_root"] = domain_digest("ASET/ContextInternalTransition/v1", {
        "previous_internal_state_root": context["internal_state_root"],
        "transition_id": transition["transition_id"],
        "transition_digest": digest,
    })
    context["local_ordinal"] += 1
    state["accepted_transition_count"] += 1
    state["transition_records"][transition["transition_id"]] = {
        "transition_id": transition["transition_id"],
        "transition_digest": digest,
        "context_id": transition["context_id"],
        "kind": transition["kind"],
        "causal_parents": list(transition["causal_parents"]),
        "causal_basis_refs": _causal_basis_refs(transition),
        "artifact_refs": list(artifacts),
        "accepted_index": state["accepted_transition_count"],
    }
    state["current_state_root"] = compute_state_root(state)

def _handle_member_context_genesis(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    payload = transition["payload"]
    parent_id = transition["context_id"]
    if payload["parent_context_id"] != parent_id:
        raise SeedError("PARENT_CONTEXT_MISMATCH")
    signer = transition["authn"]["signer_principal_id"]
    if parent_id == state["root_context_id"]:
        policy = state["bootstrap"]["policy"]
        if not state["bootstrap"]["open"]:
            raise SeedError("BOOTSTRAP_CLOSED")
        if signer != policy["validator_principal_id"]:
            raise SeedError("BOOTSTRAP_VALIDATOR_MISMATCH")
        if payload["context_kind"] not in policy["allowed_context_kinds"]:
            raise SeedError("BOOTSTRAP_CONTEXT_KIND_FORBIDDEN")
        if state["bootstrap"]["admissions_used"] >= policy["max_admissions"]:
            raise SeedError("BOOTSTRAP_ADMISSION_LIMIT")
        allowed = set(policy["allowed_initial_capabilities"])
        if any(a["capability_kind"] not in allowed for a in payload["initial_authorities"]):
            raise SeedError("BOOTSTRAP_CAPABILITY_FORBIDDEN")
    else:
        _require_authority(state, transition, "CREATE_MEMBER_CONTEXT")
    g_digest = member_genesis_digest(payload)
    context_id = compute_context_id(parent_id, g_digest)
    if context_id in state["contexts"]:
        raise SeedError("CONTEXT_ALREADY_EXISTS")
    alias_path = state["contexts"][parent_id]["alias"].rstrip("/") + "/" + payload["local_alias"]
    if alias_path in state["context_aliases"]:
        raise SeedError("CONTEXT_ALIAS_IN_USE")
    context = {
        "context_id": context_id,
        "parent_context_id": parent_id,
        "context_kind": payload["context_kind"],
        "member_principal_id": payload["member_principal_id"],
        "genesis_digest": g_digest,
        "constitution_epoch": state["constitution"]["epoch"],
        "local_ordinal": 0,
        "lifecycle": "ACTIVE",
        "guarantee_status": "CONFIRMED",
        "internal_state_root": domain_digest("ASET/EmptyContextState/v1", {"context_id": context_id}),
        "export_root": domain_digest("ASET/EmptyContextExport/v1", {"context_id": context_id}),
        "last_confirmed_export_root": domain_digest("ASET/EmptyContextExport/v1", {"context_id": context_id}),
        "alias": alias_path,
    }
    state["contexts"][context_id] = context
    state["context_aliases"][alias_path] = context_id
    artifacts = [context_id]
    for spec in payload["initial_authorities"]:
        binding = _binding_from_spec(context_id, spec, transition["transition_id"], 0)
        if binding["authority_id"] in state["authorities"]:
            raise SeedError("AUTHORITY_ALREADY_EXISTS")
        state["authorities"][binding["authority_id"]] = binding
        artifacts.append(binding["authority_id"])
    for target in payload.get("depends_on_context_ids", []):
        if target not in state["contexts"]:
            raise SeedError("DEPENDENCY_CONTEXT_UNKNOWN")
        if state["contexts"][target]["lifecycle"] != "ACTIVE":
            raise SeedError("DEPENDENCY_CONTEXT_INACTIVE")
        if target == context_id:
            raise SeedError("DEPENDENCY_SELF_REFERENCE")
        edge = {
            "source_context_id": context_id,
            "target_context_id": target,
            "dependency_kind": "NORMATIVE",
        }
        if edge not in state["normative_dependencies"]:
            state["normative_dependencies"].append(edge)
    if parent_id == state["root_context_id"]:
        state["bootstrap"]["admissions_used"] += 1
        if state["bootstrap"]["admissions_used"] >= state["bootstrap"]["policy"]["max_admissions"]:
            state["bootstrap"]["open"] = False
    return artifacts


def _handle_decision(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    signer = transition["authn"]["signer_principal_id"]
    if p["decision_kind"] in READINESS_KINDS:
        if signer != p["subject_principal_id"]:
            raise SeedError("READINESS_SUBJECT_MISMATCH")
    else:
        capability = DECISION_CAPABILITY.get(p["decision_kind"])
        if capability is None:
            raise SeedError("DECISION_KIND_UNSUPPORTED")
        _require_authority(state, transition, capability, p["scope"])
    did = artifact_id("dec", transition["transition_id"])
    state["decisions"][did] = {
        "decision_id": did,
        "context_id": transition["context_id"],
        "decision_kind": p["decision_kind"],
        "issuer_principal_id": signer,
        "subject_principal_id": p["subject_principal_id"],
        "scope": sorted(set(p["scope"])),
        "scope_digest": scope_digest(p["scope"]),
        "conditions_digest": p["conditions_digest"],
        "related_ref": p.get("related_ref"),
        "constitution_epoch": state["constitution"]["epoch"],
    }
    return [did]


def _handle_permit_issue(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "ISSUE_PERMIT", p["scope"])
    if p["success_predicate_digest"] not in set(state["constitution"]["body"]["rules"].values()):
        raise SeedError("PERMIT_SUCCESS_PREDICATE_UNRECOGNIZED")
    issue = state["decisions"].get(p["decision_ref"])
    readiness = state["decisions"].get(p["readiness_ref"])
    signer = transition["authn"]["signer_principal_id"]
    if issue is None or issue["decision_kind"] != "ISSUE_PERMIT":
        raise SeedError("ISSUE_DECISION_INVALID")
    if readiness is None or readiness["decision_kind"] not in READINESS_KINDS:
        raise SeedError("READINESS_DECISION_INVALID")
    if issue["context_id"] != transition["context_id"] or readiness["context_id"] != transition["context_id"]:
        raise SeedError("PERMIT_DECISION_CONTEXT_MISMATCH")
    if issue["issuer_principal_id"] != signer:
        raise SeedError("ISSUE_DECISION_ISSUER_MISMATCH")
    if issue["constitution_epoch"] != state["constitution"]["epoch"] or readiness["constitution_epoch"] != state["constitution"]["epoch"]:
        raise SeedError("PERMIT_DECISION_EPOCH_STALE")
    if issue["subject_principal_id"] != p["delegate_principal_id"] or readiness["subject_principal_id"] != p["delegate_principal_id"]:
        raise SeedError("PERMIT_SUBJECT_MISMATCH")
    if readiness["issuer_principal_id"] != p["delegate_principal_id"]:
        raise SeedError("READINESS_DELEGATE_MISMATCH")
    if set(issue["scope"]) != set(p["scope"]) or set(readiness["scope"]) != set(p["scope"]):
        raise SeedError("PERMIT_SCOPE_DECISION_MISMATCH")
    if p["max_attempts"] < 1:
        raise SeedError("MAX_ATTEMPTS_INVALID")
    if p["stop_on_positive"] is not True:
        raise SeedError("STOP_ON_POSITIVE_REQUIRED")
    if p["validity_end_ordinal"] <= state["contexts"][transition["context_id"]]["local_ordinal"]:
        raise SeedError("PERMIT_ALREADY_EXPIRED")
    terms = permit_terms_digest(
        p["delegate_principal_id"], p["task_digest"], p["scope"], p["success_predicate_digest"],
        p["max_attempts"], p["validity_end_ordinal"], p["caveats"],
    )
    if issue["conditions_digest"] != terms or readiness["conditions_digest"] != terms:
        raise SeedError("PERMIT_TERMS_DECISION_MISMATCH")
    if issue["related_ref"] != readiness["decision_id"]:
        raise SeedError("ISSUE_DECISION_READINESS_MISMATCH")
    pid = artifact_id("permit", transition["transition_id"])
    scope = sorted(set(p["scope"]))
    state["permits"][pid] = {
        "permit_id": pid,
        "context_id": transition["context_id"],
        "issuer_principal_id": signer,
        "delegate_principal_id": p["delegate_principal_id"],
        "decision_ref": p["decision_ref"],
        "readiness_ref": p["readiness_ref"],
        "task_digest": p["task_digest"],
        "scope": scope,
        "scope_digest": scope_digest(scope),
        "success_predicate_digest": p["success_predicate_digest"],
        "max_attempts": p["max_attempts"],
        "attempts_used": 0,
        "stop_on_positive": p["stop_on_positive"],
        "validity_end_ordinal": p["validity_end_ordinal"],
        "caveats": copy.deepcopy(p["caveats"]),
        "status": "ACTIVE",
        "final_outcome_ref": None,
        "parent_permit_ref": None,
        "constitution_epoch": state["constitution"]["epoch"],
    }
    return [pid]


def _handle_permit_attenuate(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    parent = state["permits"].get(p["parent_permit_ref"])
    if parent is None:
        raise SeedError("PARENT_PERMIT_UNKNOWN")
    if parent["context_id"] != transition["context_id"]:
        raise SeedError("PARENT_PERMIT_CONTEXT_MISMATCH")
    if parent["status"] != "ACTIVE" or parent["final_outcome_ref"] is not None:
        raise SeedError("PARENT_PERMIT_NOT_ACTIVE")
    signer = transition["authn"]["signer_principal_id"]
    if signer not in {parent["delegate_principal_id"], parent["issuer_principal_id"]}:
        raise SeedError("PERMIT_ATTENUATOR_UNAUTHORIZED")
    child_scope = set(p["scope"])
    if not child_scope.issubset(set(parent["scope"])):
        raise SeedError("PERMIT_SCOPE_ESCALATION")
    remaining = parent["max_attempts"] - parent["attempts_used"]
    if p["max_attempts"] > remaining:
        raise SeedError("PERMIT_ATTEMPT_ESCALATION")
    if p["validity_end_ordinal"] > parent["validity_end_ordinal"]:
        raise SeedError("PERMIT_VALIDITY_ESCALATION")
    for key, value in parent["caveats"].items():
        if p["caveats"].get(key) != value:
            raise SeedError("PERMIT_CAVEAT_WEAKENED")
    readiness = state["decisions"].get(p["readiness_ref"])
    if readiness is None or readiness["decision_kind"] not in READINESS_KINDS:
        raise SeedError("READINESS_DECISION_INVALID")
    if readiness["context_id"] != transition["context_id"] or readiness["issuer_principal_id"] != p["delegate_principal_id"]:
        raise SeedError("READINESS_DELEGATE_MISMATCH")
    terms = permit_terms_digest(
        p["delegate_principal_id"], parent["task_digest"], p["scope"], parent["success_predicate_digest"],
        p["max_attempts"], p["validity_end_ordinal"], p["caveats"],
    )
    if readiness["conditions_digest"] != terms or set(readiness["scope"]) != child_scope:
        raise SeedError("PERMIT_READINESS_TERMS_MISMATCH")
    pid = artifact_id("permit", transition["transition_id"])
    scope = sorted(child_scope)
    state["permits"][pid] = {
        "permit_id": pid,
        "context_id": transition["context_id"],
        "issuer_principal_id": signer,
        "delegate_principal_id": p["delegate_principal_id"],
        "decision_ref": parent["decision_ref"],
        "readiness_ref": readiness["decision_id"],
        "task_digest": parent["task_digest"],
        "scope": scope,
        "scope_digest": scope_digest(scope),
        "success_predicate_digest": parent["success_predicate_digest"],
        "max_attempts": p["max_attempts"],
        "attempts_used": 0,
        "stop_on_positive": True,
        "validity_end_ordinal": p["validity_end_ordinal"],
        "caveats": copy.deepcopy(p["caveats"]),
        "status": "ACTIVE",
        "final_outcome_ref": None,
        "parent_permit_ref": parent["permit_id"],
        "constitution_epoch": state["constitution"]["epoch"],
    }
    parent["status"] = "ATTENUATED"
    return [pid]

def _handle_permit_use(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    permit = state["permits"].get(p["permit_ref"])
    if permit is None:
        raise SeedError("PERMIT_UNKNOWN")
    if permit["context_id"] != transition["context_id"]:
        raise SeedError("PERMIT_CONTEXT_MISMATCH")
    if transition["authn"]["signer_principal_id"] != permit["delegate_principal_id"]:
        raise SeedError("PERMIT_DELEGATE_MISMATCH")
    if permit["status"] != "ACTIVE" or permit["final_outcome_ref"] is not None:
        raise SeedError("PERMIT_NOT_ACTIVE")
    if state["contexts"][transition["context_id"]]["local_ordinal"] + 1 > permit["validity_end_ordinal"]:
        raise SeedError("PERMIT_EXPIRED")
    existing = state["submission_index"].get(p["submission_id"])
    if existing is not None:
        if existing["permit_ref"] == permit["permit_id"] and existing["candidate_digest"] == p["candidate_digest"]:
            raise SeedError("IDEMPOTENT_SUBMISSION_REPLAY")
        raise SeedError("SUBMISSION_ID_COLLISION")
    if permit["attempts_used"] >= permit["max_attempts"]:
        raise SeedError("ATTEMPT_LIMIT_EXHAUSTED")
    intent_id = artifact_id("intent", transition["transition_id"])
    receipt_id = artifact_id("receipt", transition["transition_id"])
    attempt_index = permit["attempts_used"] + 1
    state["execution_intents"][intent_id] = {
        "execution_intent_id": intent_id,
        "context_id": transition["context_id"],
        "permit_ref": permit["permit_id"],
        "presenter_principal_id": transition["authn"]["signer_principal_id"],
        "submission_id": p["submission_id"],
        "candidate_digest": p["candidate_digest"],
    }
    state["permit_use_receipts"][receipt_id] = {
        "receipt_id": receipt_id,
        "context_id": transition["context_id"],
        "permit_ref": permit["permit_id"],
        "execution_intent_ref": intent_id,
        "presenter_principal_id": transition["authn"]["signer_principal_id"],
        "submission_id": p["submission_id"],
        "candidate_digest": p["candidate_digest"],
        "attempt_index": attempt_index,
    }
    state["submission_index"][p["submission_id"]] = {
        "permit_ref": permit["permit_id"],
        "candidate_digest": p["candidate_digest"],
        "receipt_ref": receipt_id,
    }
    permit["attempts_used"] = attempt_index
    if attempt_index >= permit["max_attempts"]:
        permit["status"] = "EXHAUSTED"
    return [intent_id, receipt_id]


def _handle_observation(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    receipt = state["permit_use_receipts"].get(p["receipt_ref"])
    permit = state["permits"].get(p["permit_ref"])
    if receipt is None or permit is None:
        raise SeedError("OBSERVATION_LINEAGE_MISSING")
    if receipt["permit_ref"] != permit["permit_id"]:
        raise SeedError("OBSERVATION_RECEIPT_MISMATCH")
    if permit["context_id"] != transition["context_id"]:
        raise SeedError("OBSERVATION_CONTEXT_MISMATCH")
    if transition["authn"]["signer_principal_id"] != receipt["presenter_principal_id"]:
        raise SeedError("OBSERVATION_PRESENTER_MISMATCH")
    oid = artifact_id("obs", transition["transition_id"])
    state["observations"][oid] = {
        "observation_id": oid,
        "context_id": transition["context_id"],
        "permit_ref": permit["permit_id"],
        "receipt_ref": receipt["receipt_id"],
        "observer_principal_id": transition["authn"]["signer_principal_id"],
        "claim_digest": p["claim_digest"],
        "evidence_refs": list(p["evidence_refs"]),
        "claim_subject_context_id": p.get("claim_subject_context_id"),
    }
    return [oid]


def _handle_verification(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "VERIFY")
    observation = state["observations"].get(p["observation_ref"])
    receipt = state["permit_use_receipts"].get(p["receipt_ref"])
    permit = state["permits"].get(p["permit_ref"])
    if observation is None or receipt is None or permit is None:
        raise SeedError("VERIFICATION_LINEAGE_MISSING")
    if observation["permit_ref"] != permit["permit_id"] or receipt["permit_ref"] != permit["permit_id"]:
        raise SeedError("VERIFICATION_PERMIT_MISMATCH")
    if observation["receipt_ref"] != receipt["receipt_id"]:
        raise SeedError("VERIFICATION_RECEIPT_MISMATCH")
    if permit["context_id"] != transition["context_id"] or observation["context_id"] != transition["context_id"]:
        raise SeedError("VERIFICATION_CONTEXT_MISMATCH")
    allowed = {
        "PASS": {"SUCCESS", "FAILURE", "TRUST_LINEAGE_LOST"},
        "FAIL": {"UNDETERMINED"},
        "UNKNOWN": {"UNDETERMINED"},
    }
    if p["result_class"] not in allowed[p["status"]]:
        raise SeedError("VERIFICATION_STATUS_RESULT_MISMATCH")
    recognized_policies = set(state["constitution"]["body"]["rules"].values())
    if p["policy_digest"] not in recognized_policies:
        raise SeedError("VERIFICATION_POLICY_UNRECOGNIZED")
    if p["policy_digest"] != permit["success_predicate_digest"]:
        raise SeedError("VERIFICATION_POLICY_PERMIT_MISMATCH")
    vid = artifact_id("ver", transition["transition_id"])
    state["verifications"][vid] = {
        "verification_id": vid,
        "context_id": transition["context_id"],
        "permit_ref": permit["permit_id"],
        "receipt_ref": receipt["receipt_id"],
        "observation_ref": observation["observation_id"],
        "verifier_principal_id": transition["authn"]["signer_principal_id"],
        "policy_digest": p["policy_digest"],
        "evidence_refs": list(p["evidence_refs"]),
        "status": p["status"],
        "result_class": p["result_class"],
    }
    return [vid]



def _effective_verification_ref(state: dict[str, Any], ref: str) -> str | None:
    current: str | None = ref
    seen: set[str] = set()
    while current is not None:
        if current in seen:
            raise SeedError("CORRECTION_CYCLE")
        seen.add(current)
        matches = [
            correction for correction in state["corrections"].values()
            if correction["target_ref"] == current
        ]
        if len(matches) > 1:
            raise SeedError("CORRECTION_TARGET_MULTIPLE")
        if not matches:
            return current
        current = matches[0]["replacement_ref"]
    return None


def _effective_verifications_for_permit(state: dict[str, Any], permit_id: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for ref, verification in state["verifications"].items():
        if verification["permit_ref"] != permit_id:
            continue
        effective = _effective_verification_ref(state, ref)
        if effective == ref:
            result.append(verification)
    return result


def _handle_outcome(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "CONFIRM_OUTCOME")
    permit = state["permits"].get(p["permit_ref"])
    if permit is None:
        raise SeedError("PERMIT_UNKNOWN")
    if permit["context_id"] != transition["context_id"]:
        raise SeedError("OUTCOME_CONTEXT_MISMATCH")
    if permit["final_outcome_ref"] is not None:
        raise SeedError("OUTCOME_ALREADY_FINAL")
    if permit["status"] not in {"ACTIVE", "EXHAUSTED", "EXPIRED"}:
        raise SeedError("PERMIT_NOT_OUTCOME_ELIGIBLE")
    effective = _effective_verifications_for_permit(state, permit["permit_id"])
    effective_pass = [v for v in effective if v["status"] == "PASS"]
    effective_refs = sorted(v["verification_id"] for v in effective_pass)
    if sorted(p["verification_refs"]) != effective_refs:
        raise SeedError("OUTCOME_VERIFICATION_SET_INCOMPLETE")
    if not effective_pass:
        raise SeedError("OUTCOME_VERIFICATION_MISSING")
    has_success = any(v["result_class"] == "SUCCESS" for v in effective_pass)
    has_failure = any(v["result_class"] == "FAILURE" for v in effective_pass)
    if p["outcome_class"] == "POSITIVE":
        if not has_success:
            raise SeedError("SUCCESS_NOT_VERIFIED")
    else:
        if has_success:
            raise SeedError("NEGATIVE_CONFLICTS_WITH_SUCCESS")
        expired = state["contexts"][transition["context_id"]]["local_ordinal"] + 1 > permit["validity_end_ordinal"]
        terminal = permit["status"] in NEGATIVE_COMPLETION_STATES or expired
        if not terminal:
            raise SeedError("NEGATIVE_NOT_TERMINAL")
        if not has_failure:
            raise SeedError("FAILURE_NOT_VERIFIED")
        if expired and permit["status"] == "ACTIVE":
            permit["status"] = "EXPIRED"
    oid = artifact_id("out", transition["transition_id"])
    state["outcomes"][oid] = {
        "outcome_id": oid,
        "context_id": transition["context_id"],
        "permit_ref": permit["permit_id"],
        "verification_refs": effective_refs,
        "confirmer_principal_id": transition["authn"]["signer_principal_id"],
        "outcome_class": p["outcome_class"],
    }
    permit["final_outcome_ref"] = oid
    permit["status"] = "SATISFIED" if p["outcome_class"] == "POSITIVE" else "EXHAUSTED"
    return [oid]

def _handle_export(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    _require_authority(state, transition, "EXPORT")
    p = transition["payload"]
    context = state["contexts"][transition["context_id"]]
    if context["guarantee_status"] != "CONFIRMED":
        raise SeedError("GUARANTEE_SUSPENDED_USE_LOCAL_COMMIT")
    if p["source_export_root"] != context["export_root"]:
        raise SeedError("EXPORT_ROOT_MISMATCH")
    outcome_ref = p.get("outcome_ref")
    if outcome_ref is not None:
        outcome = state["outcomes"].get(outcome_ref)
        if outcome is None:
            raise SeedError("EXPORT_OUTCOME_UNKNOWN")
        if outcome["context_id"] != transition["context_id"]:
            raise SeedError("EXPORT_OUTCOME_CONTEXT_MISMATCH")
    previous_root = context["export_root"]
    new_root = domain_digest("ASET/ExportCommit/v1", {
        "previous_export_root": previous_root,
        "claim_digest": p["claim_digest"],
        "outcome_ref": outcome_ref,
        "transition_ref": transition["transition_id"],
    })
    context["export_root"] = new_root
    context["last_confirmed_export_root"] = new_root
    eid = artifact_id("export", transition["transition_id"])
    state["exports"][eid] = {
        "export_id": eid,
        "context_id": transition["context_id"],
        "source_context_id": transition["context_id"],
        "previous_export_root": previous_root,
        "source_export_root": new_root,
        "claim_digest": p["claim_digest"],
        "outcome_ref": outcome_ref,
        "guarantee_status": context["guarantee_status"],
        "issuer_principal_id": transition["authn"]["signer_principal_id"],
        "transition_ref": transition["transition_id"],
    }
    return [eid]

def _handle_import(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "IMPORT")
    export = state["exports"].get(p["export_ref"])
    if export is None:
        raise SeedError("EXPORT_UNKNOWN")
    permit = state["permits"].get(p["local_permit_ref"])
    receipt = state["permit_use_receipts"].get(p["local_receipt_ref"])
    if permit is None or receipt is None:
        raise SeedError("IMPORT_LOCAL_LINEAGE_MISSING")
    if receipt["permit_ref"] != permit["permit_id"] or permit["context_id"] != transition["context_id"]:
        raise SeedError("IMPORT_LOCAL_LINEAGE_MISMATCH")
    signer = transition["authn"]["signer_principal_id"]
    if receipt["presenter_principal_id"] != signer or permit["delegate_principal_id"] != signer:
        raise SeedError("IMPORT_PRESENTER_MISMATCH")
    iid = artifact_id("import", transition["transition_id"])
    oid = artifact_id("obs", transition["transition_id"])
    state["imports"][iid] = {
        "import_id": iid,
        "context_id": transition["context_id"],
        "target_context_id": transition["context_id"],
        "export_ref": export["export_id"],
        "claim_digest": export["claim_digest"],
        "importer_principal_id": transition["authn"]["signer_principal_id"],
    }
    # Imported claims are Observations, not locally accepted Outcomes.
    state["observations"][oid] = {
        "observation_id": oid,
        "context_id": transition["context_id"],
        "permit_ref": p["local_permit_ref"],
        "receipt_ref": p["local_receipt_ref"],
        "observer_principal_id": transition["authn"]["signer_principal_id"],
        "claim_digest": export["claim_digest"],
        "evidence_refs": [export["export_id"]],
        "claim_subject_context_id": export["source_context_id"],
    }
    return [iid, oid]


def _handle_guarantee_suspend(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "SUSPEND_GUARANTEE")
    child = state["contexts"].get(p["child_context_id"])
    if child is None:
        raise SeedError("CONTEXT_UNKNOWN")
    if child["parent_context_id"] != transition["context_id"]:
        raise SeedError("NOT_DIRECT_CHILD_CONTEXT")
    child["guarantee_status"] = "SUSPENDED"
    return []


def compute_local_commit_id(parent_export_root: str, operation_class: str, commit_digest: str, signer_principal_id: str) -> str:
    return _hex_id("commit:", domain_digest("ASET/LocalCommitID/v1", {
        "parent_export_root": parent_export_root,
        "operation_class": operation_class,
        "commit_digest": commit_digest,
        "signer_principal_id": signer_principal_id,
    }))


def _local_commit_root(parent_export_root: str, operation_class: str, commit_digest: str, commit_id: str) -> str:
    return domain_digest("ASET/LocalExportCommit/v1", {
        "parent_export_root": parent_export_root,
        "operation_class": operation_class,
        "commit_digest": commit_digest,
        "commit_id": commit_id,
    })


def _handle_partition_local_transition(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    context = state["contexts"][transition["context_id"]]
    if context["guarantee_status"] != "SUSPENDED":
        raise SeedError("GUARANTEE_NOT_SUSPENDED")
    cls = state["constitution"]["body"]["coordination_classes"].get(p["operation_class"], "COORDINATION_REQUIRED")
    if cls == "COORDINATION_REQUIRED":
        raise SeedError("COORDINATION_REQUIRED")
    if cls == "INVARIANT_CONFLUENT":
        allowed = set(state["constitution"]["body"].get("accepted_coordination_proofs", []))
        if p.get("coordination_proof_digest") not in allowed:
            raise SeedError("COORDINATION_PROOF_MISSING")
    signer = transition["authn"]["signer_principal_id"]
    if signer != context["member_principal_id"] and not has_authority(state, transition["context_id"], "EXPORT", signer):
        raise SeedError("LOCAL_COMMIT_SIGNER_UNAUTHORIZED")
    commit_id = compute_local_commit_id(p["parent_export_root"], p["operation_class"], p["commit_digest"], signer)
    known_roots = {context["last_confirmed_export_root"]}
    known_roots.update(c["new_export_root"] for c in context.get("unconfirmed_commits", {}).values())
    if p["parent_export_root"] not in known_roots:
        raise SeedError("LOCAL_COMMIT_PARENT_UNKNOWN")
    new_root = _local_commit_root(p["parent_export_root"], p["operation_class"], p["commit_digest"], commit_id)
    context.setdefault("unconfirmed_commits", {})[commit_id] = {
        "commit_id": commit_id,
        "parent_export_root": p["parent_export_root"],
        "new_export_root": new_root,
        "operation_class": p["operation_class"],
        "commit_digest": p["commit_digest"],
        "signer_principal_id": transition["authn"]["signer_principal_id"],
    }
    return [commit_id]


def _handle_reconcile(state: dict[str, Any], transition: dict[str, Any]) -> tuple[list[str], str]:
    p = transition["payload"]
    _require_authority(state, transition, "RECONCILE")
    child = state["contexts"].get(p["child_context_id"])
    if child is None:
        raise SeedError("CONTEXT_UNKNOWN")
    if child["parent_context_id"] != transition["context_id"]:
        raise SeedError("NOT_DIRECT_CHILD_CONTEXT")
    if child["guarantee_status"] != "SUSPENDED":
        raise SeedError("GUARANTEE_NOT_SUSPENDED")
    if p["common_export_root"] != child["last_confirmed_export_root"]:
        raise SeedError("RECONCILIATION_COMMON_ROOT_MISMATCH")
    commits = p["lineage"]
    known = child.get("unconfirmed_commits", {})
    submitted_ids = {item["commit_id"] for item in commits}
    if known and not set(known).issubset(submitted_ids):
        raise SeedError("RECONCILIATION_KNOWN_COMMIT_SET_MISMATCH")
    for item in commits:
        expected_commit_id = compute_local_commit_id(
            item["parent_export_root"], item["operation_class"], item["commit_digest"], item["signer_principal_id"]
        )
        if item["commit_id"] != expected_commit_id:
            raise SeedError("LOCAL_COMMIT_ID_MISMATCH")
        if not item["proof_digest"].startswith(DIGEST_PREFIX):
            raise SeedError("AUTHENTICATION_PROOF_FORMAT")
        signer = item["signer_principal_id"]
        if signer != child["member_principal_id"] and not has_authority(state, child["context_id"], "EXPORT", signer):
            raise SeedError("LOCAL_COMMIT_SIGNER_UNAUTHORIZED")
        expected_root = _local_commit_root(
            item["parent_export_root"], item["operation_class"], item["commit_digest"], item["commit_id"]
        )
        if item["new_export_root"] != expected_root:
            raise SeedError("LOCAL_COMMIT_ROOT_MISMATCH")
    by_parent: dict[str, set[str]] = defaultdict(set)
    for item in commits:
        by_parent[item["parent_export_root"]].add(item["new_export_root"])
    fork = any(len(children) > 1 for children in by_parent.values())
    current = p["common_export_root"]
    accepted_prefix = 0
    invalid_code: str | None = None
    seen_ids: set[str] = set()
    if not fork:
        remaining = {item["commit_id"]: item for item in commits}
        while remaining:
            candidates = [item for item in remaining.values() if item["parent_export_root"] == current]
            if len(candidates) != 1:
                invalid_code = "RECONCILIATION_CHAIN_BREAK"
                break
            item = candidates[0]
            if item["commit_id"] in seen_ids:
                invalid_code = "RECONCILIATION_DUPLICATE_COMMIT"
                break
            seen_ids.add(item["commit_id"])
            cls = state["constitution"]["body"]["coordination_classes"].get(
                item["operation_class"], "COORDINATION_REQUIRED"
            )
            if cls == "COORDINATION_REQUIRED":
                invalid_code = "COORDINATION_REQUIRED"
                break
            current = item["new_export_root"]
            accepted_prefix += 1
            del remaining[item["commit_id"]]
    rid = artifact_id("reconcile", transition["transition_id"])
    if fork:
        result = "FORK_DETECTED"
        code = "FORK_DETECTED"
        invalid_code = "KNOWN_FORK"
    elif invalid_code is not None:
        result = "PARTIALLY_CONFIRMED" if accepted_prefix > 0 else "INSUFFICIENT_EVIDENCE"
        code = result
        if accepted_prefix > 0:
            child["last_confirmed_export_root"] = current
            child["export_root"] = current
    else:
        result = "CONFIRMED"
        code = "ACCEPTED"
        child["last_confirmed_export_root"] = current
        child["export_root"] = current
        child["guarantee_status"] = "CONFIRMED"
        child["unconfirmed_commits"] = {}
    state["reconciliations"][rid] = {
        "reconciliation_id": rid,
        "context_id": transition["context_id"],
        "child_context_id": child["context_id"],
        "common_export_root": p["common_export_root"],
        "result": result,
        "accepted_prefix_length": accepted_prefix,
        "invalid_code": invalid_code,
        "lineage_digest": domain_digest("ASET/ReconciliationLineage/v1", commits),
    }
    return [rid], code

def _withdraw_subtree(state: dict[str, Any], context_id: str, direct_lifecycle: str) -> list[str]:
    subtree = {context_id} | _context_descendants(state, context_id)
    for cid in subtree:
        context = state["contexts"][cid]
        context["lifecycle"] = direct_lifecycle if cid == context_id else "WITHDRAWN"
        context["guarantee_status"] = "TERMINATED"
        state["context_aliases"].pop(context["alias"], None)
    for authority in state["authorities"].values():
        if authority["context_id"] in subtree and authority["status"] == "ACTIVE":
            authority["status"] = "REVOKED"
    for permit in state["permits"].values():
        if permit["context_id"] in subtree and permit["status"] == "ACTIVE":
            permit["status"] = "TERMINATED_WITH_CONTEXT"
    state["normative_dependencies"] = [
        edge for edge in state["normative_dependencies"]
        if edge["source_context_id"] not in subtree and edge["target_context_id"] not in subtree
    ]
    return sorted(subtree)


def _handle_membership_withdraw(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    context = state["contexts"][transition["context_id"]]
    if context["parent_context_id"] is None:
        raise SeedError("ROOT_WITHDRAWAL_FORBIDDEN")
    signer = transition["authn"]["signer_principal_id"]
    if signer != context["member_principal_id"]:
        raise SeedError("WITHDRAWAL_MEMBER_SIGNATURE_REQUIRED")
    affected = compute_affected_sibling_set(state, context["parent_context_id"], context["context_id"] )
    if affected != [context["context_id"]]:
        raise SeedError("WITHDRAWAL_REDEFINITION_REQUIRED")
    withdrawn = _withdraw_subtree(state, context["context_id"], "WITHDRAWN")
    wid = artifact_id("withdrawal", transition["transition_id"] )
    state["membership_withdrawals"][wid] = {
        "withdrawal_id": wid,
        "context_id": context["context_id"],
        "parent_context_id": context["parent_context_id"],
        "mode": "VOLUNTARY_EXIT",
        "member_principal_id": signer,
        "reason_digest": transition["payload"]["reason_digest"],
        "proposal_digest": None,
        "withdrawn_context_ids": withdrawn,
        "authorization_proof_digest": transition["authn"]["proof_digest"],
        "transition_ref": transition["transition_id"],
    }
    return [wid]


def _handle_context_redefine(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    _require_authority(state, transition, "REDEFINE_CONTEXT")
    p = transition["payload"]
    proposal = p["proposal"]
    if proposal["parent_context_id"] != transition["context_id"]:
        raise SeedError("REDEFINITION_PARENT_MISMATCH")
    expected_digest = context_redefinition_proposal_digest(proposal)
    if p["proposal_digest"] != expected_digest:
        raise SeedError("REDEFINITION_PROPOSAL_DIGEST_MISMATCH")
    affected = compute_affected_sibling_set(
        state, transition["context_id"], proposal["target_context_id"]
    )
    replacements = proposal["replacements"]
    old_ids = [item["old_context_id"] for item in replacements]
    if len(old_ids) != len(set(old_ids)) or set(old_ids) != set(affected):
        raise SeedError("REDEFINITION_AFFECTED_SET_MISMATCH")
    auths = p["withdrawal_authorizations"]
    auth_ids = [item["context_id"] for item in auths]
    if len(auth_ids) != len(set(auth_ids)) or set(auth_ids) != set(affected):
        raise SeedError("REDEFINITION_AUTHORIZATION_SET_MISMATCH")
    auth_by_id = {item["context_id"]: item for item in auths}
    for cid in affected:
        context = state["contexts"][cid]
        auth = auth_by_id[cid]
        if auth["member_principal_id"] != context["member_principal_id"]:
            raise SeedError("REDEFINITION_MEMBER_MISMATCH")
        if auth["proposal_digest"] != expected_digest:
            raise SeedError("REDEFINITION_AUTHORIZATION_BINDING_MISMATCH")
    replacement_by_old = {item["old_context_id"]: item for item in replacements}
    successor_map: dict[str, str] = {}
    genesis_payloads: dict[str, dict[str, Any]] = {}
    for old_id in affected:
        old = state["contexts"][old_id]
        item = replacement_by_old[old_id]
        local_alias = old["alias"].rsplit("/", 1)[-1]
        member_payload = {
            "parent_context_id": transition["context_id"],
            "member_principal_id": old["member_principal_id"],
            "context_kind": old["context_kind"],
            "context_genesis_nonce": item["context_genesis_nonce"],
            "local_alias": local_alias,
            "initial_authorities": copy.deepcopy(item["initial_authorities"]),
            "depends_on_context_ids": list(item["depends_on_context_ids"]),
        }
        new_id = compute_context_id(transition["context_id"], member_genesis_digest(member_payload))
        if new_id in state["contexts"] or new_id in successor_map.values():
            raise SeedError("REDEFINITION_SUCCESSOR_COLLISION")
        successor_map[old_id] = new_id
        genesis_payloads[old_id] = member_payload
    # Validate dependency references against the pre-state and the exact replacement set.
    withdrawn_subtrees: set[str] = set(affected)
    for old_id in affected:
        withdrawn_subtrees.update(_context_descendants(state, old_id))
    for old_id, member_payload in genesis_payloads.items():
        for dep in member_payload["depends_on_context_ids"]:
            if dep not in state["contexts"]:
                raise SeedError("DEPENDENCY_CONTEXT_UNKNOWN")
            if dep in withdrawn_subtrees and dep not in successor_map:
                raise SeedError("REDEFINITION_DEPENDENCY_TARGET_WITHDRAWN")
            if dep not in successor_map and state["contexts"][dep]["lifecycle"] != "ACTIVE":
                raise SeedError("DEPENDENCY_CONTEXT_INACTIVE")
    withdrawal_refs: list[str] = []
    artifacts: list[str] = []
    # Atomic mutation begins only after every predicate above has passed.
    for index, old_id in enumerate(affected):
        old = state["contexts"][old_id]
        withdrawn = _withdraw_subtree(state, old_id, "SUPERSEDED")
        wid = artifact_id(f"withdrawal-{index}", transition["transition_id"] )
        state["membership_withdrawals"][wid] = {
            "withdrawal_id": wid, "context_id": old_id,
            "parent_context_id": transition["context_id"], "mode": "REDEFINITION",
            "member_principal_id": old["member_principal_id"], "reason_digest": None,
            "proposal_digest": expected_digest, "withdrawn_context_ids": withdrawn,
            "authorization_proof_digest": auth_by_id[old_id]["proof_digest"],
            "transition_ref": transition["transition_id"],
        }
        withdrawal_refs.append(wid)
        artifacts.append(wid)
    # Materialize successors and authority bindings.
    for old_id in affected:
        old = state["contexts"][old_id]
        payload = genesis_payloads[old_id]
        new_id = successor_map[old_id]
        context = {
            "context_id": new_id, "parent_context_id": transition["context_id"],
            "context_kind": old["context_kind"], "member_principal_id": old["member_principal_id"],
            "genesis_digest": member_genesis_digest(payload), "constitution_epoch": 0,
            "local_ordinal": 0, "lifecycle": "ACTIVE", "guarantee_status": "CONFIRMED",
            "internal_state_root": domain_digest("ASET/EmptyContextState/v1", {"context_id": new_id}),
            "export_root": domain_digest("ASET/EmptyContextExport/v1", {"context_id": new_id}),
            "last_confirmed_export_root": domain_digest("ASET/EmptyContextExport/v1", {"context_id": new_id}),
            "alias": old["alias"],
        }
        state["contexts"][new_id] = context
        state["context_aliases"][context["alias"]] = new_id
        artifacts.append(new_id)
        for spec in payload["initial_authorities"]:
            binding = _binding_from_spec(new_id, spec, transition["transition_id"], 0)
            if binding["authority_id"] in state["authorities"]:
                raise SeedError("AUTHORITY_ALREADY_EXISTS")
            state["authorities"][binding["authority_id"]] = binding
            artifacts.append(binding["authority_id"] )
    # Rebuild only dependencies declared by successor definitions, remapping affected peers.
    for old_id in affected:
        source_new = successor_map[old_id]
        for dep in genesis_payloads[old_id]["depends_on_context_ids"]:
            target_new = successor_map.get(dep, dep)
            edge = {
                "source_context_id": source_new,
                "target_context_id": target_new,
                "dependency_kind": "NORMATIVE",
            }
            if edge not in state["normative_dependencies"]:
                state["normative_dependencies"].append(edge)
    rid = artifact_id("redefinition", transition["transition_id"] )
    state["context_redefinitions"][rid] = {
        "redefinition_id": rid, "context_id": transition["context_id"],
        "target_context_id": proposal["target_context_id"],
        "proposal": copy.deepcopy(proposal),
        "proposal_digest": expected_digest, "affected_context_ids": affected,
        "successor_map": successor_map, "withdrawal_refs": withdrawal_refs,
        "transition_ref": transition["transition_id"],
    }
    return [rid] + artifacts

def _handle_context_terminate(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "TERMINATE_CONTEXT")
    child = state["contexts"].get(p["child_context_id"])
    if child is None:
        raise SeedError("CONTEXT_UNKNOWN")
    if child["parent_context_id"] != transition["context_id"]:
        raise SeedError("NOT_DIRECT_CHILD_CONTEXT")
    verification = state["verifications"].get(p["verification_ref"])
    if verification is None or verification["status"] != "PASS" or verification["result_class"] != "TRUST_LINEAGE_LOST":
        raise SeedError("TRUST_LINEAGE_LOSS_NOT_VERIFIED")
    observation = state["observations"][verification["observation_ref"]]
    if observation.get("claim_subject_context_id") != child["context_id"]:
        raise SeedError("TRUST_LINEAGE_LOSS_SUBJECT_MISMATCH")
    terminated = {child["context_id"]} | _context_descendants(state, child["context_id"])
    for cid in terminated:
        state["contexts"][cid]["lifecycle"] = "TERMINATED"
        state["contexts"][cid]["guarantee_status"] = "TERMINATED"
        state["context_aliases"].pop(state["contexts"][cid]["alias"], None)
    for authority in state["authorities"].values():
        if authority["context_id"] in terminated and authority["status"] == "ACTIVE":
            authority["status"] = "REVOKED"
    for permit in state["permits"].values():
        if permit["context_id"] in terminated and permit["status"] == "ACTIVE":
            permit["status"] = "TERMINATED_WITH_CONTEXT"
    return []


def _handle_correction(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "VERIFY")
    if p["target_type"] != "VERIFICATION":
        raise SeedError("CORRECTION_TARGET_TYPE_UNSUPPORTED")
    target = state["verifications"].get(p["target_ref"])
    if target is None:
        raise SeedError("CORRECTION_TARGET_UNKNOWN")
    if any(p["target_ref"] in outcome["verification_refs"] for outcome in state["outcomes"].values()):
        raise SeedError("CORRECTION_TARGET_FINALIZED")
    if target["context_id"] != transition["context_id"]:
        raise SeedError("CORRECTION_CONTEXT_MISMATCH")
    if any(c["target_ref"] == p["target_ref"] for c in state["corrections"].values()):
        raise SeedError("CORRECTION_TARGET_ALREADY_SUPERSEDED")
    replacement_ref = p.get("replacement_ref")
    if replacement_ref is not None:
        if replacement_ref == p["target_ref"]:
            raise SeedError("CORRECTION_SELF_REPLACEMENT")
        replacement = state["verifications"].get(replacement_ref)
        if replacement is None:
            raise SeedError("CORRECTION_REPLACEMENT_UNKNOWN")
        if replacement["context_id"] != transition["context_id"]:
            raise SeedError("CORRECTION_REPLACEMENT_CONTEXT_MISMATCH")
        if (
            replacement["permit_ref"] != target["permit_ref"]
            or replacement["receipt_ref"] != target["receipt_ref"]
            or replacement["observation_ref"] != target["observation_ref"]
        ):
            raise SeedError("CORRECTION_REPLACEMENT_LINEAGE_MISMATCH")
        if _effective_verification_ref(state, replacement_ref) != replacement_ref:
            raise SeedError("CORRECTION_REPLACEMENT_NOT_EFFECTIVE")
    cid = artifact_id("correction", transition["transition_id"])
    state["corrections"][cid] = {
        "correction_id": cid,
        "context_id": transition["context_id"],
        "target_type": "VERIFICATION",
        "target_ref": p["target_ref"],
        "replacement_ref": replacement_ref,
        "reason_digest": p["reason_digest"],
        "corrector_principal_id": transition["authn"]["signer_principal_id"],
    }
    return [cid]

def _transfer_task_digest(authority_ref: str, new_holder_principal_id: str) -> str:
    return domain_digest("ASET/AuthorityTransferTask/v1", {
        "authority_ref": authority_ref,
        "new_holder_principal_id": new_holder_principal_id,
    })


def _handle_authority_transfer(state: dict[str, Any], transition: dict[str, Any]) -> list[str]:
    p = transition["payload"]
    _require_authority(state, transition, "TRANSFER_AUTHORITY")
    old = state["authorities"].get(p["authority_ref"])
    outcome = state["outcomes"].get(p["outcome_ref"])
    if old is None or old["status"] != "ACTIVE":
        raise SeedError("AUTHORITY_NOT_ACTIVE")
    if old["context_id"] != transition["context_id"]:
        raise SeedError("AUTHORITY_CONTEXT_MISMATCH")
    if outcome is None or outcome["outcome_class"] != "POSITIVE":
        raise SeedError("TRANSFER_POSITIVE_OUTCOME_REQUIRED")
    permit = state["permits"][outcome["permit_ref"]]
    if outcome["context_id"] != old["context_id"] or permit["context_id"] != old["context_id"]:
        raise SeedError("TRANSFER_ACTION_CONTEXT_MISMATCH")
    expected_task = _transfer_task_digest(old["authority_id"], p["new_holder_principal_id"])
    if permit["task_digest"] != expected_task:
        raise SeedError("TRANSFER_TASK_MISMATCH")
    if permit["delegate_principal_id"] != p["new_holder_principal_id"]:
        raise SeedError("TRANSFER_NEW_HOLDER_NOT_DELEGATE")
    readiness = state["decisions"].get(permit["readiness_ref"])
    if (
        readiness is None
        or readiness["decision_kind"] != "READINESS_ACCEPT_RESPONSIBILITY"
        or readiness["issuer_principal_id"] != p["new_holder_principal_id"]
        or readiness["subject_principal_id"] != p["new_holder_principal_id"]
        or readiness["related_ref"] != old["authority_id"]
        or readiness["context_id"] != old["context_id"]
    ):
        raise SeedError("TRANSFER_RESPONSIBILITY_READINESS_REQUIRED")
    old["status"] = "TRANSFERRED"
    new_binding = {
        "authority_id": "", "context_id": old["context_id"],
        "capability_kind": old["capability_kind"], "scope": list(old["scope"]),
        "scope_digest": old["scope_digest"], "holder_principal_id": p["new_holder_principal_id"],
        "authority_epoch": old["authority_epoch"] + 1, "status": "ACTIVE",
        "grant_provenance": transition["transition_id"],
    }
    new_binding["authority_id"] = _authority_id(new_binding)
    state["authorities"][new_binding["authority_id"]] = new_binding
    return [new_binding["authority_id"]]

HANDLERS = {
    "MEMBER_CONTEXT_GENESIS": _handle_member_context_genesis,
    "DECISION": _handle_decision,
    "PERMIT_ISSUE": _handle_permit_issue,
    "PERMIT_ATTENUATE": _handle_permit_attenuate,
    "PERMIT_USE": _handle_permit_use,
    "OBSERVATION": _handle_observation,
    "VERIFICATION": _handle_verification,
    "OUTCOME": _handle_outcome,
    "EXPORT": _handle_export,
    "IMPORT": _handle_import,
    "GUARANTEE_SUSPEND": _handle_guarantee_suspend,
    "PARTITION_LOCAL_TRANSITION": _handle_partition_local_transition,
    "MEMBERSHIP_WITHDRAW": _handle_membership_withdraw,
    "CONTEXT_REDEFINE": _handle_context_redefine,
    "CONTEXT_TERMINATE": _handle_context_terminate,
    "CORRECTION": _handle_correction,
    "AUTHORITY_TRANSFER": _handle_authority_transfer,
}


def apply_transition(state: dict[str, Any], transition: dict[str, Any]) -> dict[str, Any]:
    original = copy.deepcopy(state)
    try:
        digest = _validate_envelope(state, transition)
    except SeedError as exc:
        if exc.code in {"IDEMPOTENT_REPLAY", "IDEMPOTENT_SUBMISSION_REPLAY"}:
            return {"accepted": True, "code": exc.code, "state_changed": False, "state": original, "artifacts": []}
        return {"accepted": False, "code": exc.code, "state_changed": False, "state": original, "artifacts": []}
    except Exception:
        return {"accepted": False, "code": "MALFORMED_TRANSITION", "state_changed": False, "state": original, "artifacts": []}
    working = copy.deepcopy(state)
    code = "ACCEPTED"
    try:
        if transition["kind"] == "RECONCILE":
            artifacts, code = _handle_reconcile(working, transition)
        else:
            handler = HANDLERS.get(transition["kind"])
            if handler is None:
                raise SeedError("UNSUPPORTED_TRANSITION_KIND")
            artifacts = handler(working, transition)
        _record_transition(working, transition, digest, artifacts)
        validate_state(working)
    except SeedError as exc:
        if exc.code == "IDEMPOTENT_SUBMISSION_REPLAY":
            return {"accepted": True, "code": exc.code, "state_changed": False, "state": original, "artifacts": []}
        return {"accepted": False, "code": exc.code, "state_changed": False, "state": original, "artifacts": []}
    except Exception:
        return {"accepted": False, "code": "MALFORMED_TRANSITION", "state_changed": False, "state": original, "artifacts": []}
    return {"accepted": True, "code": code, "state_changed": True, "state": working, "artifacts": artifacts}

def validate_case(case: dict[str, Any]) -> tuple[bool, dict[str, Any], dict[str, Any]]:
    try:
        state = initialize_state(copy.deepcopy(case["initial_genesis"]))
    except SeedError as exc:
        actual = {"accepted": False, "code": exc.code, "state_changed": False}
        expected = case["expected"]
        return actual == expected, actual, expected
    for setup in case.get("setup", []):
        result = apply_transition(state, setup)
        if not result["accepted"] or not result["state_changed"]:
            actual = {"accepted": False, "code": "SETUP_FAILED:" + result["code"], "state_changed": False}
            expected = case["expected"]
            return False, actual, expected
        state = result["state"]
    result = apply_transition(state, case["candidate"])
    actual = {
        "accepted": result["accepted"],
        "code": result["code"],
        "state_changed": result["state_changed"],
    }
    expected = case["expected"]
    ok = actual == expected
    for assertion in case.get("postconditions", []):
        if not result["accepted"]:
            ok = False
            break
        cursor: Any = result["state"]
        for part in assertion["path"].split("/")[1:]:
            cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
        if cursor != assertion["equals"]:
            ok = False
    return ok, actual, expected


__all__ = [
    "VERSION", "SEED_SEMANTICS_ID", "IMPLEMENTATION_VERSION", "SeedError", "canonical_bytes", "domain_digest",
    "constitution_digest", "compute_root_genesis_digest", "compute_context_id",
    "compute_trust_space_id", "member_genesis_digest", "transition_digest",
    "compute_transition_id", "compute_state_root", "artifact_id", "scope_digest", "permit_terms_digest",
    "compute_affected_sibling_set", "context_redefinition_proposal_digest", "_causal_basis_refs", "_required_causal_parents", "initialize_state", "apply_transition", "validate_state",
    "validate_case", "_transfer_task_digest", "compute_local_commit_id", "_local_commit_root",
]
