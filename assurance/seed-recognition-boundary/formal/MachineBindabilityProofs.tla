----------------------- MODULE MachineBindabilityProofs -----------------------
EXTENDS MachineBindability, TLAPS

THEOREM SameDescriptorImpliesSameDecision ==
  \A x \in Candidates, y \in Candidates :
    Describe[x] = Describe[y] => MachineDecision(x) = MachineDecision(y)
PROOF
  BY DEF MachineDecision

THEOREM DifferentDecisionRequiresDifferentDescriptor ==
  \A x \in Candidates, y \in Candidates :
    MachineDecision(x) # MachineDecision(y) => Describe[x] # Describe[y]
PROOF
  BY SameDescriptorImpliesSameDecision

=============================================================================
