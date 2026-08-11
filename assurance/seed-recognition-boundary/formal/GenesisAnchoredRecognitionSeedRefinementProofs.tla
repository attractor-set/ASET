------------ MODULE GenesisAnchoredRecognitionSeedRefinementProofs ------------
EXTENDS GenesisAnchoredRecognition, TLAPS

Seed == INSTANCE SeedResolution
  WITH ResolutionIds <- ResolutionIds,
       Bindings <- Bindings,
       Authorities <- Authorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RecognizedAuthorityBindings <- RecognizedAuthorityBindings,
       requestMeta <- requestMeta,
       terminalMeta <- terminalMeta,
       conflicts <- conflicts

THEOREM RecognitionEvaluatorEquivalent ==
  \A r \in ResolutionIds :
    /\ ResolutionOf(r) = Seed!ResolutionOf(r)
    /\ EffectPermitted(r) = Seed!EffectPermitted(r)
PROOF
  BY DEF ResolutionOf,
         EffectPermitted,
         Requests,
         TerminalRequests,
         TerminalResolution,
         Seed!ResolutionOf,
         Seed!EffectPermitted,
         Seed!Requests,
         Seed!TerminalRequests,
         Seed!TerminalResolution

THEOREM InitRefinesSeedInit ==
  Init => Seed!Init
PROOF
  BY DEF Init, Seed!Init

THEOREM RegisterRefinesSeedStep ==
  \A r \in ResolutionIds,
     c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, c, d, policy, scope, a, previous)
    =>
      Seed!RegisterRequest(
        r,
        BindingOf(c, lineage, d, policy, scope),
        a,
        previous)
PROOF
  BY SMTT(60)
     DEF RegisterRequest,
         BindingOf,
         Requests,
         lineageVars,
         Seed!RegisterRequest,
         Seed!Requests

THEOREM SubmitRefinesSeedStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) =>
      Seed!SubmitResolution(r, b, a, value)
PROOF
  BY SMTT(60)
     DEF SubmitResolution,
         RequestBinding,
         Requests,
         TerminalRequests,
         TerminalResolutions,
         lineageVars,
         Seed!SubmitResolution,
         Seed!TerminalResolutions,
         Seed!RequestBinding,
         Seed!Requests,
         Seed!TerminalRequests

THEOREM ConflictRefinesSeedStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => Seed!ObserveConflict(r)
PROOF
  BY DEF ObserveConflict,
         TerminalRequests,
         Seed!ObserveConflict,
         Seed!TerminalRequests,
         Seed!seedVars

THEOREM ApplicationStuttersSeed ==
  \A r \in ResolutionIds, e \in Events :
    ApplyRecognized(r, e) => UNCHANGED Seed!vars
PROOF
  BY DEF ApplyRecognized, recognitionVars, Seed!vars

GCRRegisterTransition ==
  \E r \in ResolutionIds,
     c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, c, d, policy, scope, a, previous)

GCRSubmitTransition ==
  \E r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)

THEOREM RegisterTransitionRefinesSeed ==
  GCRRegisterTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME GCRRegisterTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              c \in Contexts,
              d \in Descriptors,
              policy \in PolicyEpochs,
              scope \in Scopes,
              a \in Authorities,
              previous \in TerminalCommitments \cup {NoCommitment} :
          RegisterRequest(r, c, d, policy, scope, a, previous)
       BY Zenon DEF GCRRegisterTransition
  <1>2. Seed!RegisterRequest(
          r,
          BindingOf(c, lineage, d, policy, scope),
          a,
          previous)
       BY <1>1, RegisterRefinesSeedStep
  <1>3. BindingOf(c, lineage, d, policy, scope) \in Bindings
       BY <1>1 DEF RegisterRequest
  <1> QED
       BY Zenon, <1>2, <1>3
          DEF Seed!RecognizedSeedTransition

THEOREM SubmitTransitionRefinesSeed ==
  GCRSubmitTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME GCRSubmitTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              b \in Bindings,
              a \in Authorities,
              value \in TerminalResolutions :
          SubmitResolution(r, b, a, value)
       BY Zenon DEF GCRSubmitTransition
  <1>2. Seed!SubmitResolution(r, b, a, value)
       BY <1>1, SubmitRefinesSeedStep
  <1> QED
       BY <1>2
          DEF Seed!RecognizedSeedTransition,
              TerminalResolutions,
              Seed!TerminalResolutions

THEOREM RecognizedSeedLikeTransitionRefinesSeed ==
  RecognizedSeedLikeTransition => Seed!RecognizedSeedTransition
PROOF
  BY Zenon,
     RegisterTransitionRefinesSeed,
     SubmitTransitionRefinesSeed
     DEF RecognizedSeedLikeTransition,
         GCRRegisterTransition,
         GCRSubmitTransition

THEOREM EnvironmentTransitionRefinesSeed ==
  EnvironmentTransition => Seed!RecognizedEnvironmentTransition
PROOF
  BY SMTT(60),
     ConflictRefinesSeedStep
     DEF EnvironmentTransition,
         Seed!RecognizedEnvironmentTransition

THEOREM ApplicationTransitionStuttersSeed ==
  ApplicationTransition => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     ApplicationStuttersSeed
     DEF ApplicationTransition

THEOREM GCRNextRefinesSeedNextOrStutter ==
  Next => [Seed!Next]_Seed!vars
PROOF
  BY SMTT(60),
     RecognizedSeedLikeTransitionRefinesSeed,
     EnvironmentTransitionRefinesSeed,
     ApplicationTransitionStuttersSeed
     DEF Next,
         Seed!Next

THEOREM BoxGCRNextRefinesBoxSeedNext ==
  [Next]_vars => [Seed!Next]_Seed!vars
PROOF
  BY GCRNextRefinesSeedNextOrStutter
     DEF vars, Seed!vars

THEOREM GenesisAnchoredRecognitionRefinesSeedResolution ==
  Spec => Seed!Spec
PROOF
  BY PTL,
     InitRefinesSeedInit,
     BoxGCRNextRefinesBoxSeedNext
     DEF Spec, Seed!Spec

=============================================================================
