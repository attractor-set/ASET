------------------- MODULE RestrictedOperationalSemantics -------------------
EXTENDS ComponentRelations

OperationalObserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ e \in EvidenceItems
  /\ t = [s EXCEPT !.evidence = @ \cup {e}]

OperationalRecognizeAllow(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ e \in s.evidence
  /\ <<s.authority, s.subject, e, "ALLOW">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "ALLOW"]

OperationalRecognizeBlock(s, t, e) ==
  /\ s \in StateType
  /\ t \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ e \in s.evidence
  /\ <<s.authority, s.subject, e, "BLOCK">> \in AuthorityRecognition
  /\ t = [s EXCEPT !.recognition = "BLOCK"]

OperationalPreserveUnknown(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "UNKNOWN"
  /\ t = s

OperationalPreserveAllow(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "ALLOW"
  /\ t = s

OperationalPreserveBlock(s, t, e) ==
  /\ s \in StateType
  /\ s.recognition = "BLOCK"
  /\ t = s

=============================================================================
