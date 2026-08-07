------------------------------ MODULE SeedResolution ------------------------------
EXTENDS FiniteSets

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

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

RequestMetaType ==
  [binding : Bindings,
   previous : TerminalCommitments \cup {NoCommitment}]

TerminalMetaType ==
  [resolution : TerminalResolutions,
   authority : Authorities]

(* Bounded TLC fixture relations. They are configuration helpers only. *)
TLC_Authority1 == CHOOSE a \in Authorities : TRUE
TLC_Authority2 == CHOOSE a \in Authorities \ {TLC_Authority1} : TRUE
TLC_Binding1 == CHOOSE b \in Bindings : TRUE
TLC_Binding2 == CHOOSE b \in Bindings \ {TLC_Binding1} : TRUE

TLC_RequestAuthorityBindings ==
  {<<TLC_Authority1, TLC_Binding1>>,
   <<TLC_Authority2, TLC_Binding2>>}

TLC_TerminalAuthorityBindings ==
  TLC_RequestAuthorityBindings \cup
    {<<TLC_Authority2, TLC_Binding1>>}

(*
Seed-owned state and environment state are deliberately separated.

- requestMeta and terminalMeta are the only Seed-owned mutable state.
- conflicts is an environment observation because a later independently
  established conflicting valid terminal record changes the derived resolution.
- invalid/unrecognized/non-authoritative material has no state slot and is not
  a transition. It cannot mutate accepted Seed state by construction.
*)
VARIABLES
    requestMeta,
    terminalMeta,
    conflicts

seedVars == <<requestMeta, terminalMeta>>
environmentVars == <<conflicts>>
vars == <<requestMeta, terminalMeta, conflicts>>

Requests == DOMAIN requestMeta
TerminalRequests == DOMAIN terminalMeta

RequestBinding(r) == requestMeta[r].binding
PreviousCommitment(r) == requestMeta[r].previous
TerminalResolution(r) == terminalMeta[r].resolution
TerminalAuthority(r) == terminalMeta[r].authority
TerminalBinding(r) == RequestBinding(r)

Init ==
  /\ requestMeta = [r \in {} |-> r]
  /\ terminalMeta = [r \in {} |-> r]
  /\ conflicts = {}

RegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ Requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in RequestAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requestMeta' =
       [x \in Requests \cup {r} |->
          IF x = r
          THEN [binding |-> b, previous |-> previous]
          ELSE requestMeta[x]]
  /\ UNCHANGED <<terminalMeta, conflicts>>

SubmitResolution(r, b, a, value) ==
  /\ r \in Requests
  /\ b = RequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in TerminalAuthorityBindings
  /\ value \in TerminalResolutions
  /\ r \notin TerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in TerminalRequests \cup {r} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>

(* Environment transition: it changes only environment state. *)
ObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED seedVars

RecognizedSeedTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        RegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)

RecognizedEnvironmentTransition ==
  \E r \in ResolutionIds : ObserveConflict(r)

Next ==
  \/ RecognizedSeedTransition
  \/ RecognizedEnvironmentTransition

ResolutionOf(r) ==
  IF r \notin Requests \/ r \in conflicts
  THEN "UNKNOWN"
  ELSE IF r \notin TerminalRequests
       THEN "UNKNOWN"
       ELSE TerminalResolution(r)

EffectPermitted(r) == ResolutionOf(r) = "ALLOW"

(* Pure observer corresponding to wire operation EVALUATE_RESOLUTION. *)
EvaluateResolution(r) ==
  [resolution |-> ResolutionOf(r),
   effect_permitted |-> EffectPermitted(r)]

TypeOK ==
  /\ DOMAIN requestMeta \subseteq ResolutionIds
  /\ requestMeta \in [DOMAIN requestMeta -> RequestMetaType]
  /\ DOMAIN terminalMeta \subseteq ResolutionIds
  /\ terminalMeta \in [DOMAIN terminalMeta -> TerminalMetaType]
  /\ conflicts \subseteq ResolutionIds

ResolutionDomain ==
  \A r \in ResolutionIds : ResolutionOf(r) \in Resolutions

AllowSoundness ==
  \A r \in ResolutionIds :
    EffectPermitted(r) =>
      /\ r \in Requests
      /\ r \notin conflicts
      /\ r \in TerminalRequests
      /\ TerminalResolution(r) = "ALLOW"
      /\ <<TerminalAuthority(r), RequestBinding(r)>>
           \in TerminalAuthorityBindings

FailClosed ==
  \A r \in ResolutionIds :
    ResolutionOf(r) # "ALLOW" => ~EffectPermitted(r)

TerminalBindingDerived ==
  \A r \in TerminalRequests :
    /\ r \in Requests
    /\ TerminalBinding(r) = RequestBinding(r)

RequestAuthorityRecognized ==
  \A r \in Requests :
    \E a \in Authorities :
      <<a, RequestBinding(r)>> \in RequestAuthorityBindings

TerminalAuthorityRecognized ==
  \A r \in TerminalRequests :
    /\ r \in Requests
    /\ <<TerminalAuthority(r), RequestBinding(r)>>
         \in TerminalAuthorityBindings

(* One keyed terminal metadata cell makes multiple accepted terminals unrepresentable. *)
TerminalUnique ==
  terminalMeta \in [DOMAIN terminalMeta -> TerminalMetaType]

ConflictUnknown ==
  \A r \in conflicts : ResolutionOf(r) = "UNKNOWN"

FreshReconsideration ==
  \A r \in Requests :
    \/ PreviousCommitment(r) = NoCommitment
    \/ PreviousCommitment(r) \in RecognizedTerminalCommitments

TerminalRecordRequiresRequest ==
  TerminalRequests \subseteq Requests

SeedStateSafety ==
  /\ TypeOK
  /\ ResolutionDomain
  /\ AllowSoundness
  /\ FailClosed
  /\ TerminalBindingDerived
  /\ RequestAuthorityRecognized
  /\ TerminalAuthorityRecognized
  /\ TerminalUnique
  /\ ConflictUnknown
  /\ FreshReconsideration

InductiveInvariant ==
  /\ TypeOK
  /\ TerminalBindingDerived
  /\ RequestAuthorityRecognized
  /\ TerminalAuthorityRecognized
  /\ FreshReconsideration
  /\ TerminalRecordRequiresRequest

RequestsAppendOnlyStep ==
  Requests \subseteq Requests'

RequestsAppendOnly ==
  [][RequestsAppendOnlyStep]_vars

TerminalRecordsImmutableStep ==
  \A r \in TerminalRequests :
    /\ r \in TerminalRequests'
    /\ terminalMeta'[r] = terminalMeta[r]

TerminalRecordsImmutable ==
  [][TerminalRecordsImmutableStep]_vars

SeedStateChangesOnlyByRecognizedTransitionStep ==
  seedVars' # seedVars => RecognizedSeedTransition

SeedStateChangesOnlyByRecognizedTransition ==
  [][SeedStateChangesOnlyByRecognizedTransitionStep]_vars

ConflictObservationPreservesSeedStateStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED seedVars

ConflictObservationPreservesSeedState ==
  [][ConflictObservationPreservesSeedStateStep]_vars

Spec == Init /\ [][Next]_vars
=================================================================================
