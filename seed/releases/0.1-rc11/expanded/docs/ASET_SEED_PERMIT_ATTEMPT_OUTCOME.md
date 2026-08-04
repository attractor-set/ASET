# Permit, attempt and Outcome

PermitTerms bind delegate, task, scope, recognized success policy, attempt limit, validity and caveats. Each accepted submission atomically creates an ExecutionIntent and PermitUseReceipt and increments attempts exactly once. Replay does not consume attempts.

Verification policy must equal the Permit success predicate and resolve to an active Constitution rule. Outcome uses the complete effective PASS Verification set. Positive Outcome requires effective SUCCESS; negative Outcome requires verified FAILURE, no effective SUCCESS and terminal Permit conditions. Outcome is immutable.
