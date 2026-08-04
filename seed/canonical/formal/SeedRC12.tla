
----------------------------- MODULE SeedRC12 -----------------------------
EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS Contexts, Permits
VARIABLES lifecycle, authorityActive, permitActive, attempts, maxAttempts,
          verified, outcome, auditLength

vars == <<lifecycle, authorityActive, permitActive, attempts, maxAttempts,
          verified, outcome, auditLength>>

Init ==
  /\ lifecycle = [c \in Contexts |-> "ACTIVE"]
  /\ authorityActive = [c \in Contexts |-> FALSE]
  /\ permitActive = [p \in Permits |-> FALSE]
  /\ attempts = [p \in Permits |-> 0]
  /\ maxAttempts = [p \in Permits |-> 1]
  /\ verified = [p \in Permits |-> FALSE]
  /\ outcome = [p \in Permits |-> FALSE]
  /\ auditLength = 0

GrantAuthority(c) ==
  /\ lifecycle[c] = "ACTIVE"
  /\ authorityActive' = [authorityActive EXCEPT ![c] = TRUE]
  /\ UNCHANGED <<lifecycle, permitActive, attempts, maxAttempts, verified, outcome>>
  /\ auditLength' = auditLength + 1

IssuePermit(p) ==
  /\ ~permitActive[p]
  /\ permitActive' = [permitActive EXCEPT ![p] = TRUE]
  /\ UNCHANGED <<lifecycle, authorityActive, attempts, maxAttempts, verified, outcome>>
  /\ auditLength' = auditLength + 1

UsePermit(p) ==
  /\ permitActive[p]
  /\ attempts[p] < maxAttempts[p]
  /\ attempts' = [attempts EXCEPT ![p] = @ + 1]
  /\ UNCHANGED <<lifecycle, authorityActive, permitActive, maxAttempts, verified, outcome>>
  /\ auditLength' = auditLength + 1

Verify(p) ==
  /\ attempts[p] > 0
  /\ verified' = [verified EXCEPT ![p] = TRUE]
  /\ UNCHANGED <<lifecycle, authorityActive, permitActive, attempts, maxAttempts, outcome>>
  /\ auditLength' = auditLength + 1

RecognizeOutcome(p) ==
  /\ verified[p]
  /\ outcome' = [outcome EXCEPT ![p] = TRUE]
  /\ permitActive' = [permitActive EXCEPT ![p] = FALSE]
  /\ UNCHANGED <<lifecycle, authorityActive, attempts, maxAttempts, verified>>
  /\ auditLength' = auditLength + 1

Withdraw(c) ==
  /\ lifecycle[c] = "ACTIVE"
  /\ lifecycle' = [lifecycle EXCEPT ![c] = "WITHDRAWN"]
  /\ authorityActive' = [authorityActive EXCEPT ![c] = FALSE]
  /\ UNCHANGED <<permitActive, attempts, maxAttempts, verified, outcome>>
  /\ auditLength' = auditLength + 1

Next ==
  \/ \E c \in Contexts : GrantAuthority(c)
  \/ \E p \in Permits : IssuePermit(p)
  \/ \E p \in Permits : UsePermit(p)
  \/ \E p \in Permits : Verify(p)
  \/ \E p \in Permits : RecognizeOutcome(p)
  \/ \E c \in Contexts : Withdraw(c)

AttemptBound == \A p \in Permits : attempts[p] <= maxAttempts[p]
OutcomeVerified == \A p \in Permits : outcome[p] => verified[p]
InactiveNoAuthority == \A c \in Contexts : lifecycle[c] # "ACTIVE" => ~authorityActive[c]
AuditMonotone == auditLength >= 0

Spec == Init /\ [][Next]_vars
=============================================================================
