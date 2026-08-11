------------- MODULE RecognitionPayloadObservabilityProofs -------------
EXTENDS RecognitionPayloadObservability, TLAPS

THEOREM PayloadWitnessStatesValid ==
  /\ AbsentWitness \in ValidPayloadStates
  /\ PendingB0P0 \in ValidPayloadStates
  /\ PendingB1P0 \in ValidPayloadStates
  /\ PendingB0P1 \in ValidPayloadStates
  /\ AllowB0P0A0 \in ValidPayloadStates
  /\ AllowB0P0A1 \in ValidPayloadStates
PROOF
  BY SMTT(120)
     DEF AbsentWitness,
         PendingB0P0,
         PendingB1P0,
         PendingB0P1,
         AllowB0P0A0,
         AllowB0P0A1,
         ValidPayloadStates,
         ValidPayloadState,
         PayloadStateType,
         BindingsWitness,
         AuthoritiesWitness,
         PreviousWitness,
         NoBindingWitness,
         NoPreviousWitness,
         NoAuthorityWitness,
         WitnessRecognizedAuthorityBindings,
         TerminalPhases,
         OperationalPhases

THEOREM EffectiveObservationDependsOnlyOnPhase ==
  \A x \in ValidPayloadStates, y \in ValidPayloadStates :
    x.phase = y.phase
      => EffectiveStateObservables(x) = EffectiveStateObservables(y)
PROOF
  BY SMTT(60)
     DEF EffectiveStateObservables,
         EffectiveValue

THEOREM CoarseCapabilityDependsOnlyOnPhase ==
  \A x \in ValidPayloadStates, y \in ValidPayloadStates :
    x.phase = y.phase
      =>
    CoarseCapabilityStateObservables(x)
      = CoarseCapabilityStateObservables(y)
PROOF
  BY SMTT(60)
     DEF CoarseCapabilityStateObservables,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict

THEOREM RetainedHistoryDependsOnlyOnPhase ==
  \A x \in ValidPayloadStates, y \in ValidPayloadStates :
    x.phase = y.phase
      =>
    RetainedHistoryStateObservables(x)
      = RetainedHistoryStateObservables(y)
PROOF
  BY SMTT(60)
     DEF RetainedHistoryStateObservables,
         HistoryObservables,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict,
         RetainedTerminal

THEOREM PhaseOnlyPreservesEffectiveObservation ==
  FaithfulProjection(
    PhaseOnlyRepresentationMap,
    EffectiveStateObservationMap)
PROOF
  BY SMTT(120),
     EffectiveObservationDependsOnlyOnPhase
     DEF FaithfulProjection,
         PhaseOnlyRepresentationMap,
         EffectiveStateObservationMap,
         ValidPayloadStates

THEOREM PhaseOnlyPreservesCoarseCapability ==
  FaithfulProjection(
    PhaseOnlyRepresentationMap,
    CoarseCapabilityStateObservationMap)
PROOF
  BY SMTT(120),
     CoarseCapabilityDependsOnlyOnPhase
     DEF FaithfulProjection,
         PhaseOnlyRepresentationMap,
         CoarseCapabilityStateObservationMap,
         ValidPayloadStates

THEOREM PhaseOnlyPreservesRetainedHistory ==
  FaithfulProjection(
    PhaseOnlyRepresentationMap,
    RetainedHistoryStateObservationMap)
PROOF
  BY SMTT(120),
     RetainedHistoryDependsOnlyOnPhase
     DEF FaithfulProjection,
         PhaseOnlyRepresentationMap,
         RetainedHistoryStateObservationMap,
         ValidPayloadStates

THEOREM PhasePendingBindingPreservesParameterizedCapability ==
  FaithfulProjection(
    PhasePendingBindingRepresentationMap,
    ParameterizedCapabilityStateObservationMap)
PROOF
  BY SMTT(180)
     DEF FaithfulProjection,
         PhasePendingBindingRepresentationMap,
         ParameterizedCapabilityStateObservationMap,
         ParameterizedCapabilityStateObservables,
         PendingBindingKey,
         RetainedHistoryStateObservables,
         HistoryObservables,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict,
         RetainedTerminal,
         ValidPayloadStates

THEOREM SameParameterizedRepresentationImpliesSameEnabledSubmitLabels ==
  \A x \in ValidPayloadStates, y \in ValidPayloadStates :
    PhasePendingBindingRepresentationMap[x]
      = PhasePendingBindingRepresentationMap[y]
      => EnabledSubmitLabels(x) = EnabledSubmitLabels(y)
PROOF
  BY SMTT(240)
     DEF PhasePendingBindingRepresentationMap,
         PendingBindingKey,
         EnabledSubmitLabels,
         SubmitAuthorities,
         WitnessRecognizedAuthorityBindings,
         AuthoritiesWitness,
         WitnessTerminalResolutions,
         ValidPayloadStates

THEOREM BindingWitnessChangesParameterizedCapability ==
  /\ PhaseOnlyRepresentationMap[PendingB0P0]
       = PhaseOnlyRepresentationMap[PendingB1P0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[PendingB1P0]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF PhaseOnlyRepresentationMap,
         ParameterizedCapabilityStateObservationMap,
         ParameterizedCapabilityStateObservables,
         PendingBindingKey,
         RetainedHistoryStateObservables,
         PendingB0P0,
         PendingB1P0,
         ValidPayloadStates

THEOREM PreviousWitnessInvisibleToParameterizedCapability ==
  ParameterizedCapabilityStateObservationMap[PendingB0P0]
    = ParameterizedCapabilityStateObservationMap[PendingB0P1]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF ParameterizedCapabilityStateObservationMap,
         ParameterizedCapabilityStateObservables,
         PendingBindingKey,
         RetainedHistoryStateObservables,
         HistoryObservables,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict,
         RetainedTerminal,
         PendingB0P0,
         PendingB0P1,
         ValidPayloadStates

THEOREM TerminalAuthorityWitnessInvisibleToParameterizedCapability ==
  ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
    = ParameterizedCapabilityStateObservationMap[AllowB0P0A1]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF ParameterizedCapabilityStateObservationMap,
         ParameterizedCapabilityStateObservables,
         PendingBindingKey,
         RetainedHistoryStateObservables,
         HistoryObservables,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict,
         RetainedTerminal,
         AllowB0P0A0,
         AllowB0P0A1,
         ValidPayloadStates

THEOREM FullCanonicalRepresentationPreservesExactState ==
  FaithfulProjection(
    FullCanonicalRepresentationMap,
    ExactStateObservationMap)
PROOF
  BY SMTT(60)
     DEF FaithfulProjection,
         FullCanonicalRepresentationMap,
         ExactStateObservationMap,
         ExactStateObservables,
         ValidPayloadStates

THEOREM DropBindingExactCounterexample ==
  /\ DropBindingRepresentationMap[PendingB0P0]
       = DropBindingRepresentationMap[PendingB1P0]
  /\ ExactStateObservationMap[PendingB0P0]
       # ExactStateObservationMap[PendingB1P0]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF DropBindingRepresentationMap,
         ExactStateObservationMap,
         ExactStateObservables,
         PendingB0P0,
         PendingB1P0,
         ValidPayloadStates

THEOREM DropPreviousExactCounterexample ==
  /\ DropPreviousRepresentationMap[PendingB0P0]
       = DropPreviousRepresentationMap[PendingB0P1]
  /\ ExactStateObservationMap[PendingB0P0]
       # ExactStateObservationMap[PendingB0P1]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF DropPreviousRepresentationMap,
         ExactStateObservationMap,
         ExactStateObservables,
         PendingB0P0,
         PendingB0P1,
         ValidPayloadStates

THEOREM DropAuthorityExactCounterexample ==
  /\ DropAuthorityRepresentationMap[AllowB0P0A0]
       = DropAuthorityRepresentationMap[AllowB0P0A1]
  /\ ExactStateObservationMap[AllowB0P0A0]
       # ExactStateObservationMap[AllowB0P0A1]
PROOF
  BY SMTT(120), PayloadWitnessStatesValid
     DEF DropAuthorityRepresentationMap,
         ExactStateObservationMap,
         ExactStateObservables,
         AllowB0P0A0,
         AllowB0P0A1,
         ValidPayloadStates

THEOREM PayloadObservationSummary ==
  /\ FaithfulProjection(
       PhaseOnlyRepresentationMap,
       EffectiveStateObservationMap)
  /\ FaithfulProjection(
       PhaseOnlyRepresentationMap,
       CoarseCapabilityStateObservationMap)
  /\ FaithfulProjection(
       PhaseOnlyRepresentationMap,
       RetainedHistoryStateObservationMap)
  /\ FaithfulProjection(
       PhasePendingBindingRepresentationMap,
       ParameterizedCapabilityStateObservationMap)
  /\ FaithfulProjection(
       FullCanonicalRepresentationMap,
       ExactStateObservationMap)
PROOF
  BY PhaseOnlyPreservesEffectiveObservation,
     PhaseOnlyPreservesCoarseCapability,
     PhaseOnlyPreservesRetainedHistory,
     PhasePendingBindingPreservesParameterizedCapability,
     FullCanonicalRepresentationPreservesExactState

=============================================================================
