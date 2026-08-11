---------------- MODULE ParametricLocalStateCardinality ----------------
EXTENDS FiniteSets

(***************************************************************************)
(* PUBLIC / NON-NORMATIVE ASSURANCE.                                                *)
(*                                                                         *)
(* Parametric local exact-state normal form induced by CanonicalPhaseSeed. *)
(*                                                                         *)
(* PPrevious denotes the admissible previous-value set, i.e. the analogue *)
(* of {NoCommitment} \cup RecognizedTerminalCommitments.                   *)
(*                                                                         *)
(* PRAB denotes RecognizedAuthorityBindings.                               *)
(*                                                                         *)
(* A binding is PENDING-admissible exactly when it occurs in PRAB, because *)
(* CanonicalPhaseSeed!PhaseRegister requires <<authority,binding>> in RAB.  *)
(***************************************************************************)

CONSTANTS
  PBindings,
  PAuthorities,
  PPrevious,
  PRAB,
  PNoBinding,
  PNoPrevious,
  PNoAuthority

ParametricAssumptions ==
  /\ IsFiniteSet(PBindings)
  /\ IsFiniteSet(PAuthorities)
  /\ IsFiniteSet(PPrevious)
  /\ PRAB \subseteq (PAuthorities \X PBindings)

ASSUME ParametricAssumptions

PRecognizedBindings ==
  {b \in PBindings :
     \E a \in PAuthorities : <<a, b>> \in PRAB}

TerminalPhaseCodes == 1..4

TerminalTag(k) ==
  CASE k = 1 -> "ALLOW"
    [] k = 2 -> "BLOCK"
    [] k = 3 -> "INVALIDATED_ALLOW"
    [] OTHER -> "INVALIDATED_BLOCK"

AbsentStateP ==
  [phase |-> "ABSENT",
   binding |-> PNoBinding,
   previous |-> PNoPrevious,
   authority |-> PNoAuthority]

PendingDomain ==
  PRecognizedBindings \X PPrevious

PendingCtor(x) ==
  [phase |-> "PENDING",
   binding |-> x[1],
   previous |-> x[2],
   authority |-> PNoAuthority]

PendingStatesP ==
  {PendingCtor(x) : x \in PendingDomain}

TerminalPayloadDomain ==
  PRAB \X PPrevious

TerminalDomain ==
  TerminalPhaseCodes \X TerminalPayloadDomain

TerminalCtor(x) ==
  [phase |-> TerminalTag(x[1]),
   binding |-> x[2][1][2],
   previous |-> x[2][2],
   authority |-> x[2][1][1]]

TerminalStatesP ==
  {TerminalCtor(x) : x \in TerminalDomain}

ExactLocalStatesP ==
  {AbsentStateP} \cup PendingStatesP \cup TerminalStatesP

ParametricExactCount ==
  1
  + Cardinality(PRecognizedBindings) * Cardinality(PPrevious)
  + 4 * Cardinality(PRAB) * Cardinality(PPrevious)

=============================================================================
