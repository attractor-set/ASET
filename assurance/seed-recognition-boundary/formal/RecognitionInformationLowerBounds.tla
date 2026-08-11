---------------- MODULE RecognitionInformationLowerBounds ----------------
EXTENDS RecognitionPayloadObservability

(***************************************************************************)
(* Representation-independent distinguishability lower bounds.             *)
(*                                                                         *)
(* Scope:                                                                  *)
(* - cardinality of observational equivalence classes;                     *)
(* - fixed-width binary code lower bounds derived from class count.         *)
(*                                                                         *)
(* Non-scope:                                                              *)
(* - Shannon entropy;                                                      *)
(* - average variable-length code length;                                  *)
(* - compression under a probability distribution.                         *)
(***************************************************************************)

TwoCodes ==
  {"0", "1"}

FourCodes ==
  {"00", "01", "10", "11"}

SixteenCodes ==
  {"0000", "0001", "0010", "0011",
   "0100", "0101", "0110", "0111",
   "1000", "1001", "1010", "1011",
   "1100", "1101", "1110", "1111"}

FaithfulOnWitnesses(f, representatives, observationMap, codomain) ==
  /\ f \in [representatives -> codomain]
  /\ \A x \in representatives, y \in representatives :
       observationMap[x] # observationMap[y] => f[x] # f[y]

PendingB1P1 ==
  [phase |-> "PENDING",
   binding |-> "B1",
   previous |-> "P1",
   authority |-> NoAuthorityWitness]

BlockB0P0A0 ==
  [phase |-> "BLOCK",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A0"]

InvalidatedAllowB0P0A0 ==
  [phase |-> "INVALIDATED_ALLOW",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A0"]

InvalidatedBlockB0P0A0 ==
  [phase |-> "INVALIDATED_BLOCK",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A0"]

ParameterizedSevenRepresentatives ==
  {AbsentWitness,
   PendingB0P0,
   PendingB1P0,
   AllowB0P0A0,
   BlockB0P0A0,
   InvalidatedAllowB0P0A0,
   InvalidatedBlockB0P0A0}

AllowB0P1A0 ==
  [phase |-> "ALLOW",
   binding |-> "B0",
   previous |-> "P1",
   authority |-> "A0"]

AllowB0P0A1 ==
  [phase |-> "ALLOW",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A1"]

AllowB0P1A1 ==
  [phase |-> "ALLOW",
   binding |-> "B0",
   previous |-> "P1",
   authority |-> "A1"]

AllowB1P0A0 ==
  [phase |-> "ALLOW",
   binding |-> "B1",
   previous |-> "P0",
   authority |-> "A0"]

AllowB1P1A0 ==
  [phase |-> "ALLOW",
   binding |-> "B1",
   previous |-> "P1",
   authority |-> "A0"]

BlockB0P1A0 ==
  [phase |-> "BLOCK",
   binding |-> "B0",
   previous |-> "P1",
   authority |-> "A0"]

BlockB0P0A1 ==
  [phase |-> "BLOCK",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A1"]

BlockB0P1A1 ==
  [phase |-> "BLOCK",
   binding |-> "B0",
   previous |-> "P1",
   authority |-> "A1"]

BlockB1P0A0 ==
  [phase |-> "BLOCK",
   binding |-> "B1",
   previous |-> "P0",
   authority |-> "A0"]

BlockB1P1A0 ==
  [phase |-> "BLOCK",
   binding |-> "B1",
   previous |-> "P1",
   authority |-> "A0"]

ExactSeventeenRepresentatives ==
  {AbsentWitness,
   PendingB0P0,
   PendingB0P1,
   PendingB1P0,
   PendingB1P1,
   AllowB0P0A0,
   AllowB0P1A0,
   AllowB0P0A1,
   AllowB0P1A1,
   AllowB1P0A0,
   AllowB1P1A0,
   BlockB0P0A0,
   BlockB0P1A0,
   BlockB0P0A1,
   BlockB0P1A1,
   BlockB1P0A0,
   BlockB1P1A0}

=============================================================================
