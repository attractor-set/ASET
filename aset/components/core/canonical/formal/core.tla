----------------------------- MODULE CoreCanon -----------------------------
EXTENDS Naturals
VARIABLES decision, permit, consumed, crossingCount
vars == <<decision, permit, consumed, crossingCount>>
Init == /\\ decision = FALSE /\\ permit = FALSE /\\ consumed = FALSE /\\ crossingCount = 0
Resolve == /\\ ~decision /\\ decision' = TRUE /\\ UNCHANGED <<permit, consumed, crossingCount>>
Issue == /\\ decision /\\ ~permit /\\ permit' = TRUE /\\ UNCHANGED <<decision, consumed, crossingCount>>
Cross == /\\ permit /\\ ~consumed /\\ consumed' = TRUE /\\ permit' = FALSE /\\ crossingCount' = crossingCount + 1 /\\ UNCHANGED decision
Next == Resolve \\/ Issue \\/ Cross
DecisionBeforePermit == permit => decision
PermitAtMostOnce == crossingCount <= 1
Spec == Init /\\ [][Next]_vars
=============================================================================
