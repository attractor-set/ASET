-------------------------- MODULE MachineBindability --------------------------
EXTENDS FiniteSets

CONSTANTS Candidates, Descriptors, Decisions, Describe, Decide

ASSUME Candidates # {}
ASSUME Descriptors # {}
ASSUME Decisions # {}
ASSUME Describe \in [Candidates -> Descriptors]
ASSUME Decide \in [Descriptors -> Decisions]

MachineDecision(c) == Decide[Describe[c]]

=============================================================================
