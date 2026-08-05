----------------------------- MODULE ContextCanon -----------------------------
EXTENDS Naturals
VARIABLES sourceVersion, headVersion, permitAvailable, consumed, patched
vars == <<sourceVersion, headVersion, permitAvailable, consumed, patched>>
Init == /\\ sourceVersion = 0 /\\ headVersion = 0 /\\ permitAvailable = FALSE /\\ consumed = FALSE /\\ patched = FALSE
IssuePermit == /\\ sourceVersion = headVersion /\\ ~permitAvailable /\\ permitAvailable' = TRUE /\\ UNCHANGED <<sourceVersion, headVersion, consumed, patched>>
ConcurrentAdvance == /\\ ~patched /\\ headVersion' = headVersion + 1 /\\ UNCHANGED <<sourceVersion, permitAvailable, consumed, patched>>
Cross == /\\ permitAvailable /\\ ~consumed /\\ sourceVersion = headVersion /\\ headVersion' = headVersion + 1 /\\ consumed' = TRUE /\\ patched' = TRUE /\\ permitAvailable' = FALSE /\\ UNCHANGED sourceVersion
Next == IssuePermit \\/ ConcurrentAdvance \\/ Cross
PatchRequiresExactSource == patched => consumed
OneCrossing == consumed => patched
Spec == Init /\\ [][Next]_vars
=============================================================================
