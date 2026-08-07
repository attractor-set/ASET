---------------- MODULE SeedCanonProjection ----------------
EXTENDS FiniteSets

(*
GENERATED FILE. DO NOT EDIT.
Source: seed/canonical/source/seed-model.json
Source SHA-256: sha256:c43ca7b642a11c3ab140884a6bbff34bbd741f5cb905e6a779c860c813998fcf
Projection profile: ASET-SEED-CANON-TLA-PROJECTION-V4

V4 is a standalone projection. It does not EXTEND or import SeedResolution.
The refinement proof explicitly instantiates this model onto the target state.
Seed-owned state is requestMeta + terminalMeta. Conflict is environment state.
EVALUATE_RESOLUTION is a pure observer and is not part of CanonNext.
*)

CONSTANTS ResolutionIds, Bindings, Authorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment,
          RequestAuthorityBindings, TerminalAuthorityBindings

ASSUME ResolutionIds # {}
ASSUME Bindings # {}
ASSUME Authorities # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME RequestAuthorityBindings \subseteq Authorities \X Bindings
ASSUME TerminalAuthorityBindings \subseteq Authorities \X Bindings
ASSUME RequestAuthorityBindings \subseteq TerminalAuthorityBindings

CanonResolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
CanonTerminalResolutions == {"ALLOW", "BLOCK"}
CanonDerivedResolution == "UNKNOWN"
CanonEffectPermittedValue == "ALLOW"
CanonFailClosedValues == {"UNKNOWN", "BLOCK"}
CanonConflictResult == "UNKNOWN"

CanonRequestMetaType ==
  [binding : Bindings,
   previous : TerminalCommitments \cup {NoCommitment}]

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
  /\ requestMeta = [r \in {} |-> r]
  /\ terminalMeta = [r \in {} |-> r]
  /\ conflicts = {}

CanonRegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ CanonRequests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in RequestAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requestMeta' =
       [x \in CanonRequests \cup {r} |->
          IF x = r
          THEN [binding |-> b, previous |-> previous]
          ELSE requestMeta[x]]
  /\ UNCHANGED <<terminalMeta, conflicts>>

CanonSubmitResolution(r, b, a, value) ==
  /\ r \in CanonRequests
  /\ b = CanonRequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in TerminalAuthorityBindings
  /\ value \in CanonTerminalResolutions
  /\ r \notin CanonTerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in CanonTerminalRequests \cup {r} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>

CanonObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED CanonSeedVars

CanonRecognizedSeedTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
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
