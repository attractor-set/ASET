----------------------------- MODULE ProtocolCanon -----------------------------
EXTENDS Naturals
VARIABLES schemaValid, canonical, admitted, businessAuthority
vars == <<schemaValid, canonical, admitted, businessAuthority>>
Init == /\\ schemaValid = FALSE /\\ canonical = FALSE /\\ admitted = FALSE /\\ businessAuthority = FALSE
Validate == /\\ ~schemaValid /\\ schemaValid' = TRUE /\\ UNCHANGED <<canonical, admitted, businessAuthority>>
Canonicalize == /\\ schemaValid /\\ ~canonical /\\ canonical' = TRUE /\\ UNCHANGED <<schemaValid, admitted, businessAuthority>>
Admit == /\\ canonical /\\ ~admitted /\\ admitted' = TRUE /\\ UNCHANGED <<schemaValid, canonical, businessAuthority>>
Next == Validate \\/ Canonicalize \\/ Admit
SchemaBeforeAdmission == admitted => schemaValid /\\ canonical
NoBusinessAuthority == ~businessAuthority
Spec == Init /\\ [][Next]_vars
=============================================================================
