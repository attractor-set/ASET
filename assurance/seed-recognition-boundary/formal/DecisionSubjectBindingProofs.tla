-------------------- MODULE DecisionSubjectBindingProofs --------------------
EXTENDS DecisionSubjectBinding, TLAPS

THEOREM BindingOfIsCanonicalBinding ==
  \A c \in Contexts,
     g \in GenesisValues,
     prefix \in Prefixes,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes :
    BindingOf(c, g, prefix, d, policy, scope) \in Bindings
PROOF
  BY SMTT(30)
     DEF BindingOf, Bindings, DecisionSubject, StateIdentity

THEOREM BindingEqualityImpliesSubjectEquality ==
  \A c1 \in Contexts, c2 \in Contexts,
     g1 \in GenesisValues, g2 \in GenesisValues,
     p1 \in Prefixes, p2 \in Prefixes,
     d1 \in Descriptors, d2 \in Descriptors,
     e1 \in PolicyEpochs, e2 \in PolicyEpochs,
     s1 \in Scopes, s2 \in Scopes :
    BindingOf(c1, g1, p1, d1, e1, s1)
      = BindingOf(c2, g2, p2, d2, e2, s2)
    =>
      /\ c1 = c2
      /\ g1 = g2
      /\ p1 = p2
      /\ d1 = d2
      /\ e1 = e2
      /\ s1 = s2
PROOF
  BY SMTT(30)
     DEF BindingOf, DecisionSubject, StateIdentity

THEOREM DifferentDescriptorChangesBinding ==
  \A c \in Contexts,
     g \in GenesisValues,
     prefix \in Prefixes,
     d1 \in Descriptors, d2 \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes :
    d1 # d2
    =>
      BindingOf(c, g, prefix, d1, policy, scope)
        # BindingOf(c, g, prefix, d2, policy, scope)
PROOF
  BY SMTT(30)
     DEF BindingOf, DecisionSubject, StateIdentity

THEOREM DifferentPrefixChangesBinding ==
  \A c \in Contexts,
     g \in GenesisValues,
     p1 \in Prefixes, p2 \in Prefixes,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes :
    p1 # p2
    =>
      BindingOf(c, g, p1, d, policy, scope)
        # BindingOf(c, g, p2, d, policy, scope)
PROOF
  BY SMTT(30)
     DEF BindingOf, DecisionSubject, StateIdentity

THEOREM DifferentGenesisChangesBinding ==
  \A c \in Contexts,
     g1 \in GenesisValues, g2 \in GenesisValues,
     prefix \in Prefixes,
     d \in Descriptors,
     policy \in PolicyEpochs,
     scope \in Scopes :
    g1 # g2
    =>
      BindingOf(c, g1, prefix, d, policy, scope)
        # BindingOf(c, g2, prefix, d, policy, scope)
PROOF
  BY SMTT(30)
     DEF BindingOf, DecisionSubject, StateIdentity

=============================================================================
