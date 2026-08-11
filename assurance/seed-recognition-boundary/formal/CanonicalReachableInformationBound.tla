--------------- MODULE CanonicalReachableInformationBound ---------------
EXTENDS CanonicalLocalReachability

(***************************************************************************)
(* PUBLIC / NON-NORMATIVE ASSURANCE.                                                *)
(*                                                                         *)
(* Target: compose the mechanically proved exact parametric        *)
(* cardinality theorem with the mechanically proved canonical-local    *)
(* reachability equivalence, then state a representation-independent       *)
(* finite-code lower bound.                                                *)
(*                                                                         *)
(* This module adds no recognition state, transition, authority rule,      *)
(* observation rule, or canonical semantics.                               *)
(*                                                                         *)
(* The mechanically targeted result is stronger and cleaner than a         *)
(* binary-only theorem: every finite faithful code space must contain at   *)
(* least as many distinguishable code states as the exact reachable local  *)
(* canonical state space.                                                  *)
(*                                                                         *)
(* Binary fixed-width consequence (external arithmetic corollary):         *)
(*   if a k-bit code space has at most 2^k code states, then                *)
(*     2^k >= ParametricExactCount.                                        *)
(* Hence k >= ceil(log2(ParametricExactCount)).                            *)
(*                                                                         *)
(* No Shannon entropy or expected code-length claim is made.               *)
(***************************************************************************)

ReachableLocalStates ==
  {s \in ExactLocalStatesP : ReachableWithinThree(s)}

FaithfulReachableEncoding(f, codomain) ==
  /\ f \in [ReachableLocalStates -> codomain]
  /\ \A x \in ReachableLocalStates,
        y \in ReachableLocalStates :
       x # y => f[x] # f[y]

FiniteCodeCapacity(codomain, capacity) ==
  /\ IsFiniteSet(codomain)
  /\ capacity \in Nat
  /\ Cardinality(codomain) <= capacity

FaithfulFiniteCapacity(f, codomain, capacity) ==
  /\ FaithfulReachableEncoding(f, codomain)
  /\ FiniteCodeCapacity(codomain, capacity)

=============================================================================
