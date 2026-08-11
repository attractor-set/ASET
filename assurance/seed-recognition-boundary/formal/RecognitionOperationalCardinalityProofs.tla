------------- MODULE RecognitionOperationalCardinalityProofs -------------
EXTENDS RecognitionOperationalCardinality, TLAPS

THEOREM CapabilityObservationValues ==
  /\ CapabilityObservationMap["ABSENT"] =
       [effective |-> "UNKNOWN",
        can_register |-> TRUE,
        can_submit |-> FALSE,
        can_conflict |-> FALSE]
  /\ CapabilityObservationMap["PENDING"] =
       [effective |-> "UNKNOWN",
        can_register |-> FALSE,
        can_submit |-> TRUE,
        can_conflict |-> FALSE]
  /\ CapabilityObservationMap["ALLOW"] =
       [effective |-> "ALLOW",
        can_register |-> FALSE,
        can_submit |-> FALSE,
        can_conflict |-> TRUE]
  /\ CapabilityObservationMap["BLOCK"] =
       [effective |-> "BLOCK",
        can_register |-> FALSE,
        can_submit |-> FALSE,
        can_conflict |-> TRUE]
  /\ CapabilityObservationMap["INVALIDATED_ALLOW"] =
       [effective |-> "UNKNOWN",
        can_register |-> FALSE,
        can_submit |-> FALSE,
        can_conflict |-> FALSE]
  /\ CapabilityObservationMap["INVALIDATED_BLOCK"] =
       [effective |-> "UNKNOWN",
        can_register |-> FALSE,
        can_submit |-> FALSE,
        can_conflict |-> FALSE]
PROOF
  BY SMTT(120)
     DEF CapabilityObservationMap,
         CapabilityObservables,
         EffectiveValue,
         CanRegister,
         CanSubmit,
         CanConflict,
         OperationalPhases

THEOREM HistoryCapabilityProjection ==
  \A s \in OperationalPhases :
    HistoryObservationMap[s].capability = CapabilityObservationMap[s]
PROOF
  BY SMTT(60)
     DEF HistoryObservationMap,
         HistoryObservables,
         CapabilityObservationMap,
         OperationalPhases

THEOREM HistoryRetainedTerminalProjection ==
  \A s \in OperationalPhases :
    HistoryObservationMap[s].retained_terminal = RetainedTerminal(s)
PROOF
  BY SMTT(60)
     DEF HistoryObservationMap,
         HistoryObservables,
         OperationalPhases

THEOREM CapabilityInvalidatedVariantsEquivalent ==
  CapabilityObservationMap["INVALIDATED_ALLOW"]
    = CapabilityObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAbsentDiffersFromPending ==
  CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["PENDING"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAbsentDiffersFromAllow ==
  CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAbsentDiffersFromBlock ==
  CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["BLOCK"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAbsentDiffersFromInvalidated ==
  CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityPendingDiffersFromAllow ==
  CapabilityObservationMap["PENDING"] # CapabilityObservationMap["ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityPendingDiffersFromBlock ==
  CapabilityObservationMap["PENDING"] # CapabilityObservationMap["BLOCK"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityPendingDiffersFromInvalidated ==
  CapabilityObservationMap["PENDING"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAllowDiffersFromBlock ==
  CapabilityObservationMap["ALLOW"] # CapabilityObservationMap["BLOCK"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAllowDiffersFromInvalidated ==
  CapabilityObservationMap["ALLOW"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityBlockDiffersFromInvalidated ==
  CapabilityObservationMap["BLOCK"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60), CapabilityObservationValues

THEOREM CapabilityAbsentDiffersFromInvalidatedBlock ==
  CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityAbsentDiffersFromInvalidated,
     CapabilityInvalidatedVariantsEquivalent

THEOREM CapabilityPendingDiffersFromInvalidatedBlock ==
  CapabilityObservationMap["PENDING"] # CapabilityObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityPendingDiffersFromInvalidated,
     CapabilityInvalidatedVariantsEquivalent

THEOREM CapabilityAllowDiffersFromInvalidatedBlock ==
  CapabilityObservationMap["ALLOW"] # CapabilityObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityAllowDiffersFromInvalidated,
     CapabilityInvalidatedVariantsEquivalent

THEOREM CapabilityBlockDiffersFromInvalidatedBlock ==
  CapabilityObservationMap["BLOCK"] # CapabilityObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityBlockDiffersFromInvalidated,
     CapabilityInvalidatedVariantsEquivalent

THEOREM CapabilityRepresentativesPairwiseDistinct ==
  /\ CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["PENDING"]
  /\ CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["ALLOW"]
  /\ CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["BLOCK"]
  /\ CapabilityObservationMap["ABSENT"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
  /\ CapabilityObservationMap["PENDING"] # CapabilityObservationMap["ALLOW"]
  /\ CapabilityObservationMap["PENDING"] # CapabilityObservationMap["BLOCK"]
  /\ CapabilityObservationMap["PENDING"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
  /\ CapabilityObservationMap["ALLOW"] # CapabilityObservationMap["BLOCK"]
  /\ CapabilityObservationMap["ALLOW"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
  /\ CapabilityObservationMap["BLOCK"] # CapabilityObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY CapabilityAbsentDiffersFromPending,
     CapabilityAbsentDiffersFromAllow,
     CapabilityAbsentDiffersFromBlock,
     CapabilityAbsentDiffersFromInvalidated,
     CapabilityPendingDiffersFromAllow,
     CapabilityPendingDiffersFromBlock,
     CapabilityPendingDiffersFromInvalidated,
     CapabilityAllowDiffersFromBlock,
     CapabilityAllowDiffersFromInvalidated,
     CapabilityBlockDiffersFromInvalidated

THEOREM HistoryEqualityImpliesCapabilityEquality ==
  \A x \in OperationalPhases, y \in OperationalPhases :
    HistoryObservationMap[x] = HistoryObservationMap[y]
      => CapabilityObservationMap[x] = CapabilityObservationMap[y]
PROOF
  BY SMTT(60), HistoryCapabilityProjection

THEOREM CapabilityDifferenceLiftsToHistoryDifference ==
  \A x \in OperationalPhases, y \in OperationalPhases :
    CapabilityObservationMap[x] # CapabilityObservationMap[y]
      => HistoryObservationMap[x] # HistoryObservationMap[y]
PROOF
  BY SMTT(60), HistoryEqualityImpliesCapabilityEquality

THEOREM HistoryEqualityImpliesRetainedTerminalEquality ==
  \A x \in OperationalPhases, y \in OperationalPhases :
    HistoryObservationMap[x] = HistoryObservationMap[y]
      => RetainedTerminal(x) = RetainedTerminal(y)
PROOF
  BY SMTT(60), HistoryRetainedTerminalProjection

THEOREM InvalidatedRetainedTerminalsDiffer ==
  RetainedTerminal("INVALIDATED_ALLOW")
    # RetainedTerminal("INVALIDATED_BLOCK")
PROOF
  BY DEF RetainedTerminal

THEOREM HistoryInvalidatedVariantsDistinct ==
  HistoryObservationMap["INVALIDATED_ALLOW"]
    # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     HistoryEqualityImpliesRetainedTerminalEquality,
     InvalidatedRetainedTerminalsDiffer
     DEF OperationalPhases

THEOREM HistoryAbsentDiffersFromPending ==
  HistoryObservationMap["ABSENT"] # HistoryObservationMap["PENDING"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAbsentDiffersFromPending
     DEF OperationalPhases

THEOREM HistoryAbsentDiffersFromAllow ==
  HistoryObservationMap["ABSENT"] # HistoryObservationMap["ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAbsentDiffersFromAllow
     DEF OperationalPhases

THEOREM HistoryAbsentDiffersFromBlock ==
  HistoryObservationMap["ABSENT"] # HistoryObservationMap["BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAbsentDiffersFromBlock
     DEF OperationalPhases

THEOREM HistoryAbsentDiffersFromInvalidatedAllow ==
  HistoryObservationMap["ABSENT"]
    # HistoryObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAbsentDiffersFromInvalidated
     DEF OperationalPhases

THEOREM HistoryAbsentDiffersFromInvalidatedBlock ==
  HistoryObservationMap["ABSENT"]
    # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAbsentDiffersFromInvalidatedBlock
     DEF OperationalPhases

THEOREM HistoryPendingDiffersFromAllow ==
  HistoryObservationMap["PENDING"] # HistoryObservationMap["ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityPendingDiffersFromAllow
     DEF OperationalPhases

THEOREM HistoryPendingDiffersFromBlock ==
  HistoryObservationMap["PENDING"] # HistoryObservationMap["BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityPendingDiffersFromBlock
     DEF OperationalPhases

THEOREM HistoryPendingDiffersFromInvalidatedAllow ==
  HistoryObservationMap["PENDING"]
    # HistoryObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityPendingDiffersFromInvalidated
     DEF OperationalPhases

THEOREM HistoryPendingDiffersFromInvalidatedBlock ==
  HistoryObservationMap["PENDING"]
    # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityPendingDiffersFromInvalidatedBlock
     DEF OperationalPhases

THEOREM HistoryAllowDiffersFromBlock ==
  HistoryObservationMap["ALLOW"] # HistoryObservationMap["BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAllowDiffersFromBlock
     DEF OperationalPhases

THEOREM HistoryAllowDiffersFromInvalidatedAllow ==
  HistoryObservationMap["ALLOW"]
    # HistoryObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAllowDiffersFromInvalidated
     DEF OperationalPhases

THEOREM HistoryAllowDiffersFromInvalidatedBlock ==
  HistoryObservationMap["ALLOW"]
    # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityAllowDiffersFromInvalidatedBlock
     DEF OperationalPhases

THEOREM HistoryBlockDiffersFromInvalidatedAllow ==
  HistoryObservationMap["BLOCK"]
    # HistoryObservationMap["INVALIDATED_ALLOW"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityBlockDiffersFromInvalidated
     DEF OperationalPhases

THEOREM HistoryBlockDiffersFromInvalidatedBlock ==
  HistoryObservationMap["BLOCK"]
    # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY SMTT(60),
     CapabilityDifferenceLiftsToHistoryDifference,
     CapabilityBlockDiffersFromInvalidatedBlock
     DEF OperationalPhases

THEOREM HistoryAllSixPairwiseDistinct ==
  /\ HistoryObservationMap["ABSENT"] # HistoryObservationMap["PENDING"]
  /\ HistoryObservationMap["ABSENT"] # HistoryObservationMap["ALLOW"]
  /\ HistoryObservationMap["ABSENT"] # HistoryObservationMap["BLOCK"]
  /\ HistoryObservationMap["ABSENT"] # HistoryObservationMap["INVALIDATED_ALLOW"]
  /\ HistoryObservationMap["ABSENT"] # HistoryObservationMap["INVALIDATED_BLOCK"]
  /\ HistoryObservationMap["PENDING"] # HistoryObservationMap["ALLOW"]
  /\ HistoryObservationMap["PENDING"] # HistoryObservationMap["BLOCK"]
  /\ HistoryObservationMap["PENDING"] # HistoryObservationMap["INVALIDATED_ALLOW"]
  /\ HistoryObservationMap["PENDING"] # HistoryObservationMap["INVALIDATED_BLOCK"]
  /\ HistoryObservationMap["ALLOW"] # HistoryObservationMap["BLOCK"]
  /\ HistoryObservationMap["ALLOW"] # HistoryObservationMap["INVALIDATED_ALLOW"]
  /\ HistoryObservationMap["ALLOW"] # HistoryObservationMap["INVALIDATED_BLOCK"]
  /\ HistoryObservationMap["BLOCK"] # HistoryObservationMap["INVALIDATED_ALLOW"]
  /\ HistoryObservationMap["BLOCK"] # HistoryObservationMap["INVALIDATED_BLOCK"]
  /\ HistoryObservationMap["INVALIDATED_ALLOW"]
       # HistoryObservationMap["INVALIDATED_BLOCK"]
PROOF
  BY HistoryAbsentDiffersFromPending,
     HistoryAbsentDiffersFromAllow,
     HistoryAbsentDiffersFromBlock,
     HistoryAbsentDiffersFromInvalidatedAllow,
     HistoryAbsentDiffersFromInvalidatedBlock,
     HistoryPendingDiffersFromAllow,
     HistoryPendingDiffersFromBlock,
     HistoryPendingDiffersFromInvalidatedAllow,
     HistoryPendingDiffersFromInvalidatedBlock,
     HistoryAllowDiffersFromBlock,
     HistoryAllowDiffersFromInvalidatedAllow,
     HistoryAllowDiffersFromInvalidatedBlock,
     HistoryBlockDiffersFromInvalidatedAllow,
     HistoryBlockDiffersFromInvalidatedBlock,
     HistoryInvalidatedVariantsDistinct

THEOREM NoFaithfulFourValueCapabilityEncoding ==
  ~\E f :
    FaithfulOn(
      f,
      CapabilityRepresentatives,
      CapabilityObservationMap,
      FourValues)
PROOF
  BY SMTT(180),
     CapabilityRepresentativesPairwiseDistinct
     DEF FaithfulOn,
         CapabilityRepresentatives,
         CapabilityObservationMap,
         FourValues

THEOREM CanonicalFiveEncodingValues ==
  /\ CanonicalFiveEncoding["ABSENT"] = "0"
  /\ CanonicalFiveEncoding["PENDING"] = "1"
  /\ CanonicalFiveEncoding["ALLOW"] = "2"
  /\ CanonicalFiveEncoding["BLOCK"] = "3"
  /\ CanonicalFiveEncoding["INVALIDATED_ALLOW"] = "4"
PROOF
  BY SMTT(120)
     DEF CanonicalFiveEncoding,
         CapabilityRepresentatives

THEOREM CanonicalFiveEncodingType ==
  CanonicalFiveEncoding \in [CapabilityRepresentatives -> FiveValues]
PROOF
  BY SMTT(180),
     CanonicalFiveEncodingValues
     DEF CanonicalFiveEncoding,
         CapabilityRepresentatives,
         FiveValues

THEOREM CanonicalFiveEncodingInjective ==
  \A x \in CapabilityRepresentatives, y \in CapabilityRepresentatives :
    x # y => CanonicalFiveEncoding[x] # CanonicalFiveEncoding[y]
PROOF
  BY SMTT(180),
     CanonicalFiveEncodingValues
     DEF CapabilityRepresentatives

THEOREM CanonicalFiveEncodingPreservesCapabilities ==
  FaithfulOn(
    CanonicalFiveEncoding,
    CapabilityRepresentatives,
    CapabilityObservationMap,
    FiveValues)
PROOF
  BY SMTT(120),
     CanonicalFiveEncodingType,
     CanonicalFiveEncodingInjective
     DEF FaithfulOn

THEOREM FiveOperationalCapabilityClassesAreMinimal ==
  /\ ~\E f :
       FaithfulOn(
         f,
         CapabilityRepresentatives,
         CapabilityObservationMap,
         FourValues)
  /\ \E f :
       FaithfulOn(
         f,
         CapabilityRepresentatives,
         CapabilityObservationMap,
         FiveValues)
PROOF
  <1>1. ~\E f :
          FaithfulOn(
            f,
            CapabilityRepresentatives,
            CapabilityObservationMap,
            FourValues)
    BY NoFaithfulFourValueCapabilityEncoding
  <1>2. \E f :
          FaithfulOn(
            f,
            CapabilityRepresentatives,
            CapabilityObservationMap,
            FiveValues)
    BY CanonicalFiveEncodingPreservesCapabilities
  <1> QED
    BY <1>1, <1>2

THEOREM NoFaithfulFiveValueHistoryEncoding ==
  ~\E f :
    FaithfulOn(
      f,
      OperationalPhases,
      HistoryObservationMap,
      FiveValues)
PROOF
  BY SMTT(240),
     HistoryAllSixPairwiseDistinct
     DEF FaithfulOn,
         OperationalPhases,
         HistoryObservationMap,
         FiveValues

THEOREM CanonicalSixEncodingValues ==
  /\ CanonicalSixEncoding["ABSENT"] = "0"
  /\ CanonicalSixEncoding["PENDING"] = "1"
  /\ CanonicalSixEncoding["ALLOW"] = "2"
  /\ CanonicalSixEncoding["BLOCK"] = "3"
  /\ CanonicalSixEncoding["INVALIDATED_ALLOW"] = "4"
  /\ CanonicalSixEncoding["INVALIDATED_BLOCK"] = "5"
PROOF
  BY SMTT(120)
     DEF CanonicalSixEncoding,
         OperationalPhases

THEOREM CanonicalSixEncodingPreservesHistory ==
  FaithfulOn(
    CanonicalSixEncoding,
    OperationalPhases,
    HistoryObservationMap,
    SixValues)
PROOF
  BY SMTT(240),
     HistoryAllSixPairwiseDistinct,
     CanonicalSixEncodingValues
     DEF FaithfulOn,
         OperationalPhases,
         SixValues,
         CanonicalSixEncoding

THEOREM SixRetainedHistoryClassesAreMinimal ==
  /\ ~\E f :
       FaithfulOn(
         f,
         OperationalPhases,
         HistoryObservationMap,
         FiveValues)
  /\ \E f :
       FaithfulOn(
         f,
         OperationalPhases,
         HistoryObservationMap,
         SixValues)
PROOF
  <1>1. ~\E f :
          FaithfulOn(
            f,
            OperationalPhases,
            HistoryObservationMap,
            FiveValues)
    BY NoFaithfulFiveValueHistoryEncoding
  <1>2. \E f :
          FaithfulOn(
            f,
            OperationalPhases,
            HistoryObservationMap,
            SixValues)
    BY CanonicalSixEncodingPreservesHistory
  <1> QED
    BY <1>1, <1>2

=============================================================================
