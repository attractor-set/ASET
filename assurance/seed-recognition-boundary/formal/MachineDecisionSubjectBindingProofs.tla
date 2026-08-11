--------------- MODULE MachineDecisionSubjectBindingProofs ---------------
EXTENDS DecisionSubjectBindingProofs, TLAPS

CONSTANTS Candidates, Decisions, Describe, Decide

ASSUME Candidates # {}
ASSUME Decisions # {}
ASSUME DescribeType == Describe \in [Candidates -> Descriptors]
ASSUME DecideType == Decide \in [Descriptors -> Decisions]

MB == INSTANCE MachineBindability
  WITH Candidates <- Candidates,
       Descriptors <- Descriptors,
       Decisions <- Decisions,
       Describe <- Describe,
       Decide <- Decide

THEOREM MachineCandidateProducesCanonicalBinding ==
  \A x \in Candidates,
     c \in Contexts,
     g \in GenesisValues,
     prefix \in Prefixes,
     policy \in PolicyEpochs,
     scope \in Scopes :
    BindingOf(c, g, prefix, Describe[x], policy, scope) \in Bindings
PROOF
  <1> SUFFICES ASSUME NEW x \in Candidates,
                      NEW c \in Contexts,
                      NEW g \in GenesisValues,
                      NEW prefix \in Prefixes,
                      NEW policy \in PolicyEpochs,
                      NEW scope \in Scopes
               PROVE BindingOf(c, g, prefix, Describe[x], policy, scope) \in Bindings
       OBVIOUS
  <1>1. Describe[x] \in Descriptors
       BY DescribeType, SMTT(30)
  <1> QED
       BY SMTT(30), <1>1, BindingOfIsCanonicalBinding

THEOREM DifferentMachineDecisionProducesDifferentExactBinding ==
  \A x \in Candidates, y \in Candidates,
     c \in Contexts,
     g \in GenesisValues,
     prefix \in Prefixes,
     policy \in PolicyEpochs,
     scope \in Scopes :
    MB!MachineDecision(x) # MB!MachineDecision(y)
    =>
      BindingOf(c, g, prefix, Describe[x], policy, scope)
        # BindingOf(c, g, prefix, Describe[y], policy, scope)
PROOF
  BY SMTT(30)
     DEF MB!MachineDecision, BindingOf, DecisionSubject, StateIdentity

=============================================================================
