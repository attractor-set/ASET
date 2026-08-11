------------- MODULE ParametricLocalStateCardinalityProofs -------------
EXTENDS ParametricLocalStateCardinality, TLAPS, FiniteSetTheorems

ASSUME ParametricAssumptions

THEOREM ParametricBindingsFinite ==
  IsFiniteSet(PBindings)
PROOF
  BY ParametricAssumptions
     DEF ParametricAssumptions

THEOREM ParametricAuthoritiesFinite ==
  IsFiniteSet(PAuthorities)
PROOF
  BY ParametricAssumptions
     DEF ParametricAssumptions

THEOREM ParametricPreviousFinite ==
  IsFiniteSet(PPrevious)
PROOF
  BY ParametricAssumptions
     DEF ParametricAssumptions

THEOREM ParametricRABSubsetProduct ==
  PRAB \subseteq (PAuthorities \X PBindings)
PROOF
  BY ParametricAssumptions
     DEF ParametricAssumptions

THEOREM ProductPairReconstruction ==
  \A z \in PAuthorities \X PBindings :
    z = <<z[1], z[2]>>
PROOF
  BY SMTT(120)

THEOREM TerminalPayloadPairReconstruction ==
  \A z \in PRAB \X PPrevious :
    z = <<z[1], z[2]>>
PROOF
  BY SMTT(120)

THEOREM TerminalOuterPairReconstruction ==
  \A z \in TerminalPhaseCodes \X TerminalPayloadDomain :
    z = <<z[1], z[2]>>
PROOF
  BY SMTT(120)

THEOREM RecognizedBindingsSubset ==
  PRecognizedBindings \subseteq PBindings
PROOF
  BY DEF PRecognizedBindings

THEOREM RecognizedBindingsFinite ==
  IsFiniteSet(PRecognizedBindings)
PROOF
  <1>1. IsFiniteSet(PBindings)
        BY ParametricBindingsFinite
  <1>2. PRecognizedBindings \in SUBSET PBindings
        BY SMTT(60), RecognizedBindingsSubset
  <1>. QED
        BY <1>1, <1>2, FS_Subset

THEOREM AuthorityBindingProductFinite ==
  IsFiniteSet(PAuthorities \X PBindings)
PROOF
  <1>1. IsFiniteSet(PAuthorities)
        BY ParametricAuthoritiesFinite
  <1>2. IsFiniteSet(PBindings)
        BY ParametricBindingsFinite
  <1>. QED
        BY <1>1, <1>2, FS_Product

THEOREM RABFinite ==
  IsFiniteSet(PRAB)
PROOF
  <1>1. IsFiniteSet(PAuthorities \X PBindings)
        BY AuthorityBindingProductFinite
  <1>2. PRAB \in SUBSET (PAuthorities \X PBindings)
        BY SMTT(60), ParametricRABSubsetProduct
  <1>. QED
        BY <1>1, <1>2, FS_Subset

THEOREM PendingDomainCardinality ==
  /\ IsFiniteSet(PendingDomain)
  /\ Cardinality(PendingDomain)
       = Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
PROOF
  <1>1. IsFiniteSet(PRecognizedBindings)
        BY RecognizedBindingsFinite
  <1>2. IsFiniteSet(PPrevious)
        BY ParametricPreviousFinite
  <1>3. /\ IsFiniteSet(PRecognizedBindings \X PPrevious)
         /\ Cardinality(PRecognizedBindings \X PPrevious)
              = Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
        BY <1>1, <1>2, FS_Product
  <1>. QED
        BY <1>3 DEF PendingDomain

THEOREM TerminalPhaseCodesCardinality ==
  /\ IsFiniteSet(TerminalPhaseCodes)
  /\ Cardinality(TerminalPhaseCodes) = 4
PROOF
  BY FS_Interval
     DEF TerminalPhaseCodes

THEOREM TerminalPayloadDomainCardinality ==
  /\ IsFiniteSet(TerminalPayloadDomain)
  /\ Cardinality(TerminalPayloadDomain)
       = Cardinality(PRAB) * Cardinality(PPrevious)
PROOF
  <1>1. IsFiniteSet(PRAB)
        BY RABFinite
  <1>2. IsFiniteSet(PPrevious)
        BY ParametricPreviousFinite
  <1>3. /\ IsFiniteSet(PRAB \X PPrevious)
         /\ Cardinality(PRAB \X PPrevious)
              = Cardinality(PRAB) * Cardinality(PPrevious)
        BY <1>1, <1>2, FS_Product
  <1>. QED
        BY <1>3 DEF TerminalPayloadDomain

THEOREM TerminalDomainCardinality ==
  /\ IsFiniteSet(TerminalDomain)
  /\ Cardinality(TerminalDomain)
       = 4 * (Cardinality(PRAB) * Cardinality(PPrevious))
PROOF
  BY TerminalPhaseCodesCardinality,
     TerminalPayloadDomainCardinality,
     FS_Product
     DEF TerminalDomain

THEOREM TerminalTagInjective ==
  \A i \in TerminalPhaseCodes, j \in TerminalPhaseCodes :
    TerminalTag(i) = TerminalTag(j) => i = j
PROOF
  BY SMTT(120)
     DEF TerminalPhaseCodes, TerminalTag

THEOREM PendingCtorInjective ==
  \A x \in PendingDomain, y \in PendingDomain :
    PendingCtor(x) = PendingCtor(y) => x = y
PROOF
  BY SMTT(120)
     DEF PendingDomain, PendingCtor

THEOREM TerminalCtorInjective ==
  \A x \in TerminalDomain, y \in TerminalDomain :
    TerminalCtor(x) = TerminalCtor(y) => x = y
PROOF
  <1> SUFFICES
        ASSUME NEW x \in TerminalDomain,
               NEW y \in TerminalDomain,
               TerminalCtor(x) = TerminalCtor(y)
        PROVE x = y
       OBVIOUS
  <1>1. /\ x \in TerminalPhaseCodes \X TerminalPayloadDomain
         /\ y \in TerminalPhaseCodes \X TerminalPayloadDomain
       BY DEF TerminalDomain
  <1>2. /\ x[1] \in TerminalPhaseCodes
         /\ y[1] \in TerminalPhaseCodes
         /\ x[2] \in TerminalPayloadDomain
         /\ y[2] \in TerminalPayloadDomain
       BY SMTT(120), <1>1
  <1>3. TerminalTag(x[1]) = TerminalTag(y[1])
       BY SMTT(60)
          DEF TerminalCtor
  <1>4. x[1] = y[1]
       BY <1>2, <1>3, TerminalTagInjective
  <1>5. /\ x[2] \in PRAB \X PPrevious
         /\ y[2] \in PRAB \X PPrevious
       BY <1>2
          DEF TerminalPayloadDomain
  <1>6. /\ x[2][1] \in PRAB
         /\ y[2][1] \in PRAB
         /\ x[2][2] \in PPrevious
         /\ y[2][2] \in PPrevious
       BY SMTT(120), <1>5
  <1>7. /\ x[2][1] \in PAuthorities \X PBindings
         /\ y[2][1] \in PAuthorities \X PBindings
       BY SMTT(120), <1>6, ParametricRABSubsetProduct
  <1>8. /\ x[2][1][1] = y[2][1][1]
         /\ x[2][1][2] = y[2][1][2]
         /\ x[2][2] = y[2][2]
       BY SMTT(120)
          DEF TerminalCtor
  <1>9. /\ x[2][1] = <<x[2][1][1], x[2][1][2]>>
         /\ y[2][1] = <<y[2][1][1], y[2][1][2]>>
       BY <1>7, ProductPairReconstruction
  <1>10. x[2][1] = y[2][1]
       BY SMTT(120), <1>8, <1>9
  <1>11. /\ x[2] = <<x[2][1], x[2][2]>>
          /\ y[2] = <<y[2][1], y[2][2]>>
       BY <1>5, TerminalPayloadPairReconstruction
  <1>12. x[2] = y[2]
       BY SMTT(120), <1>8, <1>10, <1>11
  <1>13. /\ x = <<x[1], x[2]>>
          /\ y = <<y[1], y[2]>>
       BY <1>1, TerminalOuterPairReconstruction
  <1>. QED
       BY SMTT(120), <1>4, <1>12, <1>13

THEOREM PendingBijectionExists ==
  ExistsBijection(PendingDomain, PendingStatesP)
PROOF
  <1>. DEFINE f == [x \in PendingDomain |-> PendingCtor(x)]
  <1>1. f \in Bijection(PendingDomain, PendingStatesP)
        BY SMTT(180), PendingCtorInjective
           DEF f,
               PendingStatesP,
               Bijection,
               Injection,
               IsInjective,
               Surjection
  <1>. QED
        BY <1>1 DEF ExistsBijection

THEOREM TerminalBijectionExists ==
  ExistsBijection(TerminalDomain, TerminalStatesP)
PROOF
  <1>. DEFINE f == [x \in TerminalDomain |-> TerminalCtor(x)]
  <1>1. f \in Bijection(TerminalDomain, TerminalStatesP)
        BY SMTT(240), TerminalCtorInjective
           DEF f,
               TerminalStatesP,
               Bijection,
               Injection,
               IsInjective,
               Surjection
  <1>. QED
        BY <1>1 DEF ExistsBijection

THEOREM PendingStatesCardinality ==
  /\ IsFiniteSet(PendingStatesP)
  /\ Cardinality(PendingStatesP)
       = Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
PROOF
  <1>1. /\ IsFiniteSet(PendingStatesP)
         /\ Cardinality(PendingStatesP) = Cardinality(PendingDomain)
        BY PendingDomainCardinality,
           PendingBijectionExists,
           FS_Bijection
  <1>. QED
        BY <1>1, PendingDomainCardinality

THEOREM TerminalStatesCardinality ==
  /\ IsFiniteSet(TerminalStatesP)
  /\ Cardinality(TerminalStatesP)
       = 4 * (Cardinality(PRAB) * Cardinality(PPrevious))
PROOF
  <1>1. /\ IsFiniteSet(TerminalStatesP)
         /\ Cardinality(TerminalStatesP) = Cardinality(TerminalDomain)
        BY TerminalDomainCardinality,
           TerminalBijectionExists,
           FS_Bijection
  <1>. QED
        BY <1>1, TerminalDomainCardinality

THEOREM AbsentSingletonCardinality ==
  /\ IsFiniteSet({AbsentStateP})
  /\ Cardinality({AbsentStateP}) = 1
PROOF
  BY FS_Singleton

THEOREM AbsentPendingDisjoint ==
  {AbsentStateP} \cap PendingStatesP = {}
PROOF
  BY SMTT(120)
     DEF AbsentStateP,
         PendingStatesP,
         PendingCtor,
         PendingDomain

THEOREM AbsentTerminalDisjoint ==
  {AbsentStateP} \cap TerminalStatesP = {}
PROOF
  BY SMTT(180)
     DEF AbsentStateP,
         TerminalStatesP,
         TerminalCtor,
         TerminalDomain,
         TerminalPhaseCodes,
         TerminalTag

THEOREM PendingTerminalDisjoint ==
  PendingStatesP \cap TerminalStatesP = {}
PROOF
  BY SMTT(240)
     DEF PendingStatesP,
         PendingCtor,
         PendingDomain,
         TerminalStatesP,
         TerminalCtor,
         TerminalDomain,
         TerminalPhaseCodes,
         TerminalTag

THEOREM AbsentCardinalityType ==
  Cardinality({AbsentStateP}) \in Nat
PROOF
  BY AbsentSingletonCardinality,
     FS_CardinalityType

THEOREM PendingStatesCardinalityType ==
  Cardinality(PendingStatesP) \in Nat
PROOF
  BY PendingStatesCardinality,
     FS_CardinalityType

THEOREM TerminalStatesCardinalityType ==
  Cardinality(TerminalStatesP) \in Nat
PROOF
  BY TerminalStatesCardinality,
     FS_CardinalityType

THEOREM RecognizedBindingsCardinalityType ==
  Cardinality(PRecognizedBindings) \in Nat
PROOF
  BY RecognizedBindingsFinite,
     FS_CardinalityType

THEOREM RABCardinalityType ==
  Cardinality(PRAB) \in Nat
PROOF
  BY RABFinite,
     FS_CardinalityType

THEOREM PreviousCardinalityType ==
  Cardinality(PPrevious) \in Nat
PROOF
  BY ParametricPreviousFinite,
     FS_CardinalityType

THEOREM AbsentPendingUnionCardinality ==
  /\ IsFiniteSet({AbsentStateP} \cup PendingStatesP)
  /\ Cardinality({AbsentStateP} \cup PendingStatesP)
       = 1
         + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
PROOF
  <1>1. /\ IsFiniteSet({AbsentStateP})
         /\ Cardinality({AbsentStateP}) = 1
        BY AbsentSingletonCardinality
  <1>2. /\ IsFiniteSet(PendingStatesP)
         /\ Cardinality(PendingStatesP)
              = Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
        BY PendingStatesCardinality
  <1>3. /\ IsFiniteSet({AbsentStateP} \cup PendingStatesP)
         /\ Cardinality({AbsentStateP} \cup PendingStatesP)
              = Cardinality({AbsentStateP})
                + Cardinality(PendingStatesP)
                - Cardinality({AbsentStateP} \cap PendingStatesP)
        BY <1>1, <1>2, FS_Union
  <1>4. {AbsentStateP} \cap PendingStatesP = {}
        BY AbsentPendingDisjoint
  <1>5. Cardinality({AbsentStateP} \cap PendingStatesP) = 0
        BY <1>4, FS_EmptySet
  <1>6. Cardinality({AbsentStateP} \cup PendingStatesP)
          = Cardinality({AbsentStateP}) + Cardinality(PendingStatesP)
        BY SMTT(60), <1>3, <1>5,
           AbsentCardinalityType,
           PendingStatesCardinalityType
  <1>7. Cardinality({AbsentStateP} \cup PendingStatesP)
          = 1 + Cardinality(PendingStatesP)
        BY SMTT(60), <1>1, <1>6
  <1>8. Cardinality({AbsentStateP} \cup PendingStatesP)
          = 1
            + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
        BY SMTT(60), <1>2, <1>7
  <1>. QED
        BY <1>3, <1>8

THEOREM AbsentPendingUnionDisjointTerminal ==
  ({AbsentStateP} \cup PendingStatesP) \cap TerminalStatesP = {}
PROOF
  BY AbsentTerminalDisjoint,
     PendingTerminalDisjoint

THEOREM ExactLocalStatesFinite ==
  IsFiniteSet(ExactLocalStatesP)
PROOF
  <1>1. IsFiniteSet({AbsentStateP} \cup PendingStatesP)
        BY AbsentPendingUnionCardinality
  <1>2. IsFiniteSet(TerminalStatesP)
        BY TerminalStatesCardinality
  <1>3. IsFiniteSet(
          ({AbsentStateP} \cup PendingStatesP) \cup TerminalStatesP)
        BY <1>1, <1>2, FS_Union
  <1>. QED
        BY <1>3 DEF ExactLocalStatesP

THEOREM ParametricExactLocalStateCardinality ==
  Cardinality(ExactLocalStatesP) = ParametricExactCount
PROOF
  <1>1. /\ IsFiniteSet({AbsentStateP} \cup PendingStatesP)
         /\ Cardinality({AbsentStateP} \cup PendingStatesP)
              = 1
                + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
        BY AbsentPendingUnionCardinality
  <1>2. /\ IsFiniteSet(TerminalStatesP)
         /\ Cardinality(TerminalStatesP)
              = 4 * (Cardinality(PRAB) * Cardinality(PPrevious))
        BY TerminalStatesCardinality
  <1>3. /\ IsFiniteSet(
            ({AbsentStateP} \cup PendingStatesP) \cup TerminalStatesP)
         /\ Cardinality(
              ({AbsentStateP} \cup PendingStatesP) \cup TerminalStatesP)
              =
            Cardinality({AbsentStateP} \cup PendingStatesP)
              + Cardinality(TerminalStatesP)
              - Cardinality(
                  ({AbsentStateP} \cup PendingStatesP)
                    \cap TerminalStatesP)
        BY <1>1, <1>2, FS_Union
  <1>4. ({AbsentStateP} \cup PendingStatesP) \cap TerminalStatesP = {}
        BY AbsentPendingUnionDisjointTerminal
  <1>5. Cardinality(
          ({AbsentStateP} \cup PendingStatesP) \cap TerminalStatesP) = 0
        BY <1>4, FS_EmptySet
  <1>6. ExactLocalStatesP
          = ({AbsentStateP} \cup PendingStatesP) \cup TerminalStatesP
        BY DEF ExactLocalStatesP
  <1>7. Cardinality(ExactLocalStatesP)
          =
        Cardinality({AbsentStateP} \cup PendingStatesP)
          + Cardinality(TerminalStatesP)
        BY SMTT(60), <1>3, <1>5, <1>6,
           TerminalStatesCardinalityType
  <1>8. Cardinality(ExactLocalStatesP)
          =
        (1
          + Cardinality(PRecognizedBindings) * Cardinality(PPrevious))
          + Cardinality(TerminalStatesP)
        BY SMTT(60), <1>1, <1>7
  <1>9. Cardinality(ExactLocalStatesP)
          =
        (1
          + Cardinality(PRecognizedBindings) * Cardinality(PPrevious))
          + 4 * (Cardinality(PRAB) * Cardinality(PPrevious))
        BY SMTT(60), <1>2, <1>8
  <1>10. 4 * (Cardinality(PRAB) * Cardinality(PPrevious))
           =
         4 * Cardinality(PRAB) * Cardinality(PPrevious)
        BY SMTT(60),
           RABCardinalityType,
           PreviousCardinalityType
  <1>11. Cardinality(ExactLocalStatesP)
           =
         1
           + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
           + 4 * Cardinality(PRAB) * Cardinality(PPrevious)
        BY SMTT(60), <1>9, <1>10,
           RecognizedBindingsCardinalityType,
           RABCardinalityType,
           PreviousCardinalityType
  <1>12. ParametricExactCount
           =
         1
           + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
           + 4 * Cardinality(PRAB) * Cardinality(PPrevious)
        BY DEF ParametricExactCount
  <1>. QED
        BY <1>11, <1>12

THEOREM ParametricCardinalitySummary ==
  /\ IsFiniteSet(ExactLocalStatesP)
  /\ Cardinality(ExactLocalStatesP)
       =
       1
       + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
       + 4 * Cardinality(PRAB) * Cardinality(PPrevious)
PROOF
  BY ExactLocalStatesFinite,
     ParametricExactLocalStateCardinality
     DEF ParametricExactCount

=============================================================================
