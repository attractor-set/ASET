---------------- MODULE OperationalRelationalPairingProofs ----------------
EXTENDS RestrictedOperationalSemantics, TLAPS

THEOREM ObserveUnknownPairing ==
  \A s, t, e : OperationalObserveUnknown(s, t, e) <=> ObserveUnknown(s, t, e)
PROOF
  BY DEF OperationalObserveUnknown, ObserveUnknown

THEOREM RecognizeAllowPairing ==
  \A s, t, e : OperationalRecognizeAllow(s, t, e) <=> RecognizeAllow(s, t, e)
PROOF
  BY DEF OperationalRecognizeAllow, RecognizeAllow

THEOREM RecognizeBlockPairing ==
  \A s, t, e : OperationalRecognizeBlock(s, t, e) <=> RecognizeBlock(s, t, e)
PROOF
  BY DEF OperationalRecognizeBlock, RecognizeBlock

THEOREM PreserveUnknownPairing ==
  \A s, t, e : OperationalPreserveUnknown(s, t, e) <=> PreserveUnknown(s, t, e)
PROOF
  BY DEF OperationalPreserveUnknown, PreserveUnknown

THEOREM PreserveAllowPairing ==
  \A s, t, e : OperationalPreserveAllow(s, t, e) <=> PreserveAllow(s, t, e)
PROOF
  BY DEF OperationalPreserveAllow, PreserveAllow

THEOREM PreserveBlockPairing ==
  \A s, t, e : OperationalPreserveBlock(s, t, e) <=> PreserveBlock(s, t, e)
PROOF
  BY DEF OperationalPreserveBlock, PreserveBlock

THEOREM OperationalRelationalPairing ==
  /\ ObserveUnknownPairing
  /\ RecognizeAllowPairing
  /\ RecognizeBlockPairing
  /\ PreserveUnknownPairing
  /\ PreserveAllowPairing
  /\ PreserveBlockPairing
PROOF
  BY ObserveUnknownPairing,
     RecognizeAllowPairing,
     RecognizeBlockPairing,
     PreserveUnknownPairing,
     PreserveAllowPairing,
     PreserveBlockPairing

=============================================================================
