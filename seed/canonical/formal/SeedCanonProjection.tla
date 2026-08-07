---------------- MODULE SeedCanonProjection ----------------
EXTENDS SeedResolution

(*
GENERATED FILE. DO NOT EDIT.
Source: seed/canonical/source/seed-model.json
Source SHA-256: sha256:b5e68692317600fd2833474a1f9c31f09e44d37ae92ec14573b416076c5dd7f6
Projection profile: ASET-SEED-CANON-TLA-PROJECTION-V3

V3 projects the same canonical behavior onto the normalized three-variable
Seed state. Immutable Authority relations are context constants. Accepted
terminal binding is derived from requestMeta; invalid/non-authoritative inputs
are stuttering observations rather than retained canonical state.
*)

CanonResolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
CanonTerminalResolutions == {"ALLOW", "BLOCK"}
CanonDerivedResolution == "UNKNOWN"
CanonEffectPermittedValue == "ALLOW"
CanonFailClosedValues == {"UNKNOWN", "BLOCK"}
CanonConflictResult == "UNKNOWN"

CanonInit ==
  /\ requestMeta = [r \in {} |-> r]
  /\ terminalMeta = [r \in {} |-> r]
  /\ conflicts = {}

CanonRegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ Requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in LocalAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requestMeta' =
       [x \in Requests \cup {r} |->
          IF x = r
          THEN [binding |-> b, previous |-> previous]
          ELSE requestMeta[x]]
  /\ UNCHANGED <<terminalMeta, conflicts>>

CanonSubmitResolution(r, b, a, value) ==
  /\ r \in Requests
  /\ b = RequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in AuthorityProofBindings
  /\ value \in CanonTerminalResolutions
  /\ r \notin TerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in TerminalRequests \cup {r} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>

CanonObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<requestMeta, terminalMeta>>

CanonObserveInvalidMaterial(r) ==
  /\ r \in ResolutionIds
  /\ UNCHANGED vars

CanonObserveNonAuthoritativeInput(r) ==
  /\ r \in ResolutionIds
  /\ UNCHANGED vars

CanonEvaluate == UNCHANGED vars

CanonRecognizedSeedTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        CanonRegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in CanonTerminalResolutions :
        CanonSubmitResolution(r, b, a, value)

CanonRecognizedEnvironmentTransition ==
  \/ \E r \in ResolutionIds : CanonObserveConflict(r)
  \/ \E r \in ResolutionIds : CanonObserveInvalidMaterial(r)
  \/ \E r \in ResolutionIds : CanonObserveNonAuthoritativeInput(r)

CanonRecognizedCanonicalTransition ==
  \/ CanonRecognizedSeedTransition
  \/ CanonRecognizedEnvironmentTransition

CanonNext ==
  \/ CanonRecognizedCanonicalTransition
  \/ CanonEvaluate

CanonResolutionOf(r) ==
  IF r \notin Requests \/ r \in conflicts
  THEN CanonConflictResult
  ELSE IF r \notin TerminalRequests
       THEN CanonDerivedResolution
       ELSE TerminalResolution(r)

CanonEffectPermitted(r) ==
  CanonResolutionOf(r) = CanonEffectPermittedValue

CanonSpec == CanonInit /\ [][CanonNext]_vars
=============================================================================
