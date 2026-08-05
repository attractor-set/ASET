----------------------------- MODULE MemoryCanon -----------------------------
EXTENDS Naturals
VARIABLES retrieved, verifiedFact, mutationPermit, mutated
vars == <<retrieved, verifiedFact, mutationPermit, mutated>>
Init == /\\ retrieved = FALSE /\\ verifiedFact = FALSE /\\ mutationPermit = FALSE /\\ mutated = FALSE
Retrieve == /\\ ~retrieved /\\ retrieved' = TRUE /\\ UNCHANGED <<verifiedFact, mutationPermit, mutated>>
AuthorizeMutation == /\\ ~mutationPermit /\\ mutationPermit' = TRUE /\\ UNCHANGED <<retrieved, verifiedFact, mutated>>
Mutate == /\\ mutationPermit /\\ ~mutated /\\ mutated' = TRUE /\\ UNCHANGED <<retrieved, verifiedFact, mutationPermit>>
Next == Retrieve \\/ AuthorizeMutation \\/ Mutate
RetrievalNotVerification == retrieved => ~verifiedFact
MutationAuthorized == mutated => mutationPermit
Spec == Init /\\ [][Next]_vars
=============================================================================
