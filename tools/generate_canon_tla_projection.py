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

EXPECTED_PROFILE = "ASET-SEED-CANON-TLA-PROJECTION-V2"
EXPECTED_REQUIREMENT_PREDICATES = [
    "binding_exact",
    "request_fresh",
    "resolution_domain",
    "allow_only",
    "fail_closed",
    "local_authority",
    "proof_attenuating",
    "inputs_non_authoritative",
    "terminal_unique",
    "record_immutable",
    "reconsider_fresh",
    "implementation_neutral",
]
EXPECTED_TRANSITIONS = [
    ("SEED-TX-001", "REGISTER_REQUEST"),
    ("SEED-TX-002", "SUBMIT_RESOLUTION"),
    ("SEED-TX-003", "EVALUATE_RESOLUTION"),
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

    transitions = [(item["id"], item["kind"]) for item in model["transitions"]]
    if transitions != EXPECTED_TRANSITIONS:
        errors.append("unsupported transition catalogue")

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

    return f"""---------------- MODULE SeedCanonProjection ----------------
EXTENDS SeedResolution

(*
GENERATED FILE. DO NOT EDIT.
Source: seed/canonical/source/seed-model.json
Source SHA-256: {source_sha}
Projection profile: {profile}

This module is the deterministic TLA+ interpretation used by the
canon-to-TLA refinement assurance. It intentionally preserves the declared
opaque Binding, authorityProofBindings and RecognizedTerminalCommitments
abstractions.
*)

CanonResolutions == {tla_set(algebra["values"])}
CanonTerminalResolutions == {tla_set(algebra["stored_terminal"])}
CanonDerivedResolution == {json.dumps(algebra["derived"])}
CanonEffectPermittedValue == {json.dumps(algebra["effect_permitted_if"])}
CanonFailClosedValues == {tla_set(algebra["fail_closed_values"])}
CanonConflictResult == {json.dumps(algebra["conflict_result"])}

CanonInit ==
  /\\ localAuthorityBindings \\in SUBSET (Authorities \\X Bindings)
  /\\ authorityProofBindings \\in SUBSET (Authorities \\X Bindings)
  /\\ localAuthorityBindings \\subseteq authorityProofBindings
  /\\ requests = {{}}
  /\\ requestBinding = [r \\in ResolutionIds |-> CHOOSE b \\in Bindings : TRUE]
  /\\ requestAuthority = [r \\in ResolutionIds |-> CHOOSE a \\in Authorities : TRUE]
  /\\ previousResolutionCommitment = [r \\in ResolutionIds |-> NoCommitment]
  /\\ terminalRecord = [r \\in ResolutionIds |-> NoRecord]
  /\\ terminalBinding = [r \\in ResolutionIds |-> CHOOSE b \\in Bindings : TRUE]
  /\\ terminalAuthority = [r \\in ResolutionIds |-> CHOOSE a \\in Authorities : TRUE]
  /\\ conflicts = {{}}
  /\\ invalidMaterial = {{}}
  /\\ observedInputs = {{}}

CanonRegisterRequest(r, b, a, previous) ==
  /\\ r \\in ResolutionIds \\ requests
  /\\ b \\in Bindings
  /\\ a \\in Authorities
  /\\ <<a, b>> \\in localAuthorityBindings
  /\\ \\/ previous = NoCommitment
     \\/ previous \\in RecognizedTerminalCommitments
  /\\ requests' = requests \\cup {{r}}
  /\\ requestBinding' = [requestBinding EXCEPT ![r] = b]
  /\\ requestAuthority' = [requestAuthority EXCEPT ![r] = a]
  /\\ previousResolutionCommitment' = [previousResolutionCommitment EXCEPT ![r] = previous]
  /\\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

CanonSubmitResolution(r, b, a, value) ==
  /\\ r \\in requests
  /\\ b = requestBinding[r]
  /\\ a \\in Authorities
  /\\ <<a, b>> \\in authorityProofBindings
  /\\ value \\in CanonTerminalResolutions
  /\\ terminalRecord[r] = NoRecord
  /\\ r \\notin conflicts
  /\\ terminalRecord' = [terminalRecord EXCEPT ![r] = value]
  /\\ terminalBinding' = [terminalBinding EXCEPT ![r] = b]
  /\\ terminalAuthority' = [terminalAuthority EXCEPT ![r] = a]
  /\\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

CanonObserveConflict(r) ==
  /\\ r \\in ResolutionIds
  /\\ conflicts' = conflicts \\cup {{r}}
  /\\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  invalidMaterial,
                  observedInputs>>

CanonObserveInvalidMaterial(r) ==
  /\\ r \\in ResolutionIds
  /\\ invalidMaterial' = invalidMaterial \\cup {{r}}
  /\\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  observedInputs>>

CanonObserveNonAuthoritativeInput(r) ==
  /\\ r \\in ResolutionIds
  /\\ observedInputs' = observedInputs \\cup {{r}}
  /\\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial>>

CanonEvaluate == UNCHANGED vars

CanonRecognizedCanonicalTransition ==
  \\/ \\E r \\in ResolutionIds, b \\in Bindings, a \\in Authorities,
        previous \\in TerminalCommitments \\cup {{NoCommitment}} :
        CanonRegisterRequest(r, b, a, previous)
  \\/ \\E r \\in ResolutionIds, b \\in Bindings, a \\in Authorities,
        value \\in CanonTerminalResolutions :
        CanonSubmitResolution(r, b, a, value)
  \\/ \\E r \\in ResolutionIds : CanonObserveConflict(r)
  \\/ \\E r \\in ResolutionIds : CanonObserveInvalidMaterial(r)
  \\/ \\E r \\in ResolutionIds : CanonObserveNonAuthoritativeInput(r)

CanonNext ==
  \\/ CanonRecognizedCanonicalTransition
  \\/ CanonEvaluate

CanonResolutionOf(r) ==
  IF r \\notin requests \\/ r \\in conflicts
  THEN CanonConflictResult
  ELSE IF terminalRecord[r] = NoRecord
       THEN CanonDerivedResolution
       ELSE terminalRecord[r]

CanonEffectPermitted(r) ==
  CanonResolutionOf(r) = CanonEffectPermittedValue

CanonSpec == CanonInit /\\ [][CanonNext]_vars
=============================================================================
"""


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
        ok = (
            OUTPUT_PATH.is_file() and OUTPUT_PATH.read_text(encoding="utf-8") == content
        )
        print("CANON_TLA_PROJECTION_PARITY=" + ("PASS" if ok else "DIFFERENT"))
        return 0 if ok else 1

    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print("CANON_TLA_PROJECTION_GENERATED=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
