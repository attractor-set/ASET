------------------ MODULE ComponentCompositionProofs ------------------
EXTENDS ComponentRelations, TLAPS

THEOREM RecognitionValuesAreExactlyThree ==
  RecognitionValues = {"UNKNOWN", "ALLOW", "BLOCK"}
PROOF
  BY DEF RecognitionValues

THEOREM ObserveUnknownBoundary ==
  \A s, t, e : ObserveUnknown(s, t, e) =>
    /\ s.recognition = "UNKNOWN"
    /\ t.recognition = "UNKNOWN"
PROOF
  BY DEF ObserveUnknown, StateType

THEOREM ObserveUnknownPreservesExactSubjectAndAuthority ==
  \A s, t, e : ObserveUnknown(s, t, e) =>
    /\ t.subject = s.subject
    /\ t.authority = s.authority
PROOF
  BY DEF ObserveUnknown, StateType

THEOREM ObserveAndPreserveUnknownShareRecognitionProjection ==
  \A r, r2 :
    TheoryObserveUnknown(r, r2) <=> TheoryPreserveUnknown(r, r2)
PROOF
  BY DEF TheoryObserveUnknown, TheoryPreserveUnknown

THEOREM FreshObserveUnknownIsNotPreserveUnknown ==
  \A s, t, e :
    /\ ObserveUnknown(s, t, e)
    /\ e \notin s.evidence
    => ~PreserveUnknown(s, t, e)
PROOF
  BY SMTT(30)
     DEF ObserveUnknown,
         PreserveUnknown,
         TheoryObserveUnknown,
         TheoryPreserveUnknown,
         ToTheoryRecognition,
         StateType

THEOREM ReobserveUnknownIsPreserveUnknown ==
  \A s, t, e :
    /\ ObserveUnknown(s, t, e)
    /\ e \in s.evidence
    => PreserveUnknown(s, t, e)
PROOF
  <1> SUFFICES ASSUME NEW s, NEW t, NEW e,
                       ObserveUnknown(s, t, e),
                       e \in s.evidence
                PROVE PreserveUnknown(s, t, e)
    OBVIOUS
  <1>1. s.evidence \cup {e} = s.evidence
    BY SetExtensionality
  <1>2. t = s
    BY <1>1, SimplifyAndSolve
       DEF ObserveUnknown, StateType
  <1>. QED
    BY <1>2
       DEF ObserveUnknown,
           PreserveUnknown,
           TheoryObserveUnknown,
           TheoryPreserveUnknown,
           ToTheoryRecognition,
           StateType

THEOREM RecognizeAllowBoundary ==
  \A s, t, e : RecognizeAllow(s, t, e) =>
    /\ s.recognition = "UNKNOWN"
    /\ t.recognition = "ALLOW"
PROOF
  BY DEF RecognizeAllow, StateType

THEOREM RecognizeAllowRequiresExactLocalAuthorityEvidence ==
  \A s, t, e : RecognizeAllow(s, t, e) =>
    <<s.authority, s.subject, e, "ALLOW">> \in AuthorityRecognition
PROOF
  BY DEF RecognizeAllow

THEOREM RecognizeBlockBoundary ==
  \A s, t, e : RecognizeBlock(s, t, e) =>
    /\ s.recognition = "UNKNOWN"
    /\ t.recognition = "BLOCK"
PROOF
  BY DEF RecognizeBlock, StateType

THEOREM RecognizeBlockRequiresExactLocalAuthorityEvidence ==
  \A s, t, e : RecognizeBlock(s, t, e) =>
    <<s.authority, s.subject, e, "BLOCK">> \in AuthorityRecognition
PROOF
  BY DEF RecognizeBlock

THEOREM RecognizedTransitionsPreserveExactSubjectAndAuthority ==
  \A s, t, e :
    (RecognizeAllow(s, t, e) \/ RecognizeBlock(s, t, e)) =>
      /\ t.subject = s.subject
      /\ t.authority = s.authority
PROOF
  BY DEF RecognizeAllow, RecognizeBlock, StateType

THEOREM PreserveUnknownBoundary ==
  \A s, t, e : PreserveUnknown(s, t, e) =>
    /\ s.recognition = "UNKNOWN"
    /\ t.recognition = "UNKNOWN"
PROOF
  BY DEF PreserveUnknown

THEOREM PreserveAllowBoundary ==
  \A s, t, e : PreserveAllow(s, t, e) =>
    /\ s.recognition = "ALLOW"
    /\ t.recognition = "ALLOW"
PROOF
  BY DEF PreserveAllow

THEOREM PreserveBlockBoundary ==
  \A s, t, e : PreserveBlock(s, t, e) =>
    /\ s.recognition = "BLOCK"
    /\ t.recognition = "BLOCK"
PROOF
  BY DEF PreserveBlock

=============================================================================
