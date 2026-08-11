-------------------- MODULE SeedRecognitionMinimalityProofs --------------------
EXTENDS SeedResolution, TLAPS

Card == INSTANCE RecognitionCardinality


SeedTerminal(value) == value \in TerminalResolutions
SeedEffectPermitted(value) == value = "ALLOW"

SeedEncoding ==
  [s \in Card!RecognitionStates |->
     CASE s = "U" -> "UNKNOWN"
       [] s = "A" -> "ALLOW"
       [] OTHER   -> "BLOCK"]

THEOREM SeedResolutionAlphabetIsExactlyThree ==
  Resolutions = {"UNKNOWN", "ALLOW", "BLOCK"}
PROOF
  BY DEF Resolutions

THEOREM SeedEncodingPreservesRecognitionObservables ==
  Card!Faithful(SeedEncoding, Resolutions)
PROOF
  BY SMTT(30)
     DEF SeedEncoding,
         Resolutions,
         Card!Faithful,
         Card!RecognitionStates,
         Card!Observables,
         Card!Terminal,
         Card!EffectPermitted

THEOREM SeedEncodingPreservesTerminalityAndPermission ==
  \A s \in Card!RecognitionStates :
    /\ Card!Terminal(s) = SeedTerminal(SeedEncoding[s])
    /\ Card!EffectPermitted(s) = SeedEffectPermitted(SeedEncoding[s])
PROOF
  BY SMTT(30)
     DEF SeedEncoding,
         SeedTerminal,
         SeedEffectPermitted,
         TerminalResolutions,
         Card!RecognitionStates,
         Card!Terminal,
         Card!EffectPermitted

THEOREM SeedCardinalityObservablesPairwiseDistinct ==
  /\ Card!Observables("U") # Card!Observables("A")
  /\ Card!Observables("U") # Card!Observables("B")
  /\ Card!Observables("A") # Card!Observables("B")
PROOF
  BY DEF Card!Observables,
         Card!Terminal,
         Card!EffectPermitted

THEOREM TwoValuesCannotPreserveRecognitionObservables ==
  ~\E f : Card!Faithful(f, Card!TwoValues)
PROOF
  BY SMTT(30), SeedCardinalityObservablesPairwiseDistinct
     DEF Card!Faithful,
         Card!RecognitionStates,
         Card!TwoValues,
         Card!Observables,
         Card!Terminal,
         Card!EffectPermitted

THEOREM SeedRecognitionAlgebraMeetsCardinalityLowerBound ==
  /\ SeedEncodingPreservesRecognitionObservables
  /\ SeedEncodingPreservesTerminalityAndPermission
  /\ ~\E f : Card!Faithful(f, Card!TwoValues)
PROOF
  BY SeedEncodingPreservesRecognitionObservables,
     SeedEncodingPreservesTerminalityAndPermission,
     TwoValuesCannotPreserveRecognitionObservables

=============================================================================
