---------------- MODULE SeedCanonProjection ----------------
EXTENDS SeedResolution

(*
GENERATED FILE. DO NOT EDIT.
Source: seed/canonical/source/seed-model.json
Source SHA-256: sha256:b5e68692317600fd2833474a1f9c31f09e44d37ae92ec14573b416076c5dd7f6
Projection profile: ASET-SEED-CANON-TLA-PROJECTION-V2

This module is the deterministic TLA+ interpretation used by the
canon-to-TLA refinement assurance. It intentionally preserves the declared
opaque Binding, authorityProofBindings and RecognizedTerminalCommitments
abstractions.
*)

CanonResolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
CanonTerminalResolutions == {"ALLOW", "BLOCK"}
CanonDerivedResolution == "UNKNOWN"
CanonEffectPermittedValue == "ALLOW"
CanonFailClosedValues == {"UNKNOWN", "BLOCK"}
CanonConflictResult == "UNKNOWN"

CanonInit ==
  /\ localAuthorityBindings \in SUBSET (Authorities \X Bindings)
  /\ authorityProofBindings \in SUBSET (Authorities \X Bindings)
  /\ localAuthorityBindings \subseteq authorityProofBindings
  /\ requests = {}
  /\ requestBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ requestAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ previousResolutionCommitment = [r \in ResolutionIds |-> NoCommitment]
  /\ terminalRecord = [r \in ResolutionIds |-> NoRecord]
  /\ terminalBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ terminalAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ conflicts = {}
  /\ invalidMaterial = {}
  /\ observedInputs = {}

CanonRegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in localAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requests' = requests \cup {r}
  /\ requestBinding' = [requestBinding EXCEPT ![r] = b]
  /\ requestAuthority' = [requestAuthority EXCEPT ![r] = a]
  /\ previousResolutionCommitment' = [previousResolutionCommitment EXCEPT ![r] = previous]
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

CanonSubmitResolution(r, b, a, value) ==
  /\ r \in requests
  /\ b = requestBinding[r]
  /\ a \in Authorities
  /\ <<a, b>> \in authorityProofBindings
  /\ value \in CanonTerminalResolutions
  /\ terminalRecord[r] = NoRecord
  /\ r \notin conflicts
  /\ terminalRecord' = [terminalRecord EXCEPT ![r] = value]
  /\ terminalBinding' = [terminalBinding EXCEPT ![r] = b]
  /\ terminalAuthority' = [terminalAuthority EXCEPT ![r] = a]
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

CanonObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
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
  /\ r \in ResolutionIds
  /\ invalidMaterial' = invalidMaterial \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
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
  /\ r \in ResolutionIds
  /\ observedInputs' = observedInputs \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
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
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        CanonRegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in CanonTerminalResolutions :
        CanonSubmitResolution(r, b, a, value)
  \/ \E r \in ResolutionIds : CanonObserveConflict(r)
  \/ \E r \in ResolutionIds : CanonObserveInvalidMaterial(r)
  \/ \E r \in ResolutionIds : CanonObserveNonAuthoritativeInput(r)

CanonNext ==
  \/ CanonRecognizedCanonicalTransition
  \/ CanonEvaluate

CanonResolutionOf(r) ==
  IF r \notin requests \/ r \in conflicts
  THEN CanonConflictResult
  ELSE IF terminalRecord[r] = NoRecord
       THEN CanonDerivedResolution
       ELSE terminalRecord[r]

CanonEffectPermitted(r) ==
  CanonResolutionOf(r) = CanonEffectPermittedValue

CanonSpec == CanonInit /\ [][CanonNext]_vars
=============================================================================
