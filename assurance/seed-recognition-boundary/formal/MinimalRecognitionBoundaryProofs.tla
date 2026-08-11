---------------- MODULE MinimalRecognitionBoundaryProofs ----------------
EXTENDS MinimalRecognitionBoundary, TLAPS

(***************************************************************************)
(* Local operational safety lemmas for the minimal boundary.               *)
(*                                                                         *)
(* An earlier proof attempt used a global dynamic-domain TypeOK induction. That invariant *)
(* is auxiliary and is not a premise of the direct Seed refinement.        *)
(* This proof keeps the source model unchanged and proves the actual operational   *)
(* guards/stutter properties used to characterize the source boundary.     *)
(***************************************************************************)

THEOREM MinOpenRequiresFreshDecisionId ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => r \in DecisionIds \ MinRequests
PROOF
  BY DEF MinOpen

THEOREM MinOpenRequiresRecognizedPreviousOrNone ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => \/ previous = NoCommitment
         \/ previous \in RecognizedTerminalCommitments
PROOF
  BY DEF MinOpen

THEOREM MinOpenPreservesTerminalConflictApplication ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => UNCHANGED <<minTerminalMeta, minConflicts, minApplication>>
PROOF
  BY DEF MinOpen

THEOREM MinDecideRequiresOpenFreshNonconflictedRequest ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => /\ r \in MinRequests
         /\ r \notin MinTerminalRequests
         /\ r \notin minConflicts
         /\ outcome \in MinTerminalOutcomes
PROOF
  BY DEF MinDecide

THEOREM MinDecidePreservesRequestConflictApplication ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => UNCHANGED <<minRequestMeta, minConflicts, minApplication>>
PROOF
  BY DEF MinDecide

THEOREM MinConflictRequiresTerminalNonconflictedRequest ==
  \A r \in DecisionIds :
    MinObserveConflict(r)
      => r \in MinTerminalRequests \ minConflicts
PROOF
  BY DEF MinObserveConflict

THEOREM MinConflictPreservesRequestTerminalApplication ==
  \A r \in DecisionIds :
    MinObserveConflict(r)
      => UNCHANGED <<minRequestMeta, minTerminalMeta, minApplication>>
PROOF
  BY DEF MinObserveConflict

THEOREM MinApplicationStepStuttersRecognition ==
  \A nextApplication \in ApplicationStates :
    MinApplicationStep(nextApplication)
      => UNCHANGED minRecognitionVars
PROOF
  BY DEF MinApplicationStep

THEOREM MinStatusUnresolvedWithoutRequest ==
  \A r \in DecisionIds :
    r \notin MinRequests => MinStatusOf(r) = "UNRESOLVED"
PROOF
  BY DEF MinStatusOf

THEOREM MinStatusUnresolvedOnConflict ==
  \A r \in DecisionIds :
    r \in minConflicts => MinStatusOf(r) = "UNRESOLVED"
PROOF
  BY DEF MinStatusOf

THEOREM MinStatusAdmitForAdmitTerminal ==
  \A r \in DecisionIds :
    /\ r \in MinRequests
    /\ r \notin minConflicts
    /\ r \in MinTerminalRequests
    /\ MinTerminalOutcome(r) = "ADMIT"
    => MinStatusOf(r) = "ADMIT"
PROOF
  BY DEF MinStatusOf

THEOREM MinStatusRejectForRejectTerminal ==
  \A r \in DecisionIds :
    /\ r \in MinRequests
    /\ r \notin minConflicts
    /\ r \in MinTerminalRequests
    /\ MinTerminalOutcome(r) = "REJECT"
    => MinStatusOf(r) = "REJECT"
PROOF
  BY DEF MinStatusOf

=============================================================================
