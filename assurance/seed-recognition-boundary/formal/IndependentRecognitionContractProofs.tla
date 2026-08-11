---------------- MODULE IndependentRecognitionContractProofs ----------------
EXTENDS IndependentRecognitionContract, TLAPS

THEOREM NativeOpenUsesCurrentGenesisPrefix ==
  \A c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes :
    NativeSubjectOf(c, nativeLineage, d, policy, scope)
      = Subject!BindingOf(c, Genesis, nativeLineage, d, policy, scope)
PROOF
  BY DEF NativeSubjectOf

THEOREM NativeOpenPreservesFrozenLineage ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => NativeLineageFrozenAdditiveStep
PROOF
  BY DEF NativeOpen, nativeLineageVars, NativeLineageFrozenAdditiveStep

THEOREM NativeDecidePreservesFrozenLineage ==
  \A r \in DecisionIds, subject \in NativeSubjects,
     a \in NativeAuthorities, outcome \in NativeTerminalOutcomes :
    NativeDecide(r, subject, a, outcome)
      => NativeLineageFrozenAdditiveStep
PROOF
  BY DEF NativeDecide, nativeLineageVars, NativeLineageFrozenAdditiveStep

THEOREM NativeConflictPreservesFrozenLineage ==
  \A r \in DecisionIds :
    NativeObserveConflict(r) => NativeLineageFrozenAdditiveStep
PROOF
  BY DEF NativeObserveConflict, nativeLineageVars,
         NativeLineageFrozenAdditiveStep

THEOREM NativeCrossAppendsFrozenLineage ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => NativeLineageFrozenAdditiveStep
PROOF
  BY DEF NativeCross, NativeLineageFrozenAdditiveStep,
         NativeLineageEntryType

THEOREM NativeCrossRequiresAdmit ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => NativeEffectAdmitted(r)
PROOF
  BY DEF NativeCross

THEOREM NativeCrossIsSingleCrossing ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => /\ r \notin nativeCrossed
                         /\ r \in nativeCrossed'
PROOF
  BY DEF NativeCross

THEOREM NativeCrossMakesCrossedMonotone ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => NativeCrossedMonotoneStep
PROOF
  BY DEF NativeCross, NativeCrossedMonotoneStep

THEOREM NativeSeedLikePreservesCrossed ==
  NativeSeedLikeTransition => NativeCrossedMonotoneStep
PROOF
  BY SMTT(60)
     DEF NativeSeedLikeTransition,
         NativeOpen,
         NativeDecide,
         nativeLineageVars,
         NativeCrossedMonotoneStep

THEOREM NativeEnvironmentPreservesCrossed ==
  NativeEnvironmentTransition => NativeCrossedMonotoneStep
PROOF
  BY SMTT(60)
     DEF NativeEnvironmentTransition,
         NativeObserveConflict,
         nativeLineageVars,
         NativeCrossedMonotoneStep

THEOREM NativeNextPreservesFrozenLineage ==
  NativeNext => NativeLineageFrozenAdditiveStep
PROOF
  BY NativeOpenPreservesFrozenLineage,
     NativeDecidePreservesFrozenLineage,
     NativeConflictPreservesFrozenLineage,
     NativeCrossAppendsFrozenLineage
     DEF NativeNext,
         NativeSeedLikeTransition,
         NativeEnvironmentTransition,
         NativeApplicationTransition

THEOREM NativeNextCrossedMonotone ==
  NativeNext => NativeCrossedMonotoneStep
PROOF
  BY NativeSeedLikePreservesCrossed,
     NativeEnvironmentPreservesCrossed,
     NativeCrossMakesCrossedMonotone
     DEF NativeNext, NativeApplicationTransition

THEOREM NativeCrossCreatesOnlyAdmittedApplication ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => NativeNewCrossRequiresAdmitStep
PROOF
  BY DEF NativeCross, NativeNewCrossRequiresAdmitStep

=============================================================================
