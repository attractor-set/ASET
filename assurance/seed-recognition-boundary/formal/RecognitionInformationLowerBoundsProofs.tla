------------- MODULE RecognitionInformationLowerBoundsProofs -------------
EXTENDS RecognitionInformationLowerBounds, TLAPS, FiniteSetTheorems

SixteenCodeSlots == 1..16

ExactWitnessAt(i) ==
  CASE i = 1  -> AbsentWitness
    [] i = 2  -> PendingB0P0
    [] i = 3  -> PendingB0P1
    [] i = 4  -> PendingB1P0
    [] i = 5  -> PendingB1P1
    [] i = 6  -> AllowB0P0A0
    [] i = 7  -> AllowB0P1A0
    [] i = 8  -> AllowB0P0A1
    [] i = 9  -> AllowB0P1A1
    [] i = 10 -> AllowB1P0A0
    [] i = 11 -> AllowB1P1A0
    [] i = 12 -> BlockB0P0A0
    [] i = 13 -> BlockB0P1A0
    [] i = 14 -> BlockB0P0A1
    [] i = 15 -> BlockB0P1A1
    [] i = 16 -> BlockB1P0A0
    [] OTHER  -> BlockB1P1A0

IndexedWitnessEncoding(f) ==
  [i \in 1..17 |-> f[ExactWitnessAt(i)]]

THEOREM ExactWitnessPairwiseDistinctPart1 ==
  /\ AbsentWitness # PendingB0P0
  /\ AbsentWitness # AllowB0P0A0
  /\ AbsentWitness # AllowB1P0A0
  /\ AbsentWitness # BlockB0P0A1
  /\ PendingB0P0 # PendingB0P1
  /\ PendingB0P0 # AllowB0P1A0
  /\ PendingB0P0 # AllowB1P1A0
  /\ PendingB0P0 # BlockB0P1A1
  /\ PendingB0P1 # PendingB1P1
  /\ PendingB0P1 # AllowB0P1A1
  /\ PendingB0P1 # BlockB0P1A0
  /\ PendingB0P1 # BlockB1P1A0
  /\ PendingB1P0 # AllowB0P0A1
  /\ PendingB1P0 # BlockB0P0A0
  /\ PendingB1P0 # BlockB1P0A0
  /\ PendingB1P1 # AllowB0P0A1
  /\ PendingB1P1 # BlockB0P0A0
  /\ PendingB1P1 # BlockB1P0A0
  /\ AllowB0P0A0 # AllowB0P1A1
  /\ AllowB0P0A0 # BlockB0P1A0
  /\ AllowB0P0A0 # BlockB1P1A0
  /\ AllowB0P1A0 # AllowB1P1A0
  /\ AllowB0P1A0 # BlockB0P1A1
  /\ AllowB0P0A1 # AllowB1P0A0
  /\ AllowB0P0A1 # BlockB0P0A1
  /\ AllowB0P1A1 # AllowB1P0A0
  /\ AllowB0P1A1 # BlockB0P0A1
  /\ AllowB1P0A0 # AllowB1P1A0
  /\ AllowB1P0A0 # BlockB0P1A1
  /\ AllowB1P1A0 # BlockB0P1A0
  /\ AllowB1P1A0 # BlockB1P1A0
  /\ BlockB0P0A0 # BlockB1P0A0
  /\ BlockB0P1A0 # BlockB1P0A0
  /\ BlockB0P0A1 # BlockB1P1A0
PROOF
  BY SMTT(240)
     DEF AbsentWitness,
         PendingB0P0,
         AllowB0P0A0,
         AllowB1P0A0,
         BlockB0P0A1,
         PendingB0P1,
         AllowB0P1A0,
         AllowB1P1A0,
         BlockB0P1A1,
         PendingB1P1,
         AllowB0P1A1,
         BlockB0P1A0,
         BlockB1P1A0,
         PendingB1P0,
         AllowB0P0A1,
         BlockB0P0A0,
         BlockB1P0A0
THEOREM ExactWitnessPairwiseDistinctPart2 ==
  /\ AbsentWitness # PendingB0P1
  /\ AbsentWitness # AllowB0P1A0
  /\ AbsentWitness # AllowB1P1A0
  /\ AbsentWitness # BlockB0P1A1
  /\ PendingB0P0 # PendingB1P0
  /\ PendingB0P0 # AllowB0P0A1
  /\ PendingB0P0 # BlockB0P0A0
  /\ PendingB0P0 # BlockB1P0A0
  /\ PendingB0P1 # AllowB0P0A0
  /\ PendingB0P1 # AllowB1P0A0
  /\ PendingB0P1 # BlockB0P0A1
  /\ PendingB1P0 # PendingB1P1
  /\ PendingB1P0 # AllowB0P1A1
  /\ PendingB1P0 # BlockB0P1A0
  /\ PendingB1P0 # BlockB1P1A0
  /\ PendingB1P1 # AllowB0P1A1
  /\ PendingB1P1 # BlockB0P1A0
  /\ PendingB1P1 # BlockB1P1A0
  /\ AllowB0P0A0 # AllowB1P0A0
  /\ AllowB0P0A0 # BlockB0P0A1
  /\ AllowB0P1A0 # AllowB0P0A1
  /\ AllowB0P1A0 # BlockB0P0A0
  /\ AllowB0P1A0 # BlockB1P0A0
  /\ AllowB0P0A1 # AllowB1P1A0
  /\ AllowB0P0A1 # BlockB0P1A1
  /\ AllowB0P1A1 # AllowB1P1A0
  /\ AllowB0P1A1 # BlockB0P1A1
  /\ AllowB1P0A0 # BlockB0P0A0
  /\ AllowB1P0A0 # BlockB1P0A0
  /\ AllowB1P1A0 # BlockB0P0A1
  /\ BlockB0P0A0 # BlockB0P1A0
  /\ BlockB0P0A0 # BlockB1P1A0
  /\ BlockB0P1A0 # BlockB1P1A0
  /\ BlockB0P1A1 # BlockB1P0A0
PROOF
  BY SMTT(240)
     DEF AbsentWitness,
         PendingB0P1,
         AllowB0P1A0,
         AllowB1P1A0,
         BlockB0P1A1,
         PendingB0P0,
         PendingB1P0,
         AllowB0P0A1,
         BlockB0P0A0,
         BlockB1P0A0,
         AllowB0P0A0,
         AllowB1P0A0,
         BlockB0P0A1,
         PendingB1P1,
         AllowB0P1A1,
         BlockB0P1A0,
         BlockB1P1A0
THEOREM ExactWitnessPairwiseDistinctPart3 ==
  /\ AbsentWitness # PendingB1P0
  /\ AbsentWitness # AllowB0P0A1
  /\ AbsentWitness # BlockB0P0A0
  /\ AbsentWitness # BlockB1P0A0
  /\ PendingB0P0 # PendingB1P1
  /\ PendingB0P0 # AllowB0P1A1
  /\ PendingB0P0 # BlockB0P1A0
  /\ PendingB0P0 # BlockB1P1A0
  /\ PendingB0P1 # AllowB0P1A0
  /\ PendingB0P1 # AllowB1P1A0
  /\ PendingB0P1 # BlockB0P1A1
  /\ PendingB1P0 # AllowB0P0A0
  /\ PendingB1P0 # AllowB1P0A0
  /\ PendingB1P0 # BlockB0P0A1
  /\ PendingB1P1 # AllowB0P0A0
  /\ PendingB1P1 # AllowB1P0A0
  /\ PendingB1P1 # BlockB0P0A1
  /\ AllowB0P0A0 # AllowB0P1A0
  /\ AllowB0P0A0 # AllowB1P1A0
  /\ AllowB0P0A0 # BlockB0P1A1
  /\ AllowB0P1A0 # AllowB0P1A1
  /\ AllowB0P1A0 # BlockB0P1A0
  /\ AllowB0P1A0 # BlockB1P1A0
  /\ AllowB0P0A1 # BlockB0P0A0
  /\ AllowB0P0A1 # BlockB1P0A0
  /\ AllowB0P1A1 # BlockB0P0A0
  /\ AllowB0P1A1 # BlockB1P0A0
  /\ AllowB1P0A0 # BlockB0P1A0
  /\ AllowB1P0A0 # BlockB1P1A0
  /\ AllowB1P1A0 # BlockB0P1A1
  /\ BlockB0P0A0 # BlockB0P0A1
  /\ BlockB0P1A0 # BlockB0P0A1
  /\ BlockB0P0A1 # BlockB0P1A1
  /\ BlockB0P1A1 # BlockB1P1A0
PROOF
  BY SMTT(240)
     DEF AbsentWitness,
         PendingB1P0,
         AllowB0P0A1,
         BlockB0P0A0,
         BlockB1P0A0,
         PendingB0P0,
         PendingB1P1,
         AllowB0P1A1,
         BlockB0P1A0,
         BlockB1P1A0,
         PendingB0P1,
         AllowB0P1A0,
         AllowB1P1A0,
         BlockB0P1A1,
         AllowB0P0A0,
         AllowB1P0A0,
         BlockB0P0A1
THEOREM ExactWitnessPairwiseDistinctPart4 ==
  /\ AbsentWitness # PendingB1P1
  /\ AbsentWitness # AllowB0P1A1
  /\ AbsentWitness # BlockB0P1A0
  /\ AbsentWitness # BlockB1P1A0
  /\ PendingB0P0 # AllowB0P0A0
  /\ PendingB0P0 # AllowB1P0A0
  /\ PendingB0P0 # BlockB0P0A1
  /\ PendingB0P1 # PendingB1P0
  /\ PendingB0P1 # AllowB0P0A1
  /\ PendingB0P1 # BlockB0P0A0
  /\ PendingB0P1 # BlockB1P0A0
  /\ PendingB1P0 # AllowB0P1A0
  /\ PendingB1P0 # AllowB1P1A0
  /\ PendingB1P0 # BlockB0P1A1
  /\ PendingB1P1 # AllowB0P1A0
  /\ PendingB1P1 # AllowB1P1A0
  /\ PendingB1P1 # BlockB0P1A1
  /\ AllowB0P0A0 # AllowB0P0A1
  /\ AllowB0P0A0 # BlockB0P0A0
  /\ AllowB0P0A0 # BlockB1P0A0
  /\ AllowB0P1A0 # AllowB1P0A0
  /\ AllowB0P1A0 # BlockB0P0A1
  /\ AllowB0P0A1 # AllowB0P1A1
  /\ AllowB0P0A1 # BlockB0P1A0
  /\ AllowB0P0A1 # BlockB1P1A0
  /\ AllowB0P1A1 # BlockB0P1A0
  /\ AllowB0P1A1 # BlockB1P1A0
  /\ AllowB1P0A0 # BlockB0P0A1
  /\ AllowB1P1A0 # BlockB0P0A0
  /\ AllowB1P1A0 # BlockB1P0A0
  /\ BlockB0P0A0 # BlockB0P1A1
  /\ BlockB0P1A0 # BlockB0P1A1
  /\ BlockB0P0A1 # BlockB1P0A0
  /\ BlockB1P0A0 # BlockB1P1A0
PROOF
  BY SMTT(240)
     DEF AbsentWitness,
         PendingB1P1,
         AllowB0P1A1,
         BlockB0P1A0,
         BlockB1P1A0,
         PendingB0P0,
         AllowB0P0A0,
         AllowB1P0A0,
         BlockB0P0A1,
         PendingB0P1,
         PendingB1P0,
         AllowB0P0A1,
         BlockB0P0A0,
         BlockB1P0A0,
         AllowB0P1A0,
         AllowB1P1A0,
         BlockB0P1A1
THEOREM ExactWitnessPairwiseDistinct ==
  /\ ExactWitnessPairwiseDistinctPart1
  /\ ExactWitnessPairwiseDistinctPart2
  /\ ExactWitnessPairwiseDistinctPart3
  /\ ExactWitnessPairwiseDistinctPart4
PROOF
  BY ExactWitnessPairwiseDistinctPart1,
     ExactWitnessPairwiseDistinctPart2,
     ExactWitnessPairwiseDistinctPart3,
     ExactWitnessPairwiseDistinctPart4

THEOREM ExactWitnessAtInjective ==
  \A i \in 1..17, j \in 1..17 :
    i # j => ExactWitnessAt(i) # ExactWitnessAt(j)
PROOF
  BY SMTT(360), ExactWitnessPairwiseDistinct
     DEF ExactWitnessAt

THEOREM ExactWitnessAtInRepresentatives ==
  \A i \in 1..17 :
    ExactWitnessAt(i) \in ExactSeventeenRepresentatives
PROOF
  BY SMTT(300)
     DEF ExactWitnessAt,
         ExactSeventeenRepresentatives

THEOREM SeventeenIndexCardinality ==
  /\ IsFiniteSet(1..17)
  /\ Cardinality(1..17) = 17
PROOF
  BY SMTT(60), FS_Interval

THEOREM SixteenSlotCardinality ==
  /\ IsFiniteSet(SixteenCodeSlots)
  /\ Cardinality(SixteenCodeSlots) = 16
PROOF
  BY SMTT(60), FS_Interval
     DEF SixteenCodeSlots


THEOREM BaseInformationWitnessStatesValid ==
  /\ AbsentWitness \in ValidPayloadStates
  /\ PendingB0P0 \in ValidPayloadStates
  /\ PendingB1P0 \in ValidPayloadStates
  /\ PendingB0P1 \in ValidPayloadStates
  /\ AllowB0P0A0 \in ValidPayloadStates
  /\ AllowB0P0A1 \in ValidPayloadStates
PROOF
  BY SMTT(180)
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

THEOREM InformationWitnessStatesValid ==
  /\ PendingB1P1 \in ValidPayloadStates
  /\ BlockB0P0A0 \in ValidPayloadStates
  /\ InvalidatedAllowB0P0A0 \in ValidPayloadStates
  /\ InvalidatedBlockB0P0A0 \in ValidPayloadStates
  /\ AllowB0P1A0 \in ValidPayloadStates
  /\ AllowB0P0A1 \in ValidPayloadStates
  /\ AllowB0P1A1 \in ValidPayloadStates
  /\ AllowB1P0A0 \in ValidPayloadStates
  /\ AllowB1P1A0 \in ValidPayloadStates
  /\ BlockB0P1A0 \in ValidPayloadStates
  /\ BlockB0P0A1 \in ValidPayloadStates
  /\ BlockB0P1A1 \in ValidPayloadStates
  /\ BlockB1P0A0 \in ValidPayloadStates
  /\ BlockB1P1A0 \in ValidPayloadStates
PROOF
  BY SMTT(180), BaseInformationWitnessStatesValid
     DEF PendingB1P1,
         BlockB0P0A0,
         InvalidatedAllowB0P0A0,
         InvalidatedBlockB0P0A0,
         AllowB0P1A0,
         AllowB0P0A1,
         AllowB0P1A1,
         AllowB1P0A0,
         AllowB1P1A0,
         BlockB0P1A0,
         BlockB0P0A1,
         BlockB0P1A1,
         BlockB1P0A0,
         BlockB1P1A0,
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

THEOREM ParameterizedSevenObservationsPairwiseDistinct ==
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[PendingB0P0]
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[PendingB1P0]
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AbsentWitness]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[PendingB1P0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB0P0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB1P0]
       # ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB1P0]
       # ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB1P0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[PendingB1P0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
       # ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[AllowB0P0A0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[BlockB0P0A0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
  /\ ParameterizedCapabilityStateObservationMap[InvalidatedAllowB0P0A0]
       # ParameterizedCapabilityStateObservationMap[InvalidatedBlockB0P0A0]
PROOF
  BY SMTT(300), BaseInformationWitnessStatesValid, InformationWitnessStatesValid
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
         AbsentWitness,
         PendingB0P0,
         PendingB1P0,
         AllowB0P0A0,
         BlockB0P0A0,
         InvalidatedAllowB0P0A0,
         InvalidatedBlockB0P0A0,
         ValidPayloadStates

THEOREM NoFaithfulFourCodeParameterizedEncoding ==
  ~\E f :
    FaithfulOnWitnesses(
      f,
      ParameterizedSevenRepresentatives,
      ParameterizedCapabilityStateObservationMap,
      FourCodes)
PROOF
  BY SMTT(360), ParameterizedSevenObservationsPairwiseDistinct
     DEF FaithfulOnWitnesses,
         ParameterizedSevenRepresentatives,
         FourCodes

THEOREM ExactSeventeenRepresentativesValid ==
  ExactSeventeenRepresentatives \subseteq ValidPayloadStates
PROOF
  BY SMTT(240), BaseInformationWitnessStatesValid, InformationWitnessStatesValid
     DEF ExactSeventeenRepresentatives

THEOREM ExactObservationIsIdentityOnValidStates ==
  \A s \in ValidPayloadStates :
    ExactStateObservationMap[s] = s
PROOF
  BY SMTT(60)
     DEF ExactStateObservationMap,
         ExactStateObservables,
         ValidPayloadStates

THEOREM NoFaithfulSixteenCodeExactEncoding ==
  ~\E f :
    FaithfulOnWitnesses(
      f,
      ExactSeventeenRepresentatives,
      ExactStateObservationMap,
      SixteenCodeSlots)
PROOF
  <1> SUFFICES
        ASSUME NEW f,
               FaithfulOnWitnesses(
                 f,
                 ExactSeventeenRepresentatives,
                 ExactStateObservationMap,
                 SixteenCodeSlots)
        PROVE FALSE
       OBVIOUS
  <1>1. f \in [ExactSeventeenRepresentatives -> SixteenCodeSlots]
       BY DEF FaithfulOnWitnesses
  <1>2. IndexedWitnessEncoding(f) \in [1..17 -> SixteenCodeSlots]
       BY SMTT(180), <1>1, ExactWitnessAtInRepresentatives
          DEF IndexedWitnessEncoding
  <1>3. PICK i, j \in 1..17 :
          /\ i # j
          /\ IndexedWitnessEncoding(f)[i]
               = IndexedWitnessEncoding(f)[j]
       BY <1>2,
          SeventeenIndexCardinality,
          SixteenSlotCardinality,
          FS_PigeonHole
  <1>4. ExactWitnessAt(i) # ExactWitnessAt(j)
       BY <1>3, ExactWitnessAtInjective
  <1>5. /\ ExactWitnessAt(i) \in ValidPayloadStates
         /\ ExactWitnessAt(j) \in ValidPayloadStates
       BY <1>3,
          ExactWitnessAtInRepresentatives,
          ExactSeventeenRepresentativesValid
  <1>6. ExactStateObservationMap[ExactWitnessAt(i)]
          # ExactStateObservationMap[ExactWitnessAt(j)]
       BY SMTT(60), <1>4, <1>5,
          ExactObservationIsIdentityOnValidStates
  <1>7. /\ ExactWitnessAt(i) \in ExactSeventeenRepresentatives
         /\ ExactWitnessAt(j) \in ExactSeventeenRepresentatives
       BY <1>3, ExactWitnessAtInRepresentatives
  <1>8. f[ExactWitnessAt(i)] # f[ExactWitnessAt(j)]
       BY <1>6, <1>7
          DEF FaithfulOnWitnesses
  <1>9. /\ IndexedWitnessEncoding(f)[i]
            = f[ExactWitnessAt(i)]
         /\ IndexedWitnessEncoding(f)[j]
            = f[ExactWitnessAt(j)]
       BY <1>3
          DEF IndexedWitnessEncoding
  <1> QED
       BY <1>3, <1>8, <1>9

THEOREM RichProfileInformationLowerBounds ==
  /\ ~\E f :
       FaithfulOnWitnesses(
         f,
         ParameterizedSevenRepresentatives,
         ParameterizedCapabilityStateObservationMap,
         FourCodes)
  /\ ~\E f :
       FaithfulOnWitnesses(
         f,
         ExactSeventeenRepresentatives,
         ExactStateObservationMap,
         SixteenCodeSlots)
PROOF
  BY NoFaithfulFourCodeParameterizedEncoding,
     NoFaithfulSixteenCodeExactEncoding

=============================================================================
