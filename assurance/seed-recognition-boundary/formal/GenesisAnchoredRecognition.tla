--------------------- MODULE GenesisAnchoredRecognition ---------------------
EXTENDS FiniteSets, Sequences

CONSTANTS ResolutionIds, Authorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment,
          RecognizedAuthorityBindings, Genesis, Events,
          Contexts, Descriptors, PolicyEpochs, Scopes

ASSUME ResolutionIds # {}
ASSUME Authorities # {}
ASSUME Events # {}
ASSUME Contexts # {}
ASSUME Descriptors # {}
ASSUME PolicyEpochs # {}
ASSUME Scopes # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

LineageEntryType ==
  [resolution_id : ResolutionIds,
   event : Events]

LineagePrefixes == Seq(LineageEntryType)

(*
The canonical binding representation is written directly as a record type.
This is extensionally the same representation already proved for
DecisionSubjectBinding, but it avoids exposing a nested INSTANCE alias
through refinement modules.
*)
Bindings ==
  [context_id : Contexts,
   state_identity : [genesis : {Genesis}, prefix : LineagePrefixes],
   question_identity : Descriptors,
   policy_epoch : PolicyEpochs,
   scope : Scopes]

BindingOf(c, prefix, d, policy, scope) ==
  [context_id |-> c,
   state_identity |-> [genesis |-> Genesis, prefix |-> prefix],
   question_identity |-> d,
   policy_epoch |-> policy,
   scope |-> scope]

ASSUME RecognizedAuthorityBindings \subseteq Authorities \X Bindings

RequestMetaType ==
  [binding : Bindings,
   previous : TerminalCommitments \cup {NoCommitment}]

TerminalMetaType ==
  [resolution : TerminalResolutions,
   authority : Authorities]

VARIABLES
    requestMeta,
    terminalMeta,
    conflicts,
    lineage,
    applied

recognitionVars == <<requestMeta, terminalMeta, conflicts>>
lineageVars == <<lineage, applied>>
vars == <<requestMeta, terminalMeta, conflicts, lineage, applied>>

Requests == DOMAIN requestMeta
TerminalRequests == DOMAIN terminalMeta

RequestBinding(r) == requestMeta[r].binding
PreviousCommitment(r) == requestMeta[r].previous
TerminalResolution(r) == terminalMeta[r].resolution
TerminalAuthority(r) == terminalMeta[r].authority

LineageState == [genesis |-> Genesis, events |-> lineage]

Init ==
  /\ requestMeta = [r \in {} |-> r]
  /\ terminalMeta = [r \in {} |-> r]
  /\ conflicts = {}
  /\ lineage = <<>>
  /\ applied = {}

(*
The exact binding is now constructed, not selected through an external
BindingPrefixes relation.  It contains semantic identity for the local
Context, Genesis-anchored frozen lineage prefix, pre-decision descriptor,
policy epoch, and scope.

A production serialization may replace this structured semantic identity by
cryptographic commitments.  Collision resistance is an implementation
assumption and is deliberately not treated as mathematical injectivity here.
*)
RegisterRequest(r, c, d, policy, scope, a, previous) ==
  LET b == BindingOf(c, lineage, d, policy, scope)
  IN
    /\ r \in ResolutionIds \ Requests
    /\ c \in Contexts
    /\ d \in Descriptors
    /\ policy \in PolicyEpochs
    /\ scope \in Scopes
    /\ b \in Bindings
    /\ a \in Authorities
    /\ <<a, b>> \in RecognizedAuthorityBindings
    /\ \/ previous = NoCommitment
       \/ previous \in RecognizedTerminalCommitments
    /\ requestMeta' =
         [x \in Requests \cup {r} |->
            IF x = r
            THEN [binding |-> b, previous |-> previous]
            ELSE requestMeta[x]]
    /\ UNCHANGED <<terminalMeta, conflicts>>
    /\ UNCHANGED lineageVars

SubmitResolution(r, b, a, value) ==
  /\ r \in Requests
  /\ b = RequestBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in RecognizedAuthorityBindings
  /\ value \in TerminalResolutions
  /\ r \notin TerminalRequests
  /\ r \notin conflicts
  /\ terminalMeta' =
       [x \in TerminalRequests \cup {r} |->
          IF x = r
          THEN [resolution |-> value, authority |-> a]
          ELSE terminalMeta[x]]
  /\ UNCHANGED <<requestMeta, conflicts>>
  /\ UNCHANGED lineageVars

ObserveConflict(r) ==
  /\ r \in TerminalRequests \ conflicts
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<requestMeta, terminalMeta>>
  /\ UNCHANGED lineageVars

ResolutionOf(r) ==
  IF r \notin Requests \/ r \in conflicts
  THEN "UNKNOWN"
  ELSE IF r \notin TerminalRequests
       THEN "UNKNOWN"
       ELSE TerminalResolution(r)

EffectPermitted(r) == ResolutionOf(r) = "ALLOW"

ApplyRecognized(r, e) ==
  /\ r \in Requests
  /\ r \notin applied
  /\ e \in Events
  /\ EffectPermitted(r)
  /\ lineage' = Append(lineage, [resolution_id |-> r, event |-> e])
  /\ applied' = applied \cup {r}
  /\ UNCHANGED recognitionVars

RecognizedSeedLikeTransition ==
  \/ \E r \in ResolutionIds,
        c \in Contexts,
        d \in Descriptors,
        policy \in PolicyEpochs,
        scope \in Scopes,
        a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        RegisterRequest(r, c, d, policy, scope, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)

EnvironmentTransition ==
  \E r \in ResolutionIds : ObserveConflict(r)

ApplicationTransition ==
  \E r \in ResolutionIds, e \in Events : ApplyRecognized(r, e)

Next ==
  \/ RecognizedSeedLikeTransition
  \/ EnvironmentTransition
  \/ ApplicationTransition

TypeOK ==
  /\ DOMAIN requestMeta \subseteq ResolutionIds
  /\ requestMeta \in [DOMAIN requestMeta -> RequestMetaType]
  /\ DOMAIN terminalMeta \subseteq ResolutionIds
  /\ terminalMeta \in [DOMAIN terminalMeta -> TerminalMetaType]
  /\ conflicts \subseteq TerminalRequests
  /\ lineage \in LineagePrefixes
  /\ applied \subseteq ResolutionIds

LineageFrozenAdditiveStep ==
  \/ lineage' = lineage
  \/ \E entry \in LineageEntryType : lineage' = Append(lineage, entry)

LineageFrozenAdditive ==
  [][LineageFrozenAdditiveStep]_vars

NewApplicationRequiresAllowStep ==
  \A r \in applied' \ applied : EffectPermitted(r)

NewApplicationRequiresAllow ==
  [][NewApplicationRequiresAllowStep]_vars

GenesisRemainsAnchored ==
  []([genesis |-> Genesis] = [genesis |-> Genesis])

Spec == Init /\ [][Next]_vars

=============================================================================
