------------------------------ MODULE SeedResolution ------------------------------
EXTENDS FiniteSets

CONSTANTS ResolutionIds, Bindings, Authorities, NoResolution, NoRecord

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

(* authorityBindings is a static exact-binding local recognition relation.
   TLC explores every subset of Authorities \X Bindings and preserves the
   selected relation for the entire behavior. *)
VARIABLES authorityBindings, requests, requestBinding, previousResolution, terminalRecord
vars == <<authorityBindings, requests, requestBinding, previousResolution, terminalRecord>>

Init ==
  /\ authorityBindings \in SUBSET (Authorities \X Bindings)
  /\ requests = {}
  /\ requestBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ previousResolution = [r \in ResolutionIds |-> NoResolution]
  /\ terminalRecord = [r \in ResolutionIds |-> NoRecord]

RegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in authorityBindings
  /\ \/ previous = NoResolution
     \/ /\ previous \in requests
        /\ terminalRecord[previous] \in TerminalResolutions
  /\ requests' = requests \cup {r}
  /\ requestBinding' = [requestBinding EXCEPT ![r] = b]
  /\ previousResolution' = [previousResolution EXCEPT ![r] = previous]
  /\ UNCHANGED <<authorityBindings, terminalRecord>>

SubmitResolution(r, b, a, value) ==
  /\ r \in requests
  /\ b = requestBinding[r]
  /\ a \in Authorities
  /\ <<a, b>> \in authorityBindings
  /\ value \in TerminalResolutions
  /\ terminalRecord[r] = NoRecord
  /\ terminalRecord' = [terminalRecord EXCEPT ![r] = value]
  /\ UNCHANGED <<authorityBindings, requests, requestBinding, previousResolution>>

Evaluate == UNCHANGED vars

Next ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in ResolutionIds \cup {NoResolution} :
        RegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)
  \/ Evaluate

ResolutionOf(r) ==
  IF r \notin requests \/ terminalRecord[r] = NoRecord
  THEN "UNKNOWN"
  ELSE terminalRecord[r]

EffectPermitted(r) == ResolutionOf(r) = "ALLOW"

TypeOK ==
  /\ authorityBindings \subseteq Authorities \X Bindings
  /\ requests \subseteq ResolutionIds
  /\ requestBinding \in [ResolutionIds -> Bindings]
  /\ previousResolution \in [ResolutionIds -> ResolutionIds \cup {NoResolution}]
  /\ terminalRecord \in [ResolutionIds -> TerminalResolutions \cup {NoRecord}]

ResolutionDomain == \A r \in ResolutionIds : ResolutionOf(r) \in Resolutions
FailClosed == \A r \in ResolutionIds : ResolutionOf(r) # "ALLOW" => ~EffectPermitted(r)
AllowIffPermitted == \A r \in ResolutionIds : EffectPermitted(r) <=> ResolutionOf(r) = "ALLOW"
FreshReconsideration == \A r \in requests : previousResolution[r] = NoResolution \/ previousResolution[r] # r
TerminalUnique == \A r \in requests : terminalRecord[r] \in TerminalResolutions \cup {NoRecord}

Spec == Init /\ [][Next]_vars
=================================================================================
