------------------------- MODULE SeedResolutionProofs -------------------------
EXTENDS SeedResolution, TLAPS

(*
Unbounded safety proof for the normalized Seed state.

The proof separates Seed-owned state from environment conflict state. Authority
recognition is an exact-binding boundary predicate; concrete evidence and grant
chains remain external. Invalid and non-authoritative material are outside the
accepted transition system rather than modeled as artificial stutter actions.
*)

THEOREM EffectPermissionDefinition ==
  \A r \in ResolutionIds :
    EffectPermitted(r) <=> ResolutionOf(r) = "ALLOW"
PROOF
  BY DEF EffectPermitted

THEOREM UnregisteredResolutionIsUnknown ==
  \A r \in ResolutionIds :
    r \notin Requests => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf

THEOREM ConflictedResolutionIsUnknown ==
  \A r \in ResolutionIds :
    r \in conflicts => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf

THEOREM MissingTerminalRecordIsUnknown ==
  \A r \in ResolutionIds :
    r \notin TerminalRequests => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf

THEOREM TerminalRecordDeterminesResolution ==
  \A r \in ResolutionIds :
    (/\ r \in Requests
     /\ r \notin conflicts
     /\ r \in TerminalRequests)
    => ResolutionOf(r) = TerminalResolution(r)
PROOF
  BY DEF ResolutionOf

THEOREM AllowResolutionCharacterization ==
  \A r \in ResolutionIds :
    EffectPermitted(r) <=>
      /\ r \in Requests
      /\ r \notin conflicts
      /\ r \in TerminalRequests
      /\ TerminalResolution(r) = "ALLOW"
PROOF
  BY DEF EffectPermitted, ResolutionOf

THEOREM BlockResolutionCharacterization ==
  \A r \in ResolutionIds :
    ResolutionOf(r) = "BLOCK" <=>
      /\ r \in Requests
      /\ r \notin conflicts
      /\ r \in TerminalRequests
      /\ TerminalResolution(r) = "BLOCK"
PROOF
  BY DEF ResolutionOf

THEOREM FailClosedByEvaluator ==
  FailClosed
PROOF
  BY DEF FailClosed, EffectPermitted

THEOREM ConflictSoundFromTypeOK ==
  TypeOK => ConflictSound
PROOF
  BY ConflictedResolutionIsUnknown
     DEF TypeOK, ConflictSound

THEOREM ResolutionDomainPointwise ==
  ASSUME TypeOK,
         NEW r \in ResolutionIds
  PROVE ResolutionOf(r) \in Resolutions
PROOF
  <1>1. CASE r \notin Requests \/ r \in conflicts
    <2>1. QED
      BY <1>1 DEF ResolutionOf, Resolutions
  <1>2. CASE
          /\ ~(r \notin Requests \/ r \in conflicts)
          /\ r \notin TerminalRequests
    <2>1. QED
      BY <1>2 DEF ResolutionOf, Resolutions
  <1>3. CASE
          /\ ~(r \notin Requests \/ r \in conflicts)
          /\ r \in TerminalRequests
    <2>1. terminalMeta[r] \in TerminalMetaType
      BY <1>3 DEF TypeOK, TerminalRequests
    <2>2. TerminalResolution(r) \in TerminalResolutions
      BY <2>1 DEF TerminalMetaType, TerminalResolution
    <2>3. QED
      BY <1>3, <2>2
         DEF ResolutionOf, Resolutions, TerminalResolutions
  <1>4. QED
    BY <1>1, <1>2, <1>3

THEOREM ResolutionDomainFromTypeOK ==
  TypeOK => ResolutionDomain
PROOF
  BY ResolutionDomainPointwise
     DEF ResolutionDomain

THEOREM AcceptedTerminalUniqueFromTypeOK ==
  TypeOK => AcceptedTerminalUnique
PROOF
  BY DEF TypeOK, AcceptedTerminalUnique

THEOREM AllowSoundnessPointwise ==
  ASSUME TerminalBindingDerived,
         TerminalAuthorityRecognized,
         NEW r \in ResolutionIds,
         EffectPermitted(r)
  PROVE
    /\ r \in Requests
    /\ r \notin conflicts
    /\ r \in TerminalRequests
    /\ TerminalResolution(r) = "ALLOW"
    /\ <<TerminalAuthority(r), RequestBinding(r)>>
         \in RecognizedAuthorityBindings
PROOF
  <1>1.
    /\ r \in Requests
    /\ r \notin conflicts
    /\ r \in TerminalRequests
    /\ TerminalResolution(r) = "ALLOW"
    BY AllowResolutionCharacterization
  <1>2.
    <<TerminalAuthority(r), RequestBinding(r)>>
      \in RecognizedAuthorityBindings
    BY <1>1 DEF TerminalAuthorityRecognized
  <1>3. QED
    BY <1>1, <1>2

THEOREM AllowSoundnessFromStructuralInvariants ==
  TerminalBindingDerived /\ TerminalAuthorityRecognized
    => AllowSoundness
PROOF
  BY AllowSoundnessPointwise
     DEF AllowSoundness

THEOREM InductiveInvariantImpliesSeedStateSafety ==
  InductiveInvariant => SeedStateSafety
PROOF
  BY ResolutionDomainFromTypeOK,
     AllowSoundnessFromStructuralInvariants,
     FailClosedByEvaluator,
     AcceptedTerminalUniqueFromTypeOK,
     ConflictSoundFromTypeOK
     DEF InductiveInvariant, SeedStateSafety

THEOREM InitImpliesTypeOK ==
  Init => TypeOK
PROOF
  BY DEF Init,
         TypeOK,
         RequestMetaType,
         TerminalMetaType

THEOREM InitImpliesTerminalBindingDerived ==
  Init => TerminalBindingDerived
PROOF
  BY DEF Init,
         TerminalBindingDerived,
         Requests,
         TerminalRequests

THEOREM InitImpliesRequestAuthorityRecognized ==
  Init => RequestAuthorityRecognized
PROOF
  BY DEF Init,
         RequestAuthorityRecognized,
         Requests

THEOREM InitImpliesTerminalAuthorityRecognized ==
  Init => TerminalAuthorityRecognized
PROOF
  BY DEF Init,
         TerminalAuthorityRecognized,
         TerminalRequests

THEOREM InitImpliesFreshReconsideration ==
  Init => FreshReconsideration
PROOF
  BY DEF Init,
         FreshReconsideration,
         Requests

THEOREM InitImpliesTerminalRecordRequiresRequest ==
  Init => TerminalRecordRequiresRequest
PROOF
  BY DEF Init,
         TerminalRecordRequiresRequest,
         Requests,
         TerminalRequests

THEOREM InitImpliesInductiveInvariant ==
  Init => InductiveInvariant
PROOF
  BY InitImpliesTypeOK,
     InitImpliesTerminalBindingDerived,
     InitImpliesRequestAuthorityRecognized,
     InitImpliesTerminalAuthorityRecognized,
     InitImpliesFreshReconsideration,
     InitImpliesTerminalRecordRequiresRequest
     DEF InductiveInvariant

THEOREM RegisterRequestPreservesTypeOK ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => TypeOK'
PROOF
  BY DEF InductiveInvariant,
         TypeOK,
         RegisterRequest,
         Requests,
         TerminalRequests,
         RequestMetaType,
         TerminalMetaType

THEOREM RegisterRequestPreservesTerminalRecordRequiresRequest ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => TerminalRecordRequiresRequest'
PROOF
  BY DEF InductiveInvariant,
         TerminalRecordRequiresRequest,
         TerminalBindingDerived,
         RegisterRequest,
         Requests,
         TerminalRequests

THEOREM RegisterRequestPreservesTerminalBindingDerived ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => TerminalBindingDerived'
PROOF
  BY DEF InductiveInvariant,
         TerminalBindingDerived,
         TerminalRecordRequiresRequest,
         RegisterRequest,
         Requests,
         TerminalRequests,
         TerminalBinding,
         RequestBinding

THEOREM RegisterRequestPreservesRequestAuthorityRecognized ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => RequestAuthorityRecognized'
PROOF
  BY DEF InductiveInvariant,
         RequestAuthorityRecognized,
         RegisterRequest,
         Requests,
         RequestBinding

THEOREM RegisterRequestPreservesTerminalAuthorityRecognized ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => TerminalAuthorityRecognized'
PROOF
  BY DEF InductiveInvariant,
         TerminalAuthorityRecognized,
         TerminalRecordRequiresRequest,
         RegisterRequest,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalAuthority

THEOREM RegisterRequestPreservesFreshReconsideration ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => FreshReconsideration'
PROOF
  BY DEF InductiveInvariant,
         FreshReconsideration,
         RegisterRequest,
         Requests,
         PreviousCommitment

THEOREM RegisterRequestPreservesInductiveInvariant ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => InductiveInvariant'
PROOF
  BY RegisterRequestPreservesTypeOK,
     RegisterRequestPreservesTerminalRecordRequiresRequest,
     RegisterRequestPreservesTerminalBindingDerived,
     RegisterRequestPreservesRequestAuthorityRecognized,
     RegisterRequestPreservesTerminalAuthorityRecognized,
     RegisterRequestPreservesFreshReconsideration
     DEF InductiveInvariant

THEOREM SubmitResolutionPreservesTypeOK ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => TypeOK'
PROOF
  BY DEF InductiveInvariant,
         TypeOK,
         SubmitResolution,
         Requests,
         TerminalRequests,
         RequestMetaType,
         TerminalMetaType

THEOREM SubmitResolutionPreservesTerminalRecordRequiresRequest ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => TerminalRecordRequiresRequest'
PROOF
  BY DEF InductiveInvariant,
         TerminalRecordRequiresRequest,
         SubmitResolution,
         Requests,
         TerminalRequests

THEOREM SubmitResolutionPreservesTerminalBindingDerived ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => TerminalBindingDerived'
PROOF
  BY DEF InductiveInvariant,
         TerminalBindingDerived,
         TerminalRecordRequiresRequest,
         SubmitResolution,
         Requests,
         TerminalRequests,
         TerminalBinding,
         RequestBinding

THEOREM SubmitResolutionPreservesRequestAuthorityRecognized ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => RequestAuthorityRecognized'
PROOF
  BY DEF InductiveInvariant,
         RequestAuthorityRecognized,
         SubmitResolution,
         Requests,
         RequestBinding

THEOREM SubmitResolutionPreservesTerminalAuthorityRecognized ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => TerminalAuthorityRecognized'
PROOF
  BY DEF InductiveInvariant,
         TerminalAuthorityRecognized,
         TerminalRecordRequiresRequest,
         SubmitResolution,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalAuthority

THEOREM SubmitResolutionPreservesFreshReconsideration ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => FreshReconsideration'
PROOF
  BY DEF InductiveInvariant,
         FreshReconsideration,
         SubmitResolution,
         Requests,
         PreviousCommitment

THEOREM SubmitResolutionPreservesInductiveInvariant ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => InductiveInvariant'
PROOF
  BY SubmitResolutionPreservesTypeOK,
     SubmitResolutionPreservesTerminalRecordRequiresRequest,
     SubmitResolutionPreservesTerminalBindingDerived,
     SubmitResolutionPreservesRequestAuthorityRecognized,
     SubmitResolutionPreservesTerminalAuthorityRecognized,
     SubmitResolutionPreservesFreshReconsideration
     DEF InductiveInvariant

THEOREM StateStutterPreservesInductiveInvariant ==
  InductiveInvariant /\ UNCHANGED vars
    => InductiveInvariant'
PROOF
  BY DEF vars,
         seedVars,
         environmentVars,
         InductiveInvariant,
         TypeOK,
         TerminalBindingDerived,
         RequestAuthorityRecognized,
         TerminalAuthorityRecognized,
         FreshReconsideration,
         TerminalRecordRequiresRequest,
         Requests,
         TerminalRequests,
         RequestBinding,
         PreviousCommitment,
         TerminalBinding,
         TerminalAuthority

THEOREM ObserveConflictPreservesTypeOK ==
  \A r \in ResolutionIds :
    TypeOK /\ ObserveConflict(r) => TypeOK'
PROOF
  BY DEF TypeOK, ObserveConflict, seedVars, TerminalRequests

THEOREM ObserveConflictPreservesTerminalBindingDerived ==
  \A r \in ResolutionIds :
    TerminalBindingDerived /\ ObserveConflict(r)
      => TerminalBindingDerived'
PROOF
  BY DEF TerminalBindingDerived,
         ObserveConflict,
         seedVars,
         Requests,
         TerminalRequests,
         TerminalBinding,
         RequestBinding

THEOREM ObserveConflictPreservesRequestAuthorityRecognized ==
  \A r \in ResolutionIds :
    RequestAuthorityRecognized /\ ObserveConflict(r) => RequestAuthorityRecognized'
PROOF
  BY DEF RequestAuthorityRecognized,
         ObserveConflict,
         seedVars,
         Requests,
         RequestBinding

THEOREM ObserveConflictPreservesTerminalAuthorityRecognized ==
  \A r \in ResolutionIds :
    TerminalAuthorityRecognized /\ ObserveConflict(r)
      => TerminalAuthorityRecognized'
PROOF
  BY DEF TerminalAuthorityRecognized,
         ObserveConflict,
         seedVars,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalAuthority

THEOREM ObserveConflictPreservesFreshReconsideration ==
  \A r \in ResolutionIds :
    FreshReconsideration /\ ObserveConflict(r)
      => FreshReconsideration'
PROOF
  BY DEF FreshReconsideration,
         ObserveConflict,
         seedVars,
         Requests,
         PreviousCommitment

THEOREM ObserveConflictPreservesTerminalRecordRequiresRequest ==
  \A r \in ResolutionIds :
    TerminalRecordRequiresRequest /\ ObserveConflict(r)
      => TerminalRecordRequiresRequest'
PROOF
  BY DEF TerminalRecordRequiresRequest,
         ObserveConflict,
         seedVars,
         Requests,
         TerminalRequests

THEOREM ObserveConflictPreservesInductiveInvariant ==
  \A r \in ResolutionIds :
    InductiveInvariant /\ ObserveConflict(r)
      => InductiveInvariant'
PROOF
  BY ObserveConflictPreservesTypeOK,
     ObserveConflictPreservesTerminalBindingDerived,
     ObserveConflictPreservesRequestAuthorityRecognized,
     ObserveConflictPreservesTerminalAuthorityRecognized,
     ObserveConflictPreservesFreshReconsideration,
     ObserveConflictPreservesTerminalRecordRequiresRequest
     DEF InductiveInvariant

THEOREM RecognizedSeedTransitionPreservesInductiveInvariant ==
  InductiveInvariant /\ RecognizedSeedTransition
    => InductiveInvariant'
PROOF
  BY RegisterRequestPreservesInductiveInvariant,
     SubmitResolutionPreservesInductiveInvariant
     DEF RecognizedSeedTransition

THEOREM RecognizedEnvironmentTransitionPreservesInductiveInvariant ==
  InductiveInvariant /\ RecognizedEnvironmentTransition
    => InductiveInvariant'
PROOF
  BY ObserveConflictPreservesInductiveInvariant
     DEF RecognizedEnvironmentTransition

THEOREM NextPreservesInductiveInvariant ==
  InductiveInvariant /\ Next
    => InductiveInvariant'
PROOF
  BY RecognizedSeedTransitionPreservesInductiveInvariant,
     RecognizedEnvironmentTransitionPreservesInductiveInvariant
     DEF Next

THEOREM BoxNextPreservesInductiveInvariant ==
  InductiveInvariant /\ [Next]_vars
    => InductiveInvariant'
PROOF
  BY NextPreservesInductiveInvariant,
     StateStutterPreservesInductiveInvariant
     DEF vars

THEOREM SpecImpliesAlwaysInductiveInvariant ==
  Spec => []InductiveInvariant
PROOF
  BY PTL,
     InitImpliesInductiveInvariant,
     BoxNextPreservesInductiveInvariant
     DEF Spec

THEOREM AlwaysInductiveInvariantImpliesAlwaysSeedStateSafety ==
  []InductiveInvariant => []SeedStateSafety
PROOF
  BY PTL,
     InductiveInvariantImpliesSeedStateSafety

THEOREM SpecImpliesAlwaysSeedStateSafety ==
  Spec => []SeedStateSafety
PROOF
  BY SpecImpliesAlwaysInductiveInvariant,
     AlwaysInductiveInvariantImpliesAlwaysSeedStateSafety

THEOREM RegisterRequestSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous) => RequestsAppendOnlyStep
PROOF
  BY DEF RegisterRequest, RequestsAppendOnlyStep, Requests


THEOREM SubmitResolutionSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => RequestsAppendOnlyStep
PROOF
  BY DEF SubmitResolution, RequestsAppendOnlyStep, Requests


THEOREM ObserveConflictSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => RequestsAppendOnlyStep
PROOF
  BY DEF ObserveConflict, RequestsAppendOnlyStep, Requests, seedVars


THEOREM NextSatisfiesRequestsAppendOnlyStep ==
  Next => RequestsAppendOnlyStep
PROOF
  BY RegisterRequestSatisfiesRequestsAppendOnlyStep,
     SubmitResolutionSatisfiesRequestsAppendOnlyStep,
     ObserveConflictSatisfiesRequestsAppendOnlyStep
     DEF Next, RecognizedSeedTransition, RecognizedEnvironmentTransition


THEOREM BoxNextSatisfiesBoxRequestsAppendOnlyStep ==
  [Next]_vars => [RequestsAppendOnlyStep]_vars
PROOF
  BY NextSatisfiesRequestsAppendOnlyStep
     DEF vars, RequestsAppendOnlyStep


THEOREM SpecImpliesRequestsAppendOnly ==
  Spec => RequestsAppendOnly
PROOF
  BY PTL,
     BoxNextSatisfiesBoxRequestsAppendOnlyStep
     DEF Spec, RequestsAppendOnly


THEOREM RegisterRequestSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous) => TerminalRecordsImmutableStep
PROOF
  BY DEF RegisterRequest, TerminalRecordsImmutableStep, TerminalRequests


THEOREM SubmitResolutionSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => TerminalRecordsImmutableStep
PROOF
  BY DEF SubmitResolution, TerminalRecordsImmutableStep, TerminalRequests


THEOREM ObserveConflictSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => TerminalRecordsImmutableStep
PROOF
  BY DEF ObserveConflict, TerminalRecordsImmutableStep, TerminalRequests, seedVars


THEOREM NextSatisfiesTerminalRecordsImmutableStep ==
  Next => TerminalRecordsImmutableStep
PROOF
  BY RegisterRequestSatisfiesTerminalRecordsImmutableStep,
     SubmitResolutionSatisfiesTerminalRecordsImmutableStep,
     ObserveConflictSatisfiesTerminalRecordsImmutableStep
     DEF Next, RecognizedSeedTransition, RecognizedEnvironmentTransition


THEOREM BoxNextSatisfiesBoxTerminalRecordsImmutableStep ==
  [Next]_vars => [TerminalRecordsImmutableStep]_vars
PROOF
  BY NextSatisfiesTerminalRecordsImmutableStep
     DEF vars, TerminalRecordsImmutableStep


THEOREM SpecImpliesTerminalRecordsImmutable ==
  Spec => TerminalRecordsImmutable
PROOF
  BY PTL,
     BoxNextSatisfiesBoxTerminalRecordsImmutableStep
     DEF Spec, TerminalRecordsImmutable


THEOREM RecognizedSeedTransitionSatisfiesSeedStateTransitionStep ==
  RecognizedSeedTransition => SeedStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF SeedStateChangesOnlyByRecognizedTransitionStep


THEOREM ObserveConflictSatisfiesSeedStateTransitionStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => SeedStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF ObserveConflict, seedVars, SeedStateChangesOnlyByRecognizedTransitionStep


THEOREM NextSatisfiesSeedStateTransitionStep ==
  Next => SeedStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY RecognizedSeedTransitionSatisfiesSeedStateTransitionStep,
     ObserveConflictSatisfiesSeedStateTransitionStep
     DEF Next, RecognizedEnvironmentTransition


THEOREM BoxNextSatisfiesBoxSeedStateTransitionStep ==
  [Next]_vars => [SeedStateChangesOnlyByRecognizedTransitionStep]_vars
PROOF
  BY NextSatisfiesSeedStateTransitionStep
     DEF vars, SeedStateChangesOnlyByRecognizedTransitionStep


THEOREM SpecImpliesSeedStateChangesOnlyByRecognizedTransition ==
  Spec => SeedStateChangesOnlyByRecognizedTransition
PROOF
  BY PTL,
     BoxNextSatisfiesBoxSeedStateTransitionStep
     DEF Spec, SeedStateChangesOnlyByRecognizedTransition


THEOREM ObserveConflictPreservesSeedState ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED seedVars
PROOF
  BY DEF ObserveConflict


THEOREM NextSatisfiesConflictObservationPreservesSeedStateStep ==
  Next => ConflictObservationPreservesSeedStateStep
PROOF
  BY ObserveConflictPreservesSeedState
     DEF ConflictObservationPreservesSeedStateStep


THEOREM BoxNextSatisfiesBoxConflictObservationPreservesSeedStateStep ==
  [Next]_vars => [ConflictObservationPreservesSeedStateStep]_vars
PROOF
  BY NextSatisfiesConflictObservationPreservesSeedStateStep
     DEF vars, ConflictObservationPreservesSeedStateStep


THEOREM SpecImpliesConflictObservationPreservesSeedState ==
  Spec => ConflictObservationPreservesSeedState
PROOF
  BY PTL,
     BoxNextSatisfiesBoxConflictObservationPreservesSeedStateStep
     DEF Spec, ConflictObservationPreservesSeedState

=============================================================================
