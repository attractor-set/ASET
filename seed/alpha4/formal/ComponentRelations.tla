------------------------ MODULE ComponentRelations ------------------------
EXTENDS FiniteSets, LocalRecognitionAlgebra

CONSTANTS Subjects, Authorities, EvidenceItems, AuthorityRecognition

RecognitionValues == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalValues == {"ALLOW", "BLOCK"}

ASSUME Subjects # {}
ASSUME Authorities # {}
ASSUME EvidenceItems # {}
ASSUME AuthorityRecognition \in
  SUBSET (Authorities \X Subjects \X EvidenceItems \X TerminalValues)

StateType ==
  [subject : Subjects,
   authority : Authorities,
   evidence : SUBSET EvidenceItems,
   recognition : RecognitionValues]

ToTheoryRecognition(r) ==
  CASE r = "UNKNOWN" -> TheoryUnknown
    [] r = "ALLOW"   -> TheoryAllow
    [] OTHER         -> TheoryBlock

EffectPermitted(s) ==
  /\ s \in StateType
  /\ TheoryEffectPermitted(ToTheoryRecognition(s.recognition))

ObserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in EvidenceItems
  /\ s.recognition = "UNKNOWN"
  /\ t = [s EXCEPT !.evidence = @ \cup {e}]
  /\ TheoryObserveUnknown(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

RecognizeAllow(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in s.evidence
  /\ s.recognition = "UNKNOWN"
  /\ <<s.authority, s.subject, e, "ALLOW">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "ALLOW"]
  /\ TheoryRecognizeAllow(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

RecognizeBlock(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in s.evidence
  /\ s.recognition = "UNKNOWN"
  /\ <<s.authority, s.subject, e, "BLOCK">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "BLOCK"]
  /\ TheoryRecognizeBlock(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

PreserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ t = s
  /\ TheoryPreserveUnknown(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

PreserveAllow(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "ALLOW"
  /\ t = s
  /\ TheoryPreserveAllow(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

PreserveBlock(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "BLOCK"
  /\ t = s
  /\ TheoryPreserveBlock(
       ToTheoryRecognition(s.recognition),
       ToTheoryRecognition(t.recognition))

=============================================================================
