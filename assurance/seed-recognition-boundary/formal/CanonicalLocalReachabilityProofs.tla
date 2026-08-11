---------------- MODULE CanonicalLocalReachabilityProofs ----------------
EXTENDS CanonicalLocalReachability, TLAPS

ASSUME CanonicalLinkAssumptions

(***************************************************************************)
(* Assumption projections and canonical instance side conditions.          *)
(***************************************************************************)

THEOREM LinkParametricAssumptions ==
  ParametricAssumptions
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkBindingsNonEmpty ==
  PBindings # {}
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkAuthoritiesNonEmpty ==
  PAuthorities # {}
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkPreviousNonEmpty ==
  PPrevious # {}
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkNoCommitmentInPrevious ==
  PNoCommitmentValue \in PPrevious
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkNoAuthorityOutsideAuthorities ==
  PNoAuthority \notin PAuthorities
PROOF
  BY CanonicalLinkAssumptions
     DEF CanonicalLinkAssumptions

THEOREM LinkRABSubset ==
  PRAB \subseteq (PAuthorities \X PBindings)
PROOF
  BY LinkParametricAssumptions
     DEF ParametricAssumptions

THEOREM RABPairTyping ==
  \A a, b :
    <<a, b>> \in PRAB
      =>
    /\ a \in PAuthorities
    /\ b \in PBindings
PROOF
  BY SMTT(120), LinkRABSubset

THEOREM RABPairReconstruction ==
  \A p \in PRAB :
    p = <<p[1], p[2]>>
PROOF
  BY SMTT(120), LinkRABSubset

THEOREM PendingCtorProjection ==
  \A x \in PendingDomain :
    /\ PendingCtor(x).phase = "PENDING"
    /\ PendingCtor(x).binding = x[1]
    /\ PendingCtor(x).previous = x[2]
    /\ PendingCtor(x).authority = PNoAuthority
PROOF
  BY DEF PendingCtor

THEOREM RecognizedBindingTyped ==
  \A b \in PRecognizedBindings :
    b \in PBindings
PROOF
  BY DEF PRecognizedBindings

THEOREM RABPairImpliesRecognizedBinding ==
  \A a, b :
    <<a, b>> \in PRAB
      =>
    b \in PRecognizedBindings
PROOF
  BY SMTT(120), RABPairTyping
     DEF PRecognizedBindings

THEOREM CanonicalPreviousDomainIdentity ==
  (PPrevious \ {PNoCommitmentValue}) \cup {PNoCommitmentValue}
    = PPrevious
PROOF
  BY SMTT(60), LinkNoCommitmentInPrevious

THEOREM CanonicalRecognizedPreviousSubset ==
  PPrevious \ {PNoCommitmentValue}
    \subseteq PPrevious \ {PNoCommitmentValue}
PROOF
  OBVIOUS

THEOREM CanonicalNoCommitmentOutsideTerminal ==
  PNoCommitmentValue \notin (PPrevious \ {PNoCommitmentValue})
PROOF
  BY SMTT(60)

(***************************************************************************)
(* Map-level definitions are exactly the instantiated canonical actions.   *)
(***************************************************************************)

THEOREM CanonicalRegisterMatchesMapRegister ==
  \A b \in PBindings,
     a \in PAuthorities,
     previous \in PPrevious :
    Canonical!PhaseRegister(PResolutionId, b, a, previous)
      <=> MapRegister(linkPhaseMeta, linkPhaseMeta', b, a, previous)
PROOF
  BY SMTT(180), LinkNoCommitmentInPrevious
     DEF Canonical!PhaseRegister,
         Canonical!PhaseRequests,
         MapRegister,
         MRequests

THEOREM CanonicalSubmitMatchesMapSubmit ==
  \A b \in PBindings,
     a \in PAuthorities,
     value \in {"ALLOW", "BLOCK"} :
    Canonical!PhaseSubmit(PResolutionId, b, a, value)
      <=> MapSubmit(linkPhaseMeta, linkPhaseMeta', b, a, value)
PROOF
  BY SMTT(180)
     DEF Canonical!PhaseSubmit,
         Canonical!PhaseRequests,
         Canonical!PhaseTag,
         Canonical!PhaseBinding,
         Canonical!PhasePrevious,
         Canonical!TerminalResolutions,
         MapSubmit,
         MRequests,
         MTag,
         MBinding,
         MPrevious

THEOREM CanonicalConflictMatchesMapConflict ==
  Canonical!PhaseObserveConflict(PResolutionId)
    <=> MapObserveConflict(linkPhaseMeta, linkPhaseMeta')
PROOF
  BY SMTT(180)
     DEF Canonical!PhaseObserveConflict,
         Canonical!PhaseRequests,
         Canonical!PhaseTag,
         Canonical!PhaseBinding,
         Canonical!PhasePrevious,
         Canonical!PhaseAuthority,
         MapObserveConflict,
         MRequests,
         MTag,
         MBinding,
         MPrevious,
         MAuthority

THEOREM CanonicalNextMatchesMapNext ==
  Canonical!PhaseNext
    <=> MapNext(linkPhaseMeta, linkPhaseMeta')
PROOF
  BY SMTT(300),
     CanonicalPreviousDomainIdentity,
     CanonicalRegisterMatchesMapRegister,
     CanonicalSubmitMatchesMapSubmit,
     CanonicalConflictMatchesMapConflict
     DEF Canonical!PhaseNext,
         Canonical!PhaseRecognizedSeedTransition,
         Canonical!PhaseRecognizedEnvironmentTransition,
         Canonical!TerminalResolutions,
         MapNext

THEOREM CanonicalInitMatchesAbsentMap ==
  Canonical!PhaseInit
    <=> linkPhaseMeta = LocalMap(AbsentStateP)
PROOF
  BY DEF Canonical!PhaseInit,
         LocalMap,
         AbsentStateP

THEOREM CanonicalNextMatchesLocalStepUnderEncoding ==
  \A s \in ExactLocalStatesP,
     t \in ExactLocalStatesP :
    /\ linkPhaseMeta = LocalMap(s)
    /\ linkPhaseMeta' = LocalMap(t)
    =>
    (Canonical!PhaseNext <=> LocalStep(s, t))
PROOF
  BY CanonicalNextMatchesMapNext
     DEF LocalStep

(***************************************************************************)
(* Proof-local constructor algebra.                                        *)
(***************************************************************************)

PendingRecord(b, previous) ==
  [phase |-> "PENDING",
   binding |-> b,
   previous |-> previous,
   authority |-> PNoAuthority]

TerminalRecord(phase, b, previous, a) ==
  [phase |-> phase,
   binding |-> b,
   previous |-> previous,
   authority |-> a]

TerminalPhaseCodeOf(phase) ==
  IF phase = "ALLOW"
  THEN 1
  ELSE IF phase = "BLOCK"
       THEN 2
       ELSE IF phase = "INVALIDATED_ALLOW"
            THEN 3
            ELSE 4

TerminalIndex(phase, b, previous, a) ==
  <<TerminalPhaseCodeOf(phase), <<<<a, b>>, previous>>>>

THEOREM PendingStateHasCtorWitness ==
  \A s \in PendingStatesP :
    \E x \in PendingDomain : s = PendingCtor(x)
PROOF
  BY DEF PendingStatesP

THEOREM TerminalStateHasCtorWitness ==
  \A s \in TerminalStatesP :
    \E x \in TerminalDomain : s = TerminalCtor(x)
PROOF
  BY DEF TerminalStatesP

THEOREM PendingRecordCtorIdentity ==
  \A b \in PRecognizedBindings,
     previous \in PPrevious :
    PendingCtor(<<b, previous>>) = PendingRecord(b, previous)
PROOF
  BY DEF PendingCtor, PendingRecord

THEOREM PendingRecordInPendingStates ==
  \A b \in PRecognizedBindings,
     previous \in PPrevious :
    PendingRecord(b, previous) \in PendingStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW b \in PRecognizedBindings,
               NEW previous \in PPrevious
        PROVE PendingRecord(b, previous) \in PendingStatesP
       OBVIOUS
  <1>1. <<b, previous>> \in PendingDomain
        BY DEF PendingDomain
  <1>2. PendingCtor(<<b, previous>>) = PendingRecord(b, previous)
        BY PendingRecordCtorIdentity
  <1>. QED
        BY SMTT(60), <1>1, <1>2
           DEF PendingStatesP

THEOREM TerminalPhaseCodeRoundTrip ==
  \A phase \in
       {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"} :
    /\ TerminalPhaseCodeOf(phase) \in TerminalPhaseCodes
    /\ TerminalTag(TerminalPhaseCodeOf(phase)) = phase
PROOF
  BY SMTT(120)
     DEF TerminalPhaseCodeOf,
         TerminalPhaseCodes,
         TerminalTag

THEOREM TerminalIndexInDomain ==
  \A phase \in
       {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"} :
    \A b, a :
      \A previous \in PPrevious :
        <<a, b>> \in PRAB
          =>
        TerminalIndex(phase, b, previous, a) \in TerminalDomain
PROOF
  BY SMTT(120), TerminalPhaseCodeRoundTrip
     DEF TerminalIndex,
         TerminalDomain,
         TerminalPayloadDomain

THEOREM TerminalRecordCtorIdentity ==
  \A phase \in
       {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"} :
    \A b, a :
      \A previous \in PPrevious :
        <<a, b>> \in PRAB
          =>
        TerminalCtor(TerminalIndex(phase, b, previous, a))
          = TerminalRecord(phase, b, previous, a)
PROOF
  BY SMTT(120), TerminalPhaseCodeRoundTrip
     DEF TerminalCtor,
         TerminalIndex,
         TerminalRecord

THEOREM TerminalRecordInTerminalStates ==
  \A phase \in
       {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"} :
    \A b, a :
      \A previous \in PPrevious :
        <<a, b>> \in PRAB
          =>
        TerminalRecord(phase, b, previous, a) \in TerminalStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW phase \in
                 {"ALLOW", "BLOCK",
                  "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"},
               NEW b,
               NEW previous \in PPrevious,
               NEW a,
               <<a, b>> \in PRAB
        PROVE TerminalRecord(phase, b, previous, a) \in TerminalStatesP
       OBVIOUS
  <1>1. TerminalIndex(phase, b, previous, a) \in TerminalDomain
        BY TerminalIndexInDomain
  <1>2. TerminalCtor(TerminalIndex(phase, b, previous, a))
          = TerminalRecord(phase, b, previous, a)
        BY TerminalRecordCtorIdentity
  <1>. QED
        BY SMTT(60), <1>1, <1>2
           DEF TerminalStatesP

THEOREM LocalMapOfPendingRecord ==
  \A b, previous :
    LocalMap(PendingRecord(b, previous))
      =
    [r \in {PResolutionId} |-> PendingRecord(b, previous)]
PROOF
  BY DEF LocalMap, PendingRecord

THEOREM LocalMapOfTerminalRecord ==
  \A phase \in
       {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"} :
    \A b, previous, a :
      LocalMap(TerminalRecord(phase, b, previous, a))
        =
      [r \in {PResolutionId} |-> TerminalRecord(phase, b, previous, a)]
PROOF
  BY DEF LocalMap, TerminalRecord

THEOREM LocalMapEqualsNonAbsentImpliesStateEqual ==
  \A t, u :
    /\ u.phase # "ABSENT"
    /\ LocalMap(t) = LocalMap(u)
    => t = u
PROOF
  BY SMTT(180)
     DEF LocalMap

THEOREM TerminalCtorProjection ==
  \A x \in TerminalDomain :
    /\ TerminalCtor(x).phase = TerminalTag(x[1])
    /\ TerminalCtor(x).binding = x[2][1][2]
    /\ TerminalCtor(x).previous = x[2][2]
    /\ TerminalCtor(x).authority = x[2][1][1]
PROOF
  BY DEF TerminalCtor

THEOREM TerminalStateEqualsRecord ==
  \A s \in TerminalStatesP :
    s = TerminalRecord(s.phase, s.binding, s.previous, s.authority)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in TerminalStatesP
        PROVE
          s =
          TerminalRecord(
            s.phase,
            s.binding,
            s.previous,
            s.authority)
       OBVIOUS
  <1>1. PICK x \in TerminalDomain : s = TerminalCtor(x)
        BY TerminalStateHasCtorWitness
  <1>2. /\ s.phase = TerminalTag(x[1])
         /\ s.binding = x[2][1][2]
         /\ s.previous = x[2][2]
         /\ s.authority = x[2][1][1]
        BY SMTT(120), <1>1, TerminalCtorProjection
  <1>3.
        TerminalRecord(
          s.phase,
          s.binding,
          s.previous,
          s.authority)
          =
        TerminalCtor(x)
        BY SMTT(120), <1>2
           DEF TerminalRecord, TerminalCtor
  <1>. QED
        BY <1>1, <1>3

THEOREM ActiveTerminalSubsetExact ==
  ActiveTerminalStatesP \subseteq ExactLocalStatesP
PROOF
  BY DEF ActiveTerminalStatesP, ExactLocalStatesP

THEOREM InvalidatedTerminalSubsetExact ==
  InvalidatedTerminalStatesP \subseteq ExactLocalStatesP
PROOF
  BY DEF InvalidatedTerminalStatesP, ExactLocalStatesP

(***************************************************************************)
(* Basic exact-state decomposition.                                        *)
(***************************************************************************)

THEOREM TerminalStatesPartition ==
  TerminalStatesP
    = ActiveTerminalStatesP \cup InvalidatedTerminalStatesP
PROOF
  BY SMTT(180)
     DEF ActiveTerminalStatesP,
         InvalidatedTerminalStatesP,
         TerminalStatesP,
         TerminalCtor,
         TerminalDomain,
         TerminalPhaseCodes,
         TerminalTag

THEOREM ExactStatesFourWayPartition ==
  ExactLocalStatesP
    =
  {AbsentStateP}
    \cup PendingStatesP
    \cup ActiveTerminalStatesP
    \cup InvalidatedTerminalStatesP
PROOF
  BY TerminalStatesPartition
     DEF ExactLocalStatesP

THEOREM AbsentIsExact ==
  AbsentStateP \in ExactLocalStatesP
PROOF
  BY DEF ExactLocalStatesP

THEOREM RecognizedBindingHasAuthority ==
  \A b \in PRecognizedBindings :
    \E a \in PAuthorities : <<a, b>> \in PRAB
PROOF
  BY DEF PRecognizedBindings

THEOREM PendingStatePayload ==
  \A s \in PendingStatesP :
    /\ s.phase = "PENDING"
    /\ s.binding \in PRecognizedBindings
    /\ s.previous \in PPrevious
    /\ s.authority = PNoAuthority
PROOF
  <1> SUFFICES
        ASSUME NEW s \in PendingStatesP
        PROVE /\ s.phase = "PENDING"
              /\ s.binding \in PRecognizedBindings
              /\ s.previous \in PPrevious
              /\ s.authority = PNoAuthority
       OBVIOUS
  <1>1. PICK x \in PendingDomain : s = PendingCtor(x)
        BY PendingStateHasCtorWitness
  <1>2. /\ x[1] \in PRecognizedBindings
         /\ x[2] \in PPrevious
        BY SMTT(120), <1>1
           DEF PendingDomain
  <1>. QED
        BY SMTT(120), <1>1, <1>2
           DEF PendingCtor

THEOREM PendingStateEqualsRecord ==
  \A s \in PendingStatesP :
    s = PendingRecord(s.binding, s.previous)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in PendingStatesP
        PROVE s = PendingRecord(s.binding, s.previous)
       OBVIOUS
  <1>1. PICK x \in PendingDomain : s = PendingCtor(x)
        BY PendingStateHasCtorWitness
  <1>2. /\ s.binding = x[1]
         /\ s.previous = x[2]
        BY SMTT(120), <1>1, PendingCtorProjection
  <1>3. PendingRecord(s.binding, s.previous) = PendingCtor(x)
        BY SMTT(120), <1>2
           DEF PendingRecord, PendingCtor
  <1>. QED
        BY <1>1, <1>3

THEOREM TerminalStatePayload ==
  \A s \in TerminalStatesP :
    /\ s.phase \in
         {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
    /\ <<s.authority, s.binding>> \in PRAB
    /\ s.previous \in PPrevious
PROOF
  <1> SUFFICES
        ASSUME NEW s \in TerminalStatesP
        PROVE
          /\ s.phase \in
               {"ALLOW", "BLOCK",
                "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
          /\ <<s.authority, s.binding>> \in PRAB
          /\ s.previous \in PPrevious
       OBVIOUS
  <1>1. PICK x \in TerminalDomain : s = TerminalCtor(x)
        BY TerminalStateHasCtorWitness
  <1>2. /\ x[1] \in TerminalPhaseCodes
         /\ x[2] \in TerminalPayloadDomain
        BY SMTT(120), <1>1
           DEF TerminalDomain
  <1>3. /\ x[2][1] \in PRAB
         /\ x[2][2] \in PPrevious
        BY SMTT(120), <1>2
           DEF TerminalPayloadDomain
  <1>4. x[2][1] = <<x[2][1][1], x[2][1][2]>>
        BY <1>3, RABPairReconstruction
  <1>5. TerminalTag(x[1]) \in
          {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
        BY SMTT(120), <1>2
           DEF TerminalPhaseCodes, TerminalTag
  <1>6. /\ s.phase = TerminalTag(x[1])
         /\ s.binding = x[2][1][2]
         /\ s.previous = x[2][2]
         /\ s.authority = x[2][1][1]
        BY SMTT(120), <1>1, TerminalCtorProjection
  <1>7. <<s.authority, s.binding>> = x[2][1]
        BY SMTT(120), <1>4, <1>6
  <1>. QED
        BY SMTT(120), <1>3, <1>5, <1>6, <1>7

THEOREM ActiveTerminalStatePayload ==
  \A s \in ActiveTerminalStatesP :
    /\ s.phase \in {"ALLOW", "BLOCK"}
    /\ <<s.authority, s.binding>> \in PRAB
    /\ s.previous \in PPrevious
PROOF
  BY SMTT(120), TerminalStatePayload
     DEF ActiveTerminalStatesP

THEOREM InvalidatedTerminalStatePayload ==
  \A s \in InvalidatedTerminalStatesP :
    /\ s.phase \in {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
    /\ <<s.authority, s.binding>> \in PRAB
    /\ s.previous \in PPrevious
PROOF
  BY SMTT(120), TerminalStatePayload
     DEF InvalidatedTerminalStatesP

(***************************************************************************)
(* Constructive reachability: exact state -> canonical-local path <= 3.    *)
(***************************************************************************)

THEOREM LocalMapOfAbsent ==
  LocalMap(AbsentStateP) = [r \in {} |-> r]
PROOF
  BY DEF LocalMap, AbsentStateP

THEOREM EmptyLocalRequests ==
  MRequests(LocalMap(AbsentStateP)) = {}
PROOF
  BY LocalMapOfAbsent
     DEF MRequests

THEOREM MapRegisterImpliesMapNext ==
  \A m, n, b, a, previous :
    /\ b \in PBindings
    /\ a \in PAuthorities
    /\ previous \in PPrevious
    /\ MapRegister(m, n, b, a, previous)
    => MapNext(m, n)
PROOF
  BY DEF MapNext

THEOREM LocalMapNextDecomposition ==
  \A s, t :
    MapNext(LocalMap(s), LocalMap(t))
      =>
    \/ \E b \in PBindings,
          a \in PAuthorities,
          previous \in PPrevious :
         MapRegister(LocalMap(s), LocalMap(t), b, a, previous)
    \/ \E b \in PBindings,
          a \in PAuthorities,
          value \in {"ALLOW", "BLOCK"} :
         MapSubmit(LocalMap(s), LocalMap(t), b, a, value)
    \/ MapObserveConflict(LocalMap(s), LocalMap(t))
PROOF
  BY DEF MapNext

THEOREM MapRegisterBuildsPendingRecord ==
  \A b \in PRecognizedBindings,
     previous \in PPrevious,
     a \in PAuthorities :
    <<a, b>> \in PRAB
      =>
    MapRegister(
      LocalMap(AbsentStateP),
      LocalMap(PendingRecord(b, previous)),
      b,
      a,
      previous)
PROOF
  <1> SUFFICES
        ASSUME NEW b \in PRecognizedBindings,
               NEW previous \in PPrevious,
               NEW a \in PAuthorities,
               <<a, b>> \in PRAB
        PROVE
          MapRegister(
            LocalMap(AbsentStateP),
            LocalMap(PendingRecord(b, previous)),
            b,
            a,
            previous)
       OBVIOUS
  <1>1. b \in PBindings
        BY RecognizedBindingTyped
  <1>2. MRequests(LocalMap(AbsentStateP)) = {}
        BY EmptyLocalRequests
  <1>3. MRequests(LocalMap(AbsentStateP)) \cup {PResolutionId}
          = {PResolutionId}
        BY SMTT(60), <1>2
  <1>4. LocalMap(PendingRecord(b, previous))
          =
        [r \in {PResolutionId} |-> PendingRecord(b, previous)]
        BY LocalMapOfPendingRecord
  <1>5.
        [x \in {PResolutionId} |->
           IF x = PResolutionId
           THEN [phase |-> "PENDING",
                 binding |-> b,
                 previous |-> previous,
                 authority |-> PNoAuthority]
           ELSE LocalMap(AbsentStateP)[x]]
          =
        [r \in {PResolutionId} |-> PendingRecord(b, previous)]
        BY SMTT(180)
           DEF PendingRecord
  <1>6.
        [x \in MRequests(LocalMap(AbsentStateP)) \cup {PResolutionId} |->
           IF x = PResolutionId
           THEN [phase |-> "PENDING",
                 binding |-> b,
                 previous |-> previous,
                 authority |-> PNoAuthority]
           ELSE LocalMap(AbsentStateP)[x]]
          =
        LocalMap(PendingRecord(b, previous))
        BY <1>3, <1>4, <1>5
  <1>. QED
        BY SMTT(120), <1>1, <1>2, <1>6
           DEF MapRegister

THEOREM MapSubmitBuildsTerminalRecord ==
  \A b, a :
    \A previous \in PPrevious,
       value \in {"ALLOW", "BLOCK"} :
      <<a, b>> \in PRAB
        =>
      MapSubmit(
        LocalMap(PendingRecord(b, previous)),
        LocalMap(TerminalRecord(value, b, previous, a)),
        b,
        a,
        value)
PROOF
  BY SMTT(300), RABPairTyping
     DEF MapSubmit,
         LocalMap,
         PendingRecord,
         TerminalRecord,
         MRequests,
         MTag,
         MBinding,
         MPrevious

THEOREM MapConflictBuildsInvalidatedRecord ==
  \A phase \in {"ALLOW", "BLOCK"} :
    \A b, a :
      \A previous :
        MapObserveConflict(
          LocalMap(TerminalRecord(phase, b, previous, a)),
          LocalMap(
            TerminalRecord(
              IF phase = "ALLOW"
              THEN "INVALIDATED_ALLOW"
              ELSE "INVALIDATED_BLOCK",
              b,
              previous,
              a)))
PROOF
  BY SMTT(300)
     DEF MapObserveConflict,
         LocalMap,
         TerminalRecord,
         MRequests,
         MTag,
         MBinding,
         MPrevious,
         MAuthority

THEOREM MapNextDecomposition ==
  \A m, n :
    MapNext(m, n)
      =>
    \/ \E b \in PBindings,
          a \in PAuthorities,
          previous \in PPrevious :
         MapRegister(m, n, b, a, previous)
    \/ \E b \in PBindings,
          a \in PAuthorities,
          value \in {"ALLOW", "BLOCK"} :
         MapSubmit(m, n, b, a, value)
    \/ MapObserveConflict(m, n)
PROOF
  BY DEF MapNext

THEOREM EveryPendingStateReachableOne ==
  \A s \in PendingStatesP :
    LocalStep(AbsentStateP, s)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in PendingStatesP
        PROVE LocalStep(AbsentStateP, s)
       OBVIOUS
  <1>1. /\ s.phase = "PENDING"
         /\ s.binding \in PRecognizedBindings
         /\ s.previous \in PPrevious
         /\ s.authority = PNoAuthority
        BY PendingStatePayload
  <1>2. PICK a \in PAuthorities :
          <<a, s.binding>> \in PRAB
        BY <1>1, RecognizedBindingHasAuthority
  <1>3. s.binding \in PBindings
        BY <1>1, RecognizedBindingTyped
  <1>4. s = PendingRecord(s.binding, s.previous)
        BY PendingStateEqualsRecord
  <1>5. MapRegister(
          LocalMap(AbsentStateP),
          LocalMap(PendingRecord(s.binding, s.previous)),
          s.binding,
          a,
          s.previous)
        BY <1>1, <1>2, MapRegisterBuildsPendingRecord
  <1>6. MapRegister(
          LocalMap(AbsentStateP),
          LocalMap(s),
          s.binding,
          a,
          s.previous)
        BY <1>4, <1>5
  <1>7. MapNext(LocalMap(AbsentStateP), LocalMap(s))
        BY <1>1, <1>2, <1>3, <1>6,
           MapRegisterImpliesMapNext
  <1>. QED
        BY <1>7 DEF LocalStep

THEOREM ActivePendingPredecessorExact ==
  \A s \in ActiveTerminalStatesP :
    PendingPredecessor(s) \in PendingStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in ActiveTerminalStatesP
        PROVE PendingPredecessor(s) \in PendingStatesP
       OBVIOUS
  <1>1. /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY ActiveTerminalStatePayload
  <1>2. s.binding \in PRecognizedBindings
        BY <1>1, RABPairImpliesRecognizedBinding
  <1>3. PendingRecord(s.binding, s.previous) \in PendingStatesP
        BY <1>1, <1>2, PendingRecordInPendingStates
  <1>4. PendingPredecessor(s)
          = PendingRecord(s.binding, s.previous)
        BY DEF PendingPredecessor, PendingRecord
  <1>. QED
        BY <1>3, <1>4

THEOREM EveryActiveTerminalStateFromPending ==
  \A s \in ActiveTerminalStatesP :
    LocalStep(PendingPredecessor(s), s)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in ActiveTerminalStatesP
        PROVE LocalStep(PendingPredecessor(s), s)
       OBVIOUS
  <1>1. /\ s.phase \in {"ALLOW", "BLOCK"}
         /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY ActiveTerminalStatePayload
  <1>2. /\ s.authority \in PAuthorities
         /\ s.binding \in PBindings
        BY <1>1, RABPairTyping
  <1>3. PendingPredecessor(s)
          = PendingRecord(s.binding, s.previous)
        BY DEF PendingPredecessor, PendingRecord
  <1>4. s = TerminalRecord(
          s.phase,
          s.binding,
          s.previous,
          s.authority)
        BY ActiveTerminalStatePayload,
           TerminalStateEqualsRecord
           DEF ActiveTerminalStatesP
  <1>5. MapSubmit(
          LocalMap(PendingRecord(s.binding, s.previous)),
          LocalMap(
            TerminalRecord(
              s.phase,
              s.binding,
              s.previous,
              s.authority)),
          s.binding,
          s.authority,
          s.phase)
        BY <1>1, MapSubmitBuildsTerminalRecord
  <1>6. MapSubmit(
          LocalMap(PendingPredecessor(s)),
          LocalMap(s),
          s.binding,
          s.authority,
          s.phase)
        BY <1>3, <1>4, <1>5
  <1>. QED
        BY SMTT(120), <1>1, <1>2, <1>6
           DEF LocalStep, MapNext

THEOREM EveryActiveTerminalStateReachableTwo ==
  \A s \in ActiveTerminalStatesP :
    \E p \in ExactLocalStatesP :
      /\ LocalStep(AbsentStateP, p)
      /\ LocalStep(p, s)
PROOF
  BY SMTT(180),
     ActivePendingPredecessorExact,
     EveryPendingStateReachableOne,
     EveryActiveTerminalStateFromPending
     DEF ExactLocalStatesP

THEOREM InvalidatedPendingPredecessorExact ==
  \A s \in InvalidatedTerminalStatesP :
    PendingPredecessor(s) \in PendingStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in InvalidatedTerminalStatesP
        PROVE PendingPredecessor(s) \in PendingStatesP
       OBVIOUS
  <1>1. /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY InvalidatedTerminalStatePayload
  <1>2. s.binding \in PRecognizedBindings
        BY <1>1, RABPairImpliesRecognizedBinding
  <1>3. PendingRecord(s.binding, s.previous) \in PendingStatesP
        BY <1>1, <1>2, PendingRecordInPendingStates
  <1>4. PendingPredecessor(s)
          = PendingRecord(s.binding, s.previous)
        BY DEF PendingPredecessor, PendingRecord
  <1>. QED
        BY <1>3, <1>4

THEOREM InvalidatedActivePredecessorExact ==
  \A s \in InvalidatedTerminalStatesP :
    ActivePredecessor(s) \in ActiveTerminalStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in InvalidatedTerminalStatesP
        PROVE ActivePredecessor(s) \in ActiveTerminalStatesP
       OBVIOUS
  <1>1. /\ s.phase \in {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
         /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY InvalidatedTerminalStatePayload
  <1>2. ActivePredecessor(s).phase \in {"ALLOW", "BLOCK"}
        BY SMTT(60), <1>1
           DEF ActivePredecessor
  <1>3. TerminalRecord(
          ActivePredecessor(s).phase,
          s.binding,
          s.previous,
          s.authority) \in TerminalStatesP
        BY <1>1, <1>2, TerminalRecordInTerminalStates
  <1>4. ActivePredecessor(s)
          =
        TerminalRecord(
          ActivePredecessor(s).phase,
          s.binding,
          s.previous,
          s.authority)
        BY DEF ActivePredecessor, TerminalRecord
  <1>5. ActivePredecessor(s) \in TerminalStatesP
        BY <1>3, <1>4
  <1>. QED
        BY SMTT(60), <1>2, <1>5
           DEF ActiveTerminalStatesP

THEOREM InvalidatedActivePredecessorFromPending ==
  \A s \in InvalidatedTerminalStatesP :
    LocalStep(PendingPredecessor(s), ActivePredecessor(s))
PROOF
  <1> SUFFICES
        ASSUME NEW s \in InvalidatedTerminalStatesP
        PROVE LocalStep(PendingPredecessor(s), ActivePredecessor(s))
       OBVIOUS
  <1>1. ActivePredecessor(s) \in ActiveTerminalStatesP
        BY InvalidatedActivePredecessorExact
  <1>2. LocalStep(
          PendingPredecessor(ActivePredecessor(s)),
          ActivePredecessor(s))
        BY <1>1, EveryActiveTerminalStateFromPending
  <1>3. PendingPredecessor(ActivePredecessor(s))
          = PendingPredecessor(s)
        BY DEF PendingPredecessor, ActivePredecessor
  <1>. QED
        BY <1>2, <1>3

THEOREM EveryInvalidatedStateFromActive ==
  \A s \in InvalidatedTerminalStatesP :
    LocalStep(ActivePredecessor(s), s)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in InvalidatedTerminalStatesP
        PROVE LocalStep(ActivePredecessor(s), s)
       OBVIOUS
  <1>1. /\ s.phase \in {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
         /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY InvalidatedTerminalStatePayload
  <1>2. ActivePredecessor(s).phase \in {"ALLOW", "BLOCK"}
        BY SMTT(60), <1>1
           DEF ActivePredecessor
  <1>3. ActivePredecessor(s)
          =
        TerminalRecord(
          ActivePredecessor(s).phase,
          s.binding,
          s.previous,
          s.authority)
        BY DEF ActivePredecessor, TerminalRecord
  <1>4.
        (IF ActivePredecessor(s).phase = "ALLOW"
         THEN "INVALIDATED_ALLOW"
         ELSE "INVALIDATED_BLOCK")
          = s.phase
        BY SMTT(120), <1>1
           DEF ActivePredecessor
  <1>5. s =
        TerminalRecord(
          s.phase,
          s.binding,
          s.previous,
          s.authority)
        BY InvalidatedTerminalStatePayload,
           TerminalStateEqualsRecord
           DEF InvalidatedTerminalStatesP
  <1>6. MapObserveConflict(
          LocalMap(
            TerminalRecord(
              ActivePredecessor(s).phase,
              s.binding,
              s.previous,
              s.authority)),
          LocalMap(
            TerminalRecord(
              IF ActivePredecessor(s).phase = "ALLOW"
              THEN "INVALIDATED_ALLOW"
              ELSE "INVALIDATED_BLOCK",
              s.binding,
              s.previous,
              s.authority)))
        BY <1>2, MapConflictBuildsInvalidatedRecord
  <1>7. MapObserveConflict(
          LocalMap(ActivePredecessor(s)),
          LocalMap(s))
        BY <1>3, <1>4, <1>5, <1>6
  <1>. QED
        BY <1>7
           DEF LocalStep, MapNext

THEOREM EveryInvalidatedStateReachableThree ==
  \A s \in InvalidatedTerminalStatesP :
    \E p \in ExactLocalStatesP,
       q \in ExactLocalStatesP :
      /\ LocalStep(AbsentStateP, p)
      /\ LocalStep(p, q)
      /\ LocalStep(q, s)
PROOF
  <1> SUFFICES
        ASSUME NEW s \in InvalidatedTerminalStatesP
        PROVE
          \E p \in ExactLocalStatesP,
             q \in ExactLocalStatesP :
            /\ LocalStep(AbsentStateP, p)
            /\ LocalStep(p, q)
            /\ LocalStep(q, s)
       OBVIOUS
  <1>1. PendingPredecessor(s) \in ExactLocalStatesP
        BY InvalidatedPendingPredecessorExact
           DEF ExactLocalStatesP
  <1>2. ActivePredecessor(s) \in ExactLocalStatesP
        BY InvalidatedActivePredecessorExact,
           ActiveTerminalSubsetExact
  <1>3. LocalStep(AbsentStateP, PendingPredecessor(s))
        BY InvalidatedPendingPredecessorExact,
           EveryPendingStateReachableOne
  <1>4. LocalStep(
          PendingPredecessor(s),
          ActivePredecessor(s))
        BY InvalidatedActivePredecessorFromPending
  <1>5. LocalStep(ActivePredecessor(s), s)
        BY EveryInvalidatedStateFromActive
  <1>. QED
        BY SMTT(120), <1>1, <1>2, <1>3, <1>4, <1>5

THEOREM EveryExactStateReachableWithinThree ==
  \A s \in ExactLocalStatesP :
    ReachableWithinThree(s)
PROOF
  BY SMTT(300),
     ExactStatesFourWayPartition,
     EveryPendingStateReachableOne,
     EveryActiveTerminalStateReachableTwo,
     EveryInvalidatedStateReachableThree
     DEF ReachableWithinThree

THEOREM ExactPendingPhaseImpliesPendingState ==
  \A s \in ExactLocalStatesP :
    s.phase = "PENDING" => s \in PendingStatesP
PROOF
  BY SMTT(180), TerminalStatePayload
     DEF ExactLocalStatesP,
         AbsentStateP,
         PendingStatesP

THEOREM ExactActivePhaseImpliesActiveState ==
  \A s \in ExactLocalStatesP :
    s.phase \in {"ALLOW", "BLOCK"} => s \in ActiveTerminalStatesP
PROOF
  BY SMTT(240),
     ExactStatesFourWayPartition,
     PendingStatePayload,
     InvalidatedTerminalStatePayload
     DEF AbsentStateP

THEOREM MapRegisterFromExactProducesPending ==
  \A s \in ExactLocalStatesP :
    \A t :
      \A b \in PBindings,
         a \in PAuthorities,
         previous \in PPrevious :
        MapRegister(LocalMap(s), LocalMap(t), b, a, previous)
          => t \in PendingStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in ExactLocalStatesP,
               NEW t,
               NEW b \in PBindings,
               NEW a \in PAuthorities,
               NEW previous \in PPrevious,
               MapRegister(LocalMap(s), LocalMap(t), b, a, previous)
        PROVE t \in PendingStatesP
       OBVIOUS
  <1>1. <<a, b>> \in PRAB
        BY DEF MapRegister
  <1>2. b \in PRecognizedBindings
        BY SMTT(60), <1>1
           DEF PRecognizedBindings
  <1>3. PendingRecord(b, previous) \in PendingStatesP
        BY <1>2, PendingRecordInPendingStates
  <1>4. LocalMap(t) = LocalMap(PendingRecord(b, previous))
        BY SMTT(180)
           DEF MapRegister,
               LocalMap,
               PendingRecord,
               MRequests
  <1>5. PendingRecord(b, previous).phase # "ABSENT"
        BY DEF PendingRecord
  <1>6. t = PendingRecord(b, previous)
        BY <1>4, <1>5, LocalMapEqualsNonAbsentImpliesStateEqual
  <1>. QED
        BY <1>3, <1>6

THEOREM MapSubmitFromExactProducesTerminal ==
  \A s \in ExactLocalStatesP :
    \A t :
      \A b \in PBindings,
         a \in PAuthorities,
         value \in {"ALLOW", "BLOCK"} :
        MapSubmit(LocalMap(s), LocalMap(t), b, a, value)
          => t \in ActiveTerminalStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in ExactLocalStatesP,
               NEW t,
               NEW b \in PBindings,
               NEW a \in PAuthorities,
               NEW value \in {"ALLOW", "BLOCK"},
               MapSubmit(LocalMap(s), LocalMap(t), b, a, value)
        PROVE t \in ActiveTerminalStatesP
       OBVIOUS
  <1>1. /\ s.phase = "PENDING"
         /\ b = s.binding
         /\ <<a, b>> \in PRAB
        BY SMTT(180)
           DEF MapSubmit,
               LocalMap,
               MRequests,
               MTag,
               MBinding
  <1>2. s \in PendingStatesP
        BY <1>1, ExactPendingPhaseImpliesPendingState
  <1>3. s.previous \in PPrevious
        BY <1>2, PendingStatePayload
  <1>4. TerminalRecord(value, b, s.previous, a) \in TerminalStatesP
        BY <1>1, <1>3, TerminalRecordInTerminalStates
  <1>5. TerminalRecord(value, b, s.previous, a)
          \in ActiveTerminalStatesP
        BY <1>4
           DEF ActiveTerminalStatesP, TerminalRecord
  <1>6. LocalMap(t)
          =
        LocalMap(TerminalRecord(value, b, s.previous, a))
        BY SMTT(180), <1>1
           DEF MapSubmit,
               LocalMap,
               TerminalRecord,
               MRequests,
               MTag,
               MBinding,
               MPrevious
  <1>7. TerminalRecord(value, b, s.previous, a).phase # "ABSENT"
        BY DEF TerminalRecord
  <1>8. t = TerminalRecord(value, b, s.previous, a)
        BY <1>6, <1>7, LocalMapEqualsNonAbsentImpliesStateEqual
  <1>. QED
        BY <1>5, <1>8

THEOREM MapConflictFromExactProducesInvalidated ==
  \A s \in ExactLocalStatesP :
    \A t :
      MapObserveConflict(LocalMap(s), LocalMap(t))
        => t \in InvalidatedTerminalStatesP
PROOF
  <1> SUFFICES
        ASSUME NEW s \in ExactLocalStatesP,
               NEW t,
               MapObserveConflict(LocalMap(s), LocalMap(t))
        PROVE t \in InvalidatedTerminalStatesP
       OBVIOUS
  <1>1. s.phase \in {"ALLOW", "BLOCK"}
        BY SMTT(180)
           DEF MapObserveConflict,
               LocalMap,
               MRequests,
               MTag
  <1>2. s \in ActiveTerminalStatesP
        BY <1>1, ExactActivePhaseImpliesActiveState
  <1>3. /\ <<s.authority, s.binding>> \in PRAB
         /\ s.previous \in PPrevious
        BY <1>2, ActiveTerminalStatePayload
  <1>4. DEFINE invalidPhase ==
          IF s.phase = "ALLOW"
          THEN "INVALIDATED_ALLOW"
          ELSE "INVALIDATED_BLOCK"
  <1>5. invalidPhase \in
          {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}
        BY SMTT(60), <1>1 DEF invalidPhase
  <1>6. TerminalRecord(
          invalidPhase,
          s.binding,
          s.previous,
          s.authority) \in TerminalStatesP
        BY <1>3, <1>5, TerminalRecordInTerminalStates
  <1>7. TerminalRecord(
          invalidPhase,
          s.binding,
          s.previous,
          s.authority) \in InvalidatedTerminalStatesP
        BY <1>5, <1>6
           DEF InvalidatedTerminalStatesP, TerminalRecord
  <1>8. LocalMap(t)
          =
        LocalMap(
          TerminalRecord(
            invalidPhase,
            s.binding,
            s.previous,
            s.authority))
        BY SMTT(180), <1>1
           DEF MapObserveConflict,
               LocalMap,
               TerminalRecord,
               invalidPhase,
               MRequests,
               MTag,
               MBinding,
               MPrevious,
               MAuthority
  <1>9. TerminalRecord(
          invalidPhase,
          s.binding,
          s.previous,
          s.authority).phase # "ABSENT"
        BY <1>5 DEF TerminalRecord
  <1>10. t =
          TerminalRecord(
            invalidPhase,
            s.binding,
            s.previous,
            s.authority)
        BY <1>8, <1>9, LocalMapEqualsNonAbsentImpliesStateEqual
  <1>. QED
        BY <1>7, <1>10

THEOREM RegisterBranchProducesExact ==
  \A s \in ExactLocalStatesP :
    \A t :
    (\E b \in PBindings,
        a \in PAuthorities,
        previous \in PPrevious :
       MapRegister(LocalMap(s), LocalMap(t), b, a, previous))
      =>
    t \in ExactLocalStatesP
PROOF
  BY SMTT(180),
     MapRegisterFromExactProducesPending
     DEF ExactLocalStatesP

THEOREM SubmitBranchProducesExact ==
  \A s \in ExactLocalStatesP :
    \A t :
    (\E b \in PBindings,
        a \in PAuthorities,
        value \in {"ALLOW", "BLOCK"} :
       MapSubmit(LocalMap(s), LocalMap(t), b, a, value))
      =>
    t \in ExactLocalStatesP
PROOF
  BY SMTT(180),
     MapSubmitFromExactProducesTerminal,
     ActiveTerminalSubsetExact

THEOREM ConflictBranchProducesExact ==
  \A s \in ExactLocalStatesP :
    \A t :
    MapObserveConflict(LocalMap(s), LocalMap(t))
      =>
    t \in ExactLocalStatesP
PROOF
  BY SMTT(180),
     MapConflictFromExactProducesInvalidated,
     InvalidatedTerminalSubsetExact

THEOREM LocalStepBranchesProduceExact ==
  \A s \in ExactLocalStatesP :
    \A t :
    LocalStep(s, t)
      =>
    t \in ExactLocalStatesP
PROOF
  BY SMTT(300),
     RegisterBranchProducesExact,
     SubmitBranchProducesExact,
     ConflictBranchProducesExact
     DEF LocalStep, MapNext

THEOREM LocalStepPreservesExact ==
  \A s \in ExactLocalStatesP :
    \A t :
      LocalStep(s, t) => t \in ExactLocalStatesP
PROOF
  BY LocalStepBranchesProduceExact

THEOREM ReachableWithinThreeIsExact ==
  \A s :
    ReachableWithinThree(s) => s \in ExactLocalStatesP
PROOF
  BY SMTT(240),
     AbsentIsExact,
     LocalStepPreservesExact
     DEF ReachableWithinThree

THEOREM ExactIffReachableWithinThree ==
  \A s :
    s \in ExactLocalStatesP <=> ReachableWithinThree(s)
PROOF
  BY EveryExactStateReachableWithinThree,
     ReachableWithinThreeIsExact

(***************************************************************************)
(* Temporal safety of the canonical-local machine.                         *)
(***************************************************************************)

THEOREM LocalInitImpliesExact ==
  LocalInit => LocalExactInvariant
PROOF
  BY AbsentIsExact
     DEF LocalInit, LocalExactInvariant

THEOREM LocalNextPreservesExact ==
  /\ LocalExactInvariant
  /\ LocalNext
  => LocalExactInvariant'
PROOF
  BY SMTT(120), LocalStepPreservesExact
     DEF LocalExactInvariant, LocalNext

THEOREM LocalStateStutterPreservesExact ==
  /\ LocalExactInvariant
  /\ UNCHANGED localVars
  => LocalExactInvariant'
PROOF
  BY DEF LocalExactInvariant, localVars

THEOREM LocalBoxNextPreservesExact ==
  /\ LocalExactInvariant
  /\ [LocalNext]_localVars
  => LocalExactInvariant'
PROOF
  BY SMTT(120),
     LocalNextPreservesExact,
     LocalStateStutterPreservesExact

THEOREM LocalSpecImpliesAlwaysExact ==
  LocalSpec => []LocalExactInvariant
PROOF
  BY PTL,
     LocalInitImpliesExact,
     LocalBoxNextPreservesExact
     DEF LocalSpec

(***************************************************************************)
(* Final canonical-local bridge.                                                       *)
(***************************************************************************)

THEOREM CanonicalLocalReachabilityEquivalence ==
  /\ \A s :
       s \in ExactLocalStatesP <=> ReachableWithinThree(s)
  /\ (LocalSpec => []LocalExactInvariant)
  /\ (Canonical!PhaseInit
        <=> linkPhaseMeta = LocalMap(AbsentStateP))
  /\ (Canonical!PhaseNext
        <=> MapNext(linkPhaseMeta, linkPhaseMeta'))
PROOF
  BY ExactIffReachableWithinThree,
     LocalSpecImpliesAlwaysExact,
     CanonicalInitMatchesAbsentMap,
     CanonicalNextMatchesMapNext

=============================================================================
