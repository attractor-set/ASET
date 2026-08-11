------------------ MODULE GenesisAnchoredRecognitionProofs ------------------
EXTENDS GenesisAnchoredRecognition, TLAPS

THEOREM ConstructedBindingUsesCurrentFrozenPrefix ==
  \A c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes :
    /\ BindingOf(c, lineage, d, policy, scope).state_identity.genesis = Genesis
    /\ BindingOf(c, lineage, d, policy, scope).state_identity.prefix = lineage
    /\ BindingOf(c, lineage, d, policy, scope).context_id = c
    /\ BindingOf(c, lineage, d, policy, scope).question_identity = d
    /\ BindingOf(c, lineage, d, policy, scope).policy_epoch = policy
    /\ BindingOf(c, lineage, d, policy, scope).scope = scope
PROOF
  BY DEF BindingOf


THEOREM RegisterStoresConstructedCurrentPrefixBinding ==
  \A r \in ResolutionIds,
     c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, c, d, policy, scope, a, previous)
    =>
      requestMeta'[r].binding
        = BindingOf(c, lineage, d, policy, scope)
PROOF
  BY SMTT(30)
     DEF RegisterRequest, Requests

THEOREM RegisterPreservesFrozenLineage ==
  \A r \in ResolutionIds,
     c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, c, d, policy, scope, a, previous)
      => LineageFrozenAdditiveStep
PROOF
  BY DEF RegisterRequest, lineageVars, LineageFrozenAdditiveStep

THEOREM SubmitPreservesFrozenLineage ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => LineageFrozenAdditiveStep
PROOF
  BY DEF SubmitResolution, lineageVars, LineageFrozenAdditiveStep

THEOREM ConflictPreservesFrozenLineage ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => LineageFrozenAdditiveStep
PROOF
  BY DEF ObserveConflict, lineageVars, LineageFrozenAdditiveStep

THEOREM ApplicationAppendsFrozenLineage ==
  \A r \in ResolutionIds, e \in Events :
    ApplyRecognized(r, e) => LineageFrozenAdditiveStep
PROOF
  BY DEF ApplyRecognized, LineageFrozenAdditiveStep, LineageEntryType

THEOREM NextPreservesFrozenLineage ==
  Next => LineageFrozenAdditiveStep
PROOF
  BY RegisterPreservesFrozenLineage,
     SubmitPreservesFrozenLineage,
     ConflictPreservesFrozenLineage,
     ApplicationAppendsFrozenLineage
     DEF Next,
         RecognizedSeedLikeTransition,
         EnvironmentTransition,
         ApplicationTransition

THEOREM BoxNextPreservesFrozenLineage ==
  [Next]_vars => [LineageFrozenAdditiveStep]_vars
PROOF
  BY NextPreservesFrozenLineage
     DEF LineageFrozenAdditiveStep

THEOREM SpecImpliesFrozenAdditiveLineage ==
  Spec => LineageFrozenAdditive
PROOF
  BY PTL, BoxNextPreservesFrozenLineage
     DEF Spec, LineageFrozenAdditive

THEOREM ApplyRequiresEffectiveAllow ==
  \A r \in ResolutionIds, e \in Events :
    ApplyRecognized(r, e) => EffectPermitted(r)
PROOF
  BY DEF ApplyRecognized

THEOREM RegisterCreatesNoApplication ==
  \A r \in ResolutionIds,
     c \in Contexts,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, c, d, policy, scope, a, previous)
      => NewApplicationRequiresAllowStep
PROOF
  BY SMTT(30)
     DEF RegisterRequest, lineageVars, NewApplicationRequiresAllowStep

THEOREM SubmitCreatesNoApplication ==
  \A r \in ResolutionIds, b \in Bindings, a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => NewApplicationRequiresAllowStep
PROOF
  BY SMTT(30)
     DEF SubmitResolution, lineageVars, NewApplicationRequiresAllowStep

THEOREM ConflictCreatesNoApplication ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => NewApplicationRequiresAllowStep
PROOF
  BY SMTT(30)
     DEF ObserveConflict, lineageVars, NewApplicationRequiresAllowStep

THEOREM ApplyCreatesOnlyAllowedApplication ==
  \A r \in ResolutionIds, e \in Events :
    ApplyRecognized(r, e) => NewApplicationRequiresAllowStep
PROOF
  BY DEF ApplyRecognized, NewApplicationRequiresAllowStep

THEOREM NextRequiresAllowForNewApplication ==
  Next => NewApplicationRequiresAllowStep
PROOF
  BY RegisterCreatesNoApplication,
     SubmitCreatesNoApplication,
     ConflictCreatesNoApplication,
     ApplyCreatesOnlyAllowedApplication
     DEF Next,
         RecognizedSeedLikeTransition,
         EnvironmentTransition,
         ApplicationTransition

THEOREM BoxNextRequiresAllowForNewApplication ==
  [Next]_vars => [NewApplicationRequiresAllowStep]_vars
PROOF
  BY NextRequiresAllowForNewApplication
     DEF NewApplicationRequiresAllowStep

THEOREM SpecImpliesNewApplicationRequiresAllow ==
  Spec => NewApplicationRequiresAllow
PROOF
  BY PTL, BoxNextRequiresAllowForNewApplication
     DEF Spec, NewApplicationRequiresAllow

=============================================================================
