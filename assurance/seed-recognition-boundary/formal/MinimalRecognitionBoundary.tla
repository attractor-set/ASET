-------------------- MODULE MinimalRecognitionBoundary --------------------
EXTENDS FiniteSets

(***************************************************************************)
(* Minimal source boundary for Seed-level recognition semantics.           *)
(*                                                                         *)
(* Native recognition state contains only:                                 *)
(*   request existence + previous commitment,                              *)
(*   one terminal ADMIT/REJECT result,                                     *)
(*   monotone conflict invalidation.                                       *)
(*                                                                         *)
(* Application state is arbitrary and is outside recognition projection.   *)
(***************************************************************************)

CONSTANTS DecisionIds,
          TerminalCommitments,
          RecognizedTerminalCommitments,
          NoCommitment,
          ApplicationStates,
          InitialApplicationState,
          AdapterBindings,
          AdapterBindingOf,
          AdapterAuthorities,
          AdapterAuthority

ASSUME DecisionIds # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME ApplicationStates # {}
ASSUME InitialApplicationState \in ApplicationStates
ASSUME AdapterBindings # {}
ASSUME AdapterBindingType ==
  AdapterBindingOf \in [DecisionIds -> AdapterBindings]
ASSUME AdapterAuthorities # {}
ASSUME AdapterAuthorityType ==
  AdapterAuthority \in AdapterAuthorities

MinStatuses == {"UNRESOLVED", "ADMIT", "REJECT"}
MinTerminalOutcomes == {"ADMIT", "REJECT"}

MinRequestMetaType ==
  [previous : TerminalCommitments \cup {NoCommitment}]

MinTerminalMetaType ==
  [outcome : MinTerminalOutcomes]

VARIABLES
    minRequestMeta,
    minTerminalMeta,
    minConflicts,
    minApplication

minRecognitionVars == <<minRequestMeta, minTerminalMeta, minConflicts>>
minVars == <<minRequestMeta, minTerminalMeta, minConflicts, minApplication>>

MinRequests == DOMAIN minRequestMeta
MinTerminalRequests == DOMAIN minTerminalMeta

MinPreviousCommitment(r) == minRequestMeta[r].previous
MinTerminalOutcome(r) == minTerminalMeta[r].outcome

MinInit ==
  /\ minRequestMeta = [r \in {} |-> r]
  /\ minTerminalMeta = [r \in {} |-> r]
  /\ minConflicts = {}
  /\ minApplication = InitialApplicationState

MinOpen(r, previous) ==
  /\ r \in DecisionIds \ MinRequests
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ minRequestMeta' =
       [x \in MinRequests \cup {r} |->
          IF x = r
          THEN [previous |-> previous]
          ELSE minRequestMeta[x]]
  /\ UNCHANGED <<minTerminalMeta, minConflicts, minApplication>>

MinDecide(r, outcome) ==
  /\ r \in MinRequests
  /\ outcome \in MinTerminalOutcomes
  /\ r \notin MinTerminalRequests
  /\ r \notin minConflicts
  /\ minTerminalMeta' =
       [x \in MinTerminalRequests \cup {r} |->
          IF x = r
          THEN [outcome |-> outcome]
          ELSE minTerminalMeta[x]]
  /\ UNCHANGED <<minRequestMeta, minConflicts, minApplication>>

MinObserveConflict(r) ==
  /\ r \in MinTerminalRequests \ minConflicts
  /\ minConflicts' = minConflicts \cup {r}
  /\ UNCHANGED <<minRequestMeta, minTerminalMeta, minApplication>>

MinApplicationStep(nextApplication) ==
  /\ nextApplication \in ApplicationStates
  /\ minApplication' = nextApplication
  /\ UNCHANGED minRecognitionVars

MinStatusOf(r) ==
  IF r \notin MinRequests \/ r \in minConflicts
  THEN "UNRESOLVED"
  ELSE IF r \notin MinTerminalRequests
       THEN "UNRESOLVED"
       ELSE MinTerminalOutcome(r)

MinRecognitionTransition ==
  \/ \E r \in DecisionIds,
        previous \in TerminalCommitments \cup {NoCommitment} :
       MinOpen(r, previous)
  \/ \E r \in DecisionIds,
        outcome \in MinTerminalOutcomes :
       MinDecide(r, outcome)
  \/ \E r \in DecisionIds :
       MinObserveConflict(r)

MinApplicationTransition ==
  \E nextApplication \in ApplicationStates :
    MinApplicationStep(nextApplication)

MinNext ==
  \/ MinRecognitionTransition
  \/ MinApplicationTransition

MinTypeOK ==
  /\ DOMAIN minRequestMeta \subseteq DecisionIds
  /\ minRequestMeta \in [DOMAIN minRequestMeta -> MinRequestMetaType]
  /\ DOMAIN minTerminalMeta \subseteq DecisionIds
  /\ minTerminalMeta \in [DOMAIN minTerminalMeta -> MinTerminalMetaType]
  /\ minConflicts \subseteq MinTerminalRequests
  /\ minApplication \in ApplicationStates

MinSpec == MinInit /\ [][MinNext]_minVars

=============================================================================
