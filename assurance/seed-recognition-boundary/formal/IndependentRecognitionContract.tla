-------------------- MODULE IndependentRecognitionContract --------------------
EXTENDS FiniteSets, Sequences

(***************************************************************************)
(* Independent source contract for local causal recognition.               *)
(*                                                                         *)
(* This module deliberately does NOT instantiate or reference GCR or Seed. *)
(* It defines the source semantics in native terms.                         *)
(*                                                                         *)
(* A1 Genesis anchoring                                                    *)
(* A2 causal next-state evolution                                          *)
(* A3 frozen additive recognized history                                   *)
(* A4 local recognition of a specific subject                              *)
(* A5 pre-decision subject identity                                        *)
(* A6 local Authority relation                                             *)
(* A7 controlled effect requires effective admission                       *)
(* A8 single crossing per decision id                                      *)
(* A9 is external projection adequacy, formalized separately in            *)
(*    IndependentProjectionAdequacy.tla.                                   *)
(***************************************************************************)

CONSTANTS DecisionIds, NativeAuthorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment,
          NativeAuthoritySubjects, Genesis, NativeEvents,
          NativeContexts, NativeDescriptors, NativePolicyEpochs, NativeScopes

ASSUME DecisionIds # {}
ASSUME NativeAuthorities # {}
ASSUME NativeEvents # {}
ASSUME NativeContexts # {}
ASSUME NativeDescriptors # {}
ASSUME NativePolicyEpochs # {}
ASSUME NativeScopes # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments

NativeStatuses == {"UNRESOLVED", "ADMIT", "REJECT"}
NativeTerminalOutcomes == {"ADMIT", "REJECT"}

NativeLineageEntryType ==
  [resolution_id : DecisionIds,
   event : NativeEvents]

NativeLineagePrefixes == Seq(NativeLineageEntryType)

Subject == INSTANCE DecisionSubjectBinding
  WITH Contexts <- NativeContexts,
       GenesisValues <- {Genesis},
       Prefixes <- NativeLineagePrefixes,
       Descriptors <- NativeDescriptors,
       PolicyEpochs <- NativePolicyEpochs,
       Scopes <- NativeScopes

NativeSubjects == Subject!Bindings

NativeSubjectOf(c, prefix, d, policy, scope) ==
  Subject!BindingOf(c, Genesis, prefix, d, policy, scope)

ASSUME NativeAuthoritySubjects \subseteq NativeAuthorities \X NativeSubjects

NativeRequestMetaType ==
  [binding : NativeSubjects,
   previous : TerminalCommitments \cup {NoCommitment}]

NativeTerminalMetaType ==
  [outcome : NativeTerminalOutcomes,
   authority : NativeAuthorities]

VARIABLES
    nativeRequestMeta,
    nativeTerminalMeta,
    nativeConflicts,
    nativeLineage,
    nativeCrossed

nativeRecognitionVars == <<nativeRequestMeta, nativeTerminalMeta, nativeConflicts>>
nativeLineageVars == <<nativeLineage, nativeCrossed>>
nativeVars == <<nativeRequestMeta, nativeTerminalMeta, nativeConflicts,
                nativeLineage, nativeCrossed>>

NativeRequests == DOMAIN nativeRequestMeta
NativeTerminalRequests == DOMAIN nativeTerminalMeta

NativeRequestBinding(r) == nativeRequestMeta[r].binding
NativePreviousCommitment(r) == nativeRequestMeta[r].previous
NativeTerminalOutcome(r) == nativeTerminalMeta[r].outcome
NativeTerminalAuthority(r) == nativeTerminalMeta[r].authority

NativeInit ==
  /\ nativeRequestMeta = [r \in {} |-> r]
  /\ nativeTerminalMeta = [r \in {} |-> r]
  /\ nativeConflicts = {}
  /\ nativeLineage = <<>>
  /\ nativeCrossed = {}

NativeOpen(r, c, d, policy, scope, a, previous) ==
  LET subject == NativeSubjectOf(c, nativeLineage, d, policy, scope)
  IN
    /\ r \in DecisionIds \ NativeRequests
    /\ c \in NativeContexts
    /\ d \in NativeDescriptors
    /\ policy \in NativePolicyEpochs
    /\ scope \in NativeScopes
    /\ subject \in NativeSubjects
    /\ a \in NativeAuthorities
    /\ <<a, subject>> \in NativeAuthoritySubjects
    /\ \/ previous = NoCommitment
       \/ previous \in RecognizedTerminalCommitments
    /\ nativeRequestMeta' =
         [x \in NativeRequests \cup {r} |->
            IF x = r
            THEN [binding |-> subject, previous |-> previous]
            ELSE nativeRequestMeta[x]]
    /\ UNCHANGED <<nativeTerminalMeta, nativeConflicts>>
    /\ UNCHANGED nativeLineageVars

NativeDecide(r, subject, a, outcome) ==
  /\ r \in NativeRequests
  /\ subject = NativeRequestBinding(r)
  /\ a \in NativeAuthorities
  /\ <<a, subject>> \in NativeAuthoritySubjects
  /\ outcome \in NativeTerminalOutcomes
  /\ r \notin NativeTerminalRequests
  /\ r \notin nativeConflicts
  /\ nativeTerminalMeta' =
       [x \in NativeTerminalRequests \cup {r} |->
          IF x = r
          THEN [outcome |-> outcome, authority |-> a]
          ELSE nativeTerminalMeta[x]]
  /\ UNCHANGED <<nativeRequestMeta, nativeConflicts>>
  /\ UNCHANGED nativeLineageVars

NativeObserveConflict(r) ==
  /\ r \in NativeTerminalRequests \ nativeConflicts
  /\ nativeConflicts' = nativeConflicts \cup {r}
  /\ UNCHANGED <<nativeRequestMeta, nativeTerminalMeta>>
  /\ UNCHANGED nativeLineageVars

NativeStatusOf(r) ==
  IF r \notin NativeRequests \/ r \in nativeConflicts
  THEN "UNRESOLVED"
  ELSE IF r \notin NativeTerminalRequests
       THEN "UNRESOLVED"
       ELSE NativeTerminalOutcome(r)

NativeEffectAdmitted(r) == NativeStatusOf(r) = "ADMIT"

NativeCross(r, e) ==
  /\ r \in NativeRequests
  /\ r \notin nativeCrossed
  /\ e \in NativeEvents
  /\ NativeEffectAdmitted(r)
  /\ nativeLineage' =
       Append(nativeLineage, [resolution_id |-> r, event |-> e])
  /\ nativeCrossed' = nativeCrossed \cup {r}
  /\ UNCHANGED nativeRecognitionVars

NativeSeedLikeTransition ==
  \/ \E r \in DecisionIds,
        c \in NativeContexts,
        d \in NativeDescriptors,
        policy \in NativePolicyEpochs,
        scope \in NativeScopes,
        a \in NativeAuthorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
       NativeOpen(r, c, d, policy, scope, a, previous)
  \/ \E r \in DecisionIds,
        subject \in NativeSubjects,
        a \in NativeAuthorities,
        outcome \in NativeTerminalOutcomes :
       NativeDecide(r, subject, a, outcome)

NativeEnvironmentTransition ==
  \E r \in DecisionIds : NativeObserveConflict(r)

NativeApplicationTransition ==
  \E r \in DecisionIds, e \in NativeEvents : NativeCross(r, e)

NativeNext ==
  \/ NativeSeedLikeTransition
  \/ NativeEnvironmentTransition
  \/ NativeApplicationTransition

NativeTypeOK ==
  /\ DOMAIN nativeRequestMeta \subseteq DecisionIds
  /\ nativeRequestMeta \in [DOMAIN nativeRequestMeta -> NativeRequestMetaType]
  /\ DOMAIN nativeTerminalMeta \subseteq DecisionIds
  /\ nativeTerminalMeta \in [DOMAIN nativeTerminalMeta -> NativeTerminalMetaType]
  /\ nativeConflicts \subseteq NativeTerminalRequests
  /\ nativeLineage \in NativeLineagePrefixes
  /\ nativeCrossed \subseteq DecisionIds

NativeLineageFrozenAdditiveStep ==
  \/ nativeLineage' = nativeLineage
  \/ \E entry \in NativeLineageEntryType :
       nativeLineage' = Append(nativeLineage, entry)

NativeNewCrossRequiresAdmitStep ==
  \A r \in nativeCrossed' \ nativeCrossed : NativeEffectAdmitted(r)

NativeCrossedMonotoneStep ==
  nativeCrossed \subseteq nativeCrossed'

NativeSpec == NativeInit /\ [][NativeNext]_nativeVars

=============================================================================
