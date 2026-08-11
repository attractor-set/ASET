------------- MODULE IndependentRecognitionToGCRLiftingProofs -------------
EXTENDS IndependentRecognitionContract, TLAPS

ToGCRResolution(outcome) ==
  IF outcome = "ADMIT" THEN "ALLOW" ELSE "BLOCK"

GCRTerminalMeta ==
  [r \in DOMAIN nativeTerminalMeta |->
     [resolution |-> ToGCRResolution(nativeTerminalMeta[r].outcome),
      authority |-> nativeTerminalMeta[r].authority]]

GCR == INSTANCE GenesisAnchoredRecognition
  WITH ResolutionIds <- DecisionIds,
       Authorities <- NativeAuthorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RecognizedAuthorityBindings <- NativeAuthoritySubjects,
       Genesis <- Genesis,
       Events <- NativeEvents,
       Contexts <- NativeContexts,
       Descriptors <- NativeDescriptors,
       PolicyEpochs <- NativePolicyEpochs,
       Scopes <- NativeScopes,
       requestMeta <- nativeRequestMeta,
       terminalMeta <- GCRTerminalMeta,
       conflicts <- nativeConflicts,
       lineage <- nativeLineage,
       applied <- nativeCrossed

THEOREM NativeBindingsEqualGCRBindings ==
  NativeSubjects = GCR!Bindings
PROOF
  BY DEF NativeSubjects,
         Subject!Bindings,
         GCR!Bindings,
         GCR!LineagePrefixes,
         GCR!LineageEntryType,
         NativeLineagePrefixes,
         NativeLineageEntryType

THEOREM NativeSubjectEqualsGCRBinding ==
  \A c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes :
    NativeSubjectOf(c, nativeLineage, d, policy, scope)
      = GCR!BindingOf(c, nativeLineage, d, policy, scope)
PROOF
  BY DEF NativeSubjectOf,
         Subject!BindingOf,
         Subject!DecisionSubject,
         Subject!StateIdentity,
         GCR!BindingOf

THEOREM NativeStatusMapsToGCRResolution ==
  NativeTypeOK =>
    \A r \in DecisionIds :
      /\ (NativeStatusOf(r) = "UNRESOLVED"
            <=> GCR!ResolutionOf(r) = "UNKNOWN")
      /\ (NativeStatusOf(r) = "ADMIT"
            <=> GCR!ResolutionOf(r) = "ALLOW")
      /\ (NativeStatusOf(r) = "REJECT"
            <=> GCR!ResolutionOf(r) = "BLOCK")
      /\ NativeEffectAdmitted(r) = GCR!EffectPermitted(r)
PROOF
  BY SMTT(120)
     DEF NativeTypeOK,
         NativeTerminalMetaType,
         NativeTerminalOutcomes,
         NativeStatusOf,
         NativeEffectAdmitted,
         NativeRequests,
         NativeTerminalRequests,
         NativeTerminalOutcome,
         GCR!ResolutionOf,
         GCR!EffectPermitted,
         GCR!Requests,
         GCR!TerminalRequests,
         GCR!TerminalResolution,
         GCRTerminalMeta,
         ToGCRResolution

THEOREM NativeAdmissionImpliesGCREffectPermitted ==
  \A r \in DecisionIds :
    NativeEffectAdmitted(r) => GCR!EffectPermitted(r)
PROOF
  BY SMTT(60)
     DEF NativeEffectAdmitted,
         NativeStatusOf,
         NativeRequests,
         NativeTerminalRequests,
         NativeTerminalOutcome,
         GCR!EffectPermitted,
         GCR!ResolutionOf,
         GCR!Requests,
         GCR!TerminalRequests,
         GCR!TerminalResolution,
         GCRTerminalMeta,
         ToGCRResolution


THEOREM NativeInitRefinesGCRInit ==
  NativeInit => GCR!Init
PROOF
  BY DEF NativeInit, GCR!Init, GCRTerminalMeta

THEOREM NativeTerminalMetaStutterPreservesGCRTerminalMeta ==
  UNCHANGED nativeTerminalMeta => UNCHANGED GCRTerminalMeta
PROOF
  BY SMTT(60)
     DEF GCRTerminalMeta,
         ToGCRResolution

THEOREM NativeOpenPreservesGCRTerminalMeta ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => UNCHANGED GCRTerminalMeta
PROOF
  BY SMTT(60),
     NativeTerminalMetaStutterPreservesGCRTerminalMeta
     DEF NativeOpen,
         nativeLineageVars

THEOREM NativeOpenCarriesGCRRegisterGuards ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      =>
      /\ r \in DecisionIds \ GCR!Requests
      /\ c \in NativeContexts
      /\ d \in NativeDescriptors
      /\ policy \in NativePolicyEpochs
      /\ scope \in NativeScopes
      /\ GCR!BindingOf(c, nativeLineage, d, policy, scope) \in GCR!Bindings
      /\ a \in NativeAuthorities
      /\ <<a, GCR!BindingOf(c, nativeLineage, d, policy, scope)>>
           \in NativeAuthoritySubjects
      /\ \/ previous = NoCommitment
         \/ previous \in RecognizedTerminalCommitments
PROOF
  BY SMTT(60),
     NativeSubjectEqualsGCRBinding,
     NativeBindingsEqualGCRBindings
     DEF NativeOpen,
         NativeRequests,
         GCR!Requests

THEOREM NativeOpenRequestUpdateMatchesGCR ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      =>
      nativeRequestMeta' =
        [x \in GCR!Requests \cup {r} |->
           IF x = r
           THEN [binding |-> GCR!BindingOf(c, nativeLineage, d, policy, scope),
                 previous |-> previous]
           ELSE nativeRequestMeta[x]]
PROOF
  BY SMTT(60),
     NativeSubjectEqualsGCRBinding
     DEF NativeOpen,
         NativeRequests,
         GCR!Requests

THEOREM NativeOpenPreservesNativeConflicts ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => UNCHANGED nativeConflicts
PROOF
  BY SMTT(60)
     DEF NativeOpen

THEOREM GCRRecognitionRemainderStutterFromComponents ==
  /\ UNCHANGED GCRTerminalMeta
  /\ UNCHANGED nativeConflicts
  => UNCHANGED <<GCRTerminalMeta, nativeConflicts>>
PROOF
  BY SMTT(60)

THEOREM NativeOpenPreservesGCRRecognitionRemainder ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => UNCHANGED <<GCRTerminalMeta, nativeConflicts>>
PROOF
  BY SMTT(60),
     NativeOpenPreservesGCRTerminalMeta,
     NativeOpenPreservesNativeConflicts,
     GCRRecognitionRemainderStutterFromComponents

THEOREM NativeOpenPreservesGCRLineageVars ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => UNCHANGED GCR!lineageVars
PROOF
  BY SMTT(60)
     DEF NativeOpen,
         nativeLineageVars,
         GCR!lineageVars

THEOREM NativeOpenRefinesGCRRegister ==
  \A r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)
      => GCR!RegisterRequest(r, c, d, policy, scope, a, previous)
PROOF
  BY SMTT(60),
     NativeOpenCarriesGCRRegisterGuards,
     NativeOpenRequestUpdateMatchesGCR,
     NativeOpenPreservesGCRRecognitionRemainder,
     NativeOpenPreservesGCRLineageVars
     DEF GCR!RegisterRequest


THEOREM NativeDecideAdmitRefinesGCRSubmit ==
  \A r \in DecisionIds,
     subject \in NativeSubjects,
     a \in NativeAuthorities :
    NativeDecide(r, subject, a, "ADMIT")
      => GCR!SubmitResolution(r, subject, a, "ALLOW")
PROOF
  BY SMTT(120),
     NativeBindingsEqualGCRBindings
     DEF NativeDecide,
         NativeRequests,
         NativeTerminalRequests,
         NativeRequestBinding,
         nativeLineageVars,
         NativeTerminalOutcomes,
         GCR!SubmitResolution,
         GCR!Requests,
         GCR!TerminalRequests,
         GCR!RequestBinding,
         GCR!TerminalResolutions,
         GCR!lineageVars,
         GCRTerminalMeta,
         ToGCRResolution

THEOREM NativeDecideRejectRefinesGCRSubmit ==
  \A r \in DecisionIds,
     subject \in NativeSubjects,
     a \in NativeAuthorities :
    NativeDecide(r, subject, a, "REJECT")
      => GCR!SubmitResolution(r, subject, a, "BLOCK")
PROOF
  BY SMTT(120),
     NativeBindingsEqualGCRBindings
     DEF NativeDecide,
         NativeRequests,
         NativeTerminalRequests,
         NativeRequestBinding,
         nativeLineageVars,
         NativeTerminalOutcomes,
         GCR!SubmitResolution,
         GCR!Requests,
         GCR!TerminalRequests,
         GCR!RequestBinding,
         GCR!TerminalResolutions,
         GCR!lineageVars,
         GCRTerminalMeta,
         ToGCRResolution

THEOREM NativeConflictRefinesGCRConflict ==
  \A r \in DecisionIds :
    NativeObserveConflict(r) => GCR!ObserveConflict(r)
PROOF
  BY SMTT(60)
     DEF NativeObserveConflict,
         NativeTerminalRequests,
         nativeLineageVars,
         GCR!ObserveConflict,
         GCR!TerminalRequests,
         GCR!lineageVars,
         GCRTerminalMeta

THEOREM NativeCrossRefinesGCRApplication ==
  \A r \in DecisionIds, e \in NativeEvents :
    NativeCross(r, e) => GCR!ApplyRecognized(r, e)
PROOF
  BY SMTT(60),
     NativeAdmissionImpliesGCREffectPermitted
     DEF NativeCross,
         NativeRequests,
         nativeRecognitionVars,
         GCR!ApplyRecognized,
         GCR!Requests,
         GCR!recognitionVars,
         GCRTerminalMeta

NativeOpenTransition ==
  \E r \in DecisionIds,
     c \in NativeContexts,
     d \in NativeDescriptors,
     policy \in NativePolicyEpochs,
     scope \in NativeScopes,
     a \in NativeAuthorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    NativeOpen(r, c, d, policy, scope, a, previous)

NativeDecisionTransition ==
  \E r \in DecisionIds,
     subject \in NativeSubjects,
     a \in NativeAuthorities,
     outcome \in NativeTerminalOutcomes :
    NativeDecide(r, subject, a, outcome)

THEOREM NativeOpenTransitionRefinesGCR ==
  NativeOpenTransition => GCR!RecognizedSeedLikeTransition
PROOF
  <1> SUFFICES ASSUME NativeOpenTransition
               PROVE GCR!RecognizedSeedLikeTransition
       OBVIOUS
  <1>1. PICK r \in DecisionIds,
              c \in NativeContexts,
              d \in NativeDescriptors,
              policy \in NativePolicyEpochs,
              scope \in NativeScopes,
              a \in NativeAuthorities,
              previous \in TerminalCommitments \cup {NoCommitment} :
          NativeOpen(r, c, d, policy, scope, a, previous)
       BY Zenon DEF NativeOpenTransition
  <1>2. GCR!RegisterRequest(r, c, d, policy, scope, a, previous)
       BY <1>1, NativeOpenRefinesGCRRegister
  <1> QED
       BY <1>2
          DEF GCR!RecognizedSeedLikeTransition

THEOREM NativeDecisionTransitionRefinesGCR ==
  NativeDecisionTransition => GCR!RecognizedSeedLikeTransition
PROOF
  <1> SUFFICES ASSUME NativeDecisionTransition
               PROVE GCR!RecognizedSeedLikeTransition
       OBVIOUS
  <1>1. PICK r \in DecisionIds,
              subject \in NativeSubjects,
              a \in NativeAuthorities,
              outcome \in NativeTerminalOutcomes :
          NativeDecide(r, subject, a, outcome)
       BY Zenon DEF NativeDecisionTransition
  <1>2. outcome = "ADMIT" \/ outcome = "REJECT"
       BY <1>1 DEF NativeTerminalOutcomes
  <1>3. CASE outcome = "ADMIT"
    <2>1. GCR!SubmitResolution(r, subject, a, "ALLOW")
         BY <1>1, <1>3, NativeDecideAdmitRefinesGCRSubmit
    <2> QED
         BY <2>1, NativeBindingsEqualGCRBindings
            DEF GCR!RecognizedSeedLikeTransition, GCR!TerminalResolutions
  <1>4. CASE outcome = "REJECT"
    <2>1. GCR!SubmitResolution(r, subject, a, "BLOCK")
         BY <1>1, <1>4, NativeDecideRejectRefinesGCRSubmit
    <2> QED
         BY <2>1, NativeBindingsEqualGCRBindings
            DEF GCR!RecognizedSeedLikeTransition, GCR!TerminalResolutions
  <1> QED
       BY <1>2, <1>3, <1>4

THEOREM NativeSeedLikeTransitionRefinesGCR ==
  NativeSeedLikeTransition => GCR!RecognizedSeedLikeTransition
PROOF
  BY NativeOpenTransitionRefinesGCR,
     NativeDecisionTransitionRefinesGCR
     DEF NativeSeedLikeTransition,
         NativeOpenTransition,
         NativeDecisionTransition

THEOREM NativeEnvironmentTransitionRefinesGCR ==
  NativeEnvironmentTransition => GCR!EnvironmentTransition
PROOF
  BY SMTT(60),
     NativeConflictRefinesGCRConflict
     DEF NativeEnvironmentTransition, GCR!EnvironmentTransition

THEOREM NativeApplicationTransitionRefinesGCR ==
  NativeApplicationTransition => GCR!ApplicationTransition
PROOF
  BY SMTT(60),
     NativeCrossRefinesGCRApplication
     DEF NativeApplicationTransition, GCR!ApplicationTransition

THEOREM NativeNextRefinesGCRNext ==
  NativeNext => GCR!Next
PROOF
  BY NativeSeedLikeTransitionRefinesGCR,
     NativeEnvironmentTransitionRefinesGCR,
     NativeApplicationTransitionRefinesGCR
     DEF NativeNext, GCR!Next

THEOREM NativeStateStutterStuttersGCR ==
  UNCHANGED nativeVars => UNCHANGED GCR!vars
PROOF
  BY SMTT(60)
     DEF nativeVars,
         GCR!vars,
         GCRTerminalMeta

THEOREM BoxNativeNextRefinesBoxGCRNext ==
  [NativeNext]_nativeVars => [GCR!Next]_GCR!vars
PROOF
  BY SMTT(60),
     NativeNextRefinesGCRNext,
     NativeStateStutterStuttersGCR

THEOREM IndependentRecognitionRefinesGCR ==
  NativeSpec => GCR!Spec
PROOF
  BY PTL,
     NativeInitRefinesGCRInit,
     BoxNativeNextRefinesBoxGCRNext
     DEF NativeSpec, GCR!Spec

=============================================================================
