---------------------- MODULE SeedCanonRefinementProofs ----------------------
EXTENDS SeedCanonProjection, TLAPS

(*
This proof establishes equivalence between SeedResolution and the generated
canonical projection for ASET-SEED-CANON-TLA-PROJECTION-V2.

The theorem is intentionally limited to the declared projection. Opaque
Bindings, authorityProofBindings and RecognizedTerminalCommitments remain
abstractions; cryptographic digest construction, concrete Authority grant-chain
construction, terminal-commitment provenance, storage-compaction refinement,
natural-language text equivalence, implementation refinement and liveness are
not proved here.
*)

THEOREM CanonResolutionAlgebraEquivalent ==
  /\ Resolutions = CanonResolutions
  /\ TerminalResolutions = CanonTerminalResolutions
  /\ CanonDerivedResolution = "UNKNOWN"
  /\ CanonEffectPermittedValue = "ALLOW"
  /\ CanonFailClosedValues = {"UNKNOWN", "BLOCK"}
  /\ CanonConflictResult = "UNKNOWN"
PROOF
  BY DEF Resolutions,
         TerminalResolutions,
         CanonResolutions,
         CanonTerminalResolutions,
         CanonDerivedResolution,
         CanonEffectPermittedValue,
         CanonFailClosedValues,
         CanonConflictResult


THEOREM CanonEvaluatorEquivalent ==
  \A r \in ResolutionIds :
    /\ ResolutionOf(r) = CanonResolutionOf(r)
    /\ EffectPermitted(r) = CanonEffectPermitted(r)
PROOF
  BY DEF ResolutionOf,
         CanonResolutionOf,
         EffectPermitted,
         CanonEffectPermitted,
         CanonConflictResult,
         CanonDerivedResolution,
         CanonEffectPermittedValue


THEOREM SeedResolutionBehaviorallyEquivalentToCanonProjection ==
  Spec <=> CanonSpec
PROOF
  BY DEF Spec,
         CanonSpec,
         Init,
         CanonInit,
         Next,
         CanonNext,
         RecognizedCanonicalTransition,
         CanonRecognizedCanonicalTransition,
         RegisterRequest,
         CanonRegisterRequest,
         SubmitResolution,
         CanonSubmitResolution,
         ObserveConflict,
         CanonObserveConflict,
         ObserveInvalidMaterial,
         CanonObserveInvalidMaterial,
         ObserveNonAuthoritativeInput,
         CanonObserveNonAuthoritativeInput,
         Evaluate,
         CanonEvaluate,
         TerminalResolutions,
         CanonTerminalResolutions

=============================================================================
