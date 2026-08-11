-------------- MODULE IndependentProjectionAdequacyProofs --------------
EXTENDS IndependentProjectionAdequacy, TLAPS

THEOREM NativeAndProjectedRecognitionTracesAreTyped ==
  /\ NativeRecognitionTraceOf \in [DomainPoints -> RecognitionTraces]
  /\ ProjectedRecognitionTraceOf \in [DomainPoints -> RecognitionTraces]
PROOF
  BY NativeTraceType, ProjectedTraceType

THEOREM A9PreservesExactRecognitionTrace ==
  A9ProjectionFaithful
  =>
  \A p \in DomainPoints :
    NativeRecognitionTraceOf[p] = ProjectedRecognitionTraceOf[p]
PROOF
  BY DEF A9ProjectionFaithful, A9PointwiseFaithful, A9State

THEOREM A9RequiresNativeTraceForwardCausality ==
  A9ProjectionFaithful => NativeTraceForwardCausal
PROOF
  BY DEF A9ProjectionFaithful

THEOREM A9TransfersForwardCausalityToProjection ==
  A9ProjectionFaithful => ProjectedTraceForwardCausal
PROOF
  BY SMTT(60)
     DEF A9ProjectionFaithful,
         A9PointwiseFaithful,
         A9State,
         NativeTraceForwardCausal,
         ProjectedTraceForwardCausal,
         TracePrefix

THEOREM A9TransfersRecognitionTraceChange ==
  A9ProjectionFaithful
  =>
  \A p \in DomainPoints, q \in DomainPoints :
    NativeRecognitionTraceOf[p] # NativeRecognitionTraceOf[q]
      => ProjectedRecognitionTraceOf[p] # ProjectedRecognitionTraceOf[q]
PROOF
  BY SMTT(60)
     DEF A9ProjectionFaithful, A9PointwiseFaithful, A9State

THEOREM A9RejectsConstantProjectionForRecognitionChange ==
  \A p \in DomainPoints, q \in DomainPoints :
    /\ A9ProjectionFaithful
    /\ NativeRecognitionTraceOf[p] # NativeRecognitionTraceOf[q]
    => ~ConstantProjectedRecognitionTrace
PROOF
  BY SMTT(60)
     DEF A9ProjectionFaithful,
         A9PointwiseFaithful,
         A9State,
         ConstantProjectedRecognitionTrace

THEOREM A9ProjectedTraceCannotRollbackAlongSuppliedStep ==
  A9ProjectionFaithful
  =>
  \A p \in DomainPoints, q \in DomainPoints :
    <<p, q>> \in DomainSteps
      => TracePrefix(ProjectedRecognitionTraceOf[p],
                     ProjectedRecognitionTraceOf[q])
PROOF
  BY A9TransfersForwardCausalityToProjection
     DEF ProjectedTraceForwardCausal

=============================================================================
