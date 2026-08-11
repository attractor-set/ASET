------------- MODULE SeedToCanonicalPhaseSeedRefinementProofs -------------
EXTENDS SeedResolution, TLAPS

CONSTANT NoAuthority
ASSUME NoAuthority \notin Authorities

SeedPhaseTag(r) ==
  IF r \notin TerminalRequests
  THEN "PENDING"
  ELSE IF r \in conflicts
       THEN IF TerminalResolution(r) = "ALLOW"
            THEN "INVALIDATED_ALLOW"
            ELSE "INVALIDATED_BLOCK"
       ELSE TerminalResolution(r)

SeedPhaseAuthority(r) ==
  IF r \in TerminalRequests
  THEN terminalMeta[r].authority
  ELSE NoAuthority


PhaseMetaFromSeed ==
  [r \in Requests |->
     [phase |->
        IF r \notin TerminalRequests
        THEN "PENDING"
        ELSE IF r \in conflicts
             THEN IF terminalMeta[r].resolution = "ALLOW"
                  THEN "INVALIDATED_ALLOW"
                  ELSE "INVALIDATED_BLOCK"
             ELSE terminalMeta[r].resolution,
      binding |-> requestMeta[r].binding,
      previous |-> requestMeta[r].previous,
      authority |->
        IF r \in TerminalRequests
        THEN terminalMeta[r].authority
        ELSE NoAuthority]]


PhaseMetaFromSeedNext ==
  [r \in DOMAIN requestMeta' |->
     [phase |->
        IF r \notin DOMAIN terminalMeta'
        THEN "PENDING"
        ELSE IF r \in conflicts'
             THEN IF terminalMeta'[r].resolution = "ALLOW"
                  THEN "INVALIDATED_ALLOW"
                  ELSE "INVALIDATED_BLOCK"
             ELSE terminalMeta'[r].resolution,
      binding |-> requestMeta'[r].binding,
      previous |-> requestMeta'[r].previous,
      authority |->
        IF r \in DOMAIN terminalMeta'
        THEN terminalMeta'[r].authority
        ELSE NoAuthority]]

THEOREM PhaseMetaPrimeEqualsExplicitNext ==
  PhaseMetaFromSeed' = PhaseMetaFromSeedNext
PROOF
  BY DEF PhaseMetaFromSeed,
         PhaseMetaFromSeedNext,
         Requests,
         TerminalRequests


THEOREM PhaseMetaFromSeedNextEntryExpansion ==
  \A x \in DOMAIN requestMeta' :
    PhaseMetaFromSeedNext[x] =
      [phase |->
         IF x \notin DOMAIN terminalMeta'
         THEN "PENDING"
         ELSE IF x \in conflicts'
              THEN IF terminalMeta'[x].resolution = "ALLOW"
                   THEN "INVALIDATED_ALLOW"
                   ELSE "INVALIDATED_BLOCK"
              ELSE terminalMeta'[x].resolution,
       binding |-> requestMeta'[x].binding,
       previous |-> requestMeta'[x].previous,
       authority |->
         IF x \in DOMAIN terminalMeta'
         THEN terminalMeta'[x].authority
         ELSE NoAuthority]
PROOF
  BY DEF PhaseMetaFromSeedNext

Phase == INSTANCE CanonicalPhaseSeed
  WITH ResolutionIds <- ResolutionIds,
       Bindings <- Bindings,
       Authorities <- Authorities,
       TerminalCommitments <- TerminalCommitments,
       RecognizedTerminalCommitments <- RecognizedTerminalCommitments,
       NoCommitment <- NoCommitment,
       RecognizedAuthorityBindings <- RecognizedAuthorityBindings,
       NoAuthority <- NoAuthority,
       phaseMeta <- PhaseMetaFromSeed

SeedShapeOK ==
  /\ TerminalRequests \subseteq Requests
  /\ conflicts \subseteq TerminalRequests
  /\ \A r \in TerminalRequests :
       /\ TerminalResolution(r) \in TerminalResolutions
       /\ terminalMeta[r].authority \in Authorities
  /\ \A r \in Requests :
       /\ requestMeta[r].binding \in Bindings
       /\ requestMeta[r].previous = NoCommitment
          \/ requestMeta[r].previous \in RecognizedTerminalCommitments

THEOREM SeedInitImpliesShapeOK ==
  Init => SeedShapeOK
PROOF
  BY SMTT(60)
     DEF Init,
         SeedShapeOK,
         Requests,
         TerminalRequests

THEOREM SeedRegisterPreservesShapeOK ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous) => SeedShapeOK'
PROOF
  BY SMTT(240)
     DEF SeedShapeOK,
         RegisterRequest,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalResolution

THEOREM SeedSubmitPreservesShapeOK ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value) => SeedShapeOK'
PROOF
  BY SMTT(240)
     DEF SeedShapeOK,
         SubmitResolution,
         Requests,
         TerminalRequests,
         TerminalResolution,
         RequestBinding,
         TerminalResolutions

THEOREM SeedConflictPreservesShapeOK ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r) => SeedShapeOK'
PROOF
  BY SMTT(180)
     DEF SeedShapeOK,
         ObserveConflict,
         Requests,
         TerminalRequests,
         TerminalResolution,
         seedVars

THEOREM SeedNextPreservesShapeOK ==
  /\ SeedShapeOK
  /\ Next
  => SeedShapeOK'
PROOF
  BY SMTT(240),
     SeedRegisterPreservesShapeOK,
     SeedSubmitPreservesShapeOK,
     SeedConflictPreservesShapeOK
     DEF Next,
         RecognizedSeedTransition,
         RecognizedEnvironmentTransition

THEOREM SeedStateStutterPreservesShapeOK ==
  /\ SeedShapeOK
  /\ UNCHANGED vars
  => SeedShapeOK'
PROOF
  BY SMTT(60)
     DEF SeedShapeOK,
         vars,
         Requests,
         TerminalRequests,
         TerminalResolution

THEOREM SeedBoxNextPreservesShapeOK ==
  /\ SeedShapeOK
  /\ [Next]_vars
  => SeedShapeOK'
PROOF
  BY SMTT(120),
     SeedNextPreservesShapeOK,
     SeedStateStutterPreservesShapeOK

THEOREM SeedSpecImpliesAlwaysShapeOK ==
  Spec => []SeedShapeOK
PROOF
  BY PTL,
     SeedInitImpliesShapeOK,
     SeedBoxNextPreservesShapeOK
     DEF Spec

THEOREM PhaseRequestsEqualSeedRequests ==
  Phase!PhaseRequests = Requests
PROOF
  BY DEF Phase!PhaseRequests,
         PhaseMetaFromSeed,
         Requests

THEOREM PhaseTagMatchesSeedPhaseTag ==
  \A r \in Requests :
    Phase!PhaseTag(r) = SeedPhaseTag(r)
PROOF
  BY SMTT(120)
     DEF Phase!PhaseTag,
         PhaseMetaFromSeed,
         SeedPhaseTag,
         TerminalResolution,
         Requests,
         TerminalRequests

THEOREM PhaseBindingMatchesSeedRequest ==
  \A r \in Requests :
    Phase!PhaseBinding(r) = requestMeta[r].binding
PROOF
  BY SMTT(60)
     DEF Phase!PhaseBinding,
         PhaseMetaFromSeed,
         Requests

THEOREM PhasePreviousMatchesSeedRequest ==
  \A r \in Requests :
    Phase!PhasePrevious(r) = requestMeta[r].previous
PROOF
  BY SMTT(60)
     DEF Phase!PhasePrevious,
         PhaseMetaFromSeed,
         Requests

THEOREM PhaseTerminalResolutionsEqualSeedTerminalResolutions ==
  Phase!TerminalResolutions = TerminalResolutions
PROOF
  BY DEF Phase!TerminalResolutions, TerminalResolutions

THEOREM SeedInitRefinesPhaseInit ==
  Init => Phase!PhaseInit
PROOF
  BY DEF Init,
         Phase!PhaseInit,
         PhaseMetaFromSeed,
         Requests

(***************************************************************************)
(* Register -> phase update.                                               *)
(***************************************************************************)


THEOREM SeedShapeTerminalRequestsSubsetRequests ==
  SeedShapeOK => TerminalRequests \subseteq Requests
PROOF
  BY DEF SeedShapeOK


THEOREM PhaseAuthorityMatchesSeedTerminal ==
  SeedShapeOK =>
  \A r \in TerminalRequests :
    Phase!PhaseAuthority(r) = terminalMeta[r].authority
PROOF
  BY SMTT(120),
     SeedShapeTerminalRequestsSubsetRequests
     DEF Phase!PhaseAuthority,
         PhaseMetaFromSeed,
         Requests,
         TerminalRequests

THEOREM SeedRegisterFreshNotTerminal ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => r \notin TerminalRequests
PROOF
  BY SMTT(60),
     SeedShapeTerminalRequestsSubsetRequests
     DEF RegisterRequest


THEOREM SeedRegisterRequestsUpdate ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => Requests' = Requests \cup {r}
PROOF
  BY SMTT(60)
     DEF RegisterRequest, Requests

THEOREM SeedRegisterTerminalRequestsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => UNCHANGED TerminalRequests
PROOF
  BY SMTT(60)
     DEF RegisterRequest, TerminalRequests

THEOREM SeedRegisterConflictsUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => UNCHANGED conflicts
PROOF
  BY DEF RegisterRequest

THEOREM SeedRegisterTerminalMetaUnchangedRaw ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => UNCHANGED terminalMeta
PROOF
  BY DEF RegisterRequest

THEOREM SeedRegisterTargetRequestMeta ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    requestMeta'[r] =
      [binding |-> b, previous |-> previous]
PROOF
  BY SMTT(120)
     DEF RegisterRequest,
         Requests

THEOREM SeedRegisterExistingRequestMetaUnchanged ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    \A x \in Requests :
      requestMeta'[x] = requestMeta[x]
PROOF
  BY SMTT(180)
     DEF RegisterRequest,
         Requests

THEOREM SeedRegisterTargetInNextRequestDomain ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => r \in DOMAIN requestMeta'
PROOF
  BY SMTT(120),
     SeedRegisterRequestsUpdate
     DEF Requests

THEOREM SeedRegisterExistingInNextRequestDomain ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => \A x \in Requests : x \in DOMAIN requestMeta'
PROOF
  BY SMTT(120),
     SeedRegisterRequestsUpdate
     DEF Requests

THEOREM SeedRegisterTargetNotInNextTerminalDomain ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => r \notin DOMAIN terminalMeta'
PROOF
  BY SMTT(120),
     SeedRegisterFreshNotTerminal,
     SeedRegisterTerminalMetaUnchangedRaw
     DEF TerminalRequests

THEOREM SeedRegisterNewPhaseTagPending ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => PhaseMetaFromSeedNext[r].phase = "PENDING"
PROOF
  BY SMTT(120),
     SeedRegisterTargetInNextRequestDomain,
     SeedRegisterTargetNotInNextTerminalDomain
     DEF PhaseMetaFromSeedNext

THEOREM SeedRegisterNewPhaseAuthorityNone ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => PhaseMetaFromSeedNext[r].authority = NoAuthority
PROOF
  BY SMTT(120),
     SeedRegisterTargetInNextRequestDomain,
     SeedRegisterTargetNotInNextTerminalDomain
     DEF PhaseMetaFromSeedNext

THEOREM SeedRegisterNewPhaseBinding ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => PhaseMetaFromSeedNext[r].binding = b
PROOF
  BY SMTT(120),
     SeedRegisterTargetInNextRequestDomain,
     SeedRegisterTargetRequestMeta
     DEF PhaseMetaFromSeedNext

THEOREM SeedRegisterNewPhasePrevious ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => PhaseMetaFromSeedNext[r].previous = previous
PROOF
  BY SMTT(120),
     SeedRegisterTargetInNextRequestDomain,
     SeedRegisterTargetRequestMeta
     DEF PhaseMetaFromSeedNext

THEOREM SeedRegisterExistingPhaseEntryUnchanged ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    \A x \in Requests :
      PhaseMetaFromSeedNext[x] = PhaseMetaFromSeed[x]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               NEW b \in Bindings,
               NEW a \in Authorities,
               NEW previous \in TerminalCommitments \cup {NoCommitment},
               RegisterRequest(r, b, a, previous)
        PROVE
          \A x \in Requests :
            PhaseMetaFromSeedNext[x] = PhaseMetaFromSeed[x]
       OBVIOUS
  <1>1. TAKE x \in Requests
  <1>2. x \in DOMAIN requestMeta'
       BY SeedRegisterExistingInNextRequestDomain
  <1>3. requestMeta'[x] = requestMeta[x]
       BY SeedRegisterExistingRequestMetaUnchanged
  <1>4. terminalMeta' = terminalMeta
       BY SeedRegisterTerminalMetaUnchangedRaw
  <1>5. conflicts' = conflicts
       BY SeedRegisterConflictsUnchanged
  <1> QED
       BY SMTT(120), <1>2, <1>3, <1>4, <1>5
          DEF PhaseMetaFromSeed,
              PhaseMetaFromSeedNext,
              Requests,
              TerminalRequests

THEOREM SeedRegisterNewPhaseEntry ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    PhaseMetaFromSeedNext[r] =
      [phase |-> "PENDING",
       binding |-> b,
       previous |-> previous,
       authority |-> NoAuthority]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               NEW b \in Bindings,
               NEW a \in Authorities,
               NEW previous \in TerminalCommitments \cup {NoCommitment},
               RegisterRequest(r, b, a, previous)
        PROVE
          PhaseMetaFromSeedNext[r] =
            [phase |-> "PENDING",
             binding |-> b,
             previous |-> previous,
             authority |-> NoAuthority]
       OBVIOUS
  <1>1. r \in DOMAIN requestMeta'
       BY SeedRegisterTargetInNextRequestDomain
  <1>2. PhaseMetaFromSeedNext[r] =
          [phase |->
             IF r \notin DOMAIN terminalMeta'
             THEN "PENDING"
             ELSE IF r \in conflicts'
                  THEN IF terminalMeta'[r].resolution = "ALLOW"
                       THEN "INVALIDATED_ALLOW"
                       ELSE "INVALIDATED_BLOCK"
                  ELSE terminalMeta'[r].resolution,
           binding |-> requestMeta'[r].binding,
           previous |-> requestMeta'[r].previous,
           authority |->
             IF r \in DOMAIN terminalMeta'
             THEN terminalMeta'[r].authority
             ELSE NoAuthority]
       BY <1>1, PhaseMetaFromSeedNextEntryExpansion
  <1>3. r \notin DOMAIN terminalMeta'
       BY SeedRegisterTargetNotInNextTerminalDomain
  <1>4. requestMeta'[r] =
          [binding |-> b, previous |-> previous]
       BY SeedRegisterTargetRequestMeta
  <1> QED
       BY SMTT(120), <1>2, <1>3, <1>4

THEOREM SeedRegisterExplicitNextDomain ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    DOMAIN PhaseMetaFromSeedNext =
      Phase!PhaseRequests \cup {r}
PROOF
  BY SMTT(120),
     PhaseRequestsEqualSeedRequests,
     SeedRegisterRequestsUpdate
     DEF PhaseMetaFromSeedNext,
         Phase!PhaseRequests,
         Requests

THEOREM SeedRegisterExplicitNextPointwise ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    \A x \in Phase!PhaseRequests \cup {r} :
      PhaseMetaFromSeedNext[x] =
        IF x = r
        THEN [phase |-> "PENDING",
              binding |-> b,
              previous |-> previous,
              authority |-> NoAuthority]
        ELSE PhaseMetaFromSeed[x]
PROOF
  BY SMTT(180),
     PhaseRequestsEqualSeedRequests,
     SeedRegisterNewPhaseEntry,
     SeedRegisterExistingPhaseEntryUnchanged

THEOREM SeedRegisterProducesExplicitNextUpdate ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    PhaseMetaFromSeedNext =
      [x \in Phase!PhaseRequests \cup {r} |->
         IF x = r
         THEN [phase |-> "PENDING",
               binding |-> b,
               previous |-> previous,
               authority |-> NoAuthority]
         ELSE PhaseMetaFromSeed[x]]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               NEW b \in Bindings,
               NEW a \in Authorities,
               NEW previous \in TerminalCommitments \cup {NoCommitment},
               RegisterRequest(r, b, a, previous)
        PROVE
          PhaseMetaFromSeedNext =
            [x \in Phase!PhaseRequests \cup {r} |->
               IF x = r
               THEN [phase |-> "PENDING",
                     binding |-> b,
                     previous |-> previous,
                     authority |-> NoAuthority]
               ELSE PhaseMetaFromSeed[x]]
       OBVIOUS
  <1>1. DOMAIN PhaseMetaFromSeedNext =
          Phase!PhaseRequests \cup {r}
       BY SeedRegisterExplicitNextDomain
  <1>2. \A x \in Phase!PhaseRequests \cup {r} :
          PhaseMetaFromSeedNext[x] =
            IF x = r
            THEN [phase |-> "PENDING",
                  binding |-> b,
                  previous |-> previous,
                  authority |-> NoAuthority]
            ELSE PhaseMetaFromSeed[x]
       BY SeedRegisterExplicitNextPointwise
  <1> QED
       BY SMTT(120), <1>1, <1>2
          DEF PhaseMetaFromSeedNext

THEOREM SeedRegisterProducesPhaseUpdate ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
    PhaseMetaFromSeed' =
      [x \in Phase!PhaseRequests \cup {r} |->
         IF x = r
         THEN [phase |-> "PENDING",
               binding |-> b,
               previous |-> previous,
               authority |-> NoAuthority]
         ELSE PhaseMetaFromSeed[x]]
PROOF
  BY SMTT(60),
     PhaseMetaPrimeEqualsExplicitNext,
     SeedRegisterProducesExplicitNextUpdate

THEOREM SeedRegisterFreshInPhase ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => r \in ResolutionIds \ Phase!PhaseRequests
PROOF
  BY SMTT(60),
     PhaseRequestsEqualSeedRequests
     DEF RegisterRequest

THEOREM SeedRegisterPhaseGuards ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      =>
      /\ r \in ResolutionIds \ Phase!PhaseRequests
      /\ b \in Bindings
      /\ a \in Authorities
      /\ <<a, b>> \in RecognizedAuthorityBindings
      /\ \/ previous = NoCommitment
         \/ previous \in RecognizedTerminalCommitments
PROOF
  BY ZenonT(120),
     SeedRegisterFreshInPhase
     DEF RegisterRequest

THEOREM SeedRegisterRefinesPhaseRegister ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)
      => Phase!PhaseRegister(r, b, a, previous)
PROOF
  BY SMTT(120),
     SeedRegisterPhaseGuards,
     SeedRegisterProducesPhaseUpdate
     DEF Phase!PhaseRegister

(***************************************************************************)
(* Submit -> phase update. The existing update theorem is retained and     *)
(* action guards are made explicit.                                       *)
(***************************************************************************)

THEOREM SeedSubmitStartsFromPendingPhase ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      => Phase!PhaseTag(r) = "PENDING"
PROOF
  BY SMTT(120),
     PhaseRequestsEqualSeedRequests
     DEF SubmitResolution,
         Phase!PhaseTag,
         PhaseMetaFromSeed,
         SeedPhaseTag,
         Requests,
         TerminalRequests

THEOREM SeedSubmitBindingMatchesPhase ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      => b = Phase!PhaseBinding(r)
PROOF
  BY SMTT(120)
     DEF SubmitResolution,
         RequestBinding,
         Phase!PhaseBinding,
         PhaseMetaFromSeed,
         Requests

THEOREM SeedSubmitRequestExistsInPhase ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      => r \in Phase!PhaseRequests
PROOF
  BY SMTT(60),
     PhaseRequestsEqualSeedRequests
     DEF SubmitResolution

THEOREM SeedSubmitValueIsPhaseTerminal ==
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      => value \in Phase!TerminalResolutions
PROOF
  BY SMTT(60),
     PhaseTerminalResolutionsEqualSeedTerminalResolutions
     DEF SubmitResolution

THEOREM SeedSubmitProducesPhaseUpdate ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      =>
    PhaseMetaFromSeed' =
      [x \in Phase!PhaseRequests |->
         IF x = r
         THEN [phase |-> value,
               binding |-> Phase!PhaseBinding(r),
               previous |-> Phase!PhasePrevious(r),
               authority |-> a]
         ELSE PhaseMetaFromSeed[x]]
PROOF
  BY SMTT(300),
     PhaseRequestsEqualSeedRequests,
     SeedSubmitStartsFromPendingPhase,
     SeedSubmitBindingMatchesPhase
     DEF SubmitResolution,
         PhaseMetaFromSeed,
         SeedPhaseTag,
         SeedPhaseAuthority,
         Requests,
         TerminalRequests,
         RequestBinding,
         TerminalResolution,
         Phase!PhaseBinding,
         Phase!PhasePrevious,
         Phase!PhaseRequests

THEOREM SeedSubmitPhaseGuards ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      =>
      /\ r \in Phase!PhaseRequests
      /\ Phase!PhaseTag(r) = "PENDING"
      /\ b = Phase!PhaseBinding(r)
      /\ a \in Authorities
      /\ <<a, b>> \in RecognizedAuthorityBindings
      /\ value \in Phase!TerminalResolutions
PROOF
  BY ZenonT(120),
     SeedSubmitRequestExistsInPhase,
     SeedSubmitStartsFromPendingPhase,
     SeedSubmitBindingMatchesPhase,
     SeedSubmitValueIsPhaseTerminal
     DEF SubmitResolution

THEOREM SeedSubmitRefinesPhaseSubmit ==
  SeedShapeOK =>
  \A r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)
      => Phase!PhaseSubmit(r, b, a, value)
PROOF
  BY SMTT(120),
     SeedSubmitPhaseGuards,
     SeedSubmitProducesPhaseUpdate
     DEF Phase!PhaseSubmit

(***************************************************************************)
(* Conflict -> phase update.                                               *)
(***************************************************************************)

THEOREM SeedConflictRequestExists ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r) => r \in Requests
PROOF
  BY SMTT(60),
     SeedShapeTerminalRequestsSubsetRequests
     DEF ObserveConflict,
         TerminalRequests,
         Requests

THEOREM SeedConflictRequestExistsInPhase ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r) => r \in Phase!PhaseRequests
PROOF
  BY SMTT(60),
     PhaseRequestsEqualSeedRequests,
     SeedConflictRequestExists

THEOREM SeedConflictTerminalResolutionTyped ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      => TerminalResolution(r) \in TerminalResolutions
PROOF
  BY SMTT(60)
     DEF SeedShapeOK,
         ObserveConflict

THEOREM SeedConflictTagEqualsTerminalResolution ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      => Phase!PhaseTag(r) = TerminalResolution(r)
PROOF
  BY SMTT(120),
     SeedConflictRequestExists,
     PhaseTagMatchesSeedPhaseTag
     DEF ObserveConflict,
         SeedPhaseTag

THEOREM SeedConflictStartsFromActiveTerminalPhase ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      => Phase!PhaseTag(r) \in {"ALLOW", "BLOCK"}
PROOF
  BY SMTT(60),
     SeedConflictTagEqualsTerminalResolution,
     SeedConflictTerminalResolutionTyped
     DEF TerminalResolutions

THEOREM SeedConflictRequestsUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED Requests
PROOF
  BY SMTT(60)
     DEF ObserveConflict,
         seedVars,
         Requests

THEOREM SeedConflictTerminalRequestsUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED TerminalRequests
PROOF
  BY SMTT(60)
     DEF ObserveConflict,
         seedVars,
         TerminalRequests

THEOREM SeedConflictRequestMetaUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED requestMeta
PROOF
  BY DEF ObserveConflict, seedVars

THEOREM SeedConflictTerminalMetaUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED terminalMeta
PROOF
  BY DEF ObserveConflict, seedVars

THEOREM SeedConflictRequestMetaUnchangedRaw ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED requestMeta
PROOF
  BY DEF ObserveConflict,
         seedVars

THEOREM SeedConflictTerminalMetaUnchangedRaw ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => UNCHANGED terminalMeta
PROOF
  BY DEF ObserveConflict,
         seedVars

THEOREM SeedConflictTargetInNextRequestDomain ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r) => r \in DOMAIN requestMeta'
PROOF
  BY SMTT(120),
     SeedConflictRequestExists,
     SeedConflictRequestMetaUnchangedRaw
     DEF Requests

THEOREM SeedConflictTargetInNextTerminalDomain ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => r \in DOMAIN terminalMeta'
PROOF
  BY SMTT(120),
     SeedConflictTerminalMetaUnchangedRaw
     DEF ObserveConflict,
         TerminalRequests

THEOREM SeedConflictTargetInNextConflicts ==
  \A r \in ResolutionIds :
    ObserveConflict(r) => r \in conflicts'
PROOF
  BY SMTT(60)
     DEF ObserveConflict

THEOREM SeedConflictTargetTerminalMetaUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r)
      => terminalMeta'[r] = terminalMeta[r]
PROOF
  BY SMTT(60),
     SeedConflictTerminalMetaUnchangedRaw

THEOREM SeedConflictOtherConflictMembershipUnchanged ==
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    \A x \in Requests \ {r} :
      (x \in conflicts' <=> x \in conflicts)
PROOF
  BY SMTT(120)
     DEF ObserveConflict

THEOREM SeedConflictExistingInNextRequestDomain ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      => \A x \in Requests : x \in DOMAIN requestMeta'
PROOF
  BY SMTT(120),
     SeedConflictRequestMetaUnchangedRaw
     DEF Requests

THEOREM SeedConflictTargetTagInvalidated ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext[r].phase =
      IF Phase!PhaseTag(r) = "ALLOW"
      THEN "INVALIDATED_ALLOW"
      ELSE "INVALIDATED_BLOCK"
PROOF
  BY SMTT(180),
     SeedConflictTargetInNextRequestDomain,
     SeedConflictTargetInNextTerminalDomain,
     SeedConflictTargetInNextConflicts,
     SeedConflictTargetTerminalMetaUnchanged,
     SeedConflictTagEqualsTerminalResolution
     DEF PhaseMetaFromSeedNext,
         TerminalResolution

THEOREM SeedConflictTargetAuthorityUnchanged ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext[r].authority =
      Phase!PhaseAuthority(r)
PROOF
  BY SMTT(180),
     SeedConflictTargetInNextRequestDomain,
     SeedConflictTargetInNextTerminalDomain,
     SeedConflictTargetTerminalMetaUnchanged,
     PhaseAuthorityMatchesSeedTerminal
     DEF ObserveConflict,
         PhaseMetaFromSeedNext,
         TerminalRequests

THEOREM SeedConflictTargetBindingUnchanged ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext[r].binding =
      Phase!PhaseBinding(r)
PROOF
  BY SMTT(120),
     SeedConflictTargetInNextRequestDomain,
     SeedConflictRequestMetaUnchangedRaw,
     PhaseBindingMatchesSeedRequest,
     SeedConflictRequestExists
     DEF PhaseMetaFromSeedNext

THEOREM SeedConflictTargetPreviousUnchanged ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext[r].previous =
      Phase!PhasePrevious(r)
PROOF
  BY SMTT(120),
     SeedConflictTargetInNextRequestDomain,
     SeedConflictRequestMetaUnchangedRaw,
     PhasePreviousMatchesSeedRequest,
     SeedConflictRequestExists
     DEF PhaseMetaFromSeedNext

THEOREM SeedConflictExistingOtherPhaseEntryUnchanged ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    \A x \in Requests \ {r} :
      PhaseMetaFromSeedNext[x] = PhaseMetaFromSeed[x]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               ObserveConflict(r)
        PROVE
          \A x \in Requests \ {r} :
            PhaseMetaFromSeedNext[x] = PhaseMetaFromSeed[x]
       OBVIOUS
  <1>1. TAKE x \in Requests \ {r}
  <1>2. x \in DOMAIN requestMeta'
       BY SeedConflictExistingInNextRequestDomain
  <1>3. requestMeta' = requestMeta
       BY SeedConflictRequestMetaUnchangedRaw
  <1>4. terminalMeta' = terminalMeta
       BY SeedConflictTerminalMetaUnchangedRaw
  <1>5. (x \in conflicts' <=> x \in conflicts)
       BY SeedConflictOtherConflictMembershipUnchanged
  <1> QED
       BY SMTT(120), <1>2, <1>3, <1>4, <1>5
          DEF PhaseMetaFromSeed,
              PhaseMetaFromSeedNext,
              Requests,
              TerminalRequests

THEOREM SeedConflictTargetPhaseEntry ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext[r] =
      [phase |->
         IF Phase!PhaseTag(r) = "ALLOW"
         THEN "INVALIDATED_ALLOW"
         ELSE "INVALIDATED_BLOCK",
       binding |-> Phase!PhaseBinding(r),
       previous |-> Phase!PhasePrevious(r),
       authority |-> Phase!PhaseAuthority(r)]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               ObserveConflict(r)
        PROVE
          PhaseMetaFromSeedNext[r] =
            [phase |->
               IF Phase!PhaseTag(r) = "ALLOW"
               THEN "INVALIDATED_ALLOW"
               ELSE "INVALIDATED_BLOCK",
             binding |-> Phase!PhaseBinding(r),
             previous |-> Phase!PhasePrevious(r),
             authority |-> Phase!PhaseAuthority(r)]
       OBVIOUS
  <1>1. r \in DOMAIN requestMeta'
       BY SeedConflictTargetInNextRequestDomain
  <1>2. PhaseMetaFromSeedNext[r] =
          [phase |->
             IF r \notin DOMAIN terminalMeta'
             THEN "PENDING"
             ELSE IF r \in conflicts'
                  THEN IF terminalMeta'[r].resolution = "ALLOW"
                       THEN "INVALIDATED_ALLOW"
                       ELSE "INVALIDATED_BLOCK"
                  ELSE terminalMeta'[r].resolution,
           binding |-> requestMeta'[r].binding,
           previous |-> requestMeta'[r].previous,
           authority |->
             IF r \in DOMAIN terminalMeta'
             THEN terminalMeta'[r].authority
             ELSE NoAuthority]
       BY <1>1, PhaseMetaFromSeedNextEntryExpansion
  <1>3. r \in DOMAIN terminalMeta'
       BY SeedConflictTargetInNextTerminalDomain
  <1>4. r \in conflicts'
       BY SeedConflictTargetInNextConflicts
  <1>5. terminalMeta'[r] = terminalMeta[r]
       BY SeedConflictTargetTerminalMetaUnchanged
  <1>6. requestMeta' = requestMeta
       BY SeedConflictRequestMetaUnchangedRaw
  <1>7. Phase!PhaseTag(r) = TerminalResolution(r)
       BY SeedConflictTagEqualsTerminalResolution
  <1>8. Phase!PhaseBinding(r) = requestMeta[r].binding
       BY SeedConflictRequestExists, PhaseBindingMatchesSeedRequest
  <1>9. Phase!PhasePrevious(r) = requestMeta[r].previous
       BY SeedConflictRequestExists, PhasePreviousMatchesSeedRequest
  <1>10. r \in TerminalRequests
       BY DEF ObserveConflict
  <1>11. Phase!PhaseAuthority(r) = terminalMeta[r].authority
       BY <1>10, PhaseAuthorityMatchesSeedTerminal
  <1> QED
       BY SMTT(180),
          <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>11
          DEF TerminalResolution

THEOREM SeedConflictExplicitNextDomain ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    DOMAIN PhaseMetaFromSeedNext =
      Phase!PhaseRequests
PROOF
  BY SMTT(120),
     PhaseRequestsEqualSeedRequests,
     SeedConflictRequestMetaUnchangedRaw
     DEF PhaseMetaFromSeedNext,
         Phase!PhaseRequests,
         Requests

THEOREM SeedConflictExplicitNextPointwise ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    \A x \in Phase!PhaseRequests :
      PhaseMetaFromSeedNext[x] =
        IF x = r
        THEN [phase |->
                IF Phase!PhaseTag(r) = "ALLOW"
                THEN "INVALIDATED_ALLOW"
                ELSE "INVALIDATED_BLOCK",
              binding |-> Phase!PhaseBinding(r),
              previous |-> Phase!PhasePrevious(r),
              authority |-> Phase!PhaseAuthority(r)]
        ELSE PhaseMetaFromSeed[x]
PROOF
  BY SMTT(180),
     PhaseRequestsEqualSeedRequests,
     SeedConflictTargetPhaseEntry,
     SeedConflictExistingOtherPhaseEntryUnchanged

THEOREM SeedConflictProducesExplicitNextUpdate ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeedNext =
      [x \in Phase!PhaseRequests |->
         IF x = r
         THEN [phase |->
                 IF Phase!PhaseTag(r) = "ALLOW"
                 THEN "INVALIDATED_ALLOW"
                 ELSE "INVALIDATED_BLOCK",
               binding |-> Phase!PhaseBinding(r),
               previous |-> Phase!PhasePrevious(r),
               authority |-> Phase!PhaseAuthority(r)]
         ELSE PhaseMetaFromSeed[x]]
PROOF
  <1> SUFFICES
        ASSUME SeedShapeOK,
               NEW r \in ResolutionIds,
               ObserveConflict(r)
        PROVE
          PhaseMetaFromSeedNext =
            [x \in Phase!PhaseRequests |->
               IF x = r
               THEN [phase |->
                       IF Phase!PhaseTag(r) = "ALLOW"
                       THEN "INVALIDATED_ALLOW"
                       ELSE "INVALIDATED_BLOCK",
                     binding |-> Phase!PhaseBinding(r),
                     previous |-> Phase!PhasePrevious(r),
                     authority |-> Phase!PhaseAuthority(r)]
               ELSE PhaseMetaFromSeed[x]]
       OBVIOUS
  <1>1. DOMAIN PhaseMetaFromSeedNext = Phase!PhaseRequests
       BY SeedConflictExplicitNextDomain
  <1>2. \A x \in Phase!PhaseRequests :
          PhaseMetaFromSeedNext[x] =
            IF x = r
            THEN [phase |->
                    IF Phase!PhaseTag(r) = "ALLOW"
                    THEN "INVALIDATED_ALLOW"
                    ELSE "INVALIDATED_BLOCK",
                  binding |-> Phase!PhaseBinding(r),
                  previous |-> Phase!PhasePrevious(r),
                  authority |-> Phase!PhaseAuthority(r)]
            ELSE PhaseMetaFromSeed[x]
       BY SeedConflictExplicitNextPointwise
  <1> QED
       BY SMTT(120), <1>1, <1>2
          DEF PhaseMetaFromSeedNext

THEOREM SeedConflictProducesPhaseUpdate ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r)
      =>
    PhaseMetaFromSeed' =
      [x \in Phase!PhaseRequests |->
         IF x = r
         THEN [phase |->
                 IF Phase!PhaseTag(r) = "ALLOW"
                 THEN "INVALIDATED_ALLOW"
                 ELSE "INVALIDATED_BLOCK",
               binding |-> Phase!PhaseBinding(r),
               previous |-> Phase!PhasePrevious(r),
               authority |-> Phase!PhaseAuthority(r)]
         ELSE PhaseMetaFromSeed[x]]
PROOF
  BY SMTT(60),
     PhaseMetaPrimeEqualsExplicitNext,
     SeedConflictProducesExplicitNextUpdate

THEOREM SeedConflictRefinesPhaseConflict ==
  SeedShapeOK =>
  \A r \in ResolutionIds :
    ObserveConflict(r) => Phase!PhaseObserveConflict(r)
PROOF
  BY SMTT(120),
     SeedConflictRequestExistsInPhase,
     SeedConflictStartsFromActiveTerminalPhase,
     SeedConflictProducesPhaseUpdate
     DEF Phase!PhaseObserveConflict

(***************************************************************************)
(* Existential transition assembly.                                       *)
(***************************************************************************)

SeedRegisterTransition ==
  \E r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     previous \in TerminalCommitments \cup {NoCommitment} :
    RegisterRequest(r, b, a, previous)

SeedSubmitTransition ==
  \E r \in ResolutionIds,
     b \in Bindings,
     a \in Authorities,
     value \in TerminalResolutions :
    SubmitResolution(r, b, a, value)

SeedConflictTransition ==
  \E r \in ResolutionIds :
    ObserveConflict(r)

THEOREM SeedRegisterTransitionRefinesPhase ==
  SeedShapeOK =>
  SeedRegisterTransition => Phase!PhaseRecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME SeedShapeOK, SeedRegisterTransition
               PROVE Phase!PhaseRecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              b \in Bindings,
              a \in Authorities,
              previous \in TerminalCommitments \cup {NoCommitment} :
          RegisterRequest(r, b, a, previous)
       BY Zenon DEF SeedRegisterTransition
  <1>2. Phase!PhaseRegister(r, b, a, previous)
       BY <1>1, SeedShapeOK, SeedRegisterRefinesPhaseRegister
  <1> QED
       BY Zenon, <1>2
          DEF Phase!PhaseRecognizedSeedTransition

THEOREM SeedSubmitTransitionRefinesPhase ==
  SeedShapeOK =>
    SeedSubmitTransition => Phase!PhaseRecognizedSeedTransition
PROOF
  <1> SUFFICES ASSUME SeedShapeOK, SeedSubmitTransition
               PROVE Phase!PhaseRecognizedSeedTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds,
              b \in Bindings,
              a \in Authorities,
              value \in TerminalResolutions :
          SubmitResolution(r, b, a, value)
       BY Zenon DEF SeedSubmitTransition
  <1>2. Phase!PhaseSubmit(r, b, a, value)
       BY <1>1, SeedShapeOK, SeedSubmitRefinesPhaseSubmit
  <1>3. value \in Phase!TerminalResolutions
       BY <1>1, SeedSubmitValueIsPhaseTerminal
  <1> QED
       BY Zenon, <1>2, <1>3
          DEF Phase!PhaseRecognizedSeedTransition

THEOREM SeedConflictTransitionRefinesPhase ==
  SeedShapeOK =>
    SeedConflictTransition => Phase!PhaseRecognizedEnvironmentTransition
PROOF
  <1> SUFFICES ASSUME SeedShapeOK, SeedConflictTransition
               PROVE Phase!PhaseRecognizedEnvironmentTransition
       OBVIOUS
  <1>1. PICK r \in ResolutionIds :
          ObserveConflict(r)
       BY Zenon DEF SeedConflictTransition
  <1>2. Phase!PhaseObserveConflict(r)
       BY <1>1, SeedShapeOK, SeedConflictRefinesPhaseConflict
  <1> QED
       BY <1>2
          DEF Phase!PhaseRecognizedEnvironmentTransition

THEOREM SeedRecognizedTransitionRefinesPhase ==
  SeedShapeOK =>
    RecognizedSeedTransition => Phase!PhaseRecognizedSeedTransition
PROOF
  BY Zenon,
     SeedRegisterTransitionRefinesPhase,
     SeedSubmitTransitionRefinesPhase
     DEF RecognizedSeedTransition,
         SeedRegisterTransition,
         SeedSubmitTransition

THEOREM SeedEnvironmentTransitionRefinesPhase ==
  SeedShapeOK =>
    RecognizedEnvironmentTransition
      => Phase!PhaseRecognizedEnvironmentTransition
PROOF
  BY SMTT(60),
     SeedConflictTransitionRefinesPhase
     DEF RecognizedEnvironmentTransition,
         SeedConflictTransition

THEOREM SeedNextRefinesPhaseNext ==
  /\ SeedShapeOK
  /\ Next
  => Phase!PhaseNext
PROOF
  BY SMTT(120),
     SeedRecognizedTransitionRefinesPhase,
     SeedEnvironmentTransitionRefinesPhase
     DEF Next,
         Phase!PhaseNext

THEOREM SeedStateStutterStuttersPhase ==
  UNCHANGED vars => UNCHANGED Phase!phaseVars
PROOF
  BY SMTT(180)
     DEF vars,
         Phase!phaseVars,
         PhaseMetaFromSeed,
         SeedPhaseTag,
         SeedPhaseAuthority,
         Requests,
         TerminalRequests,
         TerminalResolution

THEOREM SeedBoxNextRefinesPhaseBoxNext ==
  /\ SeedShapeOK
  /\ [Next]_vars
  => [Phase!PhaseNext]_Phase!phaseVars
PROOF
  BY SMTT(180),
     SeedNextRefinesPhaseNext,
     SeedStateStutterStuttersPhase

THEOREM SeedResolutionRefinesCanonicalPhaseSeed ==
  Spec => Phase!PhaseSpec
PROOF
  BY PTL,
     SeedSpecImpliesAlwaysShapeOK,
     SeedInitRefinesPhaseInit,
     SeedBoxNextRefinesPhaseBoxNext
     DEF Spec,
         Phase!PhaseSpec

=============================================================================
