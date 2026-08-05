----------------------------- MODULE GatewayCanon -----------------------------
EXTENDS Naturals
VARIABLES contextVersion, requestRendered, toolEffect
vars == <<contextVersion, requestRendered, toolEffect>>
Init == /\\ contextVersion = 0 /\\ requestRendered = FALSE /\\ toolEffect = FALSE
Render == /\\ ~requestRendered /\\ requestRendered' = TRUE /\\ UNCHANGED <<contextVersion, toolEffect>>
Next == Render
ContextUnchanged == contextVersion = 0
NoToolEffect == ~toolEffect
Spec == Init /\\ [][Next]_vars
=============================================================================
