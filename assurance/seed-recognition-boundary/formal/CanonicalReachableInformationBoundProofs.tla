------------ MODULE CanonicalReachableInformationBoundProofs ------------
EXTENDS CanonicalReachableInformationBound,
        CanonicalLocalReachabilityProofs,
        ParametricLocalStateCardinalityProofs,
        TLAPS,
        FiniteSetTheorems

ASSUME CanonicalLinkAssumptions

(***************************************************************************)
(* Reachability equivalence -> exact reachable set identity.            *)
(***************************************************************************)

THEOREM ReachableLocalStatesCharacterization ==
  \A s :
    s \in ReachableLocalStates
      <=>
    ReachableWithinThree(s)
PROOF
  <1> SUFFICES
        ASSUME NEW s
        PROVE
          s \in ReachableLocalStates
            <=>
          ReachableWithinThree(s)
       OBVIOUS
  <1>1. s \in ReachableLocalStates
          =>
        ReachableWithinThree(s)
        BY DEF ReachableLocalStates
  <1>2. ReachableWithinThree(s)
          =>
        s \in ExactLocalStatesP
        BY ExactIffReachableWithinThree
  <1>3. ReachableWithinThree(s)
          =>
        s \in ReachableLocalStates
        BY <1>2
           DEF ReachableLocalStates
  <1>. QED
        BY <1>1, <1>3

THEOREM ReachableLocalStatesEqualExact ==
  ReachableLocalStates = ExactLocalStatesP
PROOF
  BY EveryExactStateReachableWithinThree
     DEF ReachableLocalStates

THEOREM ReachableLocalStatesFinite ==
  IsFiniteSet(ReachableLocalStates)
PROOF
  BY ReachableLocalStatesEqualExact,
     ExactLocalStatesFinite

(***************************************************************************)
(* Exact parametric cardinality -> exact reachable cardinality.                   *)
(***************************************************************************)

THEOREM ReachableLocalStateCardinality ==
  Cardinality(ReachableLocalStates) = ParametricExactCount
PROOF
  BY ReachableLocalStatesEqualExact,
     ParametricExactLocalStateCardinality

THEOREM ReachableLocalStateCardinalityType ==
  Cardinality(ReachableLocalStates) \in Nat
PROOF
  BY ReachableLocalStatesFinite,
     FS_CardinalityType

(***************************************************************************)
(* Generic finite faithful-code pigeonhole lower bound.                    *)
(***************************************************************************)

THEOREM NoFaithfulEncodingIntoSmallerFiniteCodomain ==
  \A codomain :
    /\ IsFiniteSet(codomain)
    /\ Cardinality(codomain) < Cardinality(ReachableLocalStates)
    =>
    ~\E f : FaithfulReachableEncoding(f, codomain)
PROOF
  <1> SUFFICES
        ASSUME NEW codomain,
               IsFiniteSet(codomain),
               Cardinality(codomain) < Cardinality(ReachableLocalStates),
               NEW f,
               FaithfulReachableEncoding(f, codomain)
        PROVE FALSE
       OBVIOUS
  <1>1. f \in [ReachableLocalStates -> codomain]
        BY DEF FaithfulReachableEncoding
  <1>2. PICK x, y \in ReachableLocalStates :
          /\ x # y
          /\ f[x] = f[y]
        BY <1>1,
           ReachableLocalStatesFinite,
           FS_PigeonHole
  <1>3. f[x] # f[y]
        BY <1>2
           DEF FaithfulReachableEncoding
  <1>. QED
        BY <1>2, <1>3

THEOREM NoFaithfulEncodingBelowParametricExactCount ==
  \A codomain :
    /\ IsFiniteSet(codomain)
    /\ Cardinality(codomain) < ParametricExactCount
    =>
    ~\E f : FaithfulReachableEncoding(f, codomain)
PROOF
  BY ReachableLocalStateCardinality,
     NoFaithfulEncodingIntoSmallerFiniteCodomain

THEOREM FaithfulEncodingCodeCardinalityLowerBound ==
  \A codomain :
    IsFiniteSet(codomain)
      =>
    \A f :
      FaithfulReachableEncoding(f, codomain)
        =>
      ParametricExactCount <= Cardinality(codomain)
PROOF
  <1> SUFFICES
        ASSUME NEW codomain,
               IsFiniteSet(codomain),
               NEW f,
               FaithfulReachableEncoding(f, codomain)
        PROVE
          ParametricExactCount <= Cardinality(codomain)
       OBVIOUS
  <1>1. Cardinality(codomain) \in Nat
        BY FS_CardinalityType
  <1>2. ParametricExactCount \in Nat
        BY ReachableLocalStateCardinality,
           ReachableLocalStateCardinalityType
  <1>3. ~(Cardinality(codomain) < ParametricExactCount)
        BY NoFaithfulEncodingBelowParametricExactCount
  <1>. QED
        BY SMTT(60), <1>1, <1>2, <1>3

(***************************************************************************)
(* Capacity-form corollary.                                                *)
(*                                                                         *)
(* A concrete fixed-width binary representation is obtained by setting     *)
(* capacity to the number of available binary codewords (at most 2^k).     *)
(***************************************************************************)

THEOREM FaithfulFiniteCapacityLowerBound ==
  \A f, codomain, capacity :
    FaithfulFiniteCapacity(f, codomain, capacity)
      =>
    ParametricExactCount <= capacity
PROOF
  <1> SUFFICES
        ASSUME NEW f,
               NEW codomain,
               NEW capacity,
               FaithfulFiniteCapacity(f, codomain, capacity)
        PROVE ParametricExactCount <= capacity
       OBVIOUS
  <1>1. /\ FaithfulReachableEncoding(f, codomain)
         /\ IsFiniteSet(codomain)
         /\ capacity \in Nat
         /\ Cardinality(codomain) <= capacity
        BY DEF FaithfulFiniteCapacity,
               FiniteCodeCapacity
  <1>2. ParametricExactCount <= Cardinality(codomain)
        BY <1>1,
           FaithfulEncodingCodeCardinalityLowerBound
  <1>3. ParametricExactCount \in Nat
        BY ReachableLocalStateCardinality,
           ReachableLocalStateCardinalityType
  <1>4. Cardinality(codomain) \in Nat
        BY <1>1, FS_CardinalityType
  <1>. QED
        BY SMTT(60), <1>1, <1>2, <1>3, <1>4

THEOREM CanonicalReachableInformationBound ==
  /\ ReachableLocalStates = ExactLocalStatesP
  /\ Cardinality(ReachableLocalStates) = ParametricExactCount
  /\ \A codomain :
       /\ IsFiniteSet(codomain)
       /\ Cardinality(codomain) < ParametricExactCount
       =>
       ~\E f : FaithfulReachableEncoding(f, codomain)
  /\ \A f, codomain, capacity :
       FaithfulFiniteCapacity(f, codomain, capacity)
         =>
       ParametricExactCount <= capacity
PROOF
  BY ReachableLocalStatesEqualExact,
     ReachableLocalStateCardinality,
     NoFaithfulEncodingBelowParametricExactCount,
     FaithfulFiniteCapacityLowerBound

=============================================================================
