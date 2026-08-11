----------------------- MODULE DecisionSubjectBinding -----------------------
CONSTANTS Contexts, GenesisValues, Prefixes, Descriptors, PolicyEpochs, Scopes

ASSUME Contexts # {}
ASSUME GenesisValues # {}
ASSUME Prefixes # {}
ASSUME Descriptors # {}
ASSUME PolicyEpochs # {}
ASSUME Scopes # {}

StateIdentity(g, prefix) ==
  [genesis |-> g,
   prefix |-> prefix]

DecisionSubject(c, g, prefix, d, policy, scope) ==
  [context_id |-> c,
   state_identity |-> StateIdentity(g, prefix),
   question_identity |-> d,
   policy_epoch |-> policy,
   scope |-> scope]

Bindings ==
  [context_id : Contexts,
   state_identity : [genesis : GenesisValues, prefix : Prefixes],
   question_identity : Descriptors,
   policy_epoch : PolicyEpochs,
   scope : Scopes]

BindingOf(c, g, prefix, d, policy, scope) ==
  DecisionSubject(c, g, prefix, d, policy, scope)

=============================================================================
