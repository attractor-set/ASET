------------------- MODULE CanonicalLocalReachability -------------------
EXTENDS ParametricLocalStateCardinality

(***************************************************************************)
(* PUBLIC / NON-NORMATIVE ASSURANCE.                                                *)
(*                                                                         *)
(* Target: connect the exact parametric local normal-form state set    *)
(* to actual CanonicalPhaseSeed single-resolution lifecycle       *)
(* reachability.                                                           *)
(*                                                                         *)
(* This module deliberately strengthens the algebraic parameter domain *)
(* with the conditions needed to instantiate CanonicalPhaseSeed itself:    *)
(*                                                                         *)
(* - Bindings and Authorities are non-empty;                               *)
(* - PPrevious is non-empty because CanonicalPhaseSeed always admits        *)
(*   NoCommitment;                                                         *)
(* - PNoCommitmentValue is the distinguished NoCommitment element;         *)
(* - PNoAuthority is outside Authorities.                                  *)
(*                                                                         *)
(* PPrevious is identified with:                                           *)
(*   {NoCommitment} \cup RecognizedTerminalCommitments.                    *)
(***************************************************************************)

CONSTANTS
  PResolutionId,
  PNoCommitmentValue

CanonicalLinkAssumptions ==
  /\ ParametricAssumptions
  /\ PBindings # {}
  /\ PAuthorities # {}
  /\ PPrevious # {}
  /\ PNoCommitmentValue \in PPrevious
  /\ PNoAuthority \notin PAuthorities

ASSUME CanonicalLinkAssumptions

VARIABLES
  localState,
  linkPhaseMeta

localVars == <<localState>>

Canonical == INSTANCE CanonicalPhaseSeed
  WITH ResolutionIds <- {PResolutionId},
       Bindings <- PBindings,
       Authorities <- PAuthorities,
       TerminalCommitments <- PPrevious \ {PNoCommitmentValue},
       RecognizedTerminalCommitments <- PPrevious \ {PNoCommitmentValue},
       NoCommitment <- PNoCommitmentValue,
       RecognizedAuthorityBindings <- PRAB,
       NoAuthority <- PNoAuthority,
       phaseMeta <- linkPhaseMeta

(***************************************************************************)
(* Pure map form of the instantiated CanonicalPhaseSeed actions.           *)
(***************************************************************************)

MRequests(m) == DOMAIN m
MTag(m, r) == m[r].phase
MBinding(m, r) == m[r].binding
MPrevious(m, r) == m[r].previous
MAuthority(m, r) == m[r].authority

MapRegister(m, n, b, a, previous) ==
  /\ PResolutionId \in {PResolutionId} \ MRequests(m)
  /\ b \in PBindings
  /\ a \in PAuthorities
  /\ <<a, b>> \in PRAB
  /\ previous \in PPrevious
  /\ n =
       [x \in MRequests(m) \cup {PResolutionId} |->
          IF x = PResolutionId
          THEN [phase |-> "PENDING",
                binding |-> b,
                previous |-> previous,
                authority |-> PNoAuthority]
          ELSE m[x]]

MapSubmit(m, n, b, a, value) ==
  /\ PResolutionId \in MRequests(m)
  /\ MTag(m, PResolutionId) = "PENDING"
  /\ b = MBinding(m, PResolutionId)
  /\ a \in PAuthorities
  /\ <<a, b>> \in PRAB
  /\ value \in {"ALLOW", "BLOCK"}
  /\ n =
       [x \in MRequests(m) |->
          IF x = PResolutionId
          THEN [phase |-> value,
                binding |-> MBinding(m, PResolutionId),
                previous |-> MPrevious(m, PResolutionId),
                authority |-> a]
          ELSE m[x]]

MapObserveConflict(m, n) ==
  /\ PResolutionId \in MRequests(m)
  /\ MTag(m, PResolutionId) \in {"ALLOW", "BLOCK"}
  /\ n =
       [x \in MRequests(m) |->
          IF x = PResolutionId
          THEN [phase |->
                  IF MTag(m, PResolutionId) = "ALLOW"
                  THEN "INVALIDATED_ALLOW"
                  ELSE "INVALIDATED_BLOCK",
                binding |-> MBinding(m, PResolutionId),
                previous |-> MPrevious(m, PResolutionId),
                authority |-> MAuthority(m, PResolutionId)]
          ELSE m[x]]

MapNext(m, n) ==
  \/ \E b \in PBindings,
        a \in PAuthorities,
        previous \in PPrevious :
       MapRegister(m, n, b, a, previous)
  \/ \E b \in PBindings,
        a \in PAuthorities,
        value \in {"ALLOW", "BLOCK"} :
       MapSubmit(m, n, b, a, value)
  \/ MapObserveConflict(m, n)

(***************************************************************************)
(* Exact encoding between a local state and the one-id canonical map.      *)
(***************************************************************************)

LocalMap(s) ==
  IF s.phase = "ABSENT"
  THEN [r \in {} |-> r]
  ELSE [r \in {PResolutionId} |-> s]

ProjectedLocalState(m) ==
  IF PResolutionId \notin DOMAIN m
  THEN AbsentStateP
  ELSE m[PResolutionId]

LocalStep(s, t) ==
  MapNext(LocalMap(s), LocalMap(t))

(***************************************************************************)
(* The local temporal machine.                                             *)
(***************************************************************************)

LocalInit ==
  localState = AbsentStateP

LocalNext ==
  LocalStep(localState, localState')

LocalSpec ==
  LocalInit /\ [][LocalNext]_localVars

LocalExactInvariant ==
  localState \in ExactLocalStatesP

(***************************************************************************)
(* Constructive finite reachability.                                       *)
(*                                                                         *)
(* Because a resolution id has only the lifecycle                          *)
(*   ABSENT -> PENDING -> ALLOW/BLOCK -> INVALIDATED_*                     *)
(* every reachable exact local state must have a witness path of length    *)
(* at most three.                                                          *)
(***************************************************************************)

ReachableWithinThree(t) ==
  \/ t = AbsentStateP
  \/ LocalStep(AbsentStateP, t)
  \/ \E s1 \in ExactLocalStatesP :
       /\ LocalStep(AbsentStateP, s1)
       /\ LocalStep(s1, t)
  \/ \E s1 \in ExactLocalStatesP,
        s2 \in ExactLocalStatesP :
       /\ LocalStep(AbsentStateP, s1)
       /\ LocalStep(s1, s2)
       /\ LocalStep(s2, t)

PendingPredecessor(s) ==
  [phase |-> "PENDING",
   binding |-> s.binding,
   previous |-> s.previous,
   authority |-> PNoAuthority]

ActivePredecessor(s) ==
  [phase |->
     IF s.phase = "INVALIDATED_ALLOW"
     THEN "ALLOW"
     ELSE "BLOCK",
   binding |-> s.binding,
   previous |-> s.previous,
   authority |-> s.authority]

ActiveTerminalStatesP ==
  {s \in TerminalStatesP : s.phase \in {"ALLOW", "BLOCK"}}

InvalidatedTerminalStatesP ==
  {s \in TerminalStatesP :
     s.phase \in {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}}

=============================================================================
