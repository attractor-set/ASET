----------------------------- MODULE MonadeCanon -----------------------------
EXTENDS Naturals
VARIABLES bound, intent, observed, verified, outcome
vars == <<bound, intent, observed, verified, outcome>>
Init == /\\ bound = FALSE /\\ intent = FALSE /\\ observed = FALSE /\\ verified = FALSE /\\ outcome = FALSE
Bind == /\\ ~bound /\\ bound' = TRUE /\\ UNCHANGED <<intent, observed, verified, outcome>>
Dispatch == /\\ bound /\\ ~intent /\\ intent' = TRUE /\\ UNCHANGED <<bound, observed, verified, outcome>>
Observe == /\\ intent /\\ ~observed /\\ observed' = TRUE /\\ UNCHANGED <<bound, intent, verified, outcome>>
Verify == /\\ observed /\\ ~verified /\\ verified' = TRUE /\\ UNCHANGED <<bound, intent, observed, outcome>>
Accept == /\\ verified /\\ ~outcome /\\ outcome' = TRUE /\\ UNCHANGED <<bound, intent, observed, verified>>
Next == Bind \\/ Dispatch \\/ Observe \\/ Verify \\/ Accept
IntentBeforeObservation == observed => intent
OutcomeVerified == outcome => verified
Spec == Init /\\ [][Next]_vars
=============================================================================
