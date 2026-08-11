------------- MODULE CanonicalPhaseSeedToSeedRefinementProofs -------------
EXTENDS CanonicalPhaseSeed, TLAPS

Seed == INSTANCE SeedResolution
  WITH ResolutionIds <- ResolutionIds,
       Bindings <- Bindings,
       Authorities <- Authorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RecognizedAuthorityBindings <- RecognizedAuthorityBindings,
       requestMeta <- PhaseRequestMeta,
       terminalMeta <- PhaseTerminalMeta,
       conflicts <- PhaseConflicts


PhaseTerminalResolutionPrime(r) ==
  IF phaseMeta'[r].phase \in {"ALLOW", "INVALIDATED_ALLOW"}
  THEN "ALLOW"
  ELSE "BLOCK"

THEOREM SeedRequestsEqualPhaseRequests ==
  Seed!Requests = PhaseRequests
PROOF
  BY DEF Seed!Requests, PhaseRequestMeta, PhaseRequests

THEOREM SeedTerminalRequestsEqualPhaseTerminalRequests ==
  Seed!TerminalRequests = PhaseTerminalRequests
PROOF
  BY DEF Seed!TerminalRequests, PhaseTerminalMeta, PhaseTerminalRequests

THEOREM SeedTerminalResolutionsEqualPhaseTerminalResolutions ==
  Seed!TerminalResolutions = TerminalResolutions
PROOF
  BY DEF Seed!TerminalResolutions, TerminalResolutions

THEOREM SeedRequestBindingEqualsPhaseBinding ==
  \A r \in PhaseRequests :
    Seed!RequestBinding(r) = PhaseBinding(r)
PROOF
  BY SMTT(60)
     DEF Seed!RequestBinding,
         PhaseRequestMeta,
         PhaseBinding,
         PhaseRequests

THEOREM SeedTerminalResolutionEqualsPhaseResolution ==
  \A r \in PhaseTerminalRequests :
    Seed!TerminalResolution(r) = PhaseTerminalResolution(r)
PROOF
  BY SMTT(60)
     DEF Seed!TerminalResolution,
         PhaseTerminalMeta,
         PhaseTerminalResolution,
         PhaseTerminalRequests

THEOREM PhaseEvaluatorEquivalentToSeed ==
  \A r \in ResolutionIds :
    /\ PhaseResolutionOf(r) = Seed!ResolutionOf(r)
    /\ PhaseEffectPermitted(r) = Seed!EffectPermitted(r)
PROOF
  BY SMTT(120),
     SeedRequestsEqualPhaseRequests,
     SeedTerminalRequestsEqualPhaseTerminalRequests,
     SeedTerminalResolutionEqualsPhaseResolution
     DEF PhaseResolutionOf,
         PhaseEffectPermitted,
         PhaseConflicts,
         Seed!ResolutionOf,
         Seed!EffectPermitted

(***************************************************************************)
(* Init views.                                                             *)
(***************************************************************************)

THEOREM PhaseInitImpliesNoRequests ==
  PhaseInit => PhaseRequests = {}
PROOF
  BY SMTT(60)
     DEF PhaseInit, PhaseRequests

THEOREM PhaseInitImpliesEmptyRequestMeta ==
  PhaseInit => PhaseRequestMeta = [r \in {} |-> r]
PROOF
  BY SMTT(60),
     PhaseInitImpliesNoRequests
     DEF PhaseRequestMeta

THEOREM PhaseInitImpliesNoTerminalRequests ==
  PhaseInit => PhaseTerminalRequests = {}
PROOF
  BY SMTT(60),
     PhaseInitImpliesNoRequests
     DEF PhaseTerminalRequests

THEOREM PhaseInitImpliesEmptyTerminalMeta ==
  PhaseInit => PhaseTerminalMeta = [r \in {} |-> r]
PROOF
  BY SMTT(60),
     PhaseInitImpliesNoTerminalRequests
     DEF PhaseTerminalMeta

THEOREM PhaseInitImpliesNoConflicts ==
  PhaseInit => PhaseConflicts = {}
PROOF
  BY SMTT(60),
     PhaseInitImpliesNoRequests
     DEF PhaseConflicts

THEOREM PhaseInitRefinesSeedInit ==
  PhaseInit => Seed!Init
PROOF
  BY SMTT(60),
     PhaseInitImpliesEmptyRequestMeta,
     PhaseInitImpliesEmptyTerminalMeta,
     PhaseInitImpliesNoConflicts
     DEF Seed!Init

(***************************************************************************)
(* Register view laws.                                                     *)
(***************************************************************************)

THEOREM PhaseRegisterRequestsUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => PhaseRequests' = PhaseRequests \cup {r}
PROOF
  BY SMTT(60)
     DEF PhaseRegister, PhaseRequests

THEOREM PhaseRegisterNewTagPending ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => phaseMeta'[r].phase = "PENDING"
PROOF
  BY SMTT(60)
     DEF PhaseRegister, PhaseTag, PhaseRequests

THEOREM PhaseRegisterExistingEntryUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => \A x \in PhaseRequests : phaseMeta'[x] = phaseMeta[x]
PROOF
  BY SMTT(60)
     DEF PhaseRegister

THEOREM PhaseRegisterTerminalRequestsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => PhaseTerminalRequests' = PhaseTerminalRequests
PROOF
  BY SMTT(180),
     PhaseRegisterRequestsUpdate,
     PhaseRegisterNewTagPending,
     PhaseRegisterExistingEntryUnchanged
     DEF PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags,
         PhaseRequests

THEOREM PhaseRegisterConflictsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => UNCHANGED PhaseConflicts
PROOF
  BY SMTT(180),
     PhaseRegisterRequestsUpdate,
     PhaseRegisterNewTagPending,
     PhaseRegisterExistingEntryUnchanged
     DEF PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags,
         PhaseRequests

THEOREM PhaseRegisterTerminalMetaPointwise ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => \A x \in PhaseTerminalRequests :
           PhaseTerminalMeta'[x] = PhaseTerminalMeta[x]
PROOF
  BY SMTT(180),
     PhaseRegisterExistingEntryUnchanged,
     PhaseRegisterTerminalRequestsUnchanged
     DEF PhaseTerminalMeta,
         PhaseTerminalResolution,
         PhaseAuthority,
         PhaseTag,
         PhaseRequests,
         PhaseTerminalRequests

THEOREM PhaseRegisterTerminalMetaUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => UNCHANGED PhaseTerminalMeta
PROOF
  BY IsaT(300),
     PhaseRegisterTerminalRequestsUnchanged,
     PhaseRegisterTerminalMetaPointwise
     DEF PhaseTerminalMeta,
         PhaseTerminalRequests

THEOREM PhaseRegisterProducesSeedRequestUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      =>
    PhaseRequestMeta' =
      [x \in Seed!Requests \cup {r} |->
         IF x = r
         THEN [binding |-> b, previous |-> previous]
         ELSE PhaseRequestMeta[x]]
PROOF
  BY SMTT(120),
     SeedRequestsEqualPhaseRequests
     DEF PhaseRegister,
         PhaseRequestMeta,
         PhaseRequests,
         PhaseBinding,
         PhasePrevious,
         Seed!Requests

THEOREM PhaseRegisterPreservesSeedRemainder ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => UNCHANGED <<PhaseTerminalMeta, PhaseConflicts>>
PROOF
  BY SMTT(60),
     PhaseRegisterTerminalMetaUnchanged,
     PhaseRegisterConflictsUnchanged

THEOREM PhaseRegisterFreshInSeedRequests ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => r \in ResolutionIds \ Seed!Requests
PROOF
  BY SMTT(60),
     SeedRequestsEqualPhaseRequests
     DEF PhaseRegister

THEOREM PhaseRegisterSeedGuards ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      =>
      /\ r \in ResolutionIds \ Seed!Requests
      /\ b \in Bindings
      /\ a \in Authorities
      /\ <<a, b>> \in RecognizedAuthorityBindings
      /\ \/ previous = NoCommitment
         \/ previous \in RecognizedTerminalCommitments
PROOF
  BY ZenonT(120),
     PhaseRegisterFreshInSeedRequests
     DEF PhaseRegister

THEOREM PhaseRegisterRefinesSeedRegister ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)
      => Seed!RegisterRequest(r, b, a, previous)
PROOF
  BY SMTT(120),
     PhaseRegisterSeedGuards,
     PhaseRegisterProducesSeedRequestUpdate,
     PhaseRegisterPreservesSeedRemainder
     DEF Seed!RegisterRequest

(***************************************************************************)
(* Submit view laws.                                                       *)
(***************************************************************************)

THEOREM PhaseSubmitRequestsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => UNCHANGED PhaseRequests
PROOF
  BY SMTT(60)
     DEF PhaseSubmit, PhaseRequests

THEOREM PhaseSubmitTargetTagValue ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => phaseMeta'[r].phase = value
PROOF
  BY SMTT(60)
     DEF PhaseSubmit, PhaseTag, PhaseRequests

THEOREM PhaseSubmitExistingOtherEntryUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => \A x \in PhaseRequests \ {r} : phaseMeta'[x] = phaseMeta[x]
PROOF
  BY SMTT(60)
     DEF PhaseSubmit

THEOREM PhaseSubmitTargetBindingUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => phaseMeta'[r].binding = PhaseBinding(r)
PROOF
  BY SMTT(60)
     DEF PhaseSubmit, PhaseBinding, PhaseRequests

THEOREM PhaseSubmitTargetPreviousUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => phaseMeta'[r].previous = PhasePrevious(r)
PROOF
  BY SMTT(60)
     DEF PhaseSubmit, PhasePrevious, PhaseRequests

THEOREM PhaseSubmitTargetAuthority ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => phaseMeta'[r].authority = a
PROOF
  BY SMTT(60)
     DEF PhaseSubmit, PhaseAuthority, PhaseRequests

THEOREM PhaseSubmitTargetWasNotTerminal ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => r \notin PhaseTerminalRequests
PROOF
  BY SMTT(60)
     DEF PhaseSubmit,
         PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags

THEOREM PhaseSubmitTargetNotConflicted ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => r \notin PhaseConflicts
PROOF
  BY SMTT(60)
     DEF PhaseSubmit,
         PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags

THEOREM PhaseSubmitTargetEntersTerminalRequests ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => r \in PhaseTerminalRequests'
PROOF
  BY IsaT(180),
     PhaseSubmitTargetTagValue,
     PhaseSubmitRequestsUnchanged
     DEF PhaseSubmit,
         PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags,
         TerminalResolutions,
         PhaseRequests

THEOREM PhaseSubmitOtherTerminalMembershipUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => \A x \in PhaseRequests \ {r} :
           (x \in PhaseTerminalRequests'
             <=> x \in PhaseTerminalRequests)
PROOF
  BY SMTT(180),
     PhaseSubmitRequestsUnchanged,
     PhaseSubmitExistingOtherEntryUnchanged
     DEF PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags,
         PhaseRequests

THEOREM PhaseSubmitTerminalRequestsUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => PhaseTerminalRequests' = PhaseTerminalRequests \cup {r}
PROOF
  BY SMTT(180),
     PhaseSubmitRequestsUnchanged,
     PhaseSubmitTargetWasNotTerminal,
     PhaseSubmitTargetEntersTerminalRequests,
     PhaseSubmitOtherTerminalMembershipUnchanged
     DEF PhaseTerminalRequests,
         PhaseRequests

THEOREM PhaseSubmitConflictsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => UNCHANGED PhaseConflicts
PROOF
  BY SMTT(180),
     PhaseSubmitRequestsUnchanged,
     PhaseSubmitTargetTagValue,
     PhaseSubmitExistingOtherEntryUnchanged,
     PhaseSubmitTargetNotConflicted
     DEF PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags,
         TerminalResolutions,
         PhaseRequests

THEOREM PhaseSubmitRequestMetaUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => UNCHANGED PhaseRequestMeta
PROOF
  BY SMTT(180),
     PhaseSubmitRequestsUnchanged,
     PhaseSubmitExistingOtherEntryUnchanged,
     PhaseSubmitTargetBindingUnchanged,
     PhaseSubmitTargetPreviousUnchanged
     DEF PhaseRequestMeta,
         PhaseBinding,
         PhasePrevious,
         PhaseRequests

THEOREM PhaseSubmitTargetTerminalMeta ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      =>
    PhaseTerminalMeta'[r] =
      [resolution |-> value, authority |-> a]
PROOF
  BY SMTT(180),
     PhaseSubmitTargetTagValue,
     PhaseSubmitTargetAuthority,
     PhaseSubmitTargetEntersTerminalRequests
     DEF PhaseTerminalMeta,
         PhaseTerminalResolution,
         PhaseAuthority,
         TerminalResolutions,
         PhaseTag

THEOREM PhaseSubmitOtherTerminalMetaUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => \A x \in PhaseTerminalRequests :
           PhaseTerminalMeta'[x] = PhaseTerminalMeta[x]
PROOF
  BY SMTT(180),
     PhaseSubmitExistingOtherEntryUnchanged,
     PhaseSubmitTargetWasNotTerminal,
     PhaseSubmitTerminalRequestsUpdate
     DEF PhaseTerminalMeta,
         PhaseTerminalResolution,
         PhaseAuthority,
         PhaseTag,
         PhaseRequests,
         PhaseTerminalRequests

THEOREM PhaseSubmitTerminalMetaDomainUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      =>
    DOMAIN PhaseTerminalMeta' =
      Seed!TerminalRequests \cup {r}
PROOF
  BY SMTT(120),
     SeedTerminalRequestsEqualPhaseTerminalRequests,
     PhaseSubmitTerminalRequestsUpdate
     DEF PhaseTerminalMeta

THEOREM PhaseSubmitTerminalMetaPointwiseUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      =>
    \A x \in Seed!TerminalRequests \cup {r} :
      PhaseTerminalMeta'[x] =
        IF x = r
        THEN [resolution |-> value, authority |-> a]
        ELSE PhaseTerminalMeta[x]
PROOF
  BY SMTT(180),
     SeedTerminalRequestsEqualPhaseTerminalRequests,
     PhaseSubmitTargetTerminalMeta,
     PhaseSubmitOtherTerminalMetaUnchanged,
     PhaseSubmitTargetWasNotTerminal

THEOREM PhaseSubmitProducesSeedTerminalUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      =>
    PhaseTerminalMeta' =
      [x \in Seed!TerminalRequests \cup {r} |->
         IF x = r
         THEN [resolution |-> value, authority |-> a]
         ELSE PhaseTerminalMeta[x]]
PROOF
  <1> SUFFICES
        ASSUME NEW r \in ResolutionIds,
               NEW b \in Bindings,
               NEW a \in Authorities,
               NEW value \in TerminalResolutions,
               PhaseSubmit(r, b, a, value)
        PROVE
          PhaseTerminalMeta' =
            [x \in Seed!TerminalRequests \cup {r} |->
               IF x = r
               THEN [resolution |-> value, authority |-> a]
               ELSE PhaseTerminalMeta[x]]
       OBVIOUS
  <1>1. DOMAIN PhaseTerminalMeta' =
          Seed!TerminalRequests \cup {r}
       BY PhaseSubmitTerminalMetaDomainUpdate
  <1>2. \A x \in Seed!TerminalRequests \cup {r} :
          PhaseTerminalMeta'[x] =
            IF x = r
            THEN [resolution |-> value, authority |-> a]
            ELSE PhaseTerminalMeta[x]
       BY PhaseSubmitTerminalMetaPointwiseUpdate
  <1> QED
       BY SMTT(120), <1>1, <1>2
          DEF PhaseTerminalMeta

THEOREM PhaseSubmitPreservesSeedRemainder ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => UNCHANGED <<PhaseRequestMeta, PhaseConflicts>>
PROOF
  BY SMTT(60),
     PhaseSubmitRequestMetaUnchanged,
     PhaseSubmitConflictsUnchanged

THEOREM PhaseSubmitRequestExistsInSeed ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => r \in Seed!Requests
PROOF
  BY SMTT(60),
     SeedRequestsEqualPhaseRequests
     DEF PhaseSubmit

THEOREM PhaseSubmitBindingMatchesSeed ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => b = Seed!RequestBinding(r)
PROOF
  BY SMTT(60),
     SeedRequestBindingEqualsPhaseBinding
     DEF PhaseSubmit

THEOREM PhaseSubmitValueIsSeedTerminal ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => value \in Seed!TerminalResolutions
PROOF
  BY SMTT(60),
     SeedTerminalResolutionsEqualPhaseTerminalResolutions
     DEF PhaseSubmit

THEOREM PhaseSubmitFreshInSeedTerminalRequests ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => r \notin Seed!TerminalRequests
PROOF
  BY SMTT(60),
     SeedTerminalRequestsEqualPhaseTerminalRequests,
     PhaseSubmitTargetWasNotTerminal

THEOREM PhaseSubmitSeedGuards ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      =>
      /\ r \in Seed!Requests
      /\ b = Seed!RequestBinding(r)
      /\ a \in Authorities
      /\ <<a, b>> \in RecognizedAuthorityBindings
      /\ value \in Seed!TerminalResolutions
      /\ r \notin Seed!TerminalRequests
      /\ r \notin PhaseConflicts
PROOF
  BY ZenonT(120),
     PhaseSubmitRequestExistsInSeed,
     PhaseSubmitBindingMatchesSeed,
     PhaseSubmitValueIsSeedTerminal,
     PhaseSubmitFreshInSeedTerminalRequests,
     PhaseSubmitTargetNotConflicted
     DEF PhaseSubmit

THEOREM PhaseSubmitRefinesSeedSubmit ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)
      => Seed!SubmitResolution(r, b, a, value)
PROOF
  BY SMTT(120),
     PhaseSubmitSeedGuards,
     PhaseSubmitProducesSeedTerminalUpdate,
     PhaseSubmitPreservesSeedRemainder
     DEF Seed!SubmitResolution

(***************************************************************************)
(* Conflict view laws.                                                     *)
(***************************************************************************)

THEOREM PhaseConflictRequestsUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => UNCHANGED PhaseRequests
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict, PhaseRequests

THEOREM PhaseConflictTargetTagInvalidated ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      =>
    phaseMeta'[r].phase =
      IF PhaseTag(r) = "ALLOW"
      THEN "INVALIDATED_ALLOW"
      ELSE "INVALIDATED_BLOCK"
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict, PhaseTag, PhaseRequests

THEOREM PhaseConflictExistingOtherEntryUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => \A x \in PhaseRequests \ {r} : phaseMeta'[x] = phaseMeta[x]
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict

THEOREM PhaseConflictTargetBindingUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => phaseMeta'[r].binding = PhaseBinding(r)
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict, PhaseBinding, PhaseRequests

THEOREM PhaseConflictTargetPreviousUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => phaseMeta'[r].previous = PhasePrevious(r)
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict, PhasePrevious, PhaseRequests

THEOREM PhaseConflictTargetAuthorityUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => phaseMeta'[r].authority = PhaseAuthority(r)
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict, PhaseAuthority, PhaseRequests

THEOREM PhaseConflictTargetWasTerminal ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => r \in PhaseTerminalRequests
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict,
         PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags

THEOREM PhaseConflictTargetWasNotConflict ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => r \notin PhaseConflicts
PROOF
  BY SMTT(60)
     DEF PhaseObserveConflict,
         PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags

THEOREM PhaseConflictTerminalRequestsUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => UNCHANGED PhaseTerminalRequests
PROOF
  BY SMTT(180),
     PhaseConflictRequestsUnchanged,
     PhaseConflictTargetTagInvalidated,
     PhaseConflictExistingOtherEntryUnchanged,
     PhaseConflictTargetWasTerminal
     DEF PhaseTerminalRequests,
         PhaseTag,
         TerminalPhaseTags,
         PhaseRequests

THEOREM PhaseConflictTargetEntersConflicts ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => r \in PhaseConflicts'
PROOF
  BY IsaT(180),
     PhaseConflictTargetTagInvalidated,
     PhaseConflictRequestsUnchanged
     DEF PhaseObserveConflict,
         PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags,
         PhaseRequests

THEOREM PhaseConflictOtherMembershipUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => \A x \in PhaseRequests \ {r} :
           (x \in PhaseConflicts' <=> x \in PhaseConflicts)
PROOF
  BY SMTT(180),
     PhaseConflictRequestsUnchanged,
     PhaseConflictExistingOtherEntryUnchanged
     DEF PhaseConflicts,
         PhaseTag,
         ConflictPhaseTags,
         PhaseRequests

THEOREM PhaseConflictProducesSeedConflictUpdate ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => PhaseConflicts' = PhaseConflicts \cup {r}
PROOF
  BY SMTT(180),
     PhaseConflictRequestsUnchanged,
     PhaseConflictTargetWasNotConflict,
     PhaseConflictTargetEntersConflicts,
     PhaseConflictOtherMembershipUnchanged
     DEF PhaseConflicts,
         PhaseRequests

THEOREM PhaseConflictRequestMetaUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => UNCHANGED PhaseRequestMeta
PROOF
  BY SMTT(180),
     PhaseConflictRequestsUnchanged,
     PhaseConflictExistingOtherEntryUnchanged,
     PhaseConflictTargetBindingUnchanged,
     PhaseConflictTargetPreviousUnchanged
     DEF PhaseRequestMeta,
         PhaseBinding,
         PhasePrevious,
         PhaseRequests

THEOREM PhaseConflictTerminalResolutionUnchangedAtTarget ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => PhaseTerminalResolutionPrime(r) = PhaseTerminalResolution(r)
PROOF
  BY SMTT(120),
     PhaseConflictTargetTagInvalidated
     DEF PhaseTerminalResolutionPrime,
         PhaseTerminalResolution,
         PhaseObserveConflict,
         PhaseTag

THEOREM PhaseConflictTerminalMetaPointwise ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => \A x \in PhaseTerminalRequests :
           PhaseTerminalMeta'[x] = PhaseTerminalMeta[x]
PROOF
  BY SMTT(240),
     PhaseConflictTerminalRequestsUnchanged,
     PhaseConflictExistingOtherEntryUnchanged,
     PhaseConflictTargetAuthorityUnchanged,
     PhaseConflictTerminalResolutionUnchangedAtTarget
     DEF PhaseTerminalMeta,
         PhaseTerminalResolution,
         PhaseTerminalResolutionPrime,
         PhaseAuthority,
         PhaseTag,
         PhaseRequests,
         PhaseTerminalRequests

THEOREM PhaseConflictTerminalMetaUnchanged ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => UNCHANGED PhaseTerminalMeta
PROOF
  BY IsaT(300),
     PhaseConflictTerminalRequestsUnchanged,
     PhaseConflictTerminalMetaPointwise
     DEF PhaseTerminalMeta,
         PhaseTerminalRequests

THEOREM PhaseConflictPreservesSeedSeedVars ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r)
      => UNCHANGED Seed!seedVars
PROOF
  BY SMTT(60),
     PhaseConflictRequestMetaUnchanged,
     PhaseConflictTerminalMetaUnchanged
     DEF Seed!seedVars

THEOREM PhaseConflictRefinesSeedConflict ==
  \A r \in ResolutionIds :
    PhaseObserveConflict(r) => Seed!ObserveConflict(r)
PROOF
  BY SMTT(120),
     SeedTerminalRequestsEqualPhaseTerminalRequests,
     PhaseConflictTargetWasTerminal,
     PhaseConflictTargetWasNotConflict,
     PhaseConflictProducesSeedConflictUpdate,
     PhaseConflictPreservesSeedSeedVars
     DEF Seed!ObserveConflict

(***************************************************************************)
(* Existential transition assembly.                                       *)
(***************************************************************************)

PhaseRegisterTransition ==
  \E r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    PhaseRegister(r, b, a, previous)

PhaseSubmitTransition ==
  \E r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    PhaseSubmit(r, b, a, value)

PhaseConflictTransition ==
  \E r \in ResolutionIds :
    PhaseObserveConflict(r)

THEOREM PhaseRegisterTransitionRefinesSeed ==
  PhaseRegisterTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME PhaseRegisterTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              b \in Bindings,
              a \in Authorities,
              previous \in TerminalCommitments \cup {NoCommitment} :
          PhaseRegister(r, b, a, previous)
       BY Zenon DEF PhaseRegisterTransition
  <1>2. Seed!RegisterRequest(r, b, a, previous)
       BY <1>1, PhaseRegisterRefinesSeedRegister
  <1> QED
       BY Zenon, <1>2
          DEF Seed!RecognizedSeedTransition

THEOREM PhaseSubmitTransitionRefinesSeed ==
  PhaseSubmitTransition => Seed!RecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME PhaseSubmitTransition
               PROVE Seed!RecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              b \in Bindings,
              a \in Authorities,
              value \in TerminalResolutions :
          PhaseSubmit(r, b, a, value)
       BY Zenon DEF PhaseSubmitTransition
  <1>2. Seed!SubmitResolution(r, b, a, value)
       BY <1>1, PhaseSubmitRefinesSeedSubmit
  <1>3. value \in Seed!TerminalResolutions
       BY <1>1, PhaseSubmitValueIsSeedTerminal
  <1> QED
       BY Zenon, <1>2, <1>3
          DEF Seed!RecognizedSeedTransition

THEOREM PhaseConflictTransitionRefinesSeed ==
  PhaseConflictTransition => Seed!RecognizedEnvironmentTransition
PROOF
  <1> SUFFICES ASSUME PhaseConflictTransition
               PROVE Seed!RecognizedEnvironmentTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds :
          PhaseObserveConflict(r)
       BY Zenon DEF PhaseConflictTransition
  <1>2. Seed!ObserveConflict(r)
       BY <1>1, PhaseConflictRefinesSeedConflict
  <1> QED
       BY <1>2
          DEF Seed!RecognizedEnvironmentTransition

THEOREM PhaseRecognizedTransitionRefinesSeed ==
  PhaseRecognizedSeedTransition => Seed!RecognizedSeedTransition
PROOF
  BY Zenon,
     PhaseRegisterTransitionRefinesSeed,
     PhaseSubmitTransitionRefinesSeed
     DEF PhaseRecognizedSeedTransition,
         PhaseRegisterTransition,
         PhaseSubmitTransition

THEOREM PhaseEnvironmentTransitionRefinesSeed ==
  PhaseRecognizedEnvironmentTransition => Seed!RecognizedEnvironmentTransition
PROOF
  BY SMTT(60),
     PhaseConflictTransitionRefinesSeed
     DEF PhaseRecognizedEnvironmentTransition,
         PhaseConflictTransition

THEOREM PhaseNextRefinesSeedNext ==
  PhaseNext => Seed!Next
PROOF
  BY SMTT(60),
     PhaseRecognizedTransitionRefinesSeed,
     PhaseEnvironmentTransitionRefinesSeed
     DEF PhaseNext,
         Seed!Next

(***************************************************************************)
(* Derived-view stutter.                                                   *)
(***************************************************************************)

THEOREM PhaseMetaStutterPreservesRequestMeta ==
  UNCHANGED phaseMeta => UNCHANGED PhaseRequestMeta
PROOF
  BY SMTT(60)
     DEF PhaseRequestMeta,
         PhaseRequests,
         PhaseBinding,
         PhasePrevious

THEOREM PhaseMetaStutterPreservesTerminalMeta ==
  UNCHANGED phaseMeta => UNCHANGED PhaseTerminalMeta
PROOF
  BY SMTT(60)
     DEF PhaseTerminalMeta,
         PhaseTerminalRequests,
         PhaseTerminalResolution,
         PhaseAuthority,
         PhaseRequests,
         PhaseTag

THEOREM PhaseMetaStutterPreservesConflicts ==
  UNCHANGED phaseMeta => UNCHANGED PhaseConflicts
PROOF
  BY SMTT(60)
     DEF PhaseConflicts,
         PhaseRequests,
         PhaseTag

THEOREM PhaseStateStutterStuttersSeed ==
  UNCHANGED phaseVars => UNCHANGED Seed!vars
PROOF
  BY SMTT(60),
     PhaseMetaStutterPreservesRequestMeta,
     PhaseMetaStutterPreservesTerminalMeta,
     PhaseMetaStutterPreservesConflicts
     DEF phaseVars,
         Seed!vars

THEOREM PhaseBoxNextRefinesSeedBoxNext ==
  [PhaseNext]_phaseVars => [Seed!Next]_Seed!vars
PROOF
  BY SMTT(120),
     PhaseNextRefinesSeedNext,
     PhaseStateStutterStuttersSeed

THEOREM CanonicalPhaseSeedRefinesSeedResolution ==
  PhaseSpec => Seed!Spec
PROOF
  BY PTL,
     PhaseInitRefinesSeedInit,
     PhaseBoxNextRefinesSeedBoxNext
     DEF PhaseSpec,
         Seed!Spec

=============================================================================
