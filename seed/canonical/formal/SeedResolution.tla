------------------------------ MODULE SeedResolution ------------------------------
EXTENDS FiniteSets

CONSTANTS ResolutionIds, Bindings, Authorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment,
          LocalAuthorityBindings, AuthorityProofBindings

ASSUME ResolutionIds # {}
ASSUME Bindings # {}
ASSUME Authorities # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME LocalAuthorityBindings \subseteq Authorities \X Bindings
ASSUME AuthorityProofBindings \subseteq Authorities \X Bindings
ASSUME LocalAuthorityBindings \subseteq AuthorityProofBindings

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

RequestMetaType ==
  [binding : Bindings,
   previous : TerminalCommitments \cup {NoCommitment}]

TerminalMetaType ==
  [resolution : TerminalResolutions,
   authority : Authorities]

(*
Bounded TLC fixture values for relation-valued constants. TLC configuration
files accept simple values and sets of simple values, but not tuple-valued set
literals. These operators are used only through cfg definition overrides; they
do not participate in the normative Seed transition semantics or TLAPS proofs.
The bounded cfg supplies exactly two Authorities and two Bindings.
*)
TLC_Authority1 == CHOOSE a \in Authorities : TRUE
TLC_Authority2 == CHOOSE a \in Authorities \ {TLC_Authority1} : TRUE
TLC_Binding1 == CHOOSE b \in Bindings : TRUE
TLC_Binding2 == CHOOSE b \in Bindings \ {TLC_Binding1} : TRUE

TLC_LocalAuthorityBindings ==
  {<<TLC_Authority1, TLC_Binding1>>,
   <<TLC_Authority2, TLC_Binding2>>}

TLC_AuthorityProofBindings ==
  TLC_LocalAuthorityBindings \cup
    {<<TLC_Authority2, TLC_Binding1>>}

(*
Minimal abstract state.

The two Authority relations are immutable context parameters rather than state:
Seed has no transition that mutates them. Request identity is represented once
in requestMeta; terminal state stores only facts that are not derivable from the
request. Consequently an accepted terminal binding cannot diverge from the
registered binding because there is no independent terminal-binding field.

Invalid material and non-authoritative inputs have no canonical state component.
They are modeled as explicit stuttering observations. Conflict is retained
because it changes the derived resolution to UNKNOWN even after a terminal
record exists.
*)
VARIABLES
    requestMeta,
    terminalMeta,
    conflicts

canonicalVars == <<requestMeta, terminalMeta, conflicts>>
vars == canonicalVars

Requests == DOMAIN requestMeta
TerminalRequests == DOMAIN terminalMeta

RequestBinding(r) == requestMeta[r].binding
PreviousCommitment(r) == requestMeta[r].previous
TerminalResolution(r) == terminalMeta[r].resolution
TerminalAuthority(r) == terminalMeta[r].authority

(* Binding of an accepted terminal record is derived from its immutable request. *)
TerminalBinding(r) == RequestBinding(r)

Init ==
  /\ requestMeta = [r \in {} |-> r]
  /\ terminalMeta = [r \in {} |-> r]
  /\ conflicts = {}

RegisterRequest(r, b, a, previous) ==
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

SubmitResolution(r, b, a, value) ==
  /\ r \in Requests
  /\ b = RequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in AuthorityProofBindings
  /\ value \in TerminalResolutions
  /\ r \notin TerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in TerminalRequests \cup {r} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>

ObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<requestMeta, terminalMeta>>

(* Invalid material cannot become accepted terminal state. *)
ObserveInvalidMaterial(r) ==
  /\ r \in ResolutionIds
  /\ UNCHANGED vars

(* Non-authoritative inputs have no canonical state representation. *)
ObserveNonAuthoritativeInput(r) ==
  /\ r \in ResolutionIds
  /\ UNCHANGED vars

Evaluate == UNCHANGED vars

RecognizedSeedTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        RegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)

RecognizedEnvironmentTransition ==
  \/ \E r \in ResolutionIds : ObserveConflict(r)
  \/ \E r \in ResolutionIds : ObserveInvalidMaterial(r)
  \/ \E r \in ResolutionIds : ObserveNonAuthoritativeInput(r)

RecognizedCanonicalTransition ==
  \/ RecognizedSeedTransition
  \/ RecognizedEnvironmentTransition

Next ==
  \/ RecognizedCanonicalTransition
  \/ Evaluate

ResolutionOf(r) ==
  IF r \notin Requests \/ r \in conflicts
  THEN "UNKNOWN"
  ELSE IF r \notin TerminalRequests
       THEN "UNKNOWN"
       ELSE TerminalResolution(r)

EffectPermitted(r) == ResolutionOf(r) = "ALLOW"

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
           \in AuthorityProofBindings

FailClosed ==
  \A r \in ResolutionIds :
    ResolutionOf(r) # "ALLOW" => ~EffectPermitted(r)

(* Exact binding is structural: accepted terminal state has no second binding. *)
TerminalBindingDerived ==
  \A r \in TerminalRequests :
    /\ r \in Requests
    /\ TerminalBinding(r) = RequestBinding(r)

LocalAuthorityRoot ==
  \A r \in Requests :
    \E a \in Authorities :
      <<a, RequestBinding(r)>> \in LocalAuthorityBindings

DelegatedAuthoritySound ==
  \A r \in TerminalRequests :
    /\ r \in Requests
    /\ <<TerminalAuthority(r), RequestBinding(r)>>
         \in AuthorityProofBindings

(*
Structural assurance: the complete canonical decision state is exactly the
three variables above; non-authoritative inputs have no independent state slot.
*)
InputsNonAuthoritative ==
  canonicalVars = <<requestMeta, terminalMeta, conflicts>>

(* A function keyed by resolution_id makes multiple accepted terminals unrepresentable. *)
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
  /\ LocalAuthorityRoot
  /\ DelegatedAuthoritySound
  /\ InputsNonAuthoritative
  /\ TerminalUnique
  /\ ConflictUnknown
  /\ FreshReconsideration

InductiveInvariant ==
  /\ TypeOK
  /\ TerminalBindingDerived
  /\ LocalAuthorityRoot
  /\ DelegatedAuthoritySound
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

CanonicalStateChangesOnlyByRecognizedTransitionStep ==
  canonicalVars' # canonicalVars => RecognizedCanonicalTransition

CanonicalStateChangesOnlyByRecognizedTransition ==
  [][CanonicalStateChangesOnlyByRecognizedTransitionStep]_vars

InvalidMaterialStutterStep ==
  \A r \in ResolutionIds :
    ObserveInvalidMaterial(r) => UNCHANGED vars

InvalidMaterialStutter ==
  [][InvalidMaterialStutterStep]_vars

NonAuthoritativeInputsStutterStep ==
  \A r \in ResolutionIds :
    ObserveNonAuthoritativeInput(r) => UNCHANGED vars

NonAuthoritativeInputsStutter ==
  [][NonAuthoritativeInputsStutterStep]_vars

Spec == Init /\ [][Next]_vars
=================================================================================
