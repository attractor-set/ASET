------------------- MODULE RecognitionCardinalityProofs -------------------
EXTENDS RecognitionCardinality, TLAPS

THEOREM RecognitionObservablesPairwiseDistinct ==
  /\ Observables("U") # Observables("A")
  /\ Observables("U") # Observables("B")
  /\ Observables("A") # Observables("B")
PROOF
  BY DEF Observables, Terminal, EffectPermitted

THEOREM NoFaithfulTwoValueEncoding ==
  ~\E f : Faithful(f, TwoValues)
PROOF
  BY SMTT(30), RecognitionObservablesPairwiseDistinct
     DEF Faithful, RecognitionStates, TwoValues

THEOREM CanonicalThreeEncodingIsFaithful ==
  Faithful(CanonicalThreeEncoding, ThreeValues)
PROOF
  BY SMTT(30), RecognitionObservablesPairwiseDistinct
     DEF Faithful,
         CanonicalThreeEncoding,
         RecognitionStates,
         ThreeValues,
         Observables,
         Terminal,
         EffectPermitted

THEOREM ThreeRecognitionValuesAreCardinalityMinimal ==
  /\ ~\E f : Faithful(f, TwoValues)
  /\ \E f : Faithful(f, ThreeValues)
PROOF
  <1>1. ~\E f : Faithful(f, TwoValues)
    BY NoFaithfulTwoValueEncoding
  <1>2. \E f : Faithful(f, ThreeValues)
    BY CanonicalThreeEncodingIsFaithful
  <1>3. QED
    BY <1>1, <1>2

=============================================================================
