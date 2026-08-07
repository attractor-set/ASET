------------------------- MODULE SeedResolutionProofs -------------------------
EXTENDS SeedResolution, TLAPS

(*
Unbounded safety proof for the normalized Seed state.

Compared with the previous projection, request/terminal metadata are stored once,
Authority relations are immutable context constants, and invalid/non-authoritative
observations are explicit semantic stutters. The proof therefore establishes the
same observable resolution safety over a smaller representable state space.
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


THEOREM InputsNonAuthoritativeByStructure ==
  InputsNonAuthoritative
PROOF
  BY DEF InputsNonAuthoritative, canonicalVars


THEOREM ConflictUnknownFromTypeOK ==
  TypeOK => ConflictUnknown
PROOF
  BY ConflictedResolutionIsUnknown
     DEF TypeOK, ConflictUnknown


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


THEOREM TerminalUniqueFromTypeOK ==
  TypeOK => TerminalUnique
PROOF
  BY DEF TypeOK, TerminalUnique


THEOREM AllowSoundnessPointwise ==
  ASSUME TerminalBindingDerived,
         DelegatedAuthoritySound,
         NEW r \in ResolutionIds,
         EffectPermitted(r)
  PROVE
    /\ r \in Requests
    /\ r \notin conflicts
    /\ r \in TerminalRequests
    /\ TerminalResolution(r) = "ALLOW"
    /\ <<TerminalAuthority(r), RequestBinding(r)>>
         \in AuthorityProofBindings
PROOF
  <1>1.
    /\ r \in Requests
    /\ r \notin conflicts
    /\ r \in TerminalRequests
    /\ TerminalResolution(r) = "ALLOW"
    BY AllowResolutionCharacterization
  <1>2.
    <<TerminalAuthority(r), RequestBinding(r)>>
      \in AuthorityProofBindings
    BY <1>1 DEF DelegatedAuthoritySound
  <1>3. QED
    BY <1>1, <1>2


THEOREM AllowSoundnessFromStructuralInvariants ==
  TerminalBindingDerived /\ DelegatedAuthoritySound
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
     InputsNonAuthoritativeByStructure,
     TerminalUniqueFromTypeOK,
     ConflictUnknownFromTypeOK
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


THEOREM InitImpliesLocalAuthorityRoot ==
  Init => LocalAuthorityRoot
PROOF
  BY DEF Init,
         LocalAuthorityRoot,
         Requests


THEOREM InitImpliesDelegatedAuthoritySound ==
  Init => DelegatedAuthoritySound
PROOF
  BY DEF Init,
         DelegatedAuthoritySound,
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
     InitImpliesLocalAuthorityRoot,
     InitImpliesDelegatedAuthoritySound,
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


THEOREM RegisterRequestPreservesLocalAuthorityRoot ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => LocalAuthorityRoot'
PROOF
  BY DEF InductiveInvariant,
         LocalAuthorityRoot,
         RegisterRequest,
         Requests,
         RequestBinding


THEOREM RegisterRequestPreservesDelegatedAuthoritySound ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    InductiveInvariant /\ RegisterRequest(r, b, a, previous)
      => DelegatedAuthoritySound'
PROOF
  BY DEF InductiveInvariant,
         DelegatedAuthoritySound,
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
     RegisterRequestPreservesLocalAuthorityRoot,
     RegisterRequestPreservesDelegatedAuthoritySound,
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


THEOREM SubmitResolutionPreservesLocalAuthorityRoot ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => LocalAuthorityRoot'
PROOF
  BY DEF InductiveInvariant,
         LocalAuthorityRoot,
         SubmitResolution,
         Requests,
         RequestBinding


THEOREM SubmitResolutionPreservesDelegatedAuthoritySound ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    InductiveInvariant /\ SubmitResolution(r, b, a, value)
      => DelegatedAuthoritySound'
PROOF
  BY DEF InductiveInvariant,
         DelegatedAuthoritySound,
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
     SubmitResolutionPreservesLocalAuthorityRoot,
     SubmitResolutionPreservesDelegatedAuthoritySound,
     SubmitResolutionPreservesFreshReconsideration
     DEF InductiveInvariant


THEOREM StateStutterPreservesInductiveInvariant ==
  InductiveInvariant /\ UNCHANGED vars
    => InductiveInvariant'
PROOF
  BY DEF vars,
         canonicalVars,
         InductiveInvariant,
         TypeOK,
         TerminalBindingDerived,
         LocalAuthorityRoot,
         DelegatedAuthoritySound,
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
  BY DEF TypeOK, ObserveConflict


THEOREM ObserveConflictPreservesTerminalBindingDerived ==
  \A r \in ResolutionIds :
    TerminalBindingDerived /\ ObserveConflict(r)
      => TerminalBindingDerived'
PROOF
  BY DEF TerminalBindingDerived,
         ObserveConflict,
         Requests,
         TerminalRequests,
         TerminalBinding,
         RequestBinding


THEOREM ObserveConflictPreservesLocalAuthorityRoot ==
  \A r \in ResolutionIds :
    LocalAuthorityRoot /\ ObserveConflict(r) => LocalAuthorityRoot'
PROOF
  BY DEF LocalAuthorityRoot,
         ObserveConflict,
         Requests,
         RequestBinding


THEOREM ObserveConflictPreservesDelegatedAuthoritySound ==
  \A r \in ResolutionIds :
    DelegatedAuthoritySound /\ ObserveConflict(r)
      => DelegatedAuthoritySound'
PROOF
  BY DEF DelegatedAuthoritySound,
         ObserveConflict,
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
         Requests,
         PreviousCommitment


THEOREM ObserveConflictPreservesTerminalRecordRequiresRequest ==
  \A r \in ResolutionIds :
    TerminalRecordRequiresRequest /\ ObserveConflict(r)
      => TerminalRecordRequiresRequest'
PROOF
  BY DEF TerminalRecordRequiresRequest,
         ObserveConflict,
         Requests,
         TerminalRequests


THEOREM ObserveConflictPreservesInductiveInvariant ==
  \A r \in ResolutionIds :
    InductiveInvariant /\ ObserveConflict(r)
      => InductiveInvariant'
PROOF
  BY ObserveConflictPreservesTypeOK,
     ObserveConflictPreservesTerminalBindingDerived,
     ObserveConflictPreservesLocalAuthorityRoot,
     ObserveConflictPreservesDelegatedAuthoritySound,
     ObserveConflictPreservesFreshReconsideration,
     ObserveConflictPreservesTerminalRecordRequiresRequest
     DEF InductiveInvariant


THEOREM ObserveInvalidMaterialPreservesInductiveInvariant ==
  \A r \in ResolutionIds :
    InductiveInvariant /\ ObserveInvalidMaterial(r)
      => InductiveInvariant'
PROOF
  BY StateStutterPreservesInductiveInvariant
     DEF ObserveInvalidMaterial


THEOREM ObserveNonAuthoritativeInputPreservesInductiveInvariant ==
  \A r \in ResolutionIds :
    InductiveInvariant /\ ObserveNonAuthoritativeInput(r)
      => InductiveInvariant'
PROOF
  BY StateStutterPreservesInductiveInvariant
     DEF ObserveNonAuthoritativeInput


THEOREM EvaluatePreservesInductiveInvariant ==
  InductiveInvariant /\ Evaluate
    => InductiveInvariant'
PROOF
  BY StateStutterPreservesInductiveInvariant
     DEF Evaluate


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
  BY ObserveConflictPreservesInductiveInvariant,
     ObserveInvalidMaterialPreservesInductiveInvariant,
     ObserveNonAuthoritativeInputPreservesInductiveInvariant
     DEF RecognizedEnvironmentTransition


THEOREM RecognizedCanonicalTransitionPreservesInductiveInvariant ==
  InductiveInvariant /\ RecognizedCanonicalTransition
    => InductiveInvariant'
PROOF
  BY RecognizedSeedTransitionPreservesInductiveInvariant,
     RecognizedEnvironmentTransitionPreservesInductiveInvariant
     DEF RecognizedCanonicalTransition


THEOREM NextPreservesInductiveInvariant ==
  InductiveInvariant /\ Next
    => InductiveInvariant'
PROOF
  BY RecognizedCanonicalTransitionPreservesInductiveInvariant,
     EvaluatePreservesInductiveInvariant
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
  BY DEF RegisterRequest,
         RequestsAppendOnlyStep,
         Requests


THEOREM SubmitResolutionSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => RequestsAppendOnlyStep
PROOF
  BY DEF SubmitResolution,
         RequestsAppendOnlyStep,
         Requests


THEOREM ObserveConflictSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => RequestsAppendOnlyStep
PROOF
  BY DEF ObserveConflict,
         RequestsAppendOnlyStep,
         Requests


THEOREM StateStutterSatisfiesRequestsAppendOnlyStep ==
  UNCHANGED vars => RequestsAppendOnlyStep
PROOF
  BY DEF vars, canonicalVars, RequestsAppendOnlyStep, Requests


THEOREM ObserveInvalidMaterialSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds :
    ObserveInvalidMaterial(r) => RequestsAppendOnlyStep
PROOF
  BY StateStutterSatisfiesRequestsAppendOnlyStep
     DEF ObserveInvalidMaterial


THEOREM ObserveNonAuthoritativeInputSatisfiesRequestsAppendOnlyStep ==
  \A r \in ResolutionIds :
    ObserveNonAuthoritativeInput(r) => RequestsAppendOnlyStep
PROOF
  BY StateStutterSatisfiesRequestsAppendOnlyStep
     DEF ObserveNonAuthoritativeInput


THEOREM EvaluateSatisfiesRequestsAppendOnlyStep ==
  Evaluate => RequestsAppendOnlyStep
PROOF
  BY StateStutterSatisfiesRequestsAppendOnlyStep
     DEF Evaluate


THEOREM RecognizedCanonicalTransitionSatisfiesRequestsAppendOnlyStep ==
  RecognizedCanonicalTransition => RequestsAppendOnlyStep
PROOF
  BY RegisterRequestSatisfiesRequestsAppendOnlyStep,
     SubmitResolutionSatisfiesRequestsAppendOnlyStep,
     ObserveConflictSatisfiesRequestsAppendOnlyStep,
     ObserveInvalidMaterialSatisfiesRequestsAppendOnlyStep,
     ObserveNonAuthoritativeInputSatisfiesRequestsAppendOnlyStep
     DEF RecognizedCanonicalTransition,
         RecognizedSeedTransition,
         RecognizedEnvironmentTransition


THEOREM NextSatisfiesRequestsAppendOnlyStep ==
  Next => RequestsAppendOnlyStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesRequestsAppendOnlyStep,
     EvaluateSatisfiesRequestsAppendOnlyStep
     DEF Next


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
  BY DEF RegisterRequest,
         TerminalRecordsImmutableStep,
         TerminalRequests


THEOREM SubmitResolutionSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => TerminalRecordsImmutableStep
PROOF
  BY DEF SubmitResolution,
         TerminalRecordsImmutableStep,
         TerminalRequests


THEOREM ObserveConflictSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => TerminalRecordsImmutableStep
PROOF
  BY DEF ObserveConflict,
         TerminalRecordsImmutableStep,
         TerminalRequests


THEOREM StateStutterSatisfiesTerminalRecordsImmutableStep ==
  UNCHANGED vars => TerminalRecordsImmutableStep
PROOF
  BY DEF vars, canonicalVars, TerminalRecordsImmutableStep, TerminalRequests


THEOREM ObserveInvalidMaterialSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds :
    ObserveInvalidMaterial(r) => TerminalRecordsImmutableStep
PROOF
  BY StateStutterSatisfiesTerminalRecordsImmutableStep
     DEF ObserveInvalidMaterial


THEOREM ObserveNonAuthoritativeInputSatisfiesTerminalRecordsImmutableStep ==
  \A r \in ResolutionIds :
    ObserveNonAuthoritativeInput(r) => TerminalRecordsImmutableStep
PROOF
  BY StateStutterSatisfiesTerminalRecordsImmutableStep
     DEF ObserveNonAuthoritativeInput


THEOREM EvaluateSatisfiesTerminalRecordsImmutableStep ==
  Evaluate => TerminalRecordsImmutableStep
PROOF
  BY StateStutterSatisfiesTerminalRecordsImmutableStep
     DEF Evaluate


THEOREM RecognizedCanonicalTransitionSatisfiesTerminalRecordsImmutableStep ==
  RecognizedCanonicalTransition => TerminalRecordsImmutableStep
PROOF
  BY RegisterRequestSatisfiesTerminalRecordsImmutableStep,
     SubmitResolutionSatisfiesTerminalRecordsImmutableStep,
     ObserveConflictSatisfiesTerminalRecordsImmutableStep,
     ObserveInvalidMaterialSatisfiesTerminalRecordsImmutableStep,
     ObserveNonAuthoritativeInputSatisfiesTerminalRecordsImmutableStep
     DEF RecognizedCanonicalTransition,
         RecognizedSeedTransition,
         RecognizedEnvironmentTransition


THEOREM NextSatisfiesTerminalRecordsImmutableStep ==
  Next => TerminalRecordsImmutableStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesTerminalRecordsImmutableStep,
     EvaluateSatisfiesTerminalRecordsImmutableStep
     DEF Next


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


THEOREM RecognizedCanonicalTransitionSatisfiesCanonicalTransitionStep ==
  RecognizedCanonicalTransition
    => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM EvaluateSatisfiesCanonicalTransitionStep ==
  Evaluate => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF Evaluate,
         vars,
         canonicalVars,
         CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM NextSatisfiesCanonicalTransitionStep ==
  Next => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesCanonicalTransitionStep,
     EvaluateSatisfiesCanonicalTransitionStep
     DEF Next


THEOREM BoxNextSatisfiesBoxCanonicalTransitionStep ==
  [Next]_vars => [CanonicalStateChangesOnlyByRecognizedTransitionStep]_vars
PROOF
  BY NextSatisfiesCanonicalTransitionStep
     DEF vars,
         canonicalVars,
         CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM SpecImpliesCanonicalStateChangesOnlyByRecognizedTransition ==
  Spec => CanonicalStateChangesOnlyByRecognizedTransition
PROOF
  BY PTL,
     BoxNextSatisfiesBoxCanonicalTransitionStep
     DEF Spec, CanonicalStateChangesOnlyByRecognizedTransition


THEOREM InvalidMaterialActionIsStutter ==
  \A r \in ResolutionIds :
    ObserveInvalidMaterial(r) => UNCHANGED vars
PROOF
  BY DEF ObserveInvalidMaterial


THEOREM NextSatisfiesInvalidMaterialStutterStep ==
  Next => InvalidMaterialStutterStep
PROOF
  BY InvalidMaterialActionIsStutter
     DEF InvalidMaterialStutterStep


THEOREM BoxNextSatisfiesBoxInvalidMaterialStutterStep ==
  [Next]_vars => [InvalidMaterialStutterStep]_vars
PROOF
  BY NextSatisfiesInvalidMaterialStutterStep
     DEF vars, InvalidMaterialStutterStep


THEOREM SpecImpliesInvalidMaterialStutter ==
  Spec => InvalidMaterialStutter
PROOF
  BY PTL,
     BoxNextSatisfiesBoxInvalidMaterialStutterStep
     DEF Spec, InvalidMaterialStutter


THEOREM NonAuthoritativeInputActionIsStutter ==
  \A r \in ResolutionIds :
    ObserveNonAuthoritativeInput(r) => UNCHANGED vars
PROOF
  BY DEF ObserveNonAuthoritativeInput


THEOREM NextSatisfiesNonAuthoritativeInputsStutterStep ==
  Next => NonAuthoritativeInputsStutterStep
PROOF
  BY NonAuthoritativeInputActionIsStutter
     DEF NonAuthoritativeInputsStutterStep


THEOREM BoxNextSatisfiesBoxNonAuthoritativeInputsStutterStep ==
  [Next]_vars => [NonAuthoritativeInputsStutterStep]_vars
PROOF
  BY NextSatisfiesNonAuthoritativeInputsStutterStep
     DEF vars, NonAuthoritativeInputsStutterStep


THEOREM SpecImpliesNonAuthoritativeInputsStutter ==
  Spec => NonAuthoritativeInputsStutter
PROOF
  BY PTL,
     BoxNextSatisfiesBoxNonAuthoritativeInputsStutterStep
     DEF Spec, NonAuthoritativeInputsStutter

=============================================================================
