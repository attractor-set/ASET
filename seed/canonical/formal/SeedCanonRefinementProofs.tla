---------------------- MODULE SeedCanonRefinementProofs ----------------------
EXTENDS SeedResolution, TLAPS

(*
Behavioral equivalence proof for projection profile V4.

SeedCanonProjection is standalone and does not import SeedResolution. The
instance below explicitly maps the generated projection constants and state
onto SeedResolution. This removes target-model aliasing from the projection
module while keeping opaque Binding, Authority-recognition and terminal-
commitment boundaries explicit.
*)

Canon == INSTANCE SeedCanonProjection
  WITH ResolutionIds <- ResolutionIds,
       Bindings <- Bindings,
       Authorities <- Authorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RequestAuthorityBindings <- RequestAuthorityBindings,
       TerminalAuthorityBindings <- TerminalAuthorityBindings,
       requestMeta <- requestMeta,
       terminalMeta <- terminalMeta,
       conflicts <- conflicts

THEOREM CanonResolutionAlgebraEquivalent ==
  /\ Resolutions = Canon!CanonResolutions
  /\ TerminalResolutions = Canon!CanonTerminalResolutions
  /\ Canon!CanonDerivedResolution = "UNKNOWN"
  /\ Canon!CanonEffectPermittedValue = "ALLOW"
  /\ Canon!CanonFailClosedValues = {"UNKNOWN", "BLOCK"}
  /\ Canon!CanonConflictResult = "UNKNOWN"
PROOF
  BY DEF Resolutions,
         TerminalResolutions,
         Canon!CanonResolutions,
         Canon!CanonTerminalResolutions,
         Canon!CanonDerivedResolution,
         Canon!CanonEffectPermittedValue,
         Canon!CanonFailClosedValues,
         Canon!CanonConflictResult


THEOREM CanonEvaluatorEquivalent ==
  \A r \in ResolutionIds :
    /\ ResolutionOf(r) = Canon!CanonResolutionOf(r)
    /\ EffectPermitted(r) = Canon!CanonEffectPermitted(r)
    /\ EvaluateResolution(r) = Canon!CanonEvaluateResolution(r)
PROOF
  BY DEF ResolutionOf,
         EffectPermitted,
         EvaluateResolution,
         Requests,
         TerminalRequests,
         TerminalResolution,
         Canon!CanonResolutionOf,
         Canon!CanonEffectPermitted,
         Canon!CanonEvaluateResolution,
         Canon!CanonRequests,
         Canon!CanonTerminalRequests,
         Canon!CanonTerminalResolution,
         Canon!CanonConflictResult,
         Canon!CanonDerivedResolution,
         Canon!CanonEffectPermittedValue


THEOREM SeedResolutionBehaviorallyEquivalentToCanonProjection ==
  Spec <=> Canon!CanonSpec
PROOF
  BY DEF Spec,
         Init,
         Next,
         RecognizedSeedTransition,
         RecognizedEnvironmentTransition,
         RegisterRequest,
         SubmitResolution,
         ObserveConflict,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalResolutions,
         vars,
         seedVars,
         Canon!CanonSpec,
         Canon!CanonInit,
         Canon!CanonNext,
         Canon!CanonRecognizedSeedTransition,
         Canon!CanonRecognizedEnvironmentTransition,
         Canon!CanonRegisterRequest,
         Canon!CanonSubmitResolution,
         Canon!CanonObserveConflict,
         Canon!CanonRequests,
         Canon!CanonTerminalRequests,
         Canon!CanonRequestBinding,
         Canon!CanonTerminalResolutions,
         Canon!CanonVars,
         Canon!CanonSeedVars

=============================================================================
