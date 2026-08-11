----------- MODULE MinimalRecognitionBoundaryToSeedRefinementProofs -----------
EXTENDS MinimalRecognitionBoundary, TLAPS

ToSeedResolution(outcome) ==
  IF outcome = "ADMIT" THEN "ALLOW" ELSE "BLOCK"

SeedRequestMeta ==
  [r \in DOMAIN minRequestMeta |->
     [binding |-> AdapterBindingOf[r],
      previous |-> minRequestMeta[r].previous]]

SeedTerminalMeta ==
  [r \in DOMAIN minTerminalMeta |->
     [resolution |-> ToSeedResolution(minTerminalMeta[r].outcome),
      authority |-> AdapterAuthority]]

AdapterAuthorityBindings ==
  {AdapterAuthority} \X AdapterBindings

Seed == INSTANCE SeedResolution
  WITH ResolutionIds <- DecisionIds,
       Bindings <- AdapterBindings,
       Authorities <- AdapterAuthorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RecognizedAuthorityBindings <- AdapterAuthorityBindings,
       requestMeta <- SeedRequestMeta,
       terminalMeta <- SeedTerminalMeta,
       conflicts <- minConflicts

THEOREM SeedRequestsEqualMinRequests ==
  Seed!Requests = MinRequests
PROOF
  BY DEF Seed!Requests, SeedRequestMeta, MinRequests

THEOREM SeedTerminalRequestsEqualMinTerminalRequests ==
  Seed!TerminalRequests = MinTerminalRequests
PROOF
  BY DEF Seed!TerminalRequests, SeedTerminalMeta, MinTerminalRequests

THEOREM AdapterBindingOfIsSeedBinding ==
  \A r \in DecisionIds : AdapterBindingOf[r] \in AdapterBindings
PROOF
  BY SMTT(60), AdapterBindingType

THEOREM AdapterAuthorityIsSeedAuthority ==
  AdapterAuthority \in AdapterAuthorities
PROOF
  BY AdapterAuthorityType

THEOREM AdapterAuthorityRecognizesSynthesizedBinding ==
  \A r \in DecisionIds :
    <<AdapterAuthority, AdapterBindingOf[r]>> \in AdapterAuthorityBindings
PROOF
  BY SMTT(60),
     AdapterBindingOfIsSeedBinding,
     AdapterAuthorityIsSeedAuthority
     DEF AdapterAuthorityBindings

THEOREM ToSeedResolutionIsTerminalResolution ==
  \A outcome \in MinTerminalOutcomes :
    ToSeedResolution(outcome) \in Seed!TerminalResolutions
PROOF
  BY SMTT(60)
     DEF ToSeedResolution,
         MinTerminalOutcomes,
         Seed!TerminalResolutions

THEOREM MinInitRefinesSeedInit ==
  MinInit => Seed!Init
PROOF
  BY DEF MinInit,
         Seed!Init,
         SeedRequestMeta,
         SeedTerminalMeta

THEOREM MinRequestMetaStutterPreservesSeedRequestMeta ==
  UNCHANGED minRequestMeta => UNCHANGED SeedRequestMeta
PROOF
  BY SMTT(60)
     DEF SeedRequestMeta

THEOREM MinTerminalMetaStutterPreservesSeedTerminalMeta ==
  UNCHANGED minTerminalMeta => UNCHANGED SeedTerminalMeta
PROOF
  BY SMTT(60)
     DEF SeedTerminalMeta,
         ToSeedResolution

THEOREM SeedVarsStutterFromComponents ==
  /\ UNCHANGED SeedRequestMeta
  /\ UNCHANGED SeedTerminalMeta
  /\ UNCHANGED minConflicts
  => UNCHANGED Seed!vars
PROOF
  BY SMTT(60)
     DEF Seed!vars

THEOREM SeedSeedVarsStutterFromComponents ==
  /\ UNCHANGED SeedRequestMeta
  /\ UNCHANGED SeedTerminalMeta
  => UNCHANGED Seed!seedVars
PROOF
  BY SMTT(60)
     DEF Seed!seedVars

THEOREM MinRecognitionStutterStuttersSeed ==
  UNCHANGED minRecognitionVars => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     MinRequestMetaStutterPreservesSeedRequestMeta,
     MinTerminalMetaStutterPreservesSeedTerminalMeta,
     SeedVarsStutterFromComponents
     DEF minRecognitionVars

THEOREM MinApplicationStuttersSeed ==
  \A nextApplication \in ApplicationStates :
    MinApplicationStep(nextApplication) => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     MinRecognitionStutterStuttersSeed
     DEF MinApplicationStep

THEOREM MinOpenProducesSeedRequestUpdate ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
    =>
    SeedRequestMeta' =
      [x \in Seed!Requests \cup {r} |->
         IF x = r
         THEN [binding |-> AdapterBindingOf[r],
               previous |-> previous]
         ELSE SeedRequestMeta[x]]
PROOF
  BY SMTT(120),
     SeedRequestsEqualMinRequests
     DEF MinOpen,
         MinRequests,
         SeedRequestMeta,
         Seed!Requests

THEOREM MinOpenPreservesMinConflicts ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous) => UNCHANGED minConflicts
PROOF
  BY DEF MinOpen

THEOREM SeedRegisterRemainderStutterFromComponents ==
  /\ UNCHANGED SeedTerminalMeta
  /\ UNCHANGED minConflicts
  => UNCHANGED <<SeedTerminalMeta, minConflicts>>
PROOF
  BY SMTT(60)

THEOREM MinOpenPreservesSeedRegisterRemainder ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => UNCHANGED <<SeedTerminalMeta, minConflicts>>
PROOF
  BY SMTT(60),
     MinTerminalMetaStutterPreservesSeedTerminalMeta,
     MinOpenPreservesMinConflicts,
     SeedRegisterRemainderStutterFromComponents
     DEF MinOpen

THEOREM MinOpenFreshInSeedRequests ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => r \in DecisionIds \ Seed!Requests
PROOF
  BY SMTT(60),
     SeedRequestsEqualMinRequests
     DEF MinOpen

THEOREM MinOpenBindingIsSeedBinding ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => AdapterBindingOf[r] \in AdapterBindings
PROOF
  BY SMTT(60),
     AdapterBindingOfIsSeedBinding

THEOREM MinOpenAuthorityIsSeedAuthority ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => AdapterAuthority \in AdapterAuthorities
PROOF
  BY SMTT(60),
     AdapterAuthorityIsSeedAuthority

THEOREM MinOpenAuthorityBindingRecognized ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => <<AdapterAuthority, AdapterBindingOf[r]>>
           \in AdapterAuthorityBindings
PROOF
  BY SMTT(60),
     AdapterAuthorityRecognizesSynthesizedBinding

THEOREM MinOpenPreviousGuardMatchesSeed ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
      => \/ previous = NoCommitment
         \/ previous \in RecognizedTerminalCommitments
PROOF
  BY DEF MinOpen

THEOREM MinOpenRefinesSeedRegister ==
  \A r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)
    =>
    Seed!RegisterRequest(
      r,
      AdapterBindingOf[r],
      AdapterAuthority,
      previous)
PROOF
  BY SMTT(120),
     MinOpenFreshInSeedRequests,
     MinOpenBindingIsSeedBinding,
     MinOpenAuthorityIsSeedAuthority,
     MinOpenAuthorityBindingRecognized,
     MinOpenPreviousGuardMatchesSeed,
     MinOpenProducesSeedRequestUpdate,
     MinOpenPreservesSeedRegisterRemainder
     DEF Seed!RegisterRequest


THEOREM MinDecideProducesSeedTerminalUpdate ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
    =>
    SeedTerminalMeta' =
      [x \in Seed!TerminalRequests \cup {r} |->
         IF x = r
         THEN [resolution |-> ToSeedResolution(outcome),
               authority |-> AdapterAuthority]
         ELSE SeedTerminalMeta[x]]
PROOF
  BY SMTT(120),
     SeedTerminalRequestsEqualMinTerminalRequests
     DEF MinDecide,
         MinTerminalRequests,
         SeedTerminalMeta,
         Seed!TerminalRequests,
         ToSeedResolution

THEOREM SeedRequestBindingMatchesAdapter ==
  \A r \in MinRequests :
    Seed!RequestBinding(r) = AdapterBindingOf[r]
PROOF
  BY SMTT(60)
     DEF Seed!RequestBinding,
         SeedRequestMeta,
         MinRequests

THEOREM MinDecideRequestExistsInSeed ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => r \in Seed!Requests
PROOF
  BY SMTT(60),
     SeedRequestsEqualMinRequests
     DEF MinDecide

THEOREM MinDecideBindingMatchesSeedRequest ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => AdapterBindingOf[r] = Seed!RequestBinding(r)
PROOF
  BY SMTT(60),
     SeedRequestBindingMatchesAdapter
     DEF MinDecide

THEOREM MinDecideAuthorityIsSeedAuthority ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => AdapterAuthority \in AdapterAuthorities
PROOF
  BY SMTT(60),
     AdapterAuthorityIsSeedAuthority

THEOREM MinDecideAuthorityBindingRecognized ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => <<AdapterAuthority, AdapterBindingOf[r]>>
           \in AdapterAuthorityBindings
PROOF
  BY SMTT(60),
     AdapterAuthorityRecognizesSynthesizedBinding

THEOREM MinDecideResolutionIsSeedTerminal ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => ToSeedResolution(outcome) \in Seed!TerminalResolutions
PROOF
  BY SMTT(60),
     ToSeedResolutionIsTerminalResolution

THEOREM MinDecideFreshInSeedTerminalRequests ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => r \notin Seed!TerminalRequests
PROOF
  BY SMTT(60),
     SeedTerminalRequestsEqualMinTerminalRequests
     DEF MinDecide

THEOREM MinDecideNotConflicted ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => r \notin minConflicts
PROOF
  BY DEF MinDecide

THEOREM MinDecidePreservesSeedRequestMeta ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => UNCHANGED SeedRequestMeta
PROOF
  BY SMTT(60),
     MinRequestMetaStutterPreservesSeedRequestMeta
     DEF MinDecide

THEOREM MinDecidePreservesMinConflicts ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => UNCHANGED minConflicts
PROOF
  BY DEF MinDecide

THEOREM SeedSubmitRemainderStutterFromComponents ==
  /\ UNCHANGED SeedRequestMeta
  /\ UNCHANGED minConflicts
  => UNCHANGED <<SeedRequestMeta, minConflicts>>
PROOF
  BY SMTT(60)

THEOREM MinDecidePreservesSeedSubmitRemainder ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
      => UNCHANGED <<SeedRequestMeta, minConflicts>>
PROOF
  BY SMTT(60),
     MinDecidePreservesSeedRequestMeta,
     MinDecidePreservesMinConflicts,
     SeedSubmitRemainderStutterFromComponents

THEOREM MinDecideRefinesSeedSubmit ==
  \A r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)
    =>
    Seed!SubmitResolution(
      r,
      AdapterBindingOf[r],
      AdapterAuthority,
      ToSeedResolution(outcome))
PROOF
  BY SMTT(120),
     MinDecideRequestExistsInSeed,
     MinDecideBindingMatchesSeedRequest,
     MinDecideAuthorityIsSeedAuthority,
     MinDecideAuthorityBindingRecognized,
     MinDecideResolutionIsSeedTerminal,
     MinDecideFreshInSeedTerminalRequests,
     MinDecideNotConflicted,
     MinDecideProducesSeedTerminalUpdate,
     MinDecidePreservesSeedSubmitRemainder
     DEF Seed!SubmitResolution


THEOREM MinConflictPreservesSeedRequestMeta ==
  \A r \in DecisionIds :
    MinObserveConflict(r) => UNCHANGED SeedRequestMeta
PROOF
  BY SMTT(60),
     MinRequestMetaStutterPreservesSeedRequestMeta
     DEF MinObserveConflict

THEOREM MinConflictPreservesSeedTerminalMeta ==
  \A r \in DecisionIds :
    MinObserveConflict(r) => UNCHANGED SeedTerminalMeta
PROOF
  BY SMTT(60),
     MinTerminalMetaStutterPreservesSeedTerminalMeta
     DEF MinObserveConflict

THEOREM MinConflictPreservesSeedVars ==
  \A r \in DecisionIds :
    MinObserveConflict(r) => UNCHANGED Seed!seedVars
PROOF
  BY SMTT(60),
     MinConflictPreservesSeedRequestMeta,
     MinConflictPreservesSeedTerminalMeta,
     SeedSeedVarsStutterFromComponents

THEOREM MinConflictRefinesSeedConflict ==
  \A r \in DecisionIds :
    MinObserveConflict(r) => Seed!ObserveConflict(r)
PROOF
  BY SMTT(60),
     SeedTerminalRequestsEqualMinTerminalRequests,
     MinConflictPreservesSeedVars
     DEF MinObserveConflict,
         Seed!ObserveConflict

MinOpenTransition ==
  \E r \in DecisionIds,
     previous \in TerminalCommitments \cup {NoCommitment} :
    MinOpen(r, previous)

MinDecideTransition ==
  \E r \in DecisionIds,
     outcome \in MinTerminalOutcomes :
    MinDecide(r, outcome)

MinConflictTransition ==
  \E r \in DecisionIds :
    MinObserveConflict(r)

THEOREM MinOpenTransitionRefinesSeed ==
  MinOpenTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME MinOpenTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in DecisionIds,
              previous \in TerminalCommitments \cup {NoCommitment} :
          MinOpen(r, previous)
       BY Zenon DEF MinOpenTransition
  <1>2. Seed!RegisterRequest(
          r, AdapterBindingOf[r], AdapterAuthority, previous)
       BY <1>1, MinOpenRefinesSeedRegister
  <1>3. AdapterBindingOf[r] \in AdapterBindings
       BY <1>1, AdapterBindingOfIsSeedBinding
  <1> QED
       BY Zenon, <1>2, <1>3,
          AdapterAuthorityIsSeedAuthority
          DEF Seed!RecognizedSeedTransition

THEOREM MinDecideTransitionRefinesSeed ==
  MinDecideTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME MinDecideTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in DecisionIds,
              outcome \in MinTerminalOutcomes :
          MinDecide(r, outcome)
       BY Zenon DEF MinDecideTransition
  <1>2. Seed!SubmitResolution(
          r,
          AdapterBindingOf[r],
          AdapterAuthority,
          ToSeedResolution(outcome))
       BY <1>1, MinDecideRefinesSeedSubmit
  <1>3. AdapterBindingOf[r] \in AdapterBindings
       BY <1>1, AdapterBindingOfIsSeedBinding
  <1>4. ToSeedResolution(outcome) \in Seed!TerminalResolutions
       BY <1>1, ToSeedResolutionIsTerminalResolution
  <1> QED
       BY Zenon, <1>2, <1>3, <1>4,
          AdapterAuthorityIsSeedAuthority
          DEF Seed!RecognizedSeedTransition

THEOREM MinConflictTransitionRefinesSeed ==
  MinConflictTransition => Seed!RecognizedEnvironmentTransition
PROOF
  <1> SUFFICES ASSUME MinConflictTransition
               PROVE Seed!RecognizedEnvironmentTransition
       OBVIOUS
  <1>1. PICK r \in DecisionIds :
          MinObserveConflict(r)
       BY Zenon DEF MinConflictTransition
  <1>2. Seed!ObserveConflict(r)
       BY <1>1, MinConflictRefinesSeedConflict
  <1> QED
       BY <1>2
          DEF Seed!RecognizedEnvironmentTransition

THEOREM MinRecognitionTransitionRefinesSeed ==
  MinRecognitionTransition => Seed!Next
PROOF
  BY Zenon,
     MinOpenTransitionRefinesSeed,
     MinDecideTransitionRefinesSeed,
     MinConflictTransitionRefinesSeed
     DEF MinRecognitionTransition,
         MinOpenTransition,
         MinDecideTransition,
         MinConflictTransition,
         Seed!Next

THEOREM MinApplicationTransitionStuttersSeed ==
  MinApplicationTransition => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     MinApplicationStuttersSeed
     DEF MinApplicationTransition

THEOREM MinNextRefinesSeedNextOrStutter ==
  MinNext => [Seed!Next]_Seed!vars
PROOF
  BY SMTT(120),
     MinRecognitionTransitionRefinesSeed,
     MinApplicationTransitionStuttersSeed
     DEF MinNext

THEOREM MinStateStutterStuttersSeed ==
  UNCHANGED minVars => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     MinRequestMetaStutterPreservesSeedRequestMeta,
     MinTerminalMetaStutterPreservesSeedTerminalMeta,
     SeedVarsStutterFromComponents
     DEF minVars

THEOREM MinBoxNextRefinesBoxSeedNext ==
  [MinNext]_minVars => [Seed!Next]_Seed!vars
PROOF
  BY SMTT(120),
     MinNextRefinesSeedNextOrStutter,
     MinStateStutterStuttersSeed

THEOREM MinimalRecognitionBoundaryRefinesSeedResolution ==
  MinSpec => Seed!Spec
PROOF
  BY PTL,
     MinInitRefinesSeedInit,
     MinBoxNextRefinesBoxSeedNext
     DEF MinSpec,
         Seed!Spec

=============================================================================
