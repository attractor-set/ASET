---------------- MODULE IndependentProjectionAdequacy ----------------
EXTENDS FiniteSets, Sequences

(***************************************************************************)
(* A9 — typed, order-preserving projection faithfulness with temporal      *)
(*       prefix consistency.                                               *)
(*                                                                         *)
(* This module does NOT establish that NativeRecognitionTraceOf is a       *)
(* truthful observation of an arbitrary external domain. That grounding   *)
(* remains a domain-specific conformance obligation.                       *)
(*                                                                         *)
(* DomainPoints are trace-distinguishing observation/execution points.     *)
(* They need not be identical to raw application states. A domain whose    *)
(* application state merges distinct histories may use a history-lifted    *)
(* adapter that supplies distinct observation points for those executions. *)
(*                                                                         *)
(* Once a native recognition trace and DomainSteps relation are supplied,  *)
(* an admissible projection preserves the exact tagged sequence and the    *)
(* native trace moves only forward by prefix extension along supplied      *)
(* steps. Exact equality transfers the same causal-prefix property to the  *)
(* projected trace.                                                        *)
(*                                                                         *)
(* This module has no GCR or Seed dependency.                              *)
(***************************************************************************)

CONSTANTS DomainPoints, DomainSteps,
          DecisionIds, NativeAuthorities, NativeEvents,
          NativeContexts, NativeDescriptors, NativePolicyEpochs,
          NativeScopes, RecognitionSubjects,
          TerminalCommitments, NoCommitment,
          NativeRecognitionTraceOf, ProjectedRecognitionTraceOf

ASSUME DomainPoints # {}
ASSUME DomainSteps \subseteq DomainPoints \X DomainPoints
ASSUME DecisionIds # {}
ASSUME NativeAuthorities # {}
ASSUME NativeEvents # {}
ASSUME NativeContexts # {}
ASSUME NativeDescriptors # {}
ASSUME NativePolicyEpochs # {}
ASSUME NativeScopes # {}
ASSUME RecognitionSubjects # {}

NativeTerminalOutcomes == {"ADMIT", "REJECT"}

OpenEventType ==
  [kind : {"OPEN"},
   decision_id : DecisionIds,
   subject : RecognitionSubjects,
   context : NativeContexts,
   descriptor : NativeDescriptors,
   policy_epoch : NativePolicyEpochs,
   scope : NativeScopes,
   authority : NativeAuthorities,
   previous : TerminalCommitments \cup {NoCommitment}]

DecisionEventType ==
  [kind : {"DECISION"},
   decision_id : DecisionIds,
   subject : RecognitionSubjects,
   authority : NativeAuthorities,
   outcome : NativeTerminalOutcomes]

ConflictEventType ==
  [kind : {"CONFLICT"},
   decision_id : DecisionIds,
   subject : RecognitionSubjects]

ControlledEffectEventType ==
  [kind : {"CONTROLLED_EFFECT"},
   decision_id : DecisionIds,
   subject : RecognitionSubjects,
   event : NativeEvents]

RecognitionEventType ==
  OpenEventType
  \cup DecisionEventType
  \cup ConflictEventType
  \cup ControlledEffectEventType

RecognitionTraces == Seq(RecognitionEventType)

ASSUME NativeTraceType ==
  NativeRecognitionTraceOf \in [DomainPoints -> RecognitionTraces]
ASSUME ProjectedTraceType ==
  ProjectedRecognitionTraceOf \in [DomainPoints -> RecognitionTraces]

TracePrefix(before, after) ==
  \E suffix \in RecognitionTraces : after = before \o suffix

A9State(p) ==
  NativeRecognitionTraceOf[p] = ProjectedRecognitionTraceOf[p]

A9PointwiseFaithful ==
  \A p \in DomainPoints : A9State(p)

NativeTraceForwardCausal ==
  \A p \in DomainPoints, q \in DomainPoints :
    <<p, q>> \in DomainSteps
      => TracePrefix(NativeRecognitionTraceOf[p],
                     NativeRecognitionTraceOf[q])

ProjectedTraceForwardCausal ==
  \A p \in DomainPoints, q \in DomainPoints :
    <<p, q>> \in DomainSteps
      => TracePrefix(ProjectedRecognitionTraceOf[p],
                     ProjectedRecognitionTraceOf[q])

A9ProjectionFaithful ==
  /\ A9PointwiseFaithful
  /\ NativeTraceForwardCausal

ConstantProjectedRecognitionTrace ==
  \A p \in DomainPoints, q \in DomainPoints :
    ProjectedRecognitionTraceOf[p] = ProjectedRecognitionTraceOf[q]

=============================================================================
