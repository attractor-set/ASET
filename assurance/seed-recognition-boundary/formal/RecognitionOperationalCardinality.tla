---------------- MODULE RecognitionOperationalCardinality ----------------
EXTENDS FiniteSets

(***************************************************************************)
(* Three distinct minimality levels for one recognition identity.          *)
(*                                                                         *)
(* Level 1: effective output only                                          *)
(*   UNKNOWN / ALLOW / BLOCK                                               *)
(*                                                                         *)
(* Level 2: effective output + enabled recognition actions                 *)
(*   ABSENT, PENDING, ALLOW, BLOCK, INVALIDATED                            *)
(*                                                                         *)
(* Level 3: retained immutable terminal provenance                         *)
(*   ABSENT, PENDING, ALLOW, BLOCK, INVALIDATED_ALLOW, INVALIDATED_BLOCK   *)
(*                                                                         *)
(* Observation signatures are ordinary TLA+    *)
(* functions and are indexed with [x].  They are not passed/called as      *)
(* higher-order operator parameters.                                       *)
(***************************************************************************)

OperationalPhases ==
  {"ABSENT",
   "PENDING",
   "ALLOW",
   "BLOCK",
   "INVALIDATED_ALLOW",
   "INVALIDATED_BLOCK"}

EffectiveValues == {"UNKNOWN", "ALLOW", "BLOCK"}
FourValues == {"0", "1", "2", "3"}
FiveValues == {"0", "1", "2", "3", "4"}
SixValues == {"0", "1", "2", "3", "4", "5"}

EffectiveValue(s) ==
  CASE s = "ALLOW" -> "ALLOW"
    [] s = "BLOCK" -> "BLOCK"
    [] OTHER -> "UNKNOWN"

CanRegister(s) == s = "ABSENT"
CanSubmit(s) == s = "PENDING"
CanConflict(s) == s \in {"ALLOW", "BLOCK"}

CapabilityObservables(s) ==
  [effective |-> EffectiveValue(s),
   can_register |-> CanRegister(s),
   can_submit |-> CanSubmit(s),
   can_conflict |-> CanConflict(s)]

RetainedTerminal(s) ==
  CASE s \in {"ALLOW", "INVALIDATED_ALLOW"} -> "ALLOW"
    [] s \in {"BLOCK", "INVALIDATED_BLOCK"} -> "BLOCK"
    [] OTHER -> "NONE"

HistoryObservables(s) ==
  [capability |-> CapabilityObservables(s),
   retained_terminal |-> RetainedTerminal(s)]

CapabilityObservationMap ==
  [s \in OperationalPhases |-> CapabilityObservables(s)]

HistoryObservationMap ==
  [s \in OperationalPhases |-> HistoryObservables(s)]

CapabilityRepresentatives ==
  {"ABSENT", "PENDING", "ALLOW", "BLOCK", "INVALIDATED_ALLOW"}

FaithfulOn(f, representatives, observationMap, codomain) ==
  /\ f \in [representatives -> codomain]
  /\ \A x \in representatives, y \in representatives :
       observationMap[x] # observationMap[y] => f[x] # f[y]

CanonicalFiveEncoding ==
  [s \in CapabilityRepresentatives |->
     CASE s = "ABSENT" -> "0"
       [] s = "PENDING" -> "1"
       [] s = "ALLOW" -> "2"
       [] s = "BLOCK" -> "3"
       [] OTHER -> "4"]

CanonicalSixEncoding ==
  [s \in OperationalPhases |->
     CASE s = "ABSENT" -> "0"
       [] s = "PENDING" -> "1"
       [] s = "ALLOW" -> "2"
       [] s = "BLOCK" -> "3"
       [] s = "INVALIDATED_ALLOW" -> "4"
       [] OTHER -> "5"]

=============================================================================
