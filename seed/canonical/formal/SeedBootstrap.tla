---- MODULE SeedBootstrap ----
EXTENDS Naturals, FiniteSets

CONSTANTS Contexts, Permits

VARIABLES activeContexts, usedPermits

vars == <<activeContexts, usedPermits>>

Init ==
    /\ activeContexts = Contexts
    /\ usedPermits = {}

UsePermit(p) ==
    /\ p \in Permits
    /\ p \notin usedPermits
    /\ usedPermits' = usedPermits \cup {p}
    /\ UNCHANGED activeContexts

Next ==
    \E p \in Permits : UsePermit(p)

NoDoubleUse ==
    usedPermits \subseteq Permits

Spec ==
    Init /\ [][Next]_vars

====
