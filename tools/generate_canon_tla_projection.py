#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "seed/canonical/source/seed-model.json"
RELATION_PATH = ROOT / "seed/canonical/assurance/canon-tla-refinement.json"
OUTPUT_PATH = ROOT / "seed/canonical/formal/SeedCanonProjection.tla"

EXPECTED_PROFILE = "ASET-SEED-CANON-TLA-PROJECTION-V5"
EXPECTED_REQUIREMENT_PREDICATES = [
    "binding_exact",
    "request_fresh",
    "resolution_domain",
    "allow_only",
    "fail_closed",
    "local_authority",
    "authority_recognition_boundary",
    "inputs_non_authoritative",
    "accepted_terminal_unique",
    "record_immutable",
    "reconsider_fresh",
    "implementation_neutral",
]
EXPECTED_OPERATIONS = [
    ("SEED-OP-001", "REGISTER_REQUEST", "STATE_TRANSITION"),
    ("SEED-OP-002", "SUBMIT_RESOLUTION", "STATE_TRANSITION"),
    ("SEED-OP-003", "EVALUATE_RESOLUTION", "OBSERVER"),
]
EXPECTED_INVARIANTS = [f"SEED-INV-{index:03d}" for index in range(1, 13)]


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def tla_set(values: list[str]) -> str:
    return "{" + ", ".join(json.dumps(value) for value in values) + "}"


def validate_inputs(model: dict[str, Any], relation: dict[str, Any]) -> None:
    errors: list[str] = []
    if relation["generated_projection"]["profile"] != EXPECTED_PROFILE:
        errors.append("unexpected projection profile")
    if relation["source_model"]["sha256"] != digest(MODEL_PATH):
        errors.append("source model digest mismatch")
    if relation["source_model"]["model_id"] != model["model_id"]:
        errors.append("source model id mismatch")
    if relation["source_model"]["version"] != model["version"]:
        errors.append("source model version mismatch")

    predicates = [item["predicate"] for item in model["requirements"]]
    if predicates != EXPECTED_REQUIREMENT_PREDICATES:
        errors.append("unsupported requirement predicate catalogue")
    invariants = [item["id"] for item in model["invariants"]]
    if invariants != EXPECTED_INVARIANTS:
        errors.append("unsupported invariant catalogue")
    operations = [
        (item["id"], item["kind"], item["role"]) for item in model["operations"]
    ]
    if operations != EXPECTED_OPERATIONS:
        errors.append("unsupported operation catalogue")

    algebra = model["resolution_algebra"]
    if algebra["values"] != ["UNKNOWN", "ALLOW", "BLOCK"]:
        errors.append("unsupported resolution values")
    if algebra["stored_terminal"] != ["ALLOW", "BLOCK"]:
        errors.append("unsupported terminal values")
    if algebra["derived"] != "UNKNOWN":
        errors.append("unsupported derived resolution")
    if algebra["effect_permitted_if"] != "ALLOW":
        errors.append("unsupported effect permission value")
    if algebra["fail_closed_values"] != ["UNKNOWN", "BLOCK"]:
        errors.append("unsupported fail-closed values")
    if algebra["conflict_result"] != "UNKNOWN":
        errors.append("unsupported conflict result")
    if errors:
        raise ValueError("; ".join(errors))


def render(model: dict[str, Any], relation: dict[str, Any]) -> str:
    validate_inputs(model, relation)
    algebra = model["resolution_algebra"]
    source_sha = relation["source_model"]["sha256"]
    profile = relation["generated_projection"]["profile"]

    return rf'''---------------- MODULE SeedCanonProjection ----------------
EXTENDS FiniteSets

(*
GENERATED FILE. DO NOT EDIT.
Source: seed/canonical/source/seed-model.json
Source SHA-256: {source_sha}
Projection profile: {profile}

V5 is a standalone projection. It does not EXTEND or import SeedResolution.
The refinement proof explicitly instantiates this model onto the target state.
Seed-owned state is requestMeta + terminalMeta. Conflict is environment state.
EVALUATE_RESOLUTION is a pure observer and is not part of CanonNext.
*)

CONSTANTS ResolutionIds, Bindings, Authorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment,
          RecognizedAuthorityBindings

ASSUME ResolutionIds # {{}}
ASSUME Bindings # {{}}
ASSUME Authorities # {{}}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME RecognizedAuthorityBindings \subseteq Authorities \X Bindings

CanonResolutions == {tla_set(algebra["values"])}
CanonTerminalResolutions == {tla_set(algebra["stored_terminal"])}
CanonDerivedResolution == {json.dumps(algebra["derived"])}
CanonEffectPermittedValue == {json.dumps(algebra["effect_permitted_if"])}
CanonFailClosedValues == {tla_set(algebra["fail_closed_values"])}
CanonConflictResult == {json.dumps(algebra["conflict_result"])}

CanonRequestMetaType ==
  [binding : Bindings,
   previous : TerminalCommitments \cup {{NoCommitment}}]

CanonTerminalMetaType ==
  [resolution : CanonTerminalResolutions,
   authority : Authorities]

VARIABLES requestMeta, terminalMeta, conflicts

CanonSeedVars == <<requestMeta, terminalMeta>>
CanonEnvironmentVars == <<conflicts>>
CanonVars == <<requestMeta, terminalMeta, conflicts>>

CanonRequests == DOMAIN requestMeta
CanonTerminalRequests == DOMAIN terminalMeta
CanonRequestBinding(r) == requestMeta[r].binding
CanonPreviousCommitment(r) == requestMeta[r].previous
CanonTerminalResolution(r) == terminalMeta[r].resolution
CanonTerminalAuthority(r) == terminalMeta[r].authority

CanonInit ==
  /\ requestMeta = [r \in {{}} |-> r]
  /\ terminalMeta = [r \in {{}} |-> r]
  /\ conflicts = {{}}

CanonRegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ CanonRequests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in RecognizedAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requestMeta' =
       [x \in CanonRequests \cup {{r}} |->
          IF x = r
          THEN [binding |-> b, previous |-> previous]
          ELSE requestMeta[x]]
  /\ UNCHANGED <<terminalMeta, conflicts>>

CanonSubmitResolution(r, b, a, value) ==
  /\ r \in CanonRequests
  /\ b = CanonRequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in RecognizedAuthorityBindings
  /\ value \in CanonTerminalResolutions
  /\ r \notin CanonTerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in CanonTerminalRequests \cup {{r}} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>

CanonObserveConflict(r) ==
  /\ r \in CanonTerminalRequests \ conflicts
  /\ conflicts' = conflicts \cup {{r}}
  /\ UNCHANGED CanonSeedVars

CanonRecognizedSeedTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {{NoCommitment}} :
        CanonRegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in CanonTerminalResolutions :
        CanonSubmitResolution(r, b, a, value)

CanonRecognizedEnvironmentTransition ==
  \E r \in ResolutionIds : CanonObserveConflict(r)

CanonNext ==
  \/ CanonRecognizedSeedTransition
  \/ CanonRecognizedEnvironmentTransition

CanonResolutionOf(r) ==
  IF r \notin CanonRequests \/ r \in conflicts
  THEN CanonConflictResult
  ELSE IF r \notin CanonTerminalRequests
       THEN CanonDerivedResolution
       ELSE CanonTerminalResolution(r)

CanonEffectPermitted(r) ==
  CanonResolutionOf(r) = CanonEffectPermittedValue

CanonEvaluateResolution(r) ==
  [resolution |-> CanonResolutionOf(r),
   effect_permitted |-> CanonEffectPermitted(r)]

CanonSpec == CanonInit /\ [][CanonNext]_CanonVars
=============================================================================
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model = load(MODEL_PATH)
    relation = load(RELATION_PATH)
    try:
        content = render(model, relation)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"CANON_TLA_PROJECTION_ERROR={exc}")
        print("CANON_TLA_PROJECTION=FAIL")
        return 1
    if args.check:
        ok = OUTPUT_PATH.is_file() and OUTPUT_PATH.read_text(encoding="utf-8") == content
        print("CANON_TLA_PROJECTION_PARITY=" + ("PASS" if ok else "DIFFERENT"))
        return 0 if ok else 1
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print("CANON_TLA_PROJECTION_GENERATED=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
