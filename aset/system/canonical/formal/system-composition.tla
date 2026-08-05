----------------------------- MODULE SystemComposition -----------------------------
EXTENDS Naturals
VARIABLES expectationPermit, executionPermit, intent, observed, verified, outcome
vars == <<expectationPermit, executionPermit, intent, observed, verified, outcome>>
Init == /\\ expectationPermit = FALSE /\\ executionPermit = FALSE /\\ intent = FALSE /\\ observed = FALSE /\\ verified = FALSE /\\ outcome = FALSE
AuthorizeExpectation == /\\ ~expectationPermit /\\ expectationPermit' = TRUE /\\ UNCHANGED <<executionPermit, intent, observed, verified, outcome>>
AuthorizeExecution == /\\ expectationPermit /\\ ~executionPermit /\\ executionPermit' = TRUE /\\ UNCHANGED <<expectationPermit, intent, observed, verified, outcome>>
Dispatch == /\\ executionPermit /\\ ~intent /\\ intent' = TRUE /\\ UNCHANGED <<expectationPermit, executionPermit, observed, verified, outcome>>
Observe == /\\ intent /\\ ~observed /\\ observed' = TRUE /\\ UNCHANGED <<expectationPermit, executionPermit, intent, verified, outcome>>
Verify == /\\ observed /\\ ~verified /\\ verified' = TRUE /\\ UNCHANGED <<expectationPermit, executionPermit, intent, observed, outcome>>
Recognize == /\\ verified /\\ ~outcome /\\ outcome' = TRUE /\\ UNCHANGED <<expectationPermit, executionPermit, intent, observed, verified>>
Next == AuthorizeExpectation \\/ AuthorizeExecution \\/ Dispatch \\/ Observe \\/ Verify \\/ Recognize
SeparatePermits == executionPermit => expectationPermit
OutcomeRequiresVerification == outcome => verified
Spec == Init /\\ [][Next]_vars
=============================================================================
