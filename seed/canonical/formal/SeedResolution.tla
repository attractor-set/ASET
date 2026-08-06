------------------------------ MODULE SeedResolution ------------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANT Authorities

Statuses == {"UNKNOWN", "ACCEPT", "DENY"}
Enforcements == {"BLOCKED", "ALLOW"}

VARIABLES status, enforcement, currentAuthority, authorityChain, auditLength
vars == <<status, enforcement, currentAuthority, authorityChain, auditLength>>

Init ==
  /\\ status = "UNKNOWN"
  /\\ enforcement = "BLOCKED"
  /\\ currentAuthority \in Authorities
  /\\ authorityChain = <<currentAuthority>>
  /\\ auditLength = 1

ResolveAccept ==
  /\\ status = "UNKNOWN"
  /\\ status' = "ACCEPT"
  /\\ enforcement' = "ALLOW"
  /\\ UNCHANGED <<currentAuthority, authorityChain>>
  /\\ auditLength' = auditLength + 1

ResolveDeny ==
  /\\ status = "UNKNOWN"
  /\\ status' = "DENY"
  /\\ enforcement' = "BLOCKED"
  /\\ UNCHANGED <<currentAuthority, authorityChain>>
  /\\ auditLength' = auditLength + 1

Escalate(next) ==
  /\\ status = "UNKNOWN"
  /\\ next \in Authorities
  /\\ next \notin Range(authorityChain)
  /\\ status' = "UNKNOWN"
  /\\ enforcement' = "BLOCKED"
  /\\ currentAuthority' = next
  /\\ authorityChain' = Append(authorityChain, next)
  /\\ auditLength' = auditLength + 1

Next == ResolveAccept \/ ResolveDeny \/ \E next \in Authorities : Escalate(next)

StatusDomain == status \in Statuses
UnknownBlocked == status = "UNKNOWN" => enforcement = "BLOCKED"
AllowOnlyAccept == enforcement = "ALLOW" => status = "ACCEPT"
TerminalImmutable == status \in {"ACCEPT", "DENY"} => ~ENABLED Next
EscalationAuthorized == Len(authorityChain) = Cardinality(Range(authorityChain))
AuditMonotone == auditLength >= 1

Spec == Init /\\ [][Next]_vars
=============================================================================
