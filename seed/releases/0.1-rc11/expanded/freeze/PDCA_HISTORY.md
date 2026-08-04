# PDCA history — ASET Seed 0.1-rc11

Every cycle ends with a project-level public-API black-box audit. Only reproduced findings become input to the next cycle.

## Cycle 1 — replace plebiscite
**Plan:** remove recursive voting without weakening Context autonomy.  
**Do:** remove AMENDMENT, vote receipts, CUT and pruning; introduce member withdrawal and exact sibling redefinition.  
**Check:** original 55 traces restored.  
**Black-box Act:** transitive closure evidence was insufficient; Cycle 2 opened.

## Cycle 2 — transitive sibling closure
**Plan:** prove `C -> B -> A`.  
**Do:** compute minimal transitive direct-sibling closure and exact replacement mapping.  
**Check:** omission fails; full replacement remaps dependencies.  
**Black-box Act:** temporary alias race found; Cycle 3 opened.

## Cycle 3 — continuity and assurance
**Plan:** prevent alias capture and bind coverage evidence to sources.  
**Do:** rc10 draft derived alias reservation from pending records and introduced source hashes.  
**Check:** race rejected; coverage evidence source-bound.  
**Black-box Act:** exact-byte publication materialization became Cycle 4 input.

## Cycle 4 — normative convergence
**Plan:** align prose, schemas, runtime, requirements and publications.  
**Do:** regenerate carriers and release evidence.  
**Check:** clean-room checks of the then-current draft.  
**Black-box Act:** unrelated sibling could create a stranded pending withdrawal; Cycle 5 opened.

## Cycle 5 — exact affected set
**Plan:** forbid proposal-bound withdrawal outside the computed set.  
**Do:** add affected-set admission guard and public regression.  
**Check:** regression passed.  
**Black-box Act:** ancestor absorption of descendant pending proposal found; Cycle 6 opened.

## Cycle 6 — nested proposal serialization
**Plan:** prevent ancestor withdrawal from stranding descendant pending state.  
**Do:** add descendant-pending guard.  
**Check:** regression passed.  
**Black-box Act:** independent control audit showed the deeper problem: any destructive pending withdrawal can deadlock when the full authorization set never arrives.

## Cycle 7 — remove destructive pending governance
**Plan:** retain all safety goals of Cycles 1–6 with less state.  
**Do:** move all member authorizations into one atomic CONTEXT_REDEFINE; separate final standalone MEMBERSHIP_WITHDRAW; remove pending state, alias reservation, cancellation and nested serialization. Restore exact Permit success-policy binding.  
**Check:** conformance 55/55.  
**Black-box Act:** active dependency lifecycle gaps found; Cycle 8 opened.

## Cycle 8 — active dependency closure
**Plan:** prevent live Contexts from depending on historical Contexts.  
**Do:** require active dependency endpoints, reject standalone exit with active normative dependants, reject successor references to descendants withdrawn in the same commit.  
**Check:** conformance 55/55, black-box 25/25.  
**Black-box Act:** audit-record evidence completeness and branch coverage became Cycle 9 input.

## Cycle 9 — auditable records and coverage restoration
**Plan:** make governance decisions independently reconstructible and restore the mandatory branch threshold.  
**Do:** store full canonical proposal and authentication proof digests; add whole-state recomputation; add direct fail-closed branch guards.  
**Check:** independent 367/367, branch guards 252/252, branch coverage 733/806 = 90.942928%.  
**Black-box Act:** no new blocking semantic finding reproduced. Exact publication and clean-room release audit remain the final release cycle.
