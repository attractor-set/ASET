# Federation governance

Root Constitution is immutable inside one Genesis lineage. Governance is local to a parent namespace.

- `MEMBERSHIP_WITHDRAW` is a final member-signed exit and is accepted only when no active direct sibling normatively depends on the departing Context.
- `CONTEXT_REDEFINE` is parent-authorized and atomically consumes one canonical proposal plus an exact authorization from every Context in the computed transitive affected-sibling set.

No intermediate consent artifact mutates State. This removes plebiscite recursion, timeout interpretation, alias reservation, rollback and nested pending races.
