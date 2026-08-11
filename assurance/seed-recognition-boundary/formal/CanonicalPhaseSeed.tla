----------------------- MODULE CanonicalPhaseSeed -----------------------
EXTENDS FiniteSets

(***************************************************************************)
(* Canonical per-id tagged normal form for Seed recognition state.         *)
(*                                                                         *)
(* ABSENT is represented by absence from DOMAIN phaseMeta.                 *)
(* Stored tags are:                                                        *)
(*   PENDING                                                               *)
(*   ALLOW                                                                 *)
(*   BLOCK                                                                 *)
(*   INVALIDATED_ALLOW                                                     *)
(*   INVALIDATED_BLOCK                                                     *)
(*                                                                         *)
(* The record carries the immutable payload needed to reconstruct the      *)
(* pinned Seed state exactly:                                              *)
(*   binding, previous, terminal authority when terminal.                  *)
(*                                                                         *)
(* This is NOT a claim that "one variable is semantically minimal". Any    *)
(* tuple can be packed into one variable. The claim under test is that     *)
(* Seed's three-map layout has a canonical tagged per-id normal form whose *)
(* operational/history phase partition is exactly the proved six-class     *)
(* partition (including ABSENT).                                           *)
(***************************************************************************)

CONSTANTS ResolutionIds,
          Bindings,
          Authorities,
          TerminalCommitments,
          RecognizedTerminalCommitments,
          NoCommitment,
          RecognizedAuthorityBindings,
          NoAuthority

ASSUME ResolutionIds # {}
ASSUME Bindings # {}
ASSUME Authorities # {}
ASSUME RecognizedAuthorityBindings \subseteq Authorities \X Bindings
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME NoAuthority \notin Authorities

StoredPhaseTags ==
  {"PENDING",
   "ALLOW",
   "BLOCK",
   "INVALIDATED_ALLOW",
   "INVALIDATED_BLOCK"}

TerminalPhaseTags ==
  {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}

ConflictPhaseTags ==
  {"INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}

TerminalResolutions == {"ALLOW", "BLOCK"}

PhaseMetaRecordType ==
  [phase : StoredPhaseTags,
   binding : Bindings,
   previous : TerminalCommitments \cup {NoCommitment},
   authority : Authorities \cup {NoAuthority}]

VARIABLE phaseMeta

phaseVars == <<phaseMeta>>

PhaseRequests == DOMAIN phaseMeta

PhaseTag(r) == phaseMeta[r].phase
PhaseBinding(r) == phaseMeta[r].binding
PhasePrevious(r) == phaseMeta[r].previous
PhaseAuthority(r) == phaseMeta[r].authority

PhaseTerminalRequests ==
  {r \in PhaseRequests : PhaseTag(r) \in TerminalPhaseTags}

PhaseConflicts ==
  {r \in PhaseRequests : PhaseTag(r) \in ConflictPhaseTags}

PhaseTerminalResolution(r) ==
  IF PhaseTag(r) \in {"ALLOW", "INVALIDATED_ALLOW"}
  THEN "ALLOW"
  ELSE "BLOCK"

PhaseRequestMeta ==
  [r \in PhaseRequests |->
     [binding |-> PhaseBinding(r),
      previous |-> PhasePrevious(r)]]

PhaseTerminalMeta ==
  [r \in PhaseTerminalRequests |->
     [resolution |-> PhaseTerminalResolution(r),
      authority |-> PhaseAuthority(r)]]

PhaseResolutionOf(r) ==
  IF r \notin PhaseRequests \/ r \in PhaseConflicts
  THEN "UNKNOWN"
  ELSE IF r \notin PhaseTerminalRequests
       THEN "UNKNOWN"
       ELSE PhaseTerminalResolution(r)

PhaseEffectPermitted(r) == PhaseResolutionOf(r) = "ALLOW"

PhaseInit ==
  phaseMeta = [r \in {} |-> r]

PhaseRegister(r, b, a, previous) ==
  /\ r \in ResolutionIds \ PhaseRequests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in RecognizedAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ phaseMeta' =
       [x \in PhaseRequests \cup {r} |->
          IF x = r
          THEN [phase |-> "PENDING",
                binding |-> b,
                previous |-> previous,
                authority |-> NoAuthority]
          ELSE phaseMeta[x]]

PhaseSubmit(r, b, a, value) ==
  /\ r \in PhaseRequests
  /\ PhaseTag(r) = "PENDING"
  /\ b = PhaseBinding(r)
  /\ a \in Authorities
  /\ <<a, b>> \in RecognizedAuthorityBindings
  /\ value \in TerminalResolutions
  /\ phaseMeta' =
       [x \in PhaseRequests |->
          IF x = r
          THEN [phase |-> value,
                binding |-> PhaseBinding(r),
                previous |-> PhasePrevious(r),
                authority |-> a]
          ELSE phaseMeta[x]]

PhaseObserveConflict(r) ==
  /\ r \in PhaseRequests
  /\ PhaseTag(r) \in {"ALLOW", "BLOCK"}
  /\ phaseMeta' =
       [x \in PhaseRequests |->
          IF x = r
          THEN [phase |->
                  IF PhaseTag(r) = "ALLOW"
                  THEN "INVALIDATED_ALLOW"
                  ELSE "INVALIDATED_BLOCK",
                binding |-> PhaseBinding(r),
                previous |-> PhasePrevious(r),
                authority |-> PhaseAuthority(r)]
          ELSE phaseMeta[x]]

PhaseRecognizedSeedTransition ==
  \/ \E r \in ResolutionIds,
        b \in Bindings,
        a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
       PhaseRegister(r, b, a, previous)
  \/ \E r \in ResolutionIds,
        b \in Bindings,
        a \in Authorities,
        value \in TerminalResolutions :
       PhaseSubmit(r, b, a, value)

PhaseRecognizedEnvironmentTransition ==
  \E r \in ResolutionIds :
    PhaseObserveConflict(r)

PhaseNext ==
  \/ PhaseRecognizedSeedTransition
  \/ PhaseRecognizedEnvironmentTransition

PhaseSpec ==
  PhaseInit /\ [][PhaseNext]_phaseVars

PhaseStateOK ==
  /\ DOMAIN phaseMeta \subseteq ResolutionIds
  /\ phaseMeta \in [DOMAIN phaseMeta -> PhaseMetaRecordType]
  /\ \A r \in PhaseRequests :
       /\ IF PhaseTag(r) = "PENDING"
          THEN PhaseAuthority(r) = NoAuthority
          ELSE PhaseAuthority(r) \in Authorities
       /\ PhasePrevious(r) = NoCommitment
          \/ PhasePrevious(r) \in RecognizedTerminalCommitments

=============================================================================
