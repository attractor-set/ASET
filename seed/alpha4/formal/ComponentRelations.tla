------------------------ MODULE ComponentRelations ------------------------
EXTENDS FiniteSets

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

EffectPermitted(s) ==
  /\ s \in StateType
  /\ s.recognition = "ALLOW"

ObserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in EvidenceItems
  /\ s.recognition = "UNKNOWN"
  /\ t = [s EXCEPT !.evidence = @ \cup {e}]

RecognizeAllow(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in s.evidence
  /\ s.recognition = "UNKNOWN"
  /\ <<s.authority, s.subject, e, "ALLOW">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "ALLOW"]

RecognizeBlock(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ e \in s.evidence
  /\ s.recognition = "UNKNOWN"
  /\ <<s.authority, s.subject, e, "BLOCK">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "BLOCK"]

PreserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ t = s

PreserveAllow(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "ALLOW"
  /\ t = s

PreserveBlock(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "BLOCK"
  /\ t = s

=============================================================================
