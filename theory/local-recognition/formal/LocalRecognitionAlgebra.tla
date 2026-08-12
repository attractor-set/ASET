----------------------- MODULE LocalRecognitionAlgebra -----------------------
EXTENDS RecognitionCardinality

TheoryRecognitionValues == RecognitionStates
TheoryUnknown == "U"
TheoryAllow == "A"
TheoryBlock == "B"

TheoryObserveUnknown(r, r2) ==
  /\ r = TheoryUnknown
  /\ r2 = TheoryUnknown

TheoryRecognizeAllow(r, r2) ==
  /\ r = TheoryUnknown
  /\ r2 = TheoryAllow

TheoryRecognizeBlock(r, r2) ==
  /\ r = TheoryUnknown
  /\ r2 = TheoryBlock

TheoryPreserveUnknown(r, r2) ==
  /\ r = TheoryUnknown
  /\ r2 = TheoryUnknown

TheoryPreserveAllow(r, r2) ==
  /\ r = TheoryAllow
  /\ r2 = TheoryAllow

TheoryPreserveBlock(r, r2) ==
  /\ r = TheoryBlock
  /\ r2 = TheoryBlock

TheoryStep(r, r2) ==
  \/ TheoryObserveUnknown(r, r2)
  \/ TheoryRecognizeAllow(r, r2)
  \/ TheoryRecognizeBlock(r, r2)
  \/ TheoryPreserveUnknown(r, r2)
  \/ TheoryPreserveAllow(r, r2)
  \/ TheoryPreserveBlock(r, r2)

TheoryTerminal(r) == Terminal(r)
TheoryEffectPermitted(r) == EffectPermitted(r)

=============================================================================
