----------------------------- MODULE MasterCanon -----------------------------
EXTENDS Naturals
VARIABLES proposal, authorityClaim, permitClaim, outcomeClaim
vars == <<proposal, authorityClaim, permitClaim, outcomeClaim>>
Init == /\\ proposal = FALSE /\\ authorityClaim = FALSE /\\ permitClaim = FALSE /\\ outcomeClaim = FALSE
Plan == /\\ ~proposal /\\ proposal' = TRUE /\\ UNCHANGED <<authorityClaim, permitClaim, outcomeClaim>>
Next == Plan
AdvisoryOnly == proposal => ~authorityClaim
NoSelfAuthorization == ~permitClaim /\\ ~outcomeClaim
Spec == Init /\\ [][Next]_vars
=============================================================================
